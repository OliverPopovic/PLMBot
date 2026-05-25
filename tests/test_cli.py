from app.agent.schemas import ClarificationResult, ExecutableCommand
from app.cli import run_cli


class DummyInterpreter:
    def __init__(self, outcomes):
        self._outcomes = iter(outcomes)

    def interpret(self, _raw):
        return next(self._outcomes)


class DummySessionFactory:
    def __call__(self):
        return self

    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc, tb):
        return False


class SilentCallbackHandler:
    def on_interpretation(self, _raw_input, _outcome):
        return None

    def on_confirmation(self, _operation, _confirmed):
        return None

    def on_tool_start(self, _tool_name, _args):
        return None

    def on_tool_end(self, _result):
        return None


def test_read_command_executes_without_confirmation(monkeypatch):
    calls = []
    outputs = []
    interpreter = DummyInterpreter(
        [
            ExecutableCommand(
                operation="find_component",
                args={"component_code_or_name": "R-14"},
                requires_confirmation=False,
                user_summary="Find R-14",
            )
        ]
    )

    monkeypatch.setitem(
        __import__("app.cli", fromlist=["TOOL_MAP"]).TOOL_MAP,
        "find_component",
        lambda _service, args: calls.append(args) or {"status": "success", "summary": "Found component", "records": []},
    )

    responses = iter(["find R-14", "quit"])
    run_cli(
        input_func=lambda _prompt: next(responses),
        output_func=outputs.append,
        interpreter=interpreter,
        session_factory=DummySessionFactory(),
        callback_handler=SilentCallbackHandler(),
    )

    assert calls == [{"component_code_or_name": "R-14"}]
    assert any("Normalized instruction:" in line for line in outputs)
    assert any("Read result: Found component" in line for line in outputs)


def test_list_assemblies_command_executes_as_read(monkeypatch):
    calls = []
    outputs = []
    interpreter = DummyInterpreter(
        [
            ExecutableCommand(
                operation="list_assemblies",
                args={},
                requires_confirmation=False,
                user_summary="List all assemblies",
            )
        ]
    )

    monkeypatch.setitem(
        __import__("app.cli", fromlist=["TOOL_MAP"]).TOOL_MAP,
        "list_assemblies",
        lambda _service, args: calls.append(args) or {"status": "success", "summary": "Listed 1 assemblies", "records": [{"assembly_code": "A-1000"}]},
    )

    responses = iter(["list all assemblies", "quit"])
    run_cli(
        input_func=lambda _prompt: next(responses),
        output_func=outputs.append,
        interpreter=interpreter,
        session_factory=DummySessionFactory(),
        callback_handler=SilentCallbackHandler(),
    )

    assert calls == [{}]
    assert any("Read result: Listed 1 assemblies" in line for line in outputs)


def test_write_command_requires_confirmation_and_can_cancel(monkeypatch):
    calls = []
    outputs = []
    interpreter = DummyInterpreter(
        [
            ExecutableCommand(
                operation="delete_component",
                args={"component_code": "R-14"},
                requires_confirmation=True,
                user_summary="Delete R-14",
            )
        ]
    )

    monkeypatch.setitem(
        __import__("app.cli", fromlist=["TOOL_MAP"]).TOOL_MAP,
        "delete_component",
        lambda _service, args: calls.append(args) or {"status": "success", "summary": "Deleted component", "records": []},
    )

    responses = iter(["delete R-14", "n", "quit"])
    run_cli(
        input_func=lambda _prompt: next(responses),
        output_func=outputs.append,
        interpreter=interpreter,
        session_factory=DummySessionFactory(),
        callback_handler=SilentCallbackHandler(),
    )

    assert calls == []
    assert any("Cancelled. No database changes were made." in line for line in outputs)


def test_clarification_never_reaches_tool_layer(monkeypatch):
    outputs = []
    interpreter = DummyInterpreter(
        [
            ClarificationResult(
                message="Which component code should I use?",
                user_summary="Need component code",
            )
        ]
    )

    def fail_if_called(_service, _args):
        raise AssertionError("Tool layer should not be called")

    monkeypatch.setitem(__import__("app.cli", fromlist=["TOOL_MAP"]).TOOL_MAP, "find_component", fail_if_called)

    responses = iter(["find it", "quit"])
    run_cli(
        input_func=lambda _prompt: next(responses),
        output_func=outputs.append,
        interpreter=interpreter,
        session_factory=DummySessionFactory(),
        callback_handler=SilentCallbackHandler(),
    )

    assert any("Need more detail: Which component code should I use?" in line for line in outputs)
