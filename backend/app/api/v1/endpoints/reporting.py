from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import require_admin
from app.models import User
from app.schemas.reporting import ListFilters, AuditFilters, AuditPage, AuditEvent
from app.services.reporting_service import ReportingService

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/lists")
def lists(
    filters: ListFilters = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ReportingService(db).page(user, filters, page, page_size)


@router.get("/reports")
def summary(
    filters: ListFilters = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    return ReportingService(db).summary(user, filters)


@router.get("/candidate-review")
def review(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return ReportingService(db).review(page, page_size)


@router.get("/audit", response_model=AuditPage)
def audit(
    filters: AuditFilters = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return ReportingService(db).audit_page(filters, page, page_size)


@router.get("/audit/{identity}", response_model=AuditEvent)
def audit_detail(identity: int, db: Session = Depends(get_db)):
    return ReportingService(db).audit_detail(identity)


from typing import Literal
from fastapi.responses import Response
from app.services.export_service import ExportService


@router.get("/exports/lists")
def export_lists(
    format: Literal["xlsx", "csv"] = "xlsx",
    filters: ListFilters = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    content, mime, name = ExportService(db).lists(user, filters, format)
    return Response(
        content,
        media_type=mime,
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/exports/reports")
def export_reports(
    format: Literal["xlsx", "pdf"] = "xlsx",
    filters: ListFilters = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    content, mime, name = ExportService(db).lists(user, filters, format, True)
    return Response(
        content,
        media_type=mime,
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/exports/padron")
def export_padron(
    format: Literal["xlsx", "csv"] = "xlsx",
    search: str = "",
    section: str = "",
    circuit: str = "",
    state: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    content, mime, name = ExportService(db).padron(
        user, dict(search=search, section=section, circuit=circuit, state=state), format
    )
    return Response(
        content,
        media_type=mime,
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
            "Cache-Control": "no-store",
        },
    )
