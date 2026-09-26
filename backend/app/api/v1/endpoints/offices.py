from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user, require_admin
from app.models import Office, User
from app.schemas.management import OfficeInput, OfficeOutput, OfficeTypeOutput
from app.services.management_service import ManagementService

router = APIRouter()


@router.get("/", response_model=list[OfficeOutput])
def listing(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ManagementService(db).offices(user)


@router.get("/types", response_model=list[OfficeTypeOutput])
def office_types(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    return ManagementService(db).office_types()


@router.post("/", status_code=201, response_model=OfficeOutput)
def create(
    payload: OfficeInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).save_office(payload, user)


@router.put("/{identity}", response_model=OfficeOutput)
def update(
    identity: int,
    payload: OfficeInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).save_office(payload, user, identity)


@router.delete("/{identity}")
def delete(
    identity: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).deactivate(Office, identity, user)
