from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def list_users(self):
        return self.user_repository.list_all()

    def create_user(self, payload: UserCreate) -> User:
        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
            role=payload.role,
            is_active=True,
        )
        return self.user_repository.create(user)