from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.list_repository import ListRepository
from app.repositories.user_module_repository import UserModuleRepository
from app.utils.enums import UserRole


class AccessService:
    """El rol viene de la BD; el alcance del apoderado, de sus módulos habilitados."""

    def __init__(self, db: Session):
        self.modules = UserModuleRepository(db)
        from app.repositories.management_repository import ManagementRepository
        self.repo = ManagementRepository(db)
        self.lists = ListRepository(db)

    def require_module(self, user: User, election_id: int, office_id: int, municipality_id: int | None) -> None:
        if user.role == UserRole.ADMIN:
            return
        if not self.modules.has_access(user.id, election_id, office_id, municipality_id):
            raise HTTPException(status_code=403, detail="No tiene un módulo habilitado para esta elección, cargo y localidad.")

    def require_list(self, user: User, list_id: int) -> None:
        electoral_list = self.lists.get_by_id(list_id)
        if electoral_list is None:
            raise HTTPException(status_code=404, detail="Lista no encontrada.")
        self.require_module(user, electoral_list.election_id, electoral_list.office_id, electoral_list.municipality_id)

        if user.role != UserRole.ADMIN and not self.repo.assigned(list_id, user.id):
            raise HTTPException(status_code=403, detail="La lista no está asignada a este apoderado.")
