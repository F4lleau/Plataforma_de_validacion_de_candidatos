from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.electoral_list import ElectoralList
from app.models.list_assignment import ListAssignment
from app.models.list_candidate import ListCandidate
from app.repositories.user_module_repository import UserModuleRepository


class ListRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[ElectoralList]:
        stmt = select(ElectoralList).order_by(ElectoralList.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, list_id: int) -> ElectoralList | None:
        stmt = select(ElectoralList).where(ElectoralList.id == list_id)
        return self.db.scalar(stmt)

    def list_for_user(self, user_id: int) -> list[ElectoralList]:
        stmt = (
            select(ElectoralList)
            .where(
                UserModuleRepository.access_condition(
                    user_id,
                    ElectoralList.election_id,
                    ElectoralList.office_id,
                    ElectoralList.municipality_id,
                )
            )
            .where(
                select(ListAssignment.id)
                .where(
                    ListAssignment.list_id == ElectoralList.id,
                    ListAssignment.user_id == user_id,
                )
                .exists()
            )
            .order_by(ElectoralList.id.desc())
        )
        return list(self.db.scalars(stmt).all())

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

    def page(self, user, search, status, page, page_size):
        from sqlalchemy import func, or_
        from app.utils.enums import UserRole

        stmt = select(ElectoralList)
        if user.role != UserRole.ADMIN:
            stmt = stmt.where(
                UserModuleRepository.access_condition(
                    user.id,
                    ElectoralList.election_id,
                    ElectoralList.office_id,
                    ElectoralList.municipality_id,
                ),
                select(ListAssignment.id)
                .where(
                    ListAssignment.list_id == ElectoralList.id,
                    ListAssignment.user_id == user.id,
                )
                .exists(),
            )
        if search:
            stmt = stmt.where(
                or_(
                    func.lower(ElectoralList.list_name).contains(
                        search.lower(), autoescape=True
                    ),
                    func.lower(ElectoralList.list_number).contains(
                        search.lower(), autoescape=True
                    ),
                )
            )
        if status:
            stmt = stmt.where(ElectoralList.status == status)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        items = list(
            self.db.scalars(
                stmt.order_by(ElectoralList.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total
