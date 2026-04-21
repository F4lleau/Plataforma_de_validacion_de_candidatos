import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.padron import AffiliateImportResponse
from app.services.affiliate_import_service import AffiliateImportService

router = APIRouter()


@router.post("/import", response_model=AffiliateImportResponse)
def import_padron(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        temp_file.write(file.file.read())
        temp_path = temp_file.name

    try:
        service = AffiliateImportService(db)
        batch = service.import_excel(
            file_path=temp_path,
            file_name=file.filename,
            imported_by=1,  # temporal: luego reemplazamos por current_user.id
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