from app.services.composition_service import CompositionService


class ListValidationService:
    def __init__(self, list_repository, role_repository=None):
        self.lists = list_repository
        self.composition = CompositionService(list_repository.db)

    def validate(self, list_id, office_type=None):
        return self.composition.evaluate(self.lists.get_by_id(list_id))
