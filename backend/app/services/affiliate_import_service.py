import re
import unicodedata
from datetime import datetime, date, timedelta
import pandas as pd
from app.models import AffiliateImportBatch, PartyMember
from app.repositories.management_repository import ManagementRepository
from app.repositories.padron_repository import PadronRepository
from app.services.audit_service import AuditService


class AffiliateImportService:
    columns = {
        "dni": ["dni", "documento", "nro_documento", "matricula"],
        "first_name": ["nombre", "nombres"],
        "last_name": ["apellido", "apellidos"],
        "affiliate_number": ["nro_afiliado", "afiliado", "ficha"],
        "gender": ["sexo", "genero"],
        "section": ["seccion"],
        "section_code": ["cod seccion"],
        "circuit": ["circuito"],
        "circuit_code": ["cod circuito"],
        "document_type": ["tipo documento"],
        "birth_date": ["fecha nacimiento"],
        "birth_class": ["clase"],
        "elector_status": ["estado actual elector"],
        "affiliation_status": ["estado afiliacion"],
        "affiliation_date": ["fecha afiliacion"],
        "illiterate": ["analfabeto"],
        "profession": ["profesion"],
        "address_date": ["fecha domicilio"],
        "address": ["domicilio"],
    }

    def __init__(self, db):
        self.db = db
        self.repo = ManagementRepository(db)
        self.padron = PadronRepository(db)

    @staticmethod
    def normalize_text(value):
        if value is None or pd.isna(value):
            return ""
        return re.sub(
            r"\s+",
            " ",
            unicodedata.normalize("NFKD", str(value).strip().upper())
            .encode("ascii", "ignore")
            .decode(),
        )

    @classmethod
    def header(cls, value):
        return re.sub(r"[._\s]+", " ", cls.normalize_text(value)).strip().lower()

    @staticmethod
    def clean_dni(value):
        if value is None or pd.isna(value):
            return ""
        if isinstance(value, (int, float)):
            return str(int(value)) if float(value).is_integer() else ""
        value = str(value).strip()
        if re.fullmatch(r"\d+\.0", value):
            return value[:-2]
        return re.sub(r"[.\s-]", "", value)

    @staticmethod
    def parse_date(value):
        if value is None or pd.isna(value) or value == "":
            return None
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, (int, float)):
            if not 1 <= value <= 100000:
                raise ValueError("fecha Excel fuera de rango")
            return (datetime(1899, 12, 30) + timedelta(days=value)).date()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except ValueError:
                pass
        raise ValueError("fecha inválida; usar DD/MM/AAAA o AAAA-MM-DD")

    def import_excel(self, file_path, file_name, imported_by):
        # Parse before obtaining the transaction lock. Never activate a partial file.
        errors, members, duplicates, seen = [], [], 0, set()
        batch = AffiliateImportBatch(
            file_name=file_name[:255],
            imported_by=imported_by,
            status="failed",
            total_rows=0,
            valid_rows=0,
            invalid_rows=0,
            is_current=False,
        )
        try:
            df = pd.read_excel(file_path, engine="openpyxl", dtype=object)
            if len(df) > 500000:
                raise ValueError("Máximo 500000 filas por archivo.")
            batch.total_rows = len(df)
            headers = {self.header(c): c for c in df.columns}
            if len(headers) != len(df.columns):
                raise ValueError("Hay encabezados duplicados.")
            mapping = {
                field: next(
                    (
                        headers[self.header(a)]
                        for a in aliases
                        if self.header(a) in headers
                    ),
                    None,
                )
                for field, aliases in self.columns.items()
            }
            if any(mapping[k] is None for k in ("dni", "first_name", "last_name")):
                raise ValueError("Faltan columnas: DNI/Matrícula, Nombre y Apellido.")
            for index, row in df.iterrows():
                try:
                    values = {
                        field: (
                            row[col] if col is not None and pd.notna(row[col]) else None
                        )
                        for field, col in mapping.items()
                    }
                    dni = self.clean_dni(values.pop("dni"))
                    if not re.fullmatch(r"\d{7,9}", dni):
                        raise ValueError("documento inválido")
                    if dni in seen:
                        duplicates += 1
                        raise ValueError("documento duplicado")
                    seen.add(dni)
                    for key, value in values.items():
                        if key.endswith("_date"):
                            values[key] = self.parse_date(value)
                        elif key in (
                            "first_name",
                            "last_name",
                            "profession",
                            "address",
                        ):
                            values[key] = (
                                str(value).strip() if value is not None else None
                            )
                        else:
                            values[key] = self.normalize_text(value) or None
                    if not values["first_name"] or not values["last_name"]:
                        raise ValueError("nombre y apellido obligatorios")
                    for key, value in values.items():
                        length = getattr(
                            PartyMember.__table__.c[key].type, "length", None
                        )
                        if length and value and len(value) > length:
                            raise ValueError(f"{key}: longitud máxima {length}")
                    values["affiliation_status"] = values["affiliation_status"] or (
                        "activo"
                        if mapping["affiliation_status"] is None
                        else "sin informar"
                    )
                    full_name = f"{values['last_name']} {values['first_name']}"
                    if len(full_name) > 255:
                        raise ValueError("nombre completo demasiado largo")
                    members.append(
                        PartyMember(
                            dni=dni,
                            **values,
                            full_name=full_name,
                            normalized_name=self.normalize_text(full_name),
                            is_active=values["affiliation_status"].lower() == "activo",
                        )
                    )
                except (ValueError, TypeError) as exc:
                    batch.invalid_rows += 1
                    if len(errors) < 30:
                        errors.append(f"Fila {index + 2}: {exc}")
            batch.valid_rows = len(members)
            if errors or not members:
                raise ValueError("; ".join(errors) or "Archivo sin filas válidas.")
            batch.status = "completed"
            batch.notes = f"Importación completa. Duplicados: {duplicates}."
        except Exception as exc:
            batch.notes = (
                str(exc)[:2000]
                if isinstance(exc, ValueError)
                else "No se pudo leer el archivo XLSX."
            )
        try:
            self.padron.lock_import()
            self.repo.add(batch)
            if batch.status == "completed":
                for member in members:
                    member.source_batch_id = batch.id
                self.db.add_all(members)
                self.db.flush()
                self.padron.activate(batch)
            AuditService(self.db).record(
                imported_by,
                "padron.import",
                "affiliate_import_batches",
                batch.id,
                {
                    "status": batch.status,
                    "valid": batch.valid_rows,
                    "invalid": batch.invalid_rows,
                },
            )
            self.db.commit()
            return batch
        except Exception:
            self.db.rollback()
            raise
