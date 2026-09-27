from sqlalchemy import select, func, update, text
from app.models import AffiliateImportBatch, PadronCircuit, PartyMember


class PadronRepository:
    def __init__(self, db):
        self.db = db

    def lock_import(self):
        if self.db.bind.dialect.name == "postgresql":
            self.db.execute(
                text("SELECT pg_advisory_xact_lock(hashtext('padron_import'))")
            )

    def activate(self, batch):
        self.db.execute(
            update(AffiliateImportBatch)
            .where(AffiliateImportBatch.is_current.is_(True))
            .values(is_current=False)
        )
        self.db.flush()
        batch.is_current = True
        self.db.flush()

    def query(
        self,
        search="",
        section="",
        circuit="",
        state="",
        page=1,
        page_size=25,
        section_code="",
        circuit_code="",
    ):
        base = (
            select(PartyMember)
            .join(AffiliateImportBatch)
            .where(AffiliateImportBatch.is_current.is_(True))
        )
        if search:
            base = base.where(
                (PartyMember.normalized_name.contains(search, autoescape=True))
                | PartyMember.dni.contains(search, autoescape=True)
            )
        for field, value in [
            (PartyMember.section, section),
            (PartyMember.circuit, circuit),
            (PartyMember.affiliation_status, state),
            (PartyMember.section_code, section_code),
            (PartyMember.circuit_code, circuit_code),
        ]:
            if value:
                base = base.where(func.upper(field) == value.upper())
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        rows = list(
            self.db.scalars(
                base.order_by(PartyMember.last_name, PartyMember.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        current = self.db.scalar(
            select(AffiliateImportBatch).where(
                AffiliateImportBatch.is_current.is_(True)
            )
        )
        sections = (
            self.db.scalar(
                select(func.count(func.distinct(PartyMember.section))).where(
                    PartyMember.source_batch_id == current.id
                )
            )
            if current
            else 0
        )
        return {
            "items": rows,
            "total": total,
            "page": page,
            "page_size": page_size,
            "current_batch": current,
            "sections": sections,
            "total_members": current.valid_rows if current else 0,
        }

    def catalog(self):
        current = self.db.scalar(
            select(AffiliateImportBatch).where(
                AffiliateImportBatch.is_current.is_(True)
            )
        )
        if not current:
            return {"sections": [], "circuits": []}
        circuit_catalog = self.db.execute(
            select(
                PadronCircuit.id,
                PadronCircuit.name,
                PadronCircuit.code,
                PadronCircuit.section,
                PadronCircuit.section_code,
            )
            .where(PadronCircuit.source_batch_id == current.id)
            .order_by(PadronCircuit.section, PadronCircuit.name, PadronCircuit.code)
        ).all()
        if circuit_catalog:
            sections = {
                (section, section_code)
                for _, _, _, section, section_code in circuit_catalog
                if section
            }
            ordered_sections = sorted(
                sections, key=lambda item: (item[0] or "", item[1] or "")
            )
            return {
                "sections": [
                    {
                        "id": f"{section_code or section}",
                        "name": section,
                        "code": section_code,
                    }
                    for section, section_code in ordered_sections
                ],
                "circuits": [
                    {
                        "id": str(id_),
                        "name": name,
                        "code": code,
                        "section": section,
                        "section_code": section_code,
                    }
                    for id_, name, code, section, section_code in circuit_catalog
                ],
            }
        section_rows = self.db.execute(
            select(PartyMember.section, PartyMember.section_code)
            .where(PartyMember.source_batch_id == current.id)
            .where(PartyMember.section.is_not(None))
            .distinct()
            .order_by(PartyMember.section, PartyMember.section_code)
        ).all()
        circuit_rows = self.db.execute(
            select(
                PartyMember.circuit,
                PartyMember.circuit_code,
                PartyMember.section,
                PartyMember.section_code,
            )
            .where(PartyMember.source_batch_id == current.id)
            .where(PartyMember.circuit.is_not(None))
            .distinct()
            .order_by(PartyMember.section, PartyMember.circuit, PartyMember.circuit_code)
        ).all()
        return {
            "sections": [
                {
                    "id": f"{section_code or section}",
                    "name": section,
                    "code": section_code,
                }
                for section, section_code in section_rows
            ],
            "circuits": [
                {
                    "id": f"{section_code or ''}|{circuit_code or ''}|{circuit}",
                    "name": circuit,
                    "code": circuit_code,
                    "section": section,
                    "section_code": section_code,
                }
                for circuit, circuit_code, section, section_code in circuit_rows
            ],
        }

    def batches(self):
        return list(
            self.db.scalars(
                select(AffiliateImportBatch)
                .order_by(AffiliateImportBatch.id.desc())
                .limit(100)
            ).all()
        )
