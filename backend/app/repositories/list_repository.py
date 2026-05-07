from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.electoral_list import ElectoralList
from app.models.list_candidate import ListCandidate


class ListRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[ElectoralList]:
        stmt = select(ElectoralList).order_by(ElectoralList.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, list_id: int) -> ElectoralList | None:
        stmt = select(ElectoralList).where(ElectoralList.id == list_id)
        return self.db.scalar(stmt)

    def create(self, electoral_list: ElectoralList) -> ElectoralList:
        self.db.add(electoral_list)
        self.db.commit()
        self.db.refresh(electoral_list)
        return electoral_list

    def add_candidate_to_list(self, list_candidate: ListCandidate) -> ListCandidate:
        self.db.add(list_candidate)
        self.db.commit()
        self.db.refresh(list_candidate)
        return list_candidate

    def list_candidates(self, list_id: int) -> list[ListCandidate]:
        stmt = (
            select(ListCandidate)
            .where(ListCandidate.list_id == list_id)
            .order_by(ListCandidate.position_number.asc())
        )
        return list(self.db.scalars(stmt).all())