from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_validations():
    return {"message": "list validations"}