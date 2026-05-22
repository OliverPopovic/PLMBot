from app.services.bom_service import BomService
from app.services.component_service import ComponentService


class RetrievalService:
    def __init__(self, session):
        self.component_service = ComponentService(session)
        self.bom_service = BomService(session)

    def search_components(self, query: str, limit: int = 10) -> dict:
        result = self.component_service.find_component(query)
        result["records"] = result["records"][:limit]
        return result

    def search_assemblies(self, query: str, limit: int = 10) -> dict:
        # MVP placeholder keeps retrieval scope intentionally narrow.
        return {"status": "success", "operation": "search_assemblies", "summary": "Use get_bom with an assembly code for deterministic lookup", "records": [], "evidence": [], "warnings": []}

    def build_grounding_context(self, user_query: str) -> dict:
        return {"status": "success", "operation": "build_grounding_context", "summary": f"Grounding context built for query: {user_query}", "records": [], "evidence": ["service_backed_context"], "warnings": []}
