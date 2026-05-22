class TraceCallbackHandler:
    def on_tool_start(self, tool_name: str, args: dict) -> None:
        print(f"[tool_start] {tool_name} args={args}")

    def on_tool_end(self, result: dict) -> None:
        print(f"[tool_end] status={result.get('status')} summary={result.get('summary')}")
