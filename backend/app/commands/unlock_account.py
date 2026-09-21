"""Emergency server-only recovery. OS/DB operator access required; no public route."""

import argparse
from app.db.session import SessionLocal
from app.repositories.auth_repository import AuthRepository
from app.services.audit_service import AuditService


def main():
    parser = argparse.ArgumentParser(
        description="Desbloqueo excepcional auditado; no reactiva cuentas."
    )
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument(
        "--operator",
        required=True,
        help="Identidad del operador autenticado en el servidor",
    )
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    if len(args.reason.strip()) < 5 or not args.operator.strip():
        parser.error("Identifique operador y motivo concreto.")
    with SessionLocal() as db:
        user = AuthRepository(db).user(args.user_id)
        if not user:
            raise SystemExit("Cuenta inexistente.")
        before = {
            "attempts": user.failed_attempts,
            "locked_until": str(user.locked_until),
        }
        user.failed_attempts, user.locked_until, user.failure_window_at = 0, None, None
        AuditService(db).record(
            None,
            "auth.operator_unlock",
            "users",
            user.id,
            {"operator": args.operator, "reason": args.reason, "before": before},
        )
        db.commit()
        print("Bloqueo temporal retirado. Activación y contraseña conservadas.")


if __name__ == "__main__":
    main()
