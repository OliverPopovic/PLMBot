import json
from collections.abc import Callable
from contextlib import suppress

from app.agent.callbacks import TraceCallbackHandler
from app.agent.runner import CommandInterpreter
from app.agent.schemas import ClarificationResult, ExecutableCommand, RefusalResult
from app.db.session import SessionLocal
from app.services.bom_service import BomService
from app.services.component_service import ComponentService
from app.tools.bom_tools import get_bom_tool, list_assemblies_tool, where_used_tool
from app.tools.component_tools import create_component_tool, delete_component_tool, find_component_tool, list_components_tool, update_component_tool


TOOL_MAP = {
    "find_component": find_component_tool,
    "list_components": list_components_tool,
    "list_assemblies": list_assemblies_tool,
    "create_component": create_component_tool,
    "update_component": update_component_tool,
    "delete_component": delete_component_tool,
    "get_bom": get_bom_tool,
    "where_used": where_used_tool,
}

READ_OPERATIONS = {"find_component", "list_components", "list_assemblies", "get_bom", "where_used"}


def print_preview(output_func: Callable[[str], None], command: ExecutableCommand) -> None:
    output_func(f"Interpreted request: {command.user_summary}")
    output_func("Normalized instruction:")
    output_func(json.dumps(command.model_dump(exclude={"kind"}), indent=2, sort_keys=True))


def execute_command(
    command: ExecutableCommand,
    component_service: ComponentService,
    bom_service: BomService,
    callback_handler: TraceCallbackHandler | None = None,
) -> dict:
    callback_handler = callback_handler or TraceCallbackHandler()
    callback_handler.on_tool_start(command.operation, command.args)
    if command.operation in {"list_assemblies", "get_bom", "where_used"}:
        result = TOOL_MAP[command.operation](bom_service, command.args)
    else:
        result = TOOL_MAP[command.operation](component_service, command.args)
    callback_handler.on_tool_end(result)
    return result


def confirm_command(
    command: ExecutableCommand,
    input_func: Callable[[str], str],
    output_func: Callable[[str], None],
    callback_handler: TraceCallbackHandler | None = None,
) -> bool:
    callback_handler = callback_handler or TraceCallbackHandler()
    if not command.requires_confirmation:
        return True
    response = input_func("Confirm write? [y/N]: ").strip().lower()
    confirmed = response in {"y", "yes"}
    callback_handler.on_confirmation(command.operation, confirmed)
    if not confirmed:
        output_func("Cancelled. No database changes were made.")
    return confirmed


def run_cli(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
    interpreter: CommandInterpreter | None = None,
    session_factory: Callable[[], object] = SessionLocal,
    callback_handler: TraceCallbackHandler | None = None,
) -> None:
    callback_handler = callback_handler or TraceCallbackHandler()
    interpreter = interpreter or CommandInterpreter()

    output_func("PLMBot CLI. Enter a plain-English request or an explicit command like `find R-14`. Type `exit` or `quit` to leave.")
    with session_factory() as session:
        component_service = ComponentService(session)
        bom_service = BomService(session)
        while True:
            try:
                raw = input_func("> ").strip()
            except EOFError:
                output_func("")
                break
            if not raw:
                continue
            if raw.lower() in {"exit", "quit"}:
                output_func("Goodbye.")
                break

            outcome = interpreter.interpret(raw)
            callback_handler.on_interpretation(raw, outcome.model_dump())

            if isinstance(outcome, ClarificationResult):
                output_func(f"Need more detail: {outcome.message}")
                continue

            if isinstance(outcome, RefusalResult):
                output_func(f"Cannot do that safely: {outcome.message}")
                continue

            print_preview(output_func, outcome)

            if not confirm_command(outcome, input_func, output_func, callback_handler):
                continue

            result = execute_command(outcome, component_service, bom_service, callback_handler)
            status_label = "Read result" if outcome.operation in READ_OPERATIONS else "Write result"
            output_func(f"{status_label}: {result.get('summary', 'Completed')}")
            output_func(json.dumps(result, indent=2, default=str))


def main() -> None:
    with suppress(KeyboardInterrupt):
        run_cli()


if __name__ == "__main__":
    main()
