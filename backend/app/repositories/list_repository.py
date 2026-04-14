from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.electoral_list import ElectoralList


class ListRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[ElectoralList]:
        stmt = select(ElectoralList).order_by(ElectoralList.id.desc())
        return list(self.db.scalars(stmt).all())

    def create(self, electoral_list: ElectoralList) -> ElectoralList:
        self.db.add(electoral_list)
        self.db.commit()
        self.db.refresh(electoral_list)
        return electoral_list