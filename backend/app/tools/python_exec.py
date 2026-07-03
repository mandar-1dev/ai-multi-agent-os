import io
import contextlib
from app.tools.base_tool import BaseTool

_SAFE_BUILTINS = {
    "range": range, "len": len, "sum": sum, "min": min, "max": max,
    "sorted": sorted, "enumerate": enumerate, "zip": zip, "abs": abs,
    "round": round, "print": print, "str": str, "int": int, "float": float,
    "list": list, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
}


class PythonExecTool(BaseTool):
    """
    Runs short, sandboxed Python snippets with a restricted builtins set and
    no filesystem/network/import access. Intended for small data-munging /
    calculation snippets the Coding Agent produces, NOT arbitrary code.
    """
    name = "python_execution"
    description = "Execute a short Python snippet in a restricted sandbox (no imports, no I/O). Returns stdout."

    def validate(self, **kwargs):
        code = kwargs.get("code")
        if not code or not isinstance(code, str):
            return False, "Missing required string field 'code'"
        if "import" in code or "__" in code or "open(" in code:
            return False, "Code contains disallowed tokens (import / dunder / file I/O)"
        if len(code) > 4000:
            return False, "Code too long (max 4000 chars)"
        return True, None

    def _run(self, **kwargs):
        code = kwargs["code"]
        buf = io.StringIO()
        local_scope = {}
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<sandbox>", "exec"), {"__builtins__": _SAFE_BUILTINS}, local_scope)
        return {"stdout": buf.getvalue(), "locals": {k: repr(v) for k, v in local_scope.items() if not k.startswith("_")}}
