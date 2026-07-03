from app.tools.calculator import CalculatorTool
from app.tools.python_exec import PythonExecTool
from app.tools.file_reader import FileReaderTool
from app.tools.web_search import WebSearchTool

TOOL_REGISTRY = {
    tool.name: tool
    for tool in [CalculatorTool(), PythonExecTool(), FileReaderTool(), WebSearchTool()]
}


def get_tool(name: str):
    tool = TOOL_REGISTRY.get(name)
    if tool is None:
        raise KeyError(f"Unknown tool '{name}'. Available: {list(TOOL_REGISTRY.keys())}")
    return tool


def list_tools() -> list[dict]:
    return [{"name": t.name, "description": t.description} for t in TOOL_REGISTRY.values()]
