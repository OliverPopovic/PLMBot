class TraceCallbackHandler:
    def on_interpretation(self, raw_input: str, outcome: dict) -> None:
        print(f"[interpretation] input={raw_input!r} outcome={outcome}")

    def on_confirmation(self, operation: str, confirmed: bool) -> None:
        print(f"[confirmation] operation={operation} confirmed={confirmed}")

    def on_tool_start(self, tool_name: str, args: dict) -> None:
        print(f"[tool_start] {tool_name} args={args}")

    def on_tool_end(self, result: dict) -> None:
        print(f"[tool_end] status={result.get('status')} summary={result.get('summary')}")
