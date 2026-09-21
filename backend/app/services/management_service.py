from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import Election, Office, Municipality, ElectionRule, User, UserModule
from app.repositories.management_repository import ManagementRepository
from app.services.audit_service import AuditService
from app.core.security import hash_password
from app.utils.enums import UserRole, UserModuleType


class ManagementService:
    def __init__(self, db):
        self.db = db
        self.repo = ManagementRepository(db)
        self.audit = AuditService(db)

    def require(self, model, identity, lock=False):
        obj = self.repo.get(model, identity, lock)
        if obj is None:
            raise HTTPException(404, "Registro no encontrado.")
        return obj

    def commit(self):
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "El registro ya existe o entra en conflicto con otro cambio."
            ) from exc

    def catalogs(self, model, user):
        rows = self.repo.all(model)
        if user.role == UserRole.ADMIN:
            return rows
        modules = [m for m in self.repo.modules(user.id) if m.enabled]
        key = {
            Election: "election_id",
            Office: "office_id",
            Municipality: "municipality_id",
        }[model]
        ids = {getattr(m, key) for m in modules}
        return [r for r in rows if r.id in ids and r.active]

    def catalog_save(self, model, payload, actor, identity=None):
        obj = self.require(model, identity, True) if identity else model()
        before = {k: str(getattr(obj, k, None)) for k in type(payload).model_fields}
        if model == Office and identity:
            if (
                obj.code != payload.code
                or obj.municipality_based != payload.municipality_based
            ):
                raise HTTPException(
                    409, "Código y alcance del cargo son estables; cree otro cargo."
                )
        for key, value in payload.model_dump().items():
            setattr(obj, key, value)
        try:
            self.repo.add(obj)
            self.audit.record(
                actor.id,
                "catalog.updated" if identity else "catalog.created",
                model.__tablename__,
                obj.id,
                {"before": before, "after": payload.model_dump(mode="json")},
            )
            self.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Nombre o código duplicado.") from exc
        self.db.refresh(obj)
        return obj

    def save_rules(self, election_id, office_id, payload, actor):
        self.require(Election, election_id, True)
        self.require(Office, office_id)
        old = self.repo.rule(election_id, office_id)
        if (
            old
            and old.enabled == payload.enabled
            and old.rules == payload.model_dump(mode="json", exclude={"enabled"})
        ):
            return old
        rule = self.repo.add(
            ElectionRule(
                election_id=election_id,
                office_id=office_id,
                version=(old.version + 1 if old else 1),
                enabled=payload.enabled,
                rules=payload.model_dump(mode="json", exclude={"enabled"}),
            )
        )
        self.audit.record(
            actor.id,
            "rules.version_created",
            "election_rules",
            rule.id,
            {"version": rule.version, "previous_id": old.id if old else None},
        )
        self.commit()
        self.db.refresh(rule)
        return rule

    def context(self, election_id, office_id, municipality_id, window=False):
        election = self.require(Election, election_id)
        office = self.require(Office, office_id)
        if not election.active or not office.active:
            raise HTTPException(409, "Elección o cargo inactivo.")
        if office.municipality_based != (municipality_id is not None):
            raise HTTPException(
                422, "El municipio debe corresponder al alcance del cargo."
            )
        if municipality_id and not self.require(Municipality, municipality_id).active:
            raise HTTPException(409, "Municipio inactivo.")
        rule = self.repo.rule(election_id, office_id)
        if not rule or not rule.enabled:
            raise HTTPException(
                409, "Configure y habilite las reglas del cargo en esta elección."
            )
        if window:
            today = datetime.now(ZoneInfo("America/Argentina/Cordoba")).date()
            if (
                not election.loading_opens
                or not election.loading_closes
                or not election.loading_opens <= today <= election.loading_closes
            ):
                raise HTTPException(
                    409, "La carga no está abierta. Revise las fechas de configuración."
                )
        return election, office, rule

    def users(self):
        return [
            self.user_output(u)
            for u in self.repo.all(User)
            if u.role == UserRole.APODERADO
        ]

    def user_output(self, user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role": user.role,
            "modules": self.repo.modules(user.id),
        }

    def save_user(self, payload, actor, identity=None):
        user = (
            self.require(User, identity, True)
            if identity
            else User(role=UserRole.APODERADO)
        )
        if user.role != UserRole.APODERADO:
            raise HTTPException(403, "Este flujo solo administra apoderados.")
        if not identity and not payload.password:
            raise HTTPException(
                422, "Indique contraseña inicial de al menos 10 caracteres."
            )
        seen = set()
        for module in payload.modules:
            key = (module.election_id, module.office_id, module.municipality_id)
            if key in seen:
                raise HTTPException(422, "Módulo duplicado.")
            seen.add(key)
            self.require(Election, module.election_id)
            office = self.require(Office, module.office_id)
            if office.municipality_based != (module.municipality_id is not None):
                raise HTTPException(
                    422, "La localidad no corresponde al alcance del cargo."
                )
            if module.municipality_id:
                self.require(Municipality, module.municipality_id)
        before = (
            {
                "active": user.is_active,
                "modules": [m.id for m in self.repo.modules(identity)],
            }
            if identity
            else None
        )
        for key in ("username", "email", "full_name", "is_active"):
            setattr(user, key, getattr(payload, key))
        if payload.password:
            user.password_hash = hash_password(payload.password)
        try:
            self.repo.add(user)
            for old in self.repo.modules(user.id):
                self.repo.remove(old)
            self.db.flush()
            for m in payload.modules:
                office = self.require(Office, m.office_id)
                self.repo.add(
                    UserModule(
                        user_id=user.id,
                        module_type=UserModuleType.CONSEJOS_LOCALES
                        if office.municipality_based
                        else UserModuleType.DIPUTADOS_PROVINCIALES,
                        **m.model_dump(),
                    )
                )
            self.audit.record(
                actor.id,
                "apoderado.updated" if identity else "apoderado.created",
                "users",
                user.id,
                {
                    "before": before,
                    "active": user.is_active,
                    "password_changed": bool(payload.password),
                    "modules": [m.model_dump() for m in payload.modules],
                },
            )
            self.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Email o usuario ya registrado.") from exc
        return self.user_output(user)
