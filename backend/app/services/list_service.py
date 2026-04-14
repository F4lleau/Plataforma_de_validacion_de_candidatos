from app.models.electoral_list import ElectoralList
from app.repositories.list_repository import ListRepository
from app.schemas.electoral_list import ElectoralListCreate
from app.utils.enums import ListStatus


class ListService:
    def __init__(self, list_repository: ListRepository):
        self.list_repository = list_repository

    def list_lists(self):
        return self.list_repository.list_all()

    def create_list(self, payload: ElectoralListCreate, created_by: int) -> ElectoralList:
        electoral_list = ElectoralList(
            election_id=payload.election_id,
            office_id=payload.office_id,
            municipality_id=payload.municipality_id,
            list_name=payload.list_name,
            status=ListStatus.BORRADOR,
            created_by=created_by,
        )
        return self.list_repository.create(electoral_list)