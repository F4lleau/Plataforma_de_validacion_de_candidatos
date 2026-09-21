from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.management import ListInput, ListEdit, AssignmentsInput, CandidateInput
from app.services.electoral_workflow_service import ElectoralWorkflowService

router = APIRouter()


@router.get("/")
def listing(
    search: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).listing(user, search, status)


@router.post("/", status_code=201)
def create(
    payload: ListInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).create(payload, user)


@router.get("/page")
def page(
    search: str = "",
    status: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).page(user, search, status, page, page_size)


@router.get("/{identity}")
def detail(
    identity: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    from app.services.inspection_service import InspectionService
    return InspectionService(db).detail(identity, user)


@router.put("/{identity}")
def edit(
    identity: int,
    payload: ListEdit,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).edit(identity, payload, user)


@router.put("/{identity}/assignments")
def assign(
    identity: int,
    payload: AssignmentsInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ElectoralWorkflowService(db).assign(identity, payload, user)


@router.post("/{identity}/rules/adopt")
def bind_rules(
    identity: int, db: Session = Depends(get_db), user: User = Depends(require_admin)
):
    return ElectoralWorkflowService(db).bind_rules(identity, user)


@router.post("/{identity}/candidates", status_code=201)
def candidate_create(
    identity: int,
    payload: CandidateInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).save_candidate(identity, payload, user)


@router.put("/{identity}/candidates/{candidate_id}")
def candidate_update(
    identity: int,
    candidate_id: int,
    payload: CandidateInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).save_candidate(
        identity, payload, user, candidate_id
    )


@router.post("/{identity}/candidates/{candidate_id}/validate")
def candidate_validate(
    identity: int,
    candidate_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ElectoralWorkflowService(db).retry(identity, candidate_id, user)


from app.services.submission_service import SubmissionService

@router.post('/{identity}/evaluate')
def evaluate(identity: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return SubmissionService(db).evaluate(identity,user)

@router.post('/{identity}/submit')
def submit(identity: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return SubmissionService(db).submit(identity,user)
