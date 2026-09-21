"""Run: python -m app.commands.mail_worker [--once]. No sensitive delivery logs."""

import argparse
import time
from app.db.session import SessionLocal
from app.services.mail_service import MailService
from app.repositories.auth_repository import AuthRepository


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        from app.repositories.mail_repository import MailRepository

        with SessionLocal() as db:
            print(MailRepository(db).status())
        return
    cleanup_at = 0
    while True:
        try:
            with SessionLocal() as db:
                if time.monotonic() >= cleanup_at:
                    AuthRepository(db).cleanup()
                    cleanup_at = time.monotonic() + 3600
                worked = MailService(db).process_one()
        except Exception:
            print(
                "Worker: error de infraestructura; reintento en 5 segundos.", flush=True
            )
            worked = False
        if args.once:
            return
        if not worked:
            time.sleep(5)


if __name__ == "__main__":
    main()
