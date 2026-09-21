import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.padron import AffiliateImportResponse
from app.services.affiliate_import_service import AffiliateImportService

router = APIRouter()


@router.post("/import", response_model=AffiliateImportResponse)
def import_padron(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if not (file.filename or "").lower().endswith((".xlsx",)):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel.")

    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    ) as temp_file:
        content = file.file.read(20 * 1024 * 1024 + 1)
        if len(content) > 20 * 1024 * 1024:
            os.unlink(temp_file.name)
            raise HTTPException(413, "El archivo supera 20 MB.")
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        service = AffiliateImportService(db)
        batch = service.import_excel(
            file_path=temp_path,
            file_name=file.filename,
            imported_by=current_user.id,
        )

        return AffiliateImportResponse(
            batch_id=batch.id,
            file_name=batch.file_name,
            total_rows=batch.total_rows,
            valid_rows=batch.valid_rows,
            invalid_rows=batch.invalid_rows,
            status=batch.status,
            imported_at=batch.imported_at,
        )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


from app.services.padron_service import PadronService


@router.get("")
def query(
    search: str = "",
    section: str = "",
    circuit: str = "",
    state: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return PadronService(db).query(search, section, circuit, state, page, page_size)


@router.get("/batches")
def batches(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    return PadronService(db).batches()
