from app.services.bom_service import BomService
from app.tools.schemas import GetBomInput, ListAssembliesInput, WhereUsedInput


def list_assemblies_tool(service: BomService, payload: dict) -> dict:
    ListAssembliesInput(**payload)
    return service.list_assemblies()


def get_bom_tool(service: BomService, payload: dict) -> dict:
    data = GetBomInput(**payload)
    return service.get_bom(data.assembly_code)


def where_used_tool(service: BomService, payload: dict) -> dict:
    data = WhereUsedInput(**payload)
    return service.where_used(data.component_code)
