from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user, require_admin
from app.models import Election, Office, User
from app.schemas.management import (
    ElectionInput,
    ElectionOutput,
    EnabledMunicipalitiesInput,
    MunicipalityOutput,
)
from app.services.management_service import ManagementService

router = APIRouter()


@router.get("/", response_model=list[ElectionOutput])
def listing(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ManagementService(db).catalogs(Election, user)


@router.post("/", status_code=201, response_model=ElectionOutput)
def create(
    payload: ElectionInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).catalog_save(Election, payload, user)


@router.put("/{identity}", response_model=ElectionOutput)
def update(
    identity: int,
    payload: ElectionInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).catalog_save(Election, payload, user, identity)


@router.delete("/{identity}")
def delete(
    identity: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).deactivate(Election, identity, user)


@router.get("/{identity}/municipalities", response_model=list[MunicipalityOutput])
def enabled_municipalities(
    identity: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return ManagementService(db).election_municipalities(identity, user)


@router.put("/{identity}/municipalities")
def save_enabled_municipalities(
    identity: int,
    payload: EnabledMunicipalitiesInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).save_election_municipalities(identity, payload, user)


from app.schemas.management import RulesInput
from app.models import ElectionRule


@router.get("/{identity}/rules")
def rules(
    identity: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    service = ManagementService(db)
    if identity not in {e.id for e in service.catalogs(Election, user)}:
        from fastapi import HTTPException

        raise HTTPException(403, "Elección no habilitada.")
    allowed = {o.id for o in service.catalogs(Office, user)}
    return [
        service.rule_output(r)
        for r in service.repo.all(ElectionRule, election_id=identity)
        if r.office_id in allowed
    ]


@router.post("/{identity}/rules/{office_id}", status_code=201)
def save_rules(
    identity: int,
    office_id: int,
    payload: RulesInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ManagementService(db).save_rules(identity, office_id, payload, user)
