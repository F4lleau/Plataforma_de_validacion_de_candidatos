from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
def dashboard_summary():
    return {
        "total_lists": 0,
        "approved_lists": 0,
        "incomplete_lists": 0,
        "active_apoderados": 0,
    }