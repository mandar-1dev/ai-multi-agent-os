import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.tools.calculator import CalculatorTool
from app.tools.python_exec import PythonExecTool


def test_calculator_basic():
    tool = CalculatorTool()
    result = tool.run(expression="2 + 3 * 4")
    assert result.success is True
    assert result.data["result"] == 14


def test_calculator_rejects_bad_input():
    tool = CalculatorTool()
    result = tool.run(expression="__import__('os').system('ls')")
    assert result.success is False


def test_calculator_missing_field():
    tool = CalculatorTool()
    result = tool.run()
    assert result.success is False
    assert "expression" in result.error


def test_python_exec_basic():
    tool = PythonExecTool()
    result = tool.run(code="print(sum([1,2,3]))")
    assert result.success is True
    assert "6" in result.data["stdout"]


def test_python_exec_blocks_imports():
    tool = PythonExecTool()
    result = tool.run(code="import os\nprint(os.listdir('.'))")
    assert result.success is False


if __name__ == "__main__":
    test_calculator_basic()
    test_calculator_rejects_bad_input()
    test_calculator_missing_field()
    test_python_exec_basic()
    test_python_exec_blocks_imports()
    print("All tool tests passed.")
