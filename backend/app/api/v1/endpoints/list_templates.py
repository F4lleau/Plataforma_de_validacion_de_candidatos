from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.list_role_definition_repository import ListRoleDefinitionRepository
from app.schemas.list_role_definition import ListRoleDefinitionResponse
from app.services.list_template_service import ListTemplateService

router = APIRouter()


@router.get("/{office_type}", response_model=list[ListRoleDefinitionResponse])
def get_list_template(
    office_type: str,
    db: Session = Depends(get_db),
):
    repository = ListRoleDefinitionRepository(db)
    service = ListTemplateService(repository)
    return service.get_template(office_type)