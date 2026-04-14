from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_elections():
    return {"message": "list elections"}