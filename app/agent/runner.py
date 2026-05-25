import json
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.agent.prompt import SYSTEM_PROMPT
from app.agent.schemas import ClarificationResult, CommandExtraction, ExecutableCommand, RefusalResult
from app.config import settings
from app.tools.schemas import (
    CreateComponentInput,
    DeleteComponentInput,
    FindComponentInput,
    GetBomInput,
    ListAssembliesInput,
    ListComponentsInput,
    UpdateComponentInput,
    WhereUsedInput,
)

TOOL_INPUT_MODELS = {
    "find_component": FindComponentInput,
    "list_components": ListComponentsInput,
    "list_assemblies": ListAssembliesInput,
    "get_bom": GetBomInput,
    "where_used": WhereUsedInput,
    "create_component": CreateComponentInput,
    "update_component": UpdateComponentInput,
    "delete_component": DeleteComponentInput,
}

MUTATION_OPERATIONS = {"create_component", "update_component", "delete_component"}
EXPLICIT_COMMANDS = {
    "find": "find_component",
    "bom": "get_bom",
    "where-used": "where_used",
    "where_used": "where_used",
    "list": "list",
    "delete": "delete_component",
}


class CommandInterpreter:
    def __init__(self, llm: Any | None = None):
        self.llm = llm

    def interpret(self, user_input: str) -> ExecutableCommand | ClarificationResult | RefusalResult:
        stripped = user_input.strip()
        explicit = self._parse_explicit_command(stripped)
        if explicit is not None:
            return explicit

        try:
            extracted = self._get_llm().invoke(
                [
                    ("system", SYSTEM_PROMPT),
                    ("human", stripped),
                ]
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            return RefusalResult(
                message=f"Could not interpret the request safely: {exc}",
                user_summary="Interpretation failed",
            )

        extracted = CommandExtraction.model_validate(extracted)

        if extracted.decision == "clarification":
            return ClarificationResult(message=extracted.message, user_summary=extracted.user_summary)
        if extracted.decision == "refusal":
            return RefusalResult(message=extracted.message, user_summary=extracted.user_summary)
        return self._build_command(extracted.operation, extracted.args, extracted.user_summary)

    def _parse_explicit_command(self, user_input: str) -> ExecutableCommand | ClarificationResult | RefusalResult | None:
        if not user_input:
            return ClarificationResult(message="Please enter a request.", user_summary="Missing request")

        parts = user_input.split(maxsplit=1)
        verb = parts[0].lower()
        remainder = parts[1].strip() if len(parts) > 1 else ""

        if verb not in EXPLICIT_COMMANDS and verb not in {"create", "update"}:
            return None

        if verb == "find":
            if not remainder:
                return ClarificationResult(message="Tell me what component code or name to search for.", user_summary="Missing search query")
            return self._build_command("find_component", {"component_code_or_name": remainder}, f"Find component matching {remainder}")

        if verb == "list":
            normalized = remainder.lower()
            if normalized in {"components", "all components"}:
                return self._build_command("list_components", {}, "List all components")
            if normalized in {"assemblies", "all assemblies"}:
                return self._build_command("list_assemblies", {}, "List all assemblies")
            return ClarificationResult(
                message="Use `list components` or `list assemblies`, or ask in natural language for a supported listing.",
                user_summary="Unsupported list target",
            )

        if verb == "bom":
            if not remainder:
                return ClarificationResult(message="Provide the assembly code to inspect.", user_summary="Missing assembly code")
            return self._build_command("get_bom", {"assembly_code": remainder}, f"Get BOM for assembly {remainder}")

        if verb in {"where-used", "where_used"}:
            if not remainder:
                return ClarificationResult(message="Provide the component code to reverse-search.", user_summary="Missing component code")
            return self._build_command("where_used", {"component_code": remainder}, f"Find where component {remainder} is used")

        if verb == "delete":
            if not remainder:
                return ClarificationResult(message="Provide the component code to delete.", user_summary="Missing component code")
            return self._build_command("delete_component", {"component_code": remainder}, f"Delete component {remainder}")

        if verb == "create":
            payload = self._load_json_payload(remainder, "Provide JSON after `create` with the component fields.")
            if not isinstance(payload, dict):
                return payload
            return self._build_command("create_component", payload, f"Create component {payload.get('component_code', '<missing code>')}")

        if verb == "update":
            if not remainder:
                return ClarificationResult(message="Provide a component code followed by a JSON patch.", user_summary="Missing update details")
            code, _, raw_patch = remainder.partition(" ")
            if not raw_patch.strip():
                return ClarificationResult(message="Provide a JSON patch after the component code.", user_summary="Missing update patch")
            payload = self._load_json_payload(raw_patch.strip(), "Provide a valid JSON object for the update patch.")
            if not isinstance(payload, dict):
                return payload
            return self._build_command("update_component", {"component_code": code, "patch": payload}, f"Update component {code}")

        return None

    def _get_llm(self) -> Any:
        if self.llm is None:
            self.llm = ChatOpenAI(model=settings.model_name, temperature=0).with_structured_output(CommandExtraction)
        return self.llm

    def _load_json_payload(self, raw_json: str, guidance: str) -> dict | ClarificationResult:
        if not raw_json:
            return ClarificationResult(message=guidance, user_summary="Missing JSON payload")
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            return ClarificationResult(message=guidance, user_summary="Invalid JSON payload")
        if not isinstance(parsed, dict):
            return ClarificationResult(message="Provide a JSON object, not a list or scalar value.", user_summary="Invalid JSON payload")
        return parsed

    def _build_command(self, operation: str, args: dict, user_summary: str) -> ExecutableCommand | ClarificationResult:
        input_model = TOOL_INPUT_MODELS[operation]
        try:
            validated_args = input_model.model_validate(args).model_dump()
        except ValidationError as exc:
            return ClarificationResult(message=self._format_validation_error(exc), user_summary="Missing or invalid command details")
        return ExecutableCommand(
            operation=operation,
            args=validated_args,
            requires_confirmation=operation in MUTATION_OPERATIONS,
            user_summary=user_summary,
        )

    @staticmethod
    def _format_validation_error(exc: ValidationError) -> str:
        messages = []
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"])
            messages.append(f"{location}: {error['msg']}")
        return "Please clarify the request. " + "; ".join(messages)
