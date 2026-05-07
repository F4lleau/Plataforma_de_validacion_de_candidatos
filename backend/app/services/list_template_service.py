from app.repositories.list_role_definition_repository import ListRoleDefinitionRepository


class ListTemplateService:
    def __init__(self, role_repository: ListRoleDefinitionRepository):
        self.role_repository = role_repository

    def get_template(self, office_type: str):
        return self.role_repository.list_by_office_type(office_type)