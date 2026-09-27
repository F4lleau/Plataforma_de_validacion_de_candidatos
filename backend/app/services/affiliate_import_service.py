import re
import unicodedata
from datetime import date, datetime, timedelta

import pandas as pd
from openpyxl import load_workbook

from app.models import AffiliateImportBatch, PadronCircuit, PartyMember
from app.repositories.management_repository import ManagementRepository
from app.repositories.padron_repository import PadronRepository
from app.services.audit_service import AuditService


class AffiliateImportService:
    supported_extensions = (".xlsx", ".xlsm", ".xls", ".ods", ".csv", ".tsv", ".txt")
    columns = {
        "dni": [
            "dni",
            "documento",
            "nro documento",
            "numero documento",
            "nro_documento",
            "matricula",
        ],
        "first_name": ["nombre", "nombres"],
        "last_name": ["apellido", "apellidos"],
        "full_name": [
            "apellido nombre",
            "apellido y nombre",
            "apellidos y nombres",
            "nombre apellido",
            "nombre y apellido",
            "nombre completo",
        ],
        "affiliate_number": [
            "nro afiliado",
            "numero afiliado",
            "nro_afiliado",
            "afiliado",
            "ficha",
        ],
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
        return re.sub(r"[^a-zA-Z0-9]+", " ", cls.normalize_text(value)).strip().lower()

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
        raise ValueError("fecha invalida; usar DD/MM/AAAA o AAAA-MM-DD")

    @staticmethod
    def clean_text(value):
        return str(value).strip() if value is not None and not pd.isna(value) else ""

    @classmethod
    def split_full_name(cls, value, source_header=""):
        text = cls.clean_text(value)
        if not text:
            return "", ""
        if "," in text:
            last_name, first_name = text.split(",", 1)
            return first_name.strip(), last_name.strip()
        parts = text.split()
        if len(parts) == 1:
            return "", parts[0]
        if cls.header(source_header).startswith("nombre"):
            return " ".join(parts[:-1]), parts[-1]
        return " ".join(parts[1:]), parts[0]

    @staticmethod
    def fit_column(value, field):
        length = getattr(PartyMember.__table__.c[field].type, "length", None)
        if length and value and len(value) > length:
            return value[:length].strip()
        return value

    @classmethod
    def detect_header_row(cls, df):
        known_headers = {
            cls.header(alias)
            for aliases in cls.columns.values()
            for alias in aliases
        }
        best_index, best_score = None, 0
        for index, row in df.head(80).iterrows():
            values = {cls.header(value) for value in row.tolist() if cls.header(value)}
            score = len(values & known_headers)
            has_document = bool(values & {cls.header(alias) for alias in cls.columns["dni"]})
            if has_document and score > best_score:
                best_index, best_score = index, score
        if best_index is None or best_score < 2:
            raise ValueError("Falta columna obligatoria: DNI/Matricula.")
        return best_index

    @classmethod
    def with_detected_header(cls, df):
        header_index = cls.detect_header_row(df)
        headers = df.iloc[header_index].tolist()
        data = df.iloc[header_index + 1 :].copy()
        data.columns = headers
        data = data.dropna(how="all").reset_index(drop=True)
        return data

    @classmethod
    def read_openpyxl(cls, file_path):
        workbook = load_workbook(file_path, read_only=True, data_only=True)
        sheet = workbook.active
        preview, rows, headers = [], [], None
        header_index = None
        for index, row in enumerate(sheet.iter_rows(values_only=True)):
            if headers is None:
                preview.append(row)
                if len(preview) >= 80:
                    header_index = cls.detect_header_row(pd.DataFrame(preview))
                    headers = list(preview[header_index])
                    rows.extend(preview[header_index + 1 :])
                    preview = []
            else:
                rows.append(row)
        workbook.close()
        if headers is None:
            header_index = cls.detect_header_row(pd.DataFrame(preview))
            headers = list(preview[header_index])
            rows.extend(preview[header_index + 1 :])
        data = pd.DataFrame(rows, columns=headers)
        return data.dropna(how="all").reset_index(drop=True)

    @classmethod
    def read_file(cls, file_path, file_name):
        extension = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        if extension in (".csv", ".txt"):
            raw = pd.read_csv(file_path, sep=None, engine="python", dtype=object, header=None)
            return cls.with_detected_header(raw)
        if extension == ".tsv":
            raw = pd.read_csv(file_path, sep="\t", dtype=object, header=None)
            return cls.with_detected_header(raw)
        if extension in (".xlsx", ".xlsm"):
            return cls.read_openpyxl(file_path)
        if extension == ".xls":
            raw = pd.read_excel(file_path, engine="xlrd", dtype=object, header=None)
            return cls.with_detected_header(raw)
        if extension == ".ods":
            raw = pd.read_excel(file_path, engine="odf", dtype=object, header=None)
            return cls.with_detected_header(raw)
        raise ValueError("Formato no soportado.")

    def import_excel(self, file_path, file_name, imported_by):
        # Parse before obtaining the transaction lock. Never activate a partial file.
        errors, members, duplicates, seen = [], [], 0, set()
        circuit_catalog = {}
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
            df = self.read_file(file_path, file_name)
            if len(df) > 500000:
                raise ValueError("Maximo 500000 filas por archivo.")
            batch.total_rows = len(df)
            headers = {self.header(c): c for c in df.columns}
            if len(headers) != len(df.columns):
                raise ValueError("Hay encabezados duplicados.")
            mapping = {
                field: next(
                    (
                        headers[self.header(alias)]
                        for alias in aliases
                        if self.header(alias) in headers
                    ),
                    None,
                )
                for field, aliases in self.columns.items()
            }
            if mapping["dni"] is None:
                raise ValueError("Falta columna obligatoria: DNI/Matricula.")
            for index, row in df.iterrows():
                try:
                    values = {
                        field: (
                            row[col] if col is not None and pd.notna(row[col]) else None
                        )
                        for field, col in mapping.items()
                    }
                    raw_dni = values.pop("dni")
                    dni = self.clean_dni(raw_dni)
                    raw_dni_header = self.header(raw_dni)
                    if raw_dni_header in {self.header(alias) for alias in self.columns["dni"]}:
                        continue
                    if not dni and not self.clean_text(raw_dni):
                        continue
                    if not re.fullmatch(r"\d{6,9}", dni):
                        raise ValueError("documento invalido")
                    if dni in seen:
                        duplicates += 1
                        batch.invalid_rows += 1
                        continue
                    seen.add(dni)

                    raw_full_name = values.pop("full_name", None)
                    for key, value in values.items():
                        if key.endswith("_date"):
                            try:
                                values[key] = self.parse_date(value)
                            except ValueError:
                                values[key] = None
                        elif key in (
                            "first_name",
                            "last_name",
                            "profession",
                            "address",
                        ):
                            values[key] = self.clean_text(value) or None
                        else:
                            values[key] = self.normalize_text(value) or None

                    if not values["first_name"] or not values["last_name"]:
                        first_name, last_name = self.split_full_name(
                            raw_full_name, mapping["full_name"] or ""
                        )
                        values["first_name"] = values["first_name"] or first_name
                        values["last_name"] = values["last_name"] or last_name
                    values["first_name"] = values["first_name"] or ""
                    values["last_name"] = values["last_name"] or ""

                    for key, value in values.items():
                        values[key] = self.fit_column(value, key)
                    if values.get("circuit"):
                        circuit_key = (
                            values.get("section_code"),
                            values.get("circuit_code"),
                            values.get("circuit"),
                        )
                        circuit_catalog[circuit_key] = {
                            "name": values.get("circuit"),
                            "code": values.get("circuit_code"),
                            "section": values.get("section"),
                            "section_code": values.get("section_code"),
                        }

                    values["affiliation_status"] = values["affiliation_status"] or (
                        "activo"
                        if mapping["affiliation_status"] is None
                        else "sin informar"
                    )
                    full_name = (
                        f"{values['last_name']} {values['first_name']}".strip()
                        or self.clean_text(raw_full_name)
                        or dni
                    )
                    full_name = self.fit_column(full_name, "full_name")
                    members.append(
                        {
                            **values,
                            "dni": dni,
                            "full_name": full_name,
                            "normalized_name": self.normalize_text(full_name),
                            "is_active": values["affiliation_status"].lower() == "activo",
                            "created_at": datetime.utcnow(),
                        }
                    )
                except (ValueError, TypeError) as exc:
                    batch.invalid_rows += 1
                    if len(errors) < 30:
                        errors.append(f"Fila {index + 2}: {exc}")
            batch.valid_rows = len(members)
            if errors or not members:
                raise ValueError("; ".join(errors) or "Archivo sin filas validas.")
            batch.status = "completed"
            batch.notes = f"Importacion completa. Duplicados: {duplicates}."
        except Exception as exc:
            batch.notes = (
                str(exc)[:2000]
                if isinstance(exc, ValueError)
                else "No se pudo leer el archivo. Verifica el formato y las columnas."
            )
        try:
            self.padron.lock_import()
            self.repo.add(batch)
            if batch.status == "completed":
                for member in members:
                    member["source_batch_id"] = batch.id
                circuits = [
                    {**circuit, "source_batch_id": batch.id}
                    for circuit in circuit_catalog.values()
                ]
                if circuits:
                    self.db.bulk_insert_mappings(PadronCircuit, circuits)
                for start in range(0, len(members), 5000):
                    self.db.bulk_insert_mappings(
                        PartyMember, members[start : start + 5000]
                    )
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
