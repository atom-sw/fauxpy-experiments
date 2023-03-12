import ast
from _ast import FunctionDef
from pathlib import Path
from typing import List, Tuple, Any, Optional


class FunctionInformation:
    def __init__(self,
                 module_path: str,
                 function_name: str,
                 line_start: int,
                 line_end: int):
        self._module_path = module_path
        self._function_name = function_name
        self._line_start = line_start
        self._line_end = line_end

    def get_function_range(self):
        return self._line_start, self._line_end

    def _pretty_representation(self):
        return f"{self._function_name} ({self._line_start}, {self._line_end})"

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()

    def get_module_path(self):
        return self._module_path

    def get_function_name(self):
        return self._function_name

    def get_line_start(self):
        return self._line_start

    def get_line_end(self):
        return self._line_end

    def has_statement(self,
                      module_path: str,
                      line_number: int) -> bool:
        return (module_path == self._module_path and
                self._line_start <= line_number <= self._line_end)

    def get_range_length(self) -> int:
        return self._line_end - self._line_start + 1

    def __eq__(self, other):
        return (self._module_path == other.get_module_path() and
                self._function_name == other.get_function_name() and
                self._line_start == other.get_line_start() and
                self._line_end == other.get_line_end())

    def __ne__(self, other):
        return not self.__eq__(other)


class ModuleInformation:
    def __init__(self,
                 module_path: str,
                 function_info_list: List[FunctionInformation]):
        self._module_path = module_path
        self._function_info_list = function_info_list

    def _pretty_representation(self):
        return f"info for path: {self._module_path}"

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()

    def get_module_path(self):
        return self._module_path

    def get_function_information(self, line_number: int) -> Optional[FunctionInformation]:
        function_info_list_for_line = list(filter(lambda x:
                                                  x.has_statement(self._module_path, line_number),
                                                  self._function_info_list))
        min_function_info = self._get_min_function_info(function_info_list_for_line)
        return min_function_info

    @staticmethod
    def _get_min_function_info(function_info_list: List[FunctionInformation]) -> Optional[FunctionInformation]:
        if len(function_info_list) == 0:
            return None

        min_function_info = function_info_list[0]
        for item in function_info_list:
            if item.get_range_length() < min_function_info.get_range_length():
                min_function_info = item

        return min_function_info


class StatementFunctionMap:
    def __init__(self, module_info_list: List[ModuleInformation]):
        self._module_info_list = module_info_list

    def get_function_info(self, module_path: str, line_number: int) -> Optional[FunctionInformation]:
        module_info_list_for_path = list(filter(lambda x: x.get_module_path() == module_path, self._module_info_list))
        assert len(module_info_list_for_path) == 1
        module_info_for_path = module_info_list_for_path[0]
        function_info_for_line = module_info_for_path.get_function_information(line_number)

        return function_info_for_line


def get_function_class_ast_node_start_end_lines(node):
    start_line_num = node.lineno
    end_line_num = node.end_lineno
    for item in node.decorator_list:
        start_line_num = min(start_line_num, item.lineno)

    return start_line_num, end_line_num


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self._function_range_list = []

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        function_name = node.name
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        self._function_range_list.append((function_name, start_line_num, end_line_num))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: FunctionDef) -> Any:
        function_name = node.name
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        self._function_range_list.append((function_name, start_line_num, end_line_num))
        self.generic_visit(node)

    def get_function_range_list(self):
        return self._function_range_list


class FunctionManager:
    def __init__(self, workspace_path: Path, project_name: str, bug_number: int):
        self._workspace_path = workspace_path
        self._project_name = project_name
        self._bug_number = bug_number

    def get_statement_to_function_map(self,
                                      statement_list: List[Tuple[str, int]]) -> StatementFunctionMap:
        module_info_list = []
        module_path_list = list(set([x[0] for x in statement_list]))

        for item in module_path_list:
            current_function_info_list = self._get_module_function_info_list(item)
            current_module_info = ModuleInformation(item, current_function_info_list)
            module_info_list.append(current_module_info)

        statement_function_map = StatementFunctionMap(module_info_list)

        return statement_function_map

    def _get_module_function_info_list(self, module_path: str):
        module_file_path = self._get_buggy_project_path() / module_path
        with module_file_path.open("r") as file:
            tree = ast.parse(file.read())

        function_visitor_onj = FunctionVisitor()
        function_visitor_onj.visit(tree)

        function_range_list = function_visitor_onj.get_function_range_list()

        function_info_list = []
        for func_range in function_range_list:
            current_function_info = FunctionInformation(module_path, func_range[0], func_range[1], func_range[2])
            function_info_list.append(current_function_info)

        return function_info_list

    def _get_buggy_project_path(self) -> Path:
        version_prefix = "bug"
        buggy_dir_name = "buggy"
        return (Path(self._workspace_path) /
                f"{self._project_name}" /
                f"{version_prefix}{self._bug_number}" /
                buggy_dir_name /
                self._project_name)
