from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.list_repository import ListRepository
from app.repositories.list_role_definition_repository import ListRoleDefinitionRepository
from app.services.list_validation_service import ListValidationService

router = APIRouter()


@router.get("/list/{list_id}")
def validate_list(
    list_id: int,
    office_type: str = Query(...),
    db: Session = Depends(get_db),
):
    list_repository = ListRepository(db)
    role_repository = ListRoleDefinitionRepository(db)
    service = ListValidationService(list_repository, role_repository)

    return service.validate(list_id=list_id, office_type=office_type)