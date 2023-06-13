import ast
from _ast import While
from typing import List, Any


class PredicateFinderVisitor(ast.NodeVisitor):
    def __init__(self, lines: List[int], content: str):
        self._lines = lines
        self._is_predicate_in_lines = False
        self.content_lines = content.splitlines()

    def visit_If(self, node: ast.If) -> Any:
        if self._is_node_in_lines(node.test):
            self._is_predicate_in_lines = True
        self.generic_visit(node)

    def visit_While(self, node: While) -> Any:
        if self._is_node_in_lines(node.test):
            self._is_predicate_in_lines = True
        self.generic_visit(node)

    def is_predicate_in_lines(self) -> bool:
        return self._is_predicate_in_lines

    def _is_node_in_lines(self, test_node):
        line_start = test_node.lineno
        line_end = test_node.end_lineno

        start_content = self.content_lines[line_start - 1]
        end_content = self.content_lines[line_end - 1]

        for line in self._lines:
            if line_start <= line <= line_end:
                return True

        return False


class PredicateFinder:
    def __init__(self, code_content: str, code_lines: List[int]):
        self._code_content = code_content
        self._code_lines = code_lines

    def is_predicate_in_lines(self) -> bool:
        ast_tree = ast.parse(self._code_content)
        predicate_visitor = PredicateFinderVisitor(self._code_lines, self._code_content)
        predicate_visitor.visit(ast_tree)
        is_predicate_in_lines = predicate_visitor.is_predicate_in_lines()

        return is_predicate_in_lines
