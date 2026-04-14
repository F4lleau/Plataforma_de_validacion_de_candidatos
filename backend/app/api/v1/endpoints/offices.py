from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_offices():
    return {"message": "list offices"}