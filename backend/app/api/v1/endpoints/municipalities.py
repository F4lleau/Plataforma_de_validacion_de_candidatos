from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user, require_admin
from app.models import Municipality, User
from app.schemas.management import MunicipalityInput, MunicipalityOutput
from app.services.management_service import ManagementService

router = APIRouter()


@router.get("/", response_model=list[MunicipalityOutput])
def listing(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ManagementService(db).catalogs(Municipality, user)


@router.post("/", status_code=201, response_model=MunicipalityOutput)
def create(
    payload: MunicipalityInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).catalog_save(Municipality, payload, user)


@router.put("/{identity}", response_model=MunicipalityOutput)
def update(
    identity: int,
    payload: MunicipalityInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).catalog_save(Municipality, payload, user, identity)
