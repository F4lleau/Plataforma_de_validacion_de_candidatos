from io import BytesIO

import pandas as pd
from sqlalchemy import select

from app.models import PartyMember
from app.repositories.padron_repository import PadronRepository
from app.services.affiliate_import_service import AffiliateImportService
from tests.test_auth_rbac import db_session, users


def xlsx(rows):
    file = BytesIO()
    pd.DataFrame(rows).to_excel(file, index=False)
    file.seek(0)
    return file


def xlsx_raw(rows):
    file = BytesIO()
    pd.DataFrame(rows).to_excel(file, index=False, header=False)
    file.seek(0)
    return file


def test_import_accepts_single_full_name_column_and_missing_optional_columns(
    db_session, users
):
    admin, _ = users
    batch = AffiliateImportService(db_session).import_excel(
        xlsx(
            [
                {
                    "Apellido y Nombre": "Perez Ana",
                    "Matricula": 98000010,
                }
            ]
        ),
        "padron.xlsx",
        admin.id,
    )

    member = db_session.scalar(select(PartyMember).where(PartyMember.dni == "98000010"))

    assert batch.status == "completed"
    assert member.first_name == "Ana"
    assert member.last_name == "Perez"
    assert member.section is None
    assert member.affiliation_status == "activo"


def test_import_keeps_row_when_optional_date_is_invalid(db_session, users):
    admin, _ = users
    batch = AffiliateImportService(db_session).import_excel(
        xlsx(
            [
                {
                    "Apellido": "Gomez",
                    "Nombre": "Luis",
                    "Matricula": 98000011,
                    "Fecha nacimiento": "sin fecha",
                }
            ]
        ),
        "padron.xlsx",
        admin.id,
    )

    member = db_session.scalar(select(PartyMember).where(PartyMember.dni == "98000011"))

    assert batch.status == "completed"
    assert member.birth_date is None


def test_import_skips_duplicate_documents_without_failing(db_session, users):
    admin, _ = users
    batch = AffiliateImportService(db_session).import_excel(
        xlsx(
            [
                {"Apellido": "Gomez", "Nombre": "Luis", "Matricula": 98000012},
                {"Apellido": "Gomez", "Nombre": "Luis", "Matricula": 98000012},
            ]
        ),
        "padron.xlsx",
        admin.id,
    )

    rows = db_session.scalars(
        select(PartyMember).where(PartyMember.dni == "98000012")
    ).all()

    assert batch.status == "completed"
    assert batch.valid_rows == 1
    assert batch.invalid_rows == 1
    assert len(rows) == 1


def test_import_detects_header_below_metadata_and_skips_repeated_headers(
    db_session, users
):
    admin, _ = users
    header = [
        "Sección",
        "Cod. Sección",
        "Circuito",
        "Cod. Circuito",
        "Apellido",
        "Nombre",
        "Género",
        "Tipo documento",
        "Matrícula",
    ]
    batch = AffiliateImportService(db_session).import_excel(
        xlsx_raw(
            [
                ["Usuario:", "Supervisor"],
                ["Distrito:", "CHACO"],
                header,
                ["SAN FERNANDO", 1, "RESISTENCIA", 1, "Perez", "Ana", "F", "DNI", 759504],
                header,
                ["SAN FERNANDO", 1, "RESISTENCIA", 1, "Ruiz", "Luis", "M", "DNI", 98000013],
            ]
        ),
        "padron.xlsx",
        admin.id,
    )

    assert batch.status == "completed"
    assert batch.valid_rows == 2
    assert db_session.scalar(select(PartyMember).where(PartyMember.dni == "759504"))


def test_import_builds_circuit_catalog_and_filters_by_codes(db_session, users):
    admin, _ = users
    batch = AffiliateImportService(db_session).import_excel(
        xlsx(
            [
                {
                    "Seccion": "SAN FERNANDO",
                    "Cod. Seccion": 1,
                    "Circuito": "RESISTENCIA",
                    "Cod. Circuito": 11,
                    "Apellido": "Perez",
                    "Nombre": "Ana",
                    "Matricula": 98000014,
                },
                {
                    "Seccion": "CHACABUCO",
                    "Cod. Seccion": 20,
                    "Circuito": "CHARATA",
                    "Cod. Circuito": 119,
                    "Apellido": "Ruiz",
                    "Nombre": "Luis",
                    "Matricula": 98000015,
                },
            ]
        ),
        "padron.xlsx",
        admin.id,
    )

    repo = PadronRepository(db_session)
    catalog = repo.catalog()
    result = repo.query(section_code="20", circuit_code="119")

    assert batch.status == "completed"
    assert catalog["sections"] == [
        {"id": "20", "name": "CHACABUCO", "code": "20"},
        {"id": "1", "name": "SAN FERNANDO", "code": "1"},
    ]
    assert {
        (item["name"], item["code"], item["section"], item["section_code"])
        for item in catalog["circuits"]
    } == {
        ("RESISTENCIA", "11", "SAN FERNANDO", "1"),
        ("CHARATA", "119", "CHACABUCO", "20"),
    }
    assert result["total"] == 1
    assert result["items"][0].dni == "98000015"
