import ast
from _ast import FunctionDef, AsyncFunctionDef
from pathlib import Path
from typing import Any


# Here we count all functions.
# For example, if a function has a nested function,
# we count them as two.

class FunctionCounterVisitor(ast.NodeVisitor):
    def __init__(self):
        self._function_count = 0

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        self._function_count += 1
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        self._function_count += 1
        self.generic_visit(node)

    def get_function_count(self) -> int:
        return self._function_count


def count_function_num(module_path: Path) -> int:
    with module_path.open("r") as file:
        tree = ast.parse(file.read())

    function_counter_visitor = FunctionCounterVisitor()
    function_counter_visitor.visit(tree)
    function_count = function_counter_visitor.get_function_count()

    return function_count
