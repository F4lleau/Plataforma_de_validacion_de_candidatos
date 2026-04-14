from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_lists():
    return {"message": "list electoral lists"}