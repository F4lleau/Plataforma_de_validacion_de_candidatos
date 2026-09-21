from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.reporting import ListFilters
from app.services.reporting_service import ReportingService

router=APIRouter()

@router.get('/summary')
def summary(filters:ListFilters=Depends(),db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return ReportingService(db).dashboard(user,filters)
