from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def auth_health():
    return {"module": "auth", "status": "ok"}