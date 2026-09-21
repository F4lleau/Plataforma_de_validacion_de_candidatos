from pathlib import Path
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
import bcrypt
from fastapi import HTTPException

hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
BLOCKLIST = frozenset(
    Path(__file__).with_name("common_passwords.txt").read_text().splitlines()
)


def validate_password(password: str):
    if not 15 <= len(password) <= 128:
        raise HTTPException(422, "Usá entre 15 y 128 caracteres en la contraseña.")
    if password.casefold().strip() in BLOCKLIST or len(set(password)) == 1:
        raise HTTPException(422, "Elegí una contraseña menos común.")


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        if encoded.startswith("$argon2id$"):
            return hasher.verify(encoded, password)
        # Preserve bcrypt's historic byte semantics; migration occurs after successful login.
        return bcrypt.checkpw(password.encode("utf-8")[:72], encoded.encode("ascii"))
    except (VerificationError, InvalidHashError, ValueError, TypeError):
        return False


def needs_rehash(encoded: str) -> bool:
    return not encoded.startswith("$argon2id$") or hasher.check_needs_rehash(encoded)
