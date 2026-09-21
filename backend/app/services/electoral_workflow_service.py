from app.services.transaction import atomic_mutation
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import (
    ElectoralList,
    ListAssignment,
    ListCandidate,
    Candidate,
    Person,
    User,
    ElectionRule,
    CandidateValidation,
    AffiliateImportBatch,
)
from app.services.management_service import ManagementService
from app.services.access_service import AccessService
from app.services.affiliation_validation_service import AffiliationValidationService
from app.services.office_validation_service import OfficeValidationService
from app.services.renaper_validation_service import RenaperValidationService
from app.repositories.party_member_repository import PartyMemberRepository
from app.repositories.list_repository import ListRepository
from app.utils.enums import (
    UserRole,
    ListStatus,
    CandidateStatus,
    ValidationType,
    ValidationResult,
)


class ElectoralWorkflowService(ManagementService):
    editable = {
        ListStatus.BORRADOR,
        ListStatus.INCOMPLETA,
        ListStatus.RECHAZADA_COMPOSICION,
    }

    def get_list(self, identity, user, edit=False):
        row = self.require(ElectoralList, identity, edit)
        AccessService(self.db).require_list(user, identity)
        if edit:
            if row.status not in self.editable:
                raise HTTPException(
                    409, "Solo se editan listas en borrador o incompletas."
                )
            self.context(
                row.election_id, row.office_id, row.municipality_id, window=True
            )
        return row

    def listing(self, user, search="", status=""):
        if status and status not in {s.value for s in ListStatus}:
            raise HTTPException(422, "Estado de lista inválido.")
        rows = (
            ListRepository(self.db).list_all()
            if user.role == UserRole.ADMIN
            else ListRepository(self.db).list_for_user(user.id)
        )
        return [
            self.list_output(r)
            for r in rows
            if (
                not search
                or search.lower() in (r.list_name + " " + (r.list_number or "")).lower()
            )
            and (not status or r.status.value == status)
        ]

    def page(self, user, search, status, page, page_size):
        if status and status not in {s.value for s in ListStatus}:
            raise HTTPException(422, "Estado de lista inválido.")
        rows, total = ListRepository(self.db).page(
            user, search, status, page, page_size
        )
        return {
            "items": [self.list_output(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def list_output(self, row):
        result = {c.name: getattr(row, c.name) for c in row.__table__.columns}
        result["assigned_user_ids"] = [
            a.user_id for a in self.repo.all(ListAssignment, list_id=row.id)
        ]
        result["candidate_count"] = len(self.repo.all(ListCandidate, list_id=row.id))
        return result

    def detail(self, identity, user):
        row = self.get_list(identity, user)
        result = self.list_output(row)
        result["rule"] = (
            self.repo.get(ElectionRule, row.rule_version_id)
            if row.rule_version_id
            else None
        )
        result["candidates"] = [
            self.candidate_output(self.require(Candidate, m.candidate_id), m, row)
            for m in self.repo.all(ListCandidate, list_id=row.id)
        ]
        return result

    @atomic_mutation
    def create(self, payload, user):
        # Election lock serializes number allocation within an electoral process.
        from app.models import Election

        self.require(Election, payload.election_id, True)
        _, _, rule = self.context(
            payload.election_id, payload.office_id, payload.municipality_id, window=True
        )
        AccessService(self.db).require_module(
            user, payload.election_id, payload.office_id, payload.municipality_id
        )
        if self.repo.number_exists(
            payload.election_id,
            payload.office_id,
            payload.municipality_id,
            payload.list_number,
        ):
            raise HTTPException(
                409, "Número de lista ya utilizado en esta elección, cargo y distrito."
            )
        row = self.repo.add(
            ElectoralList(
                **payload.model_dump(),
                created_by=user.id,
                rule_version_id=rule.id,
                status=ListStatus.BORRADOR,
            )
        )
        if user.role == UserRole.APODERADO:
            self.repo.add(ListAssignment(list_id=row.id, user_id=user.id))
        self.audit.record(
            user.id,
            "list.created",
            "electoral_lists",
            row.id,
            {"rule_version_id": rule.id},
        )
        self.commit()
        return self.list_output(row)

    @atomic_mutation
    def edit(self, identity, payload, user):
        from app.models import Election

        row = self.get_list(identity, user, True)
        self.require(Election, row.election_id, True)
        if self.repo.number_exists(
            row.election_id,
            row.office_id,
            row.municipality_id,
            payload.list_number,
            row.id,
        ):
            raise HTTPException(409, "Número de lista ya utilizado.")
        before = {"list_name": row.list_name, "list_number": row.list_number}
        row.list_name, row.list_number = payload.list_name, payload.list_number
        self.audit.record(
            user.id,
            "list.updated",
            "electoral_lists",
            row.id,
            {"before": before, "after": payload.model_dump(mode="json")},
        )
        self.commit()
        return self.list_output(row)

    @atomic_mutation
    def assign(self, identity, payload, user):
        row = self.require(ElectoralList, identity, True)
        ids = set(payload.user_ids)
        for uid in ids:
            target = self.require(User, uid)
            if target.role != UserRole.APODERADO or not target.is_active:
                raise HTTPException(422, "Seleccione apoderados activos.")
            AccessService(self.db).require_module(
                target, row.election_id, row.office_id, row.municipality_id
            )
        old = [a.user_id for a in self.repo.all(ListAssignment, list_id=row.id)]
        for a in self.repo.all(ListAssignment, list_id=row.id):
            self.repo.remove(a)
        self.db.flush()
        for uid in ids:
            self.repo.add(ListAssignment(list_id=row.id, user_id=uid))
        self.audit.record(
            user.id,
            "list.assignments_changed",
            "electoral_lists",
            row.id,
            {"before": old, "after": sorted(ids)},
        )
        self.commit()
        return self.list_output(row)

    @atomic_mutation
    def bind_rules(self, identity, user):
        row = self.get_list(identity, user, True)
        rule = self.repo.rule(row.election_id, row.office_id)
        members = self.repo.all(ListCandidate, list_id=row.id)
        if members:
            raise HTTPException(
                409,
                "La adopción de una plantilla requiere una lista vacía; conserve la versión actual para listas con candidatos.",
            )
        row.rule_version_id = rule.id
        self.audit.record(
            user.id,
            "list.rules_bound",
            "electoral_lists",
            row.id,
            {"rule_version_id": rule.id},
        )
        self.commit()
        return self.detail(identity, user)

    @atomic_mutation
    def save_candidate(self, list_id, payload, user, candidate_id=None):
        row = self.get_list(list_id, user, True)
        rule = (
            self.repo.get(ElectionRule, row.rule_version_id)
            if row.rule_version_id
            else None
        )
        if not rule or not rule.rules.get("positions"):
            raise HTTPException(
                409,
                "La lista no tiene plantilla. Configure reglas y cree una lista nueva o adopte reglas si está vacía.",
            )
        position = next(
            (p for p in rule.rules["positions"] if p["position"] == payload.position),
            None,
        )
        if not position:
            raise HTTPException(422, "Posición fuera de la plantilla de la lista.")
        members = self.repo.all(ListCandidate, list_id=list_id)
        if any(
            m.position_number == payload.position and m.candidate_id != candidate_id
            for m in members
        ):
            raise HTTPException(409, "La posición ya está ocupada.")
        member = self.repo.membership(list_id, candidate_id) if candidate_id else None
        if candidate_id and member is None:
            raise HTTPException(404, "Candidato no encontrado en la lista.")
        person_values = payload.model_dump(exclude={"position", "action"})
        if payload.municipality_id:
            from app.models import Municipality

            self.require(Municipality, payload.municipality_id)
        person = self.repo.person(payload.dni)
        if member:
            candidate = self.require(Candidate, candidate_id, True)
            original = self.require(Person, candidate.person_id, True)
            if person and person.id != original.id:
                raise HTTPException(
                    409, "El DNI ya pertenece a otra persona registrada."
                )
            person = original
            if self.repo.person_other_candidates(person.id, candidate.id) and any(
                getattr(person, k) != v for k, v in person_values.items()
            ):
                raise HTTPException(
                    409,
                    "La persona participa en otra postulación. Requiere corrección administrativa coordinada.",
                )
            for k, v in person_values.items():
                setattr(person, k, v)
            candidate.revision += 1
        else:
            if person and any(
                self.require(Candidate, m.candidate_id).person_id == person.id
                for m in members
            ):
                raise HTTPException(409, "El DNI ya figura en esta lista.")
            if person and any(
                getattr(person, k) != v for k, v in person_values.items()
            ):
                raise HTTPException(
                    409,
                    "El DNI está registrado con otros datos; solicite revisión administrativa.",
                )
            person = person or self.repo.add(Person(**person_values))
            candidate = self.repo.add(
                Candidate(
                    person_id=person.id,
                    election_id=row.election_id,
                    office_id=row.office_id,
                    created_by=user.id,
                    revision=1,
                    candidate_status=CandidateStatus.BORRADOR,
                )
            )
            member = self.repo.add(
                ListCandidate(
                    list_id=row.id,
                    candidate_id=candidate.id,
                    cargo_label=position["name"],
                    cargo_group=position["group"],
                    position_number=payload.position,
                    gender=payload.gender,
                )
            )
        member.position_number = payload.position
        member.cargo_label, member.cargo_group, member.gender = (
            position["name"],
            position["group"],
            payload.gender,
        )
        row.status = ListStatus.BORRADOR
        member.is_validated = False
        member.validation_summary = None
        candidate.candidate_status = (
            CandidateStatus.BORRADOR
            if payload.action == "draft"
            else CandidateStatus.PENDIENTE_VALIDACION
        )
        self.db.flush()
        # Every save retains non-blocking affiliation feedback, even a draft.
        self.validate_candidate(
            candidate,
            person,
            row,
            include_requirements=payload.action == "validate",
            actor_id=user.id,
        )
        self.audit.record(
            user.id,
            "candidate.updated" if candidate_id else "candidate.created",
            "candidates",
            candidate.id,
            {
                "list_id": row.id,
                "revision": candidate.revision,
                "action": payload.action,
            },
        )
        try:
            self.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                409, "Los datos entran en conflicto con otra carga."
            ) from exc
        return self.candidate_output(candidate, member, row)

    def validate_candidate(
        self, candidate, person, row, include_requirements=True, actor_id=None
    ):
        # No network calls: RENAPER is explicitly unconfigured until a provider exists.
        rule = (
            self.repo.get(ElectionRule, row.rule_version_id)
            if row.rule_version_id
            else None
        )
        affiliation = AffiliationValidationService(
            PartyMemberRepository(self.db)
        ).validate(person.dni)
        from app.models import Election

        election = self.require(Election, row.election_id)
        requirements = (
            OfficeValidationService().validate_rules(
                rule.rules if rule else None, person.birth_date, election
            )
            if include_requirements
            else {
                "status": "pendiente",
                "message": "Borrador guardado; pulse Guardar y validar.",
            }
        )
        identity = RenaperValidationService().validate(
            person.dni, person.first_name, person.last_name
        )
        results = [
            (
                ValidationType.AFILIACION,
                {
                    **affiliation,
                    "status": "ok"
                    if affiliation["status"] == "verified"
                    else "warning",
                },
            ),
            (ValidationType.REQUISITOS_CARGO, requirements),
            (ValidationType.RENAPER, identity),
        ]
        before = {
            v.validation_type.value: v.status.value
            for v in self.repo.validations(candidate)
        }
        batches = self.repo.all(AffiliateImportBatch, is_current=True)
        for typ, result in results:
            existing = next(
                (
                    v
                    for v in self.repo.validations(candidate)
                    if v.validation_type == typ
                ),
                None,
            )
            evidence = {
                "rule_version_id": row.rule_version_id,
                "batch_id": batches[0].id if batches else None,
                "origin": "local"
                if typ != ValidationType.RENAPER
                else result.get("source", "not_configured"),
                "approvable": result.get("approvable", False)
                if typ == ValidationType.RENAPER
                else result["status"] == "ok",
                "election_date": str(election.election_date),
                "loading_closes": str(election.loading_closes),
            }
            if existing:
                existing.status, existing.message, existing.response_json = (
                    ValidationResult(result["status"]),
                    result["message"],
                    evidence,
                )
                from datetime import datetime

                existing.validated_at = datetime.utcnow()
            else:
                self.repo.add(
                    CandidateValidation(
                        candidate_id=candidate.id,
                        candidate_revision=candidate.revision,
                        validation_type=typ,
                        status=ValidationResult(result["status"]),
                        message=result["message"],
                        response_json=evidence,
                    )
                )

        self.audit.record(
            actor_id,
            "candidate.validation_evaluated",
            "candidates",
            candidate.id,
            {
                "list_id": row.id,
                "revision": candidate.revision,
                "rule_version_id": row.rule_version_id,
                "batch_id": batches[0].id if batches else None,
                "before": before,
                "after": {typ.value: result["status"] for typ, result in results},
            },
        )

    @atomic_mutation
    def retry(self, list_id, candidate_id, user):
        row = self.get_list(list_id, user, True)
        member = self.repo.membership(list_id, candidate_id)
        if not member:
            raise HTTPException(404, "Candidato no encontrado en esta lista.")
        candidate = self.require(Candidate, candidate_id, True)
        self.validate_candidate(
            candidate, self.require(Person, candidate.person_id), row, actor_id=user.id
        )
        candidate.candidate_status = CandidateStatus.PENDIENTE_VALIDACION
        self.audit.record(
            user.id,
            "candidate.revalidated",
            "candidates",
            candidate.id,
            {"revision": candidate.revision},
        )
        self.commit()
        return self.candidate_output(candidate, member, row)

    def candidate_output(
        self,
        candidate,
        member,
        row,
        person=None,
        validations=None,
        election=None,
        batch_id=None,
        context_loaded=False,
    ):
        person = (
            person if person is not None else self.require(Person, candidate.person_id)
        )
        validations = (
            validations if validations is not None else self.repo.validations(candidate)
        )
        from app.models import Election

        if not context_loaded:
            batches = self.repo.all(AffiliateImportBatch, is_current=True)
            batch_id = batches[0].id if batches else None
            election = self.require(Election, row.election_id)
        result = []
        for v in validations:
            stale = (
                v.validation_type == ValidationType.AFILIACION
                and (v.response_json or {}).get("batch_id") != batch_id
            )
            stale = stale or (
                v.validation_type == ValidationType.REQUISITOS_CARGO
                and (
                    (v.response_json or {}).get("election_date")
                    != str(election.election_date)
                    or (v.response_json or {}).get("loading_closes")
                    != str(election.loading_closes)
                )
            )
            result.append(
                {
                    "type": v.validation_type,
                    "status": "pendiente" if stale else v.status,
                    "message": "Cambió el padrón o la configuración; vuelva a validar."
                    if stale
                    else v.message,
                    "validated_at": v.validated_at,
                    "origin": (v.response_json or {}).get("origin", "legacy"),
                    "revision": candidate.revision,
                }
            )
        return {
            "id": candidate.id,
            "candidate_status": candidate.candidate_status,
            "revision": candidate.revision,
            "person": {
                c.name: getattr(person, c.name) for c in person.__table__.columns
            },
            "position": member.position_number,
            "validations": result,
        }
