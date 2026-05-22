from pydantic import BaseModel, Field


class FindComponentInput(BaseModel):
    component_code_or_name: str = Field(min_length=1)


class GetBomInput(BaseModel):
    assembly_code: str


class WhereUsedInput(BaseModel):
    component_code: str


class CreateComponentInput(BaseModel):
    component_code: str
    name: str
    component_type: str
    description: str = ""
    lifecycle_state: str = "active"
    attributes_json: dict = {}


class UpdateComponentInput(BaseModel):
    component_code: str
    patch: dict


class DeleteComponentInput(BaseModel):
    component_code: str
