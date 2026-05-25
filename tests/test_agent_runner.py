from app.agent.runner import CommandInterpreter
from app.agent.schemas import ClarificationResult, ExecutableCommand, RefusalResult


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def invoke(self, _messages):
        return self.response


def test_explicit_find_command_is_validated_without_llm():
    interpreter = CommandInterpreter(llm=FakeLLM(None))

    result = interpreter.interpret("find R-14")

    assert isinstance(result, ExecutableCommand)
    assert result.operation == "find_component"
    assert result.args == {"component_code_or_name": "R-14"}
    assert result.requires_confirmation is False


def test_explicit_create_command_requires_confirmation():
    interpreter = CommandInterpreter(llm=FakeLLM(None))

    result = interpreter.interpret('create {"component_code":"IC-555","name":"Timer","component_type":"ic"}')

    assert isinstance(result, ExecutableCommand)
    assert result.operation == "create_component"
    assert result.requires_confirmation is True
    assert result.args["component_code"] == "IC-555"


def test_llm_read_command_is_validated():
    interpreter = CommandInterpreter(
        llm=FakeLLM(
            {
                "decision": "command",
                "operation": "get_bom",
                "args": {"assembly_code": "A-1000"},
                "user_summary": "Get BOM for A-1000",
                "message": "",
            }
        )
    )

    result = interpreter.interpret("show me the BOM for A-1000")

    assert isinstance(result, ExecutableCommand)
    assert result.operation == "get_bom"
    assert result.args == {"assembly_code": "A-1000"}


def test_explicit_list_components_command_is_validated_without_llm():
    interpreter = CommandInterpreter(llm=FakeLLM(None))

    result = interpreter.interpret("list components")

    assert isinstance(result, ExecutableCommand)
    assert result.operation == "list_components"
    assert result.args == {}
    assert result.requires_confirmation is False


def test_llm_list_assemblies_command_is_validated():
    interpreter = CommandInterpreter(
        llm=FakeLLM(
            {
                "decision": "command",
                "operation": "list_assemblies",
                "args": {},
                "user_summary": "List all assemblies",
                "message": "",
            }
        )
    )

    result = interpreter.interpret("list all assemblies")

    assert isinstance(result, ExecutableCommand)
    assert result.operation == "list_assemblies"
    assert result.args == {}


def test_llm_mutation_with_extra_fields_returns_clarification():
    interpreter = CommandInterpreter(
        llm=FakeLLM(
            {
                "decision": "command",
                "operation": "delete_component",
                "args": {"component_code": "R-14", "force": True},
                "user_summary": "Delete component R-14",
                "message": "",
            }
        )
    )

    result = interpreter.interpret("force delete R-14")

    assert isinstance(result, ClarificationResult)
    assert "extra inputs are not permitted" in result.message.lower()


def test_llm_can_request_clarification():
    interpreter = CommandInterpreter(
        llm=FakeLLM(
            {
                "decision": "clarification",
                "operation": None,
                "args": {},
                "user_summary": "Need assembly code",
                "message": "Which assembly code should I use?",
            }
        )
    )

    result = interpreter.interpret("show me the bom")

    assert isinstance(result, ClarificationResult)
    assert result.message == "Which assembly code should I use?"


def test_llm_can_refuse_unsupported_requests():
    interpreter = CommandInterpreter(
        llm=FakeLLM(
            {
                "decision": "refusal",
                "operation": None,
                "args": {},
                "user_summary": "Unsupported request",
                "message": "I can only help with components and BOM lookups.",
            }
        )
    )

    result = interpreter.interpret("drop the entire database")

    assert isinstance(result, RefusalResult)
    assert "components and BOM" in result.message
