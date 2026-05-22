from sqlalchemy import select

from app.db.models import Assembly, BomItem, Component


class BomService:
    def __init__(self, session):
        self.session = session

    def get_bom(self, assembly_code: str) -> dict:
        assembly = self.session.scalar(select(Assembly).where(Assembly.assembly_code == assembly_code))
        if not assembly:
            return {"status": "not_found", "operation": "get_bom", "summary": f"Assembly {assembly_code} not found", "records": [], "evidence": [], "warnings": []}
        rows = self.session.execute(select(BomItem, Component).join(Component, BomItem.component_id == Component.id).where(BomItem.assembly_id == assembly.id)).all()
        records = [{"assembly_code": assembly_code, "component_code": c.component_code, "component_name": c.name, "quantity": bi.quantity, "reference_designator": bi.reference_designator} for bi, c in rows]
        return {"status": "success", "operation": "get_bom", "summary": f"Found {len(records)} BOM lines", "records": records, "evidence": ["assembly_component_join"], "warnings": []}

    def where_used(self, component_code: str) -> dict:
        component = self.session.scalar(select(Component).where(Component.component_code == component_code))
        if not component:
            return {"status": "not_found", "operation": "where_used", "summary": f"Component {component_code} not found", "records": [], "evidence": [], "warnings": []}
        rows = self.session.execute(select(Assembly).join(BomItem, BomItem.assembly_id == Assembly.id).where(BomItem.component_id == component.id)).scalars().all()
        return {"status": "success", "operation": "where_used", "summary": f"Used in {len(rows)} assemblies", "records": [{"assembly_code": a.assembly_code, "assembly_name": a.name} for a in rows], "evidence": ["reverse_bom_lookup"], "warnings": []}
