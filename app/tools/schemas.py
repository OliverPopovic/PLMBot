from pydantic import BaseModel, ConfigDict, Field


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FindComponentInput(StrictSchema):
    component_code_or_name: str = Field(min_length=1)


class ListComponentsInput(StrictSchema):
    pass


class ListAssembliesInput(StrictSchema):
    pass


class GetBomInput(StrictSchema):
    assembly_code: str


class WhereUsedInput(StrictSchema):
    component_code: str


class CreateComponentInput(StrictSchema):
    component_code: str
    name: str
    component_type: str
    description: str = ""
    lifecycle_state: str = "active"
    attributes_json: dict = {}


class UpdateComponentInput(StrictSchema):
    component_code: str
    patch: dict


class DeleteComponentInput(StrictSchema):
    component_code: str
