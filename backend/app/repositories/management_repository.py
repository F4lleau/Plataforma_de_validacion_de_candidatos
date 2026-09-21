"""Persistence primitives shared by administrative services; never commit here."""

from sqlalchemy import select, func
from app.models import (
    ElectionRule,
    UserModule,
    ListAssignment,
    ElectoralList,
    ListCandidate,
    Candidate,
    Person,
    CandidateValidation,
)


class ManagementRepository:
    def __init__(self, db):
        self.db = db

    def get(self, model, identity, lock=False):
        return (
            self.db.scalar(
                select(model)
                .where(model.id == identity)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            if lock
            else self.db.get(model, identity)
        )

    def all(self, model, **filters):
        return list(
            self.db.scalars(select(model).filter_by(**filters).order_by(model.id)).all()
        )

    def add(self, obj):
        self.db.add(obj)
        self.db.flush()
        return obj

    def remove(self, obj):
        self.db.delete(obj)

    def rule(self, election_id, office_id):
        return self.db.scalar(
            select(ElectionRule)
            .where(
                ElectionRule.election_id == election_id,
                ElectionRule.office_id == office_id,
            )
            .order_by(ElectionRule.version.desc())
        )

    def modules(self, user_id):
        return self.all(UserModule, user_id=user_id)

    def assigned(self, list_id, user_id):
        return bool(self.all(ListAssignment, list_id=list_id, user_id=user_id))

    def membership(self, list_id, candidate_id):
        return self.db.scalar(
            select(ListCandidate).where(
                ListCandidate.list_id == list_id,
                ListCandidate.candidate_id == candidate_id,
            )
        )

    def person(self, dni):
        return self.db.scalar(select(Person).where(Person.dni == dni))

    def number_exists(
        self, election_id, office_id, municipality_id, number, exclude=None
    ):
        query = select(ElectoralList.id).where(
            ElectoralList.election_id == election_id,
            ElectoralList.office_id == office_id,
            ElectoralList.municipality_id == municipality_id,
            ElectoralList.list_number == number,
        )
        if exclude:
            query = query.where(ElectoralList.id != exclude)
        return self.db.scalar(query) is not None

    def person_other_candidates(self, person_id, candidate_id):
        return self.db.scalar(
            select(func.count())
            .select_from(Candidate)
            .where(Candidate.person_id == person_id, Candidate.id != candidate_id)
        )

    def validations(self, candidate):
        return list(
            self.db.scalars(
                select(CandidateValidation)
                .where(
                    CandidateValidation.candidate_id == candidate.id,
                    CandidateValidation.candidate_revision == candidate.revision,
                )
                .order_by(CandidateValidation.id.desc())
            ).all()
        )
