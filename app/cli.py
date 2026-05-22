import json

from app.db.session import SessionLocal
from app.services.bom_service import BomService
from app.services.component_service import ComponentService
from app.tools.bom_tools import get_bom_tool, where_used_tool
from app.tools.component_tools import create_component_tool, delete_component_tool, find_component_tool, update_component_tool


TOOL_MAP = {
    "find_component": find_component_tool,
    "create_component": create_component_tool,
    "update_component": update_component_tool,
    "delete_component": delete_component_tool,
    "get_bom": get_bom_tool,
    "where_used": where_used_tool,
}


def main() -> None:
    print("PLMBot MVP CLI. Enter JSON: {'tool': 'find_component', 'args': {...}}. Ctrl+C to exit.")
    with SessionLocal() as session:
        component_service = ComponentService(session)
        bom_service = BomService(session)
        while True:
            raw = input("> ").strip()
            if not raw:
                continue
            req = json.loads(raw)
            tool = req["tool"]
            args = req.get("args", {})
            print(f"tool={tool}")
            print(f"validated_args={args}")
            if tool in {"get_bom", "where_used"}:
                result = TOOL_MAP[tool](bom_service, args)
            else:
                result = TOOL_MAP[tool](component_service, args)
            print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
