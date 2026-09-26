from datetime import datetime
from zoneinfo import ZoneInfo
import re
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models import (
    Election,
    Office,
    Municipality,
    ElectionRule,
    User,
    UserModule,
    OfficeType,
    ElectionOffice,
    ElectionMunicipality,
)
from app.repositories.management_repository import ManagementRepository
from app.services.audit_service import AuditService
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

    def slug(self, value):
        base = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "cargo"
        candidate = base
        suffix = 2
        while self.db.scalar(select(Office.id).where(Office.code == candidate)):
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def office_types(self):
        return [
            row for row in self.repo.all(OfficeType) if row.active
        ]

    def offices(self, user):
        rows = self.catalogs(Office, user)
        types = {row.id: row.name for row in self.repo.all(OfficeType)}
        links = self.repo.all(ElectionOffice)
        election_ids = {}
        for link in links:
            election_ids.setdefault(link.office_id, []).append(link.election_id)
        return [
            {
                "id": row.id,
                "code": row.code,
                "name": row.name,
                "office_type_id": row.office_type_id,
                "office_type_name": types.get(row.office_type_id),
                "election_id": None,
                "election_ids": sorted(election_ids.get(row.id, [])),
                "scope_type": row.scope_type,
                "municipality_based": row.municipality_based,
                "required_positions": row.required_positions,
                "requires_parity": row.requires_parity,
                "requires_alternation": row.requires_alternation,
                "active": row.active,
            }
            for row in rows
        ]

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

    def save_office(self, payload, actor, identity=None):
        obj = self.require(Office, identity, True) if identity else Office()
        self.require(OfficeType, payload.office_type_id)
        if payload.election_id:
            self.require(Election, payload.election_id)
        if identity and (
            obj.municipality_based != payload.municipality_based
            or obj.scope_type != payload.scope_type
        ):
            raise HTTPException(
                409, "El alcance del cargo es estable; creá otro cargo si cambia."
            )
        obj.name = payload.name
        obj.code = obj.code or self.slug(payload.name)
        obj.office_type_id = payload.office_type_id
        obj.scope_type = payload.scope_type
        obj.municipality_based = payload.municipality_based
        obj.required_positions = payload.required_positions
        obj.requires_parity = payload.requires_parity
        obj.requires_alternation = payload.requires_alternation
        obj.active = payload.active
        try:
            self.repo.add(obj)
            if payload.election_id and not self.db.scalar(
                select(ElectionOffice).where(
                    ElectionOffice.election_id == payload.election_id,
                    ElectionOffice.office_id == obj.id,
                )
            ):
                self.repo.add(
                    ElectionOffice(
                        election_id=payload.election_id,
                        office_id=obj.id,
                    )
                )
            self.audit.record(
                actor.id,
                "office.updated" if identity else "office.created",
                "offices",
                obj.id,
                {
                    "name": obj.name,
                    "office_type_id": obj.office_type_id,
                    "election_id": payload.election_id,
                    "active": obj.active,
                },
            )
            self.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(409, "Nombre o código duplicado.") from exc
        return self.offices(actor)[
            next(i for i, item in enumerate(self.offices(actor)) if item["id"] == obj.id)
        ]

    def deactivate(self, model, identity, actor):
        obj = self.require(model, identity, True)
        obj.active = False
        self.audit.record(actor.id, "catalog.deactivated", model.__tablename__, obj.id)
        self.commit()
        return {"message": "Registro desactivado."}

    def election_municipalities(self, election_id, user):
        self.require(Election, election_id)
        allowed = {e.id for e in self.catalogs(Election, user)}
        if election_id not in allowed:
            raise HTTPException(403, "Elección no habilitada.")
        return self.db.scalars(
            select(Municipality)
            .join(ElectionMunicipality, ElectionMunicipality.municipality_id == Municipality.id)
            .where(ElectionMunicipality.election_id == election_id)
            .order_by(Municipality.name)
        ).all()

    def save_election_municipalities(self, election_id, payload, actor):
        self.require(Election, election_id, True)
        selected = set(payload.municipality_ids)
        if selected:
            found = {
                row.id
                for row in self.db.scalars(
                    select(Municipality).where(Municipality.id.in_(selected))
                )
            }
            if found != selected:
                raise HTTPException(422, "Hay localidades inexistentes.")
        for row in self.repo.all(ElectionMunicipality, election_id=election_id):
            self.repo.remove(row)
        self.db.flush()
        for municipality_id in sorted(selected):
            self.repo.add(
                ElectionMunicipality(
                    election_id=election_id,
                    municipality_id=municipality_id,
                )
            )
        self.audit.record(
            actor.id,
            "election.municipalities_updated",
            "elections",
            election_id,
            {"municipality_ids": sorted(selected)},
        )
        self.commit()
        return {"message": "Localidades habilitadas actualizadas."}

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
            "email_verified_at": user.email_verified_at,
            "modules": self.repo.modules(user.id),
        }

    def save_user(self, payload, actor, identity=None):
        if not identity:
            raise HTTPException(
                410, "El alta manual fue reemplazada por invitaciones por correo."
            )
        user = self.require(User, identity, True)
        if user.role != UserRole.APODERADO:
            raise HTTPException(403, "Este flujo solo administra apoderados.")
        if payload.password:
            raise HTTPException(
                422,
                "Usá recuperación; no se permite asignar contraseñas a otra cuenta.",
            )
        if user.email.strip().lower() != payload.email:
            raise HTTPException(
                422,
                "El cambio de correo requiere un flujo de verificación aún no habilitado.",
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
        for key in ("username", "full_name", "is_active"):
            setattr(user, key, getattr(payload, key))
        if not user.is_active:
            from app.repositories.auth_repository import AuthRepository

            AuthRepository(self.db).revoke_all(user.id)
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
