import ast
from _ast import FunctionDef, AsyncFunctionDef, ClassDef
from enum import Enum
from typing import Tuple, List, Any, Dict, Optional


class ScopeType(Enum):
    Function = 0
    Class = 1


class ScopeItem:
    def __init__(self,
                 node_range: Tuple[int, int],
                 node_ast: ast.AST,
                 node_type: ScopeType):
        self.node_range = node_range
        self.node_ast = node_ast
        self.node_type = node_type

    def get_range(self):
        return self.node_range

    def get_ast(self):
        return self.node_ast

    def get_type(self):
        return self.node_type


class AddModeManager:

    def __init__(self,
                 buggy_content: str,
                 fixed_content: str,
                 start_add_line_num: int,
                 end_add_line_num: int,
                 fixed_to_buggy_map: Dict[int, int]):
        self.__buggy_content_lines = buggy_content.splitlines()
        self.__fixed_start_add_line_num = start_add_line_num
        self.__fixed_end_add_line_num = end_add_line_num
        self.__fixed_to_buggy_map = fixed_to_buggy_map
        self.__buggy_content_ast = ast.parse(buggy_content)
        self.__fixed_content_ast = ast.parse(fixed_content)
        self.__buggy_content_line_num = len(buggy_content.splitlines())
        self.__fixed_content_line_num = len(fixed_content.splitlines())

    def get_add_mode_ground_truth(self) -> Tuple[int, int]:
        before_start_add_line = -1
        after_end_add_line = -1

        # Finding the scope of the starting and ending added lines in fixed version.
        start_add_line_fixed_scope = self.get_sorted_scope_line_numbers(self.__fixed_content_ast,
                                                                        self.__fixed_content_line_num,
                                                                        self.__fixed_start_add_line_num)
        end_add_line_fixed_scope = self.get_sorted_scope_line_numbers(self.__fixed_content_ast,
                                                                      self.__fixed_content_line_num,
                                                                      self.__fixed_end_add_line_num)

        # Getting the scope of start add line in the fixed version.
        before_start_add_line_fixed_scope = list(
            filter(lambda x: x < self.__fixed_start_add_line_num, start_add_line_fixed_scope))

        # Getting the scope of end add line in the fixed version.
        after_end_add_line_fixed_scope = list(
            filter(lambda x: x > self.__fixed_end_add_line_num, end_add_line_fixed_scope))

        if len(before_start_add_line_fixed_scope) != 0:
            # Finding a line before the starting added line
            # in the fixed version, within its scope and
            # mapping it to the buggy version.
            tmp = before_start_add_line_fixed_scope.copy()
            tmp.reverse()
            buggy_one_line_before_start_add_line_num = -1
            for item in tmp:
                if item in self.__fixed_to_buggy_map.keys():
                    buggy_one_line_before_start_add_line_num = self.__fixed_to_buggy_map[item]
                    break
            assert buggy_one_line_before_start_add_line_num != -1

            # Finding the scope of the before line in the buggy version.
            one_line_before_start_add_line_buggy_scope = self.get_sorted_scope_line_numbers(self.__buggy_content_ast,
                                                                                            self.__buggy_content_line_num,
                                                                                            buggy_one_line_before_start_add_line_num)

            # Getting the scope before start add line in the buggy version.
            before_start_add_line_buggy_scope = list(
                filter(lambda x: x <= buggy_one_line_before_start_add_line_num,
                       one_line_before_start_add_line_buggy_scope))

            # Find a localizable line before start add line in the buggy version.
            tmp = before_start_add_line_buggy_scope.copy()
            tmp.reverse()
            before_start_add_line_selected = self.select_localizable_line_number(tmp)
            before_start_add_line = before_start_add_line_selected

        if len(after_end_add_line_fixed_scope) != 0:
            # Finding a line after the ending added line
            # in the fixed version, within its scope and
            # mapping it to the buggy version.
            buggy_one_line_after_end_add_line_num = -1
            for item in after_end_add_line_fixed_scope:
                if item in self.__fixed_to_buggy_map.keys():
                    buggy_one_line_after_end_add_line_num = self.__fixed_to_buggy_map[item]
                    break
            assert buggy_one_line_after_end_add_line_num != -1

            # Finding the scope of the after line in the buggy version.
            one_line_after_end_add_line_buggy_scope = self.get_sorted_scope_line_numbers(self.__buggy_content_ast,
                                                                                         self.__buggy_content_line_num,
                                                                                         buggy_one_line_after_end_add_line_num)

            # Getting the scope after end add line in the buggy version.
            after_end_add_line_buggy_scope = list(
                filter(lambda x: x >= buggy_one_line_after_end_add_line_num, one_line_after_end_add_line_buggy_scope))

            # Find a localizable line after end add line in the buggy version.
            after_end_add_line_selected = self.select_localizable_line_number(after_end_add_line_buggy_scope)
            after_end_add_line = after_end_add_line_selected

        return before_start_add_line, after_end_add_line

    def select_localizable_line_number(self, line_numbers: List) -> int:
        executable_line_object = ExecutableLine(self.__buggy_content_lines, self.__buggy_content_ast)
        for line in line_numbers:
            if executable_line_object.is_executable(line):
                return line

    @staticmethod
    def get_high_level_none_decl_lines(ast_node: ast.AST,
                                       start_line_num: int,
                                       end_line_num: int) -> List[int]:

        line_numbers = list(range(start_line_num, end_line_num + 1))
        high_level_none_decl_visitor = HighLevelNoneDeclVisitor(ast_node, line_numbers)
        high_level_none_decl_visitor.visit(ast_node)
        high_level_none_decl_line_numbers = high_level_none_decl_visitor.get_line_numbers()

        return high_level_none_decl_line_numbers

    @staticmethod
    def get_sorted_scope_line_numbers(file_ast_tree, file_line_num: int, line_number) -> List[int]:
        scope_finder_visitor = ScopeFinderVisitor(line_number)
        scope_finder_visitor.visit(file_ast_tree)
        scopes = scope_finder_visitor.get_scopes()
        if len(scopes) != 0:
            min_scope = AddModeManager.min_scope(scopes)
            if min_scope.node_type == ScopeType.Function:
                function_scope_lines = list(range(min_scope.node_range[0], min_scope.node_range[1] + 1))
                scope_line_numbers = function_scope_lines
            elif min_scope.node_type == ScopeType.Class:
                high_level_class_scope_lines = AddModeManager.get_high_level_none_decl_lines(min_scope.node_ast,
                                                                                             min_scope.node_range[0],
                                                                                             min_scope.node_range[1])
                scope_line_numbers = high_level_class_scope_lines
            else:
                raise Exception("This must not happen.")
        else:
            high_level_class_scope_lines = AddModeManager.get_high_level_none_decl_lines(file_ast_tree,
                                                                                         1,
                                                                                         file_line_num)
            scope_line_numbers = high_level_class_scope_lines

            scope_line_numbers.sort()

        return scope_line_numbers

    @staticmethod
    def arg_min(items):
        return items.index(min(items))

    @staticmethod
    def min_scope(scopes: List[ScopeItem]) -> ScopeItem:
        scope_len_list = list(map(lambda x: x.get_range()[1] - x.get_range()[0], scopes))
        scope_len_min_index = AddModeManager.arg_min(scope_len_list)
        return scopes[scope_len_min_index]

    def find_scopes(self):
        visitor = ScopeFinderVisitor(self.__fixed_start_add_line_num)
        visitor.visit(self.__fixed_content_ast)
        scopes = visitor.get_scopes()
        return scopes

    def get_sorted_scope_lines(self) -> List[int]:
        return []


class ScopeFinderVisitor(ast.NodeVisitor):
    def __init__(self,
                 target_line_number: int):
        self.__target_line_number = target_line_number
        self.__scopes = []

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        if node.lineno <= self.__target_line_number <= node.end_lineno:
            scope_item = ScopeItem((node.lineno, node.end_lineno),
                                   node,
                                   ScopeType.Function)
            self.__scopes.append(scope_item)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        if node.lineno <= self.__target_line_number <= node.end_lineno:
            scope_item = ScopeItem((node.lineno, node.end_lineno),
                                   node,
                                   ScopeType.Function)
            self.__scopes.append(scope_item)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        if node.lineno <= self.__target_line_number <= node.end_lineno:
            scope_item = ScopeItem((node.lineno, node.end_lineno),
                                   node,
                                   ScopeType.Class)
            self.__scopes.append(scope_item)
        self.generic_visit(node)

    def get_scopes(self):
        return self.__scopes


class HighLevelNoneDeclVisitor(ast.NodeVisitor):
    def __init__(self,
                 ast_node: ast.AST,
                 line_numbers: List[int]):
        self.ast_node = ast_node
        self.line_numbers = line_numbers.copy()

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        if node != self.ast_node:
            self.remove_lines_in_range(node.lineno, node.end_lineno)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        if node != self.ast_node:
            self.remove_lines_in_range(node.lineno, node.end_lineno)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        if node != self.ast_node:
            self.remove_lines_in_range(node.lineno, node.end_lineno)
        self.generic_visit(node)

    def remove_lines_in_range(self,
                              start_line_num: int,
                              end_line_num: int):
        for line_number in range(start_line_num, end_line_num + 1):
            if line_number in self.line_numbers:
                self.line_numbers.remove(line_number)

    def get_line_numbers(self):
        return self.line_numbers


class ExecutableLine:
    def __init__(self,
                 file_lines: List[str],
                 file_ast: ast.AST):
        self.file_lines = file_lines
        self.file_ast = file_ast

    def is_executable(self, line):
        return (not self.is_comment(line) and
                not self.is_empty(line) and
                not self.is_none_node(line) and
                not self.is_decl(line) and
                not self.is_docstring(line) and
                not self.is_decorator(line))

    def is_comment(self, line):
        return self.file_lines[line - 1].strip().startswith("#")

    def is_empty(self, line):
        return self.file_lines[line - 1].strip() == ""

    def is_none_node(self, line):
        decl_visitor = LineFinderVisitor(line)
        decl_visitor.visit(self.file_ast)
        line_node = decl_visitor.get_line_node()
        if line_node is None:
            return True
        return False

    def is_decl(self, line):
        return (self.file_lines[line - 1].strip().startswith("def") or
                self.file_lines[line - 1].strip().startswith("class") or
                self.file_lines[line - 1].strip().startswith("async def"))

    def is_docstring(self, line):
        pass

    def is_decorator(self, line):
        return self.file_lines[line - 1].strip().startswith("@")


class LineFinderVisitor(ast.NodeVisitor):
    def __init__(self,
                 line: int):
        self.line = line
        self.found_nodes = []

    def visit(self, node):
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            if node.lineno == node.end_lineno == self.line:
                self.found_nodes.append(node)
        self.generic_visit(node)

    def get_line_node(self) -> Optional[ast.AST]:
        if len(self.found_nodes) == 0:
            return None

        max_index = -1
        max_col_offset = -1
        for index, item in enumerate(self.found_nodes):
            if item.end_col_offset - item.col_offset > max_col_offset:
                max_index = index
                max_col_offset = item.end_col_offset - item.col_offset

        return self.found_nodes[max_index]
