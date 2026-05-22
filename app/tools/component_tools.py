from app.services.component_service import ComponentService
from app.tools.schemas import CreateComponentInput, DeleteComponentInput, FindComponentInput, UpdateComponentInput


def find_component_tool(service: ComponentService, payload: dict) -> dict:
    data = FindComponentInput(**payload)
    return service.find_component(data.component_code_or_name)


def create_component_tool(service: ComponentService, payload: dict) -> dict:
    data = CreateComponentInput(**payload)
    return service.create_component(data.model_dump())


def update_component_tool(service: ComponentService, payload: dict) -> dict:
    data = UpdateComponentInput(**payload)
    return service.update_component(data.component_code, data.patch)


def delete_component_tool(service: ComponentService, payload: dict) -> dict:
    data = DeleteComponentInput(**payload)
    return service.delete_component(data.component_code)
