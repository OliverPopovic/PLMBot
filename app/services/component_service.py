from sqlalchemy import or_, select

from app.db.models import BomItem, Component

MUTABLE_FIELDS = {"name", "description", "component_type", "lifecycle_state", "attributes_json"}


class ComponentService:
    def __init__(self, session):
        self.session = session

    def find_component(self, query: str) -> dict:
        exact = self.session.scalar(select(Component).where(Component.component_code == query))
        if exact:
            return {"status": "success", "operation": "find_component", "summary": f"Exact match for {query}", "records": [self._row(exact)], "evidence": ["exact_code_match"], "warnings": []}
        like = self.session.scalars(select(Component).where(or_(Component.component_code.ilike(f"%{query}%"), Component.name.ilike(f"%{query}%"), Component.description.ilike(f"%{query}%"))).limit(10)).all()
        status = "success" if like else "not_found"
        return {"status": status, "operation": "find_component", "summary": f"Found {len(like)} fuzzy candidates", "records": [self._row(c) for c in like], "evidence": ["ilike_component_search"], "warnings": []}

    def create_component(self, data: dict) -> dict:
        component = Component(**data)
        self.session.add(component)
        self.session.commit()
        self.session.refresh(component)
        return {"status": "success", "operation": "create_component", "summary": f"Created {component.component_code}", "records": [self._row(component)], "evidence": ["insert_component"], "warnings": []}

    def update_component(self, component_code: str, patch: dict) -> dict:
        component = self.session.scalar(select(Component).where(Component.component_code == component_code))
        if not component:
            return {"status": "not_found", "operation": "update_component", "summary": f"Component {component_code} not found", "records": [], "evidence": [], "warnings": []}
        safe_patch = {k: v for k, v in patch.items() if k in MUTABLE_FIELDS}
        for key, value in safe_patch.items():
            setattr(component, key, value)
        self.session.commit()
        return {"status": "success", "operation": "update_component", "summary": f"Updated {component_code}", "records": [self._row(component)], "evidence": ["update_component"], "warnings": []}

    def delete_component(self, component_code: str) -> dict:
        component = self.session.scalar(select(Component).where(Component.component_code == component_code))
        if not component:
            return {"status": "not_found", "operation": "delete_component", "summary": f"Component {component_code} not found", "records": [], "evidence": [], "warnings": []}
        in_bom = self.session.scalar(select(BomItem).where(BomItem.component_id == component.id))
        if in_bom:
            return {"status": "error", "operation": "delete_component", "summary": f"Component {component_code} is referenced by BOM items", "records": [], "evidence": ["referential_safety_check"], "warnings": ["delete_blocked"]}
        self.session.delete(component)
        self.session.commit()
        return {"status": "success", "operation": "delete_component", "summary": f"Deleted {component_code}", "records": [], "evidence": ["delete_component"], "warnings": []}

    @staticmethod
    def _row(component: Component) -> dict:
        return {
            "component_code": component.component_code,
            "name": component.name,
            "description": component.description,
            "component_type": component.component_type,
            "lifecycle_state": component.lifecycle_state,
            "attributes_json": component.attributes_json,
        }
