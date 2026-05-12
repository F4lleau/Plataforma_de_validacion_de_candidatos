from fastapi import APIRouter

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
    list_templates
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(elections.router, prefix="/elections", tags=["Elections"])
api_router.include_router(offices.router, prefix="/offices", tags=["Offices"])
api_router.include_router(municipalities.router, prefix="/municipalities", tags=["Municipalities"])
api_router.include_router(lists.router, prefix="/lists", tags=["Lists"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(validations.router, prefix="/validations", tags=["Validations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(padron.router, prefix="/padron", tags=["Padron"])
api_router.include_router(list_templates.router, prefix="/list-templates", tags=["List Templates"])