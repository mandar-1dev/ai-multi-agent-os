import ast
import operator
from app.tools.base_tool import BaseTool

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos, ast.FloorDiv: operator.floordiv,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluate a numeric arithmetic expression (+ - * / ** % //). No variables or functions."

    def validate(self, **kwargs):
        expr = kwargs.get("expression")
        if not expr or not isinstance(expr, str):
            return False, "Missing required string field 'expression'"
        return True, None

    def _run(self, **kwargs):
        expr = kwargs["expression"]
        tree = ast.parse(expr, mode="eval")
        result = _safe_eval(tree.body)
        return {"expression": expr, "result": result}
