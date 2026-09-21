from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.management import ApoderadoInput, ApoderadoOutput
from app.services.management_service import ManagementService

router = APIRouter()


@router.get("/", response_model=list[ApoderadoOutput])
def listing(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    return ManagementService(db).users()


@router.post("/", status_code=201, response_model=ApoderadoOutput)
def create(
    payload: ApoderadoInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).save_user(payload, user)


@router.put("/{identity}", response_model=ApoderadoOutput)
def update(
    identity: int,
    payload: ApoderadoInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).save_user(payload, user, identity)


@router.get("/{identity}", response_model=ApoderadoOutput)
def detail(
    identity: int, db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    from fastapi import HTTPException
    from app.utils.enums import UserRole

    service = ManagementService(db)
    target = service.require(User, identity)
    if target.role != UserRole.APODERADO:
        raise HTTPException(404, "Apoderado no encontrado.")
    return service.user_output(target)
