from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.list_role_definition import ListRoleDefinition


class ListRoleDefinitionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_office_type(self, office_type: str) -> list[ListRoleDefinition]:
        stmt = (
            select(ListRoleDefinition)
            .where(ListRoleDefinition.office_type == office_type)
            .order_by(ListRoleDefinition.position_order.asc())
        )
        return list(self.db.scalars(stmt).all())

    def create_many(self, roles: list[ListRoleDefinition]) -> None:
        self.db.add_all(roles)
        self.db.commit()