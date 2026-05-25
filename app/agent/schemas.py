from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


OperationName = Literal[
    "find_component",
    "list_components",
    "list_assemblies",
    "get_bom",
    "where_used",
    "create_component",
    "update_component",
    "delete_component",
]


class CommandExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["command", "clarification", "refusal"]
    operation: OperationName | None = None
    args: dict = Field(default_factory=dict)
    user_summary: str = Field(min_length=1)
    message: str = ""

    @model_validator(mode="after")
    def validate_shape(self) -> "CommandExtraction":
        if self.decision == "command" and self.operation is None:
            raise ValueError("operation is required for command decisions")
        if self.decision != "command" and self.operation is not None:
            raise ValueError("operation must be omitted for non-command decisions")
        if self.decision == "command" and self.message:
            raise ValueError("message must be empty for command decisions")
        if self.decision != "command" and not self.message:
            raise ValueError("message is required for non-command decisions")
        return self


class ExecutableCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["command"] = "command"
    operation: OperationName
    args: dict
    requires_confirmation: bool
    user_summary: str


class ClarificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["clarification"] = "clarification"
    message: str
    user_summary: str


class RefusalResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["refusal"] = "refusal"
    message: str
    user_summary: str
