import os

from sqlalchemy import select

from app.core.security import hash_password
from app.core.passwords import validate_password
from app.db.session import SessionLocal
from app.models.user import User
from app.utils.enums import UserRole


def main() -> None:
    email = os.environ.get("INITIAL_ADMIN_EMAIL")
    password = os.environ.get("INITIAL_ADMIN_PASSWORD")
    full_name = os.environ.get("INITIAL_ADMIN_FULL_NAME", "Administrador inicial")
    username = os.environ.get("INITIAL_ADMIN_USERNAME") or (
        email.split("@", 1)[0] if email else ""
    )

    if not email or not password:
        raise SystemExit(
            "INITIAL_ADMIN_EMAIL e INITIAL_ADMIN_PASSWORD son obligatorios."
        )

    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email.lower().strip()))
        if existing:
            print(f"El usuario administrador ya existe: {existing.email}")
            return

        validate_password(password)
        db.add(
            User(
                username=username,
                email=email.lower().strip(),
                full_name=full_name,
                password_hash=hash_password(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        db.commit()
        print(f"Administrador creado: {email}")


if __name__ == "__main__":
    main()
