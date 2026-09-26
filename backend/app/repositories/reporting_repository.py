from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import aliased
from app.models import (
    ElectoralList,
    ListCandidate,
    ListAssignment,
    Candidate,
    Person,
    CandidateValidation,
    Election,
    Office,
    Municipality,
    User,
    UserModule,
    AuditLog,
    ListValidation,
)
from app.repositories.user_module_repository import UserModuleRepository
from app.utils.enums import UserRole, ListStatus, ValidationResult, ValidationType


class ReportingRepository:
    def __init__(self, db):
        self.db = db

    def list_query(self, user, filters):
        stmt = select(ElectoralList)
        if user.role != UserRole.ADMIN:
            stmt = stmt.where(
                UserModuleRepository.access_condition(
                    user.id,
                    ElectoralList.election_id,
                    ElectoralList.office_id,
                    ElectoralList.municipality_id,
                ),
                select(ListAssignment.id)
                .where(
                    ListAssignment.list_id == ElectoralList.id,
                    ListAssignment.user_id == user.id,
                )
                .exists(),
            )
        for field in ("election_id", "office_id", "municipality_id", "status"):
            value = getattr(filters, field)
            if value is not None:
                stmt = stmt.where(getattr(ElectoralList, field) == value)
        if filters.apoderado_id:
            stmt = stmt.where(
                select(ListAssignment.id)
                .where(
                    ListAssignment.list_id == ElectoralList.id,
                    ListAssignment.user_id == filters.apoderado_id,
                )
                .exists()
            )
        if filters.search:
            stmt = stmt.where(
                or_(
                    func.lower(ElectoralList.list_name).contains(
                        filters.search.lower(), autoescape=True
                    ),
                    func.lower(ElectoralList.list_number).contains(
                        filters.search.lower(), autoescape=True
                    ),
                )
            )
        return stmt

    def list_page(self, user, filters, page=1, page_size=25):
        query = self.list_query(user, filters)
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        rows = list(
            self.db.scalars(
                query.order_by(ElectoralList.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return self.decorate(rows), total

    def decorate(self, rows):
        if not rows:
            return []
        ids = [r.id for r in rows]
        counts = dict(
            self.db.execute(
                select(ListCandidate.list_id, func.count())
                .where(ListCandidate.list_id.in_(ids))
                .group_by(ListCandidate.list_id)
            ).all()
        )
        elections = {
            r.id: r.name
            for r in self.db.scalars(
                select(Election).where(Election.id.in_({r.election_id for r in rows}))
            )
        }
        offices = {
            r.id: r.name
            for r in self.db.scalars(
                select(Office).where(Office.id.in_({r.office_id for r in rows}))
            )
        }
        municipalities = {
            r.id: r.name
            for r in self.db.scalars(
                select(Municipality).where(
                    Municipality.id.in_(
                        {r.municipality_id for r in rows if r.municipality_id}
                    )
                )
            )
        }
        assigned = {}
        for lid, uid, name in self.db.execute(
            select(ListAssignment.list_id, User.id, User.full_name)
            .join(User, User.id == ListAssignment.user_id)
            .where(ListAssignment.list_id.in_(ids))
        ):
            assigned.setdefault(lid, []).append({"id": uid, "name": name})
        return [
            {
                **{c.name: getattr(r, c.name) for c in r.__table__.columns},
                "election_name": elections.get(r.election_id),
                "office_name": offices.get(r.office_id),
                "municipality_name": municipalities.get(
                    r.municipality_id, "Provincial"
                ),
                "candidate_count": counts.get(r.id, 0),
                "apoderados": assigned.get(r.id, []),
            }
            for r in rows
        ]

    def summary(self, user, filters):
        scope = self.list_query(user, filters).subquery()
        counts = {
            status.value: count
            for status, count in self.db.execute(
                select(scope.c.status, func.count()).group_by(scope.c.status)
            )
        }
        total = sum(counts.values())
        candidates = self.db.scalar(
            select(func.count(ListCandidate.id)).join(
                scope, scope.c.id == ListCandidate.list_id
            )
        )
        users_query = select(func.count(User.id)).where(
            User.role == UserRole.APODERADO, User.is_active.is_(True)
        )
        # With filters, count active assignees on selected lists. Global dashboard includes users without a list.
        if any(v is not None and v != "" for v in filters.model_dump().values()):
            users_query = users_query.where(
                select(ListAssignment.id)
                .join(scope, scope.c.id == ListAssignment.list_id)
                .where(ListAssignment.user_id == User.id)
                .exists()
            )
        active_users = (
            self.db.scalar(users_query) if user.role == UserRole.ADMIN else None
        )
        candidate_counts = (
            select(ListCandidate.list_id, func.count().label("qty"))
            .group_by(ListCandidate.list_id)
            .subquery()
        )
        by_office = [
            {
                "office_id": oid,
                "office_name": name,
                "lists": qty,
                "candidates": int(cqty),
            }
            for oid, name, qty, cqty in self.db.execute(
                select(
                    scope.c.office_id,
                    Office.name,
                    func.count(),
                    func.coalesce(func.sum(candidate_counts.c.qty), 0),
                )
                .join(Office, Office.id == scope.c.office_id)
                .outerjoin(candidate_counts, candidate_counts.c.list_id == scope.c.id)
                .group_by(scope.c.office_id, Office.name)
                .order_by(Office.name)
            )
        ]
        approved = counts.get(ListStatus.APROBADA_SISTEMA.value, 0)
        return {
            "total_lists": total,
            "total_candidates": candidates,
            "active_apoderados": active_users,
            "approved_lists": approved,
            "sent_lists": counts.get(ListStatus.ENVIADA_ADMIN.value, 0),
            "incomplete_lists": counts.get(ListStatus.INCOMPLETA.value, 0),
            "rejected_lists": counts.get(ListStatus.RECHAZADA_COMPOSICION.value, 0),
            "by_status": counts,
            "by_office": by_office,
            "approval_rate": round(100 * approved / total, 2) if total else 0,
            "approval_denominator": total,
        }

    def modules(self, user_id):
        return [
            {
                "id": m.id,
                "election_id": m.election_id,
                "office_id": m.office_id,
                "election_name": en,
                "office_name": on,
                "municipality_name": mn or "Provincial",
            }
            for m, en, on, mn in self.db.execute(
                select(UserModule, Election.name, Office.name, Municipality.name)
                .join(Election, Election.id == UserModule.election_id)
                .join(Office, Office.id == UserModule.office_id)
                .outerjoin(Municipality, Municipality.id == UserModule.municipality_id)
                .where(UserModule.user_id == user_id, UserModule.enabled.is_(True))
                .order_by(UserModule.id)
            )
        ]

    def members(self, list_id):
        return list(
            self.db.execute(
                select(ListCandidate, Candidate, Person)
                .join(Candidate, Candidate.id == ListCandidate.candidate_id)
                .join(Person, Person.id == Candidate.person_id)
                .where(ListCandidate.list_id == list_id)
                .order_by(ListCandidate.position_number, ListCandidate.id)
            )
        )

    def validation_history(self, candidate_ids):
        if not candidate_ids:
            return []
        return list(
            self.db.scalars(
                select(CandidateValidation)
                .where(
                    CandidateValidation.candidate_id.in_(candidate_ids),
                    CandidateValidation.validation_type != ValidationType.RENAPER,
                )
                .order_by(CandidateValidation.id.desc())
            )
        )

    def list_evaluations(self, list_id, limit=25):
        return list(
            self.db.scalars(
                select(ListValidation)
                .where(ListValidation.list_id == list_id)
                .order_by(ListValidation.id.desc())
                .limit(limit)
            )
        )

    def review_page(self, page, page_size):
        cv = CandidateValidation
        versioned = aliased(CandidateValidation)
        has_history = (
            select(versioned.id)
            .where(
                versioned.candidate_id == Candidate.id,
                versioned.validation_type != ValidationType.RENAPER,
                versioned.candidate_revision.is_not(None),
            )
            .correlate(Candidate)
            .exists()
        )
        current = (
            select(cv.id)
            .where(
                cv.candidate_id == Candidate.id,
                cv.validation_type != ValidationType.RENAPER,
                or_(
                    cv.candidate_revision == Candidate.revision,
                    and_(cv.candidate_revision.is_(None), ~has_history),
                ),
                cv.status == ValidationResult.WARNING,
            )
            .exists()
        )
        query = (
            select(Candidate, Person)
            .join(Person, Person.id == Candidate.person_id)
            .where(current)
        )
        total = self.db.scalar(select(func.count()).select_from(query.subquery()))
        rows = list(
            self.db.execute(
                query.order_by(Candidate.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        ids = [c.id for c, p in rows]
        links = {}
        if ids:
            for cid, lid, name in self.db.execute(
                select(
                    ListCandidate.candidate_id,
                    ElectoralList.id,
                    ElectoralList.list_name,
                )
                .join(ElectoralList, ElectoralList.id == ListCandidate.list_id)
                .where(ListCandidate.candidate_id.in_(ids))
            ):
                links.setdefault(cid, []).append({"id": lid, "name": name})
        return [
            {
                **{col.name: getattr(c, col.name) for col in c.__table__.columns},
                "first_name": p.first_name,
                "last_name": p.last_name,
                "dni": p.dni,
                "status": c.candidate_status,
                "lists": links.get(c.id, []),
            }
            for c, p in rows
        ], total

    def audit_page(self, filters, page, page_size):
        stmt = select(AuditLog, User.full_name).outerjoin(
            User, User.id == AuditLog.user_id
        )
        for field, column in [
            ("actor_id", "user_id"),
            ("action", "action"),
            ("entity_type", "entity_type"),
            ("entity_id", "entity_id"),
        ]:
            value = getattr(filters, field)
            if value:
                stmt = stmt.where(getattr(AuditLog, column) == value)
        if filters.list_id:
            cids = select(ListCandidate.candidate_id).where(
                ListCandidate.list_id == filters.list_id
            )
            stmt = stmt.where(
                or_(
                    and_(
                        AuditLog.entity_type == "electoral_lists",
                        AuditLog.entity_id == filters.list_id,
                    ),
                    and_(
                        AuditLog.entity_type == "candidates",
                        AuditLog.entity_id.in_(cids),
                    ),
                )
            )
        for day, after in [(filters.date_from, True), (filters.date_to, False)]:
            if day:
                local = datetime.combine(
                    day + (timedelta(days=0) if after else timedelta(days=1)),
                    time.min,
                    tzinfo=ZoneInfo("America/Argentina/Cordoba"),
                )
                utc = local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
                stmt = stmt.where(
                    AuditLog.created_at >= utc if after else AuditLog.created_at < utc
                )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = self.db.execute(
            stmt.order_by(AuditLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return [
            {
                "id": a.id,
                "actor_id": a.user_id,
                "actor_name": name or "Sistema",
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "details": a.details_json,
                "created_at": a.created_at,
            }
            for a, name in rows
        ], total
