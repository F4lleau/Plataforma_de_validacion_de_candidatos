from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.access_service import AccessService
from app.repositories.list_repository import ListRepository
from app.repositories.list_role_definition_repository import ListRoleDefinitionRepository
from app.services.list_validation_service import ListValidationService

router = APIRouter()


@router.get("/list/{list_id}")
def validate_list(
    list_id: int,
    office_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    AccessService(db).require_list(current_user, list_id)
    list_repository = ListRepository(db)
    role_repository = ListRoleDefinitionRepository(db)
    service = ListValidationService(list_repository, role_repository)

    return service.validate(list_id=list_id, office_type=office_type)
