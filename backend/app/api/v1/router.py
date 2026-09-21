from fastapi import APIRouter, Depends
from app.core.security import get_current_user, require_admin

from app.api.v1.endpoints import (
    auth,
    users,
    elections,
    offices,
    municipalities,
    lists,
    candidates,
    validations,
    dashboard,
    padron,
    list_templates,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(
    users.router, prefix="/users", tags=["Users"], dependencies=[Depends(require_admin)]
)
api_router.include_router(
    elections.router,
    prefix="/elections",
    tags=["Elections"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    offices.router,
    prefix="/offices",
    tags=["Offices"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    municipalities.router,
    prefix="/municipalities",
    tags=["Municipalities"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(lists.router, prefix="/lists", tags=["Lists"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(
    validations.router, prefix="/validations", tags=["Validations"]
)
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(padron.router, prefix="/padron", tags=["Padron"])
api_router.include_router(
    list_templates.router,
    prefix="/list-templates",
    tags=["List Templates"],
    dependencies=[Depends(get_current_user)],
)

from app.api.v1.endpoints import reporting

api_router.include_router(reporting.router, prefix="/admin", tags=["Reports and audit"])

from app.api.v1.endpoints import account_security

api_router.include_router(
    account_security.router, prefix="/admin", tags=["Account security"]
)

from app.api.v1.endpoints import invitations

api_router.include_router(
    invitations.admin_router, prefix="/admin/invitations", tags=["Invitations"]
)
api_router.include_router(
    invitations.public_router, prefix="/auth/invitations", tags=["Invitations"]
)
