from app.core.security import verify_password, create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, username: str, password: str) -> dict | None:
        user = self.user_repository.get_by_username(username)
        if not user or not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        access_token = create_access_token(
            subject=str(user.id),
            extra_data={"role": user.role.value},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }