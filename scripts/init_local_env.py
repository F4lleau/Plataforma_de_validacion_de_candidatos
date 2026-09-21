"""Genera configuración local sin sobrescribir archivos ni imprimir secretos."""

import getpass
import os
from pathlib import Path
import re
import secrets


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    targets = (root / ".env", root / "backend" / ".env")
    existing = [str(path.relative_to(root)) for path in targets if path.exists()]
    if existing:
        raise SystemExit(
            "No se sobrescribió configuración existente: " + ", ".join(existing)
            + ". Para volver a levantar el entorno, continuar con Docker Compose."
        )

    username = re.sub(r"[^a-z0-9_]", "_", getpass.getuser().lower())[:40] or "local_user"
    password = secrets.token_hex(24)
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    if not 1 <= port <= 65535:
        raise SystemExit("POSTGRES_PORT debe estar entre 1 y 65535.")

    values = (
        f"POSTGRES_DB=junta_electoral\nPOSTGRES_USER={username}\n"
        f"POSTGRES_PASSWORD={password}\nPOSTGRES_PORT={port}\n",
        f"DATABASE_URL=postgresql+psycopg://{username}:{password}@127.0.0.1:{port}/junta_electoral\n"
        f"SECRET_KEY={secrets.token_hex(32)}\n"
        "APP_ENV=development\n"
        'CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]\n'
        f"INITIAL_ADMIN_EMAIL={username}@example.com\n"
        f"INITIAL_ADMIN_PASSWORD={secrets.token_urlsafe(24)}\n",
    )
    for path, content in zip(targets, values):
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(content)
    print("Creados .env y backend/.env (ignorados por Git, permisos 600).")
    print("Credenciales de acceso local: INITIAL_ADMIN_EMAIL y INITIAL_ADMIN_PASSWORD en backend/.env.")


if __name__ == "__main__":
    main()
