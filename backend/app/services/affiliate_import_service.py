import re
import unicodedata

import pandas as pd
from sqlalchemy.orm import Session

from app.models.affiliate_import_batch import AffiliateImportBatch
from app.models.party_member import PartyMember
from app.repositories.affiliate_import_batch_repository import AffiliateImportBatchRepository
from app.repositories.party_member_repository import PartyMemberRepository


class AffiliateImportService:
    def __init__(self, db: Session):
        self.db = db
        self.batch_repository = AffiliateImportBatchRepository(db)
        self.party_member_repository = PartyMemberRepository(db)

    @staticmethod
    def normalize_text(value: str | None) -> str:
        if not value:
            return ""

        value = str(value).strip().upper()
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("utf-8")
        value = re.sub(r"\s+", " ", value)
        return value

    @staticmethod
    def clean_dni(value: str | int | float | None) -> str:
        if value is None:
            return ""

        value = str(value)
        digits = re.sub(r"\D", "", value)
        return digits

    def import_excel(self, file_path: str, file_name: str, imported_by: int) -> AffiliateImportBatch:
        batch = AffiliateImportBatch(
            file_name=file_name,
            imported_by=imported_by,
            status="processing",
        )
        batch = self.batch_repository.create(batch)

        df = pd.read_excel(file_path)

        # Ajustar estos nombres cuando confirmemos columnas reales del padrón
        expected_columns = {
            "dni": ["dni", "documento", "nro_documento"],
            "first_name": ["nombre", "nombres"],
            "last_name": ["apellido", "apellidos"],
            "affiliate_number": ["nro_afiliado", "afiliado", "ficha"],
            "gender": ["sexo", "genero"],
            "section": ["seccion"],
            "circuit": ["circuito"],
        }

        normalized_columns = {col.lower().strip(): col for col in df.columns}

        def resolve_column(options: list[str]) -> str | None:
            for option in options:
                if option in normalized_columns:
                    return normalized_columns[option]
            return None

        dni_col = resolve_column(expected_columns["dni"])
        first_name_col = resolve_column(expected_columns["first_name"])
        last_name_col = resolve_column(expected_columns["last_name"])
        affiliate_number_col = resolve_column(expected_columns["affiliate_number"])
        gender_col = resolve_column(expected_columns["gender"])
        section_col = resolve_column(expected_columns["section"])
        circuit_col = resolve_column(expected_columns["circuit"])

        if not dni_col or not first_name_col or not last_name_col:
            batch.status = "failed"
            batch.notes = "No se encontraron columnas mínimas requeridas: dni, nombre, apellido."
            batch = self.batch_repository.update(batch)
            return batch

        members: list[PartyMember] = []
        total_rows = len(df)
        valid_rows = 0
        invalid_rows = 0

        for _, row in df.iterrows():
            dni = self.clean_dni(row.get(dni_col))
            first_name = self.normalize_text(row.get(first_name_col))
            last_name = self.normalize_text(row.get(last_name_col))

            if not dni or not first_name or not last_name:
                invalid_rows += 1
                continue

            full_name = f"{last_name} {first_name}".strip()

            member = PartyMember(
                dni=dni,
                affiliate_number=str(row.get(affiliate_number_col)).strip() if affiliate_number_col and pd.notna(row.get(affiliate_number_col)) else None,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                normalized_name=full_name,
                gender=self.normalize_text(row.get(gender_col)) if gender_col and pd.notna(row.get(gender_col)) else None,
                section=self.normalize_text(row.get(section_col)) if section_col and pd.notna(row.get(section_col)) else None,
                circuit=self.normalize_text(row.get(circuit_col)) if circuit_col and pd.notna(row.get(circuit_col)) else None,
                affiliation_status="activo",
                source_batch_id=batch.id,
                is_active=True,
            )
            members.append(member)
            valid_rows += 1

        if members:
            self.party_member_repository.bulk_create(members)

        batch.total_rows = total_rows
        batch.valid_rows = valid_rows
        batch.invalid_rows = invalid_rows
        batch.status = "completed"
        batch.notes = f"Importación finalizada. Registros válidos: {valid_rows}. Inválidos: {invalid_rows}."
        batch = self.batch_repository.update(batch)

        return batch