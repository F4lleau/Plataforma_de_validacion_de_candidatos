from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.office import Office
from app.models.user_module import UserModule


class UserModuleRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def access_condition(user_id, election_id, office_id, municipality_id):
        """Sirve tanto para un recurso concreto como para filtrar una consulta."""
        return (
            select(UserModule.id)
            .join(Office, Office.id == UserModule.office_id)
            .where(
                UserModule.user_id == user_id,
                UserModule.enabled.is_(True),
                UserModule.election_id == election_id,
                UserModule.office_id == office_id,
                or_(
                    and_(Office.municipality_based.is_(False), UserModule.municipality_id.is_(None)),
                    and_(
                        Office.municipality_based.is_(True),
                        UserModule.municipality_id.is_not(None),
                        UserModule.municipality_id == municipality_id,
                    ),
                ),
            )
            .exists()
        )

    def has_access(self, user_id: int, election_id: int, office_id: int, municipality_id: int | None) -> bool:
        return bool(self.db.scalar(select(self.access_condition(user_id, election_id, office_id, municipality_id))))
