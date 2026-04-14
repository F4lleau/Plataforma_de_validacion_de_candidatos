from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_candidates():
    return {"message": "list candidates"}