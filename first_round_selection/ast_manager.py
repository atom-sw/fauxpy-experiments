import ast
from _ast import FunctionDef, AsyncFunctionDef, ClassDef, Expr, AST
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

    def get_range_len(self):
        return self.node_range[1] - self.node_range[0]

    def contains(self, other) -> bool:
        return (self.get_range_len() > other.get_range_len() and
                self.node_range[0] <= other.get_range()[0] and
                self.node_range[1] >= other.get_range()[1])

    def get_lines(self) -> List[int]:
        return list(range(self.node_range[0], self.node_range[1] + 1))

    def __eq__(self, other):
        return (self.node_range[0] == other.get_range()[0] and
                self.node_range[1] == other.get_range()[1] and
                self.node_type == other.get_type() and
                self.node_ast == other.get_ast())

    def __ne__(self, other):
        return not self.__eq__(other)


class AddModeManager:

    def __init__(self,
                 buggy_content: str,
                 fixed_content: str,
                 start_add_line_num: int,
                 end_add_line_num: int,
                 fixed_to_buggy_map: Dict[int, int]):
        self.__buggy_content_lines = buggy_content.splitlines()
        self.__fixed_content_lines = fixed_content.splitlines()
        self.__fixed_start_add_line_num = start_add_line_num
        self.__fixed_end_add_line_num = end_add_line_num
        self.__fixed_to_buggy_map = fixed_to_buggy_map
        self.__buggy_content_ast = ast.parse(buggy_content)
        self.__fixed_content_ast = ast.parse(fixed_content)

    def get_add_mode_ground_truth(self) -> Tuple[int, int]:
        before_start_add_line = -1
        after_end_add_line = -1

        # Finding the scope of the starting and ending added lines in fixed version.
        start_add_line_fixed_scope = self.get_sorted_scope_line_numbers(self.__fixed_content_ast,
                                                                        self.__fixed_content_lines,
                                                                        self.__fixed_start_add_line_num)
        end_add_line_fixed_scope = self.get_sorted_scope_line_numbers(self.__fixed_content_ast,
                                                                      self.__fixed_content_lines,
                                                                      self.__fixed_end_add_line_num)

        # Getting the scope of start add line in the fixed version.
        before_start_add_line_fixed_scope = [x for x in start_add_line_fixed_scope
                                             if x < self.__fixed_start_add_line_num]

        # Getting the scope of end add line in the fixed version.
        after_end_add_line_fixed_scope = [x for x in end_add_line_fixed_scope
                                          if x > self.__fixed_end_add_line_num]

        # If the added code is a whole scope (e.g., whole function)
        if (self.is_same_list(start_add_line_fixed_scope, end_add_line_fixed_scope) and
                len(before_start_add_line_fixed_scope) == 0 and
                len(after_end_add_line_fixed_scope) == 0):
            scope_lines = start_add_line_fixed_scope
            whole_scope_parent = WholeScopeParent(self.__fixed_content_ast, self.__fixed_content_lines, scope_lines)
            parent_scope_lines = whole_scope_parent.get_parent_scope_lines()

            # Getting the scope of start add line in the fixed version.
            before_start_add_line_fixed_scope = [x for x in parent_scope_lines
                                                 if x < self.__fixed_start_add_line_num]

            # Getting the scope of end add line in the fixed version.
            after_end_add_line_fixed_scope = [x for x in parent_scope_lines
                                              if x > self.__fixed_end_add_line_num]

        if len(before_start_add_line_fixed_scope) != 0:
            # Finding a line before the starting added line
            # in the fixed version, within its scope and
            # mapping it to the buggy version.
            tmp = before_start_add_line_fixed_scope.copy()
            tmp.reverse()
            buggy_one_line_before_start_add_line_num = -1
            for item in tmp:
                if item in self.__fixed_to_buggy_map.keys():
                    if self.__fixed_content_lines[item - 1] != "":
                        buggy_one_line_before_start_add_line_num = self.__fixed_to_buggy_map[item]
                        break

            if buggy_one_line_before_start_add_line_num == -1:
                before_start_add_line = -1
            else:
                # Finding the scope of the before line in the buggy version.
                none_empty_one_line_before_start_add_line_buggy_scope = self.get_sorted_scope_line_numbers(
                    self.__buggy_content_ast,
                    self.__buggy_content_lines,
                    buggy_one_line_before_start_add_line_num)

                # Getting the scope before start add line in the buggy version.
                before_start_add_line_buggy_scope = [x for x in none_empty_one_line_before_start_add_line_buggy_scope if
                                                     x <= buggy_one_line_before_start_add_line_num]

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
                    if self.__fixed_content_lines[item - 1] != "":
                        buggy_one_line_after_end_add_line_num = self.__fixed_to_buggy_map[item]
                        break

            if buggy_one_line_after_end_add_line_num == -1:
                after_end_add_line = -1
            else:
                # Finding the scope of the after line in the buggy version.
                one_line_after_end_add_line_buggy_scope = self.get_sorted_scope_line_numbers(self.__buggy_content_ast,
                                                                                             self.__buggy_content_lines,
                                                                                             buggy_one_line_after_end_add_line_num)

                # Getting the scope after end add line in the buggy version.
                after_end_add_line_buggy_scope = list(
                    filter(lambda x: x >= buggy_one_line_after_end_add_line_num,
                           one_line_after_end_add_line_buggy_scope))

                # Find a localizable line after end add line in the buggy version.
                after_end_add_line_selected = self.select_localizable_line_number(after_end_add_line_buggy_scope)
                after_end_add_line = after_end_add_line_selected

        return before_start_add_line, after_end_add_line

    def select_localizable_line_number(self, line_numbers: List) -> int:
        executable_line_object = ExecutableLine(self.__buggy_content_lines, self.__buggy_content_ast)
        for line in line_numbers:
            if executable_line_object.is_executable(line):
                return line
        return -1

    @staticmethod
    def get_high_level_none_decl_lines(ast_node: ast.AST,
                                       start_line_num: int,
                                       end_line_num: int) -> List[int]:

        line_numbers = list(range(start_line_num, end_line_num + 1))
        high_level_none_decl_visitor = HighLevelNoneDeclVisitor(ast_node, line_numbers)
        high_level_none_decl_visitor.visit(ast_node)
        high_level_none_decl_line_numbers = high_level_none_decl_visitor.get_line_numbers()

        return high_level_none_decl_line_numbers

    @classmethod
    def get_sorted_scope_line_numbers(cls, file_ast_tree: ast.AST, file_lines: List[str], line_number: int) -> List[
        int]:
        scope_finder_visitor = ScopeFinderVisitor(line_number)
        scope_finder_visitor.visit(file_ast_tree)
        scopes = scope_finder_visitor.get_scopes()
        if len(scopes) != 0:
            min_scope = cls.min_scope(scopes)
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
            global_scope_lines = AddModeManager.get_high_level_none_decl_lines(file_ast_tree,
                                                                               1,
                                                                               len(file_lines))
            scope_line_numbers = global_scope_lines

            scope_line_numbers.sort()

        return scope_line_numbers

    @staticmethod
    def arg_max(items):
        return items.index(max(items))

    @staticmethod
    def arg_min(items):
        return items.index(min(items))

    @classmethod
    def min_scope(cls, scopes: List[ScopeItem]) -> ScopeItem:
        for item_x in scopes:
            for item_y in scopes:
                assert item_x == item_y or item_x.get_range_len() != item_y.get_range_len()
                if item_x.get_range_len() > item_y.get_range_len():
                    assert item_x.contains(item_y)

        scope_len_list = [x.get_range()[1] - x.get_range()[0] for x in scopes]

        scope_len_min_index = cls.arg_min(scope_len_list)
        min_scope = scopes[scope_len_min_index]

        return min_scope

    @staticmethod
    def is_same_list(list_a: List, list_b: List) -> bool:
        if len(list_a) != len(list_b):
            return False

        for item_a in list_a:
            if item_a not in list_b:
                return False

        return True


def get_function_class_ast_node_start_end_lines(node):
    start_line_num = node.lineno
    end_line_num = node.end_lineno
    for item in node.decorator_list:
        start_line_num = min(start_line_num, item.lineno)

    return start_line_num, end_line_num


class ScopeFinderVisitor(ast.NodeVisitor):
    def __init__(self,
                 target_line_number: int):
        self.__target_line_number = target_line_number
        self.__scopes = []

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        if start_line_num <= self.__target_line_number <= end_line_num:
            scope_item = ScopeItem((start_line_num, end_line_num),
                                   node,
                                   ScopeType.Function)
            self.__scopes.append(scope_item)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        if start_line_num <= self.__target_line_number <= end_line_num:
            scope_item = ScopeItem((start_line_num, end_line_num),
                                   node,
                                   ScopeType.Function)
            self.__scopes.append(scope_item)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        if start_line_num <= self.__target_line_number <= end_line_num:
            scope_item = ScopeItem((start_line_num, end_line_num),
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
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        if node != self.ast_node:
            self._remove_lines_in_range(start_line_num, end_line_num)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        if node != self.ast_node:
            self._remove_lines_in_range(start_line_num, end_line_num)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        if node != self.ast_node:
            self._remove_lines_in_range(start_line_num, end_line_num)
        self.generic_visit(node)

    def _remove_lines_in_range(self,
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
                # not self.is_none_node(line) and
                not self.is_decl(line) and
                not self.is_docstring(line) and
                not self.is_decorator(line) and
                not self.is_only_brackets(line) and
                not self.is_else(line) and
                not self.is_finally(line))

    def is_comment(self, line):
        return self.file_lines[line - 1].strip().startswith("#")

    def is_empty(self, line):
        return self.file_lines[line - 1].strip() == ""

    def is_decl(self, line):
        return (self.file_lines[line - 1].strip().startswith("def") or
                self.file_lines[line - 1].strip().startswith("class") or
                self.file_lines[line - 1].strip().startswith("async def"))

    def is_docstring(self, line):
        line_text = self.file_lines[line - 1]
        if (line_text.startswith("'''") or
                line_text.startswith('"""') or
                line_text.endswith("'''") or
                line_text.endswith('"""')):
            return True

        docstring_visitor = DocstringVisitor(line)
        docstring_visitor.visit(self.file_ast)
        temp = docstring_visitor.is_docstring()
        return temp

    def is_decorator(self, line):
        return self.file_lines[line - 1].strip().startswith("@")

    def is_only_brackets(self, line: int):
        line_text = self.file_lines[line - 1].strip()
        bracket_count = 0
        for c in line_text:
            if c in [",", "[", "(", "{", "}", ")", "]"]:
                bracket_count += 1

        return len(line_text) == bracket_count

    def is_else(self, line):
        return self.file_lines[line - 1].strip().startswith("else")

    def is_finally(self, line):
        return self.file_lines[line - 1].strip().startswith("finally")


class DocstringVisitor(ast.NodeVisitor):
    def __init__(self,
                 line: int):
        self.__line = line
        self.__is_string = False

    def visit_Expr(self, node: Expr) -> Any:
        if node.lineno <= self.__line <= node.end_lineno:
            if (hasattr(node, "value") and
                    isinstance(node.value, ast.Constant) and
                    hasattr(node.value, "value")):
                self.__is_string = True
        self.generic_visit(node)

    def is_docstring(self):
        return self.__is_string


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self,
                 lines: List[int]):
        self._lines = lines
        self._function_names = []
        self._function_nodes = []

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        if self._is_in_lines(node):
            function_name = self._get_function_name(node)
            self._function_names.append(function_name)
            self._function_nodes.append(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        if self._is_in_lines(node):
            function_name = self._get_function_name(node)
            self._function_names.append(function_name)
            self._function_nodes.append(node)
        self.generic_visit(node)

    def get_function_names(self) -> List[str]:
        return self._function_names

    def get_function_nodes(self) -> List:
        return self._function_nodes

    def _is_in_lines(self, node) -> bool:
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        for line in self._lines:
            if start_line_num <= line <= end_line_num:
                return True
        return False

    @staticmethod
    def _get_function_name(node):
        start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)
        return f"{node.name}::{start_line_num}::{end_line_num}"


def get_functions_for_lines(module_content: str,
                            lines: List[int]) -> List[str]:
    tree = ast.parse(module_content)
    function_visitor = FunctionVisitor(lines)
    function_visitor.visit(tree)
    functions = function_visitor.get_function_names()
    return functions


class WholeScopeParent:
    def __init__(self,
                 content_ast: ast.AST,
                 content_lines: List[str],
                 scope_lines: List[int]):
        self._content_ast = content_ast
        self._content_lines = content_lines
        self._scope_lines = scope_lines

    def get_parent_scope_lines(self) -> List[int]:
        min_scope = self._get_min_scope()
        parent_scope_lines = self._get_parent_scope_lines(min_scope)
        return parent_scope_lines

    def _get_min_scope(self) -> ScopeItem:
        scope_list = []
        for line_item in self._scope_lines:
            scope_finder_visitor = ScopeFinderVisitor(line_item)
            scope_finder_visitor.visit(self._content_ast)
            scopes = scope_finder_visitor.get_scopes()
            for scope in scopes:
                if scope not in scope_list:
                    scope_list.append(scope)

        min_scope = min(scope_list, key=lambda x: x.get_range_len())

        for scope_item in scope_list:
            assert scope_item == min_scope or scope_item.contains(min_scope)

        return min_scope

    def _get_parent_scope_lines(self, scope: ScopeItem) -> List[int]:
        scope_lines = scope.get_lines()
        parent_visitor = ParentVisitor(scope_lines, scope.get_ast())
        parent_visitor.visit(self._content_ast)
        min_parent_ast = parent_visitor.get_min_parent_ast()

        if min_parent_ast is None:
            line_numbers = list(range(1, len(self._content_lines) + 1))
            high_level_none_decl_visitor = HighLevelNoneDeclVisitor(self._content_ast, line_numbers)
            high_level_none_decl_visitor.visit(self._content_ast)
            parent_scope_lines = high_level_none_decl_visitor.get_line_numbers()
        else:
            parent_scope_lines = self._get_node_lines(min_parent_ast)

        return parent_scope_lines

    @staticmethod
    def _get_node_lines(node) -> List[int]:
        start_line_num = node.lineno
        end_line_num = node.end_lineno

        if (isinstance(node, ast.FunctionDef) or
                isinstance(node, ast.AsyncFunctionDef) or
                isinstance(node, ast.ClassDef)):
            start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)

        node_lines = list(range(start_line_num, end_line_num + 1))

        return node_lines


class ParentVisitor(ast.NodeVisitor):
    def __init__(self,
                 scope_lines: List[int],
                 scope_ast: ast.AST):
        self._lines = scope_lines
        self._scope_ast = scope_ast
        self._parent_nodes = []

    def visit(self, node: AST) -> Any:
        if self._contains_all_lines(node):
            self._parent_nodes.append(node)
        self.generic_visit(node)

    def _contains_all_lines(self, node) -> bool:
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return False

        if node == self._scope_ast:
            return False

        start_line_num = node.lineno
        end_line_num = node.end_lineno

        if (isinstance(node, ast.FunctionDef) or
                isinstance(node, ast.AsyncFunctionDef) or
                isinstance(node, ast.ClassDef)):
            start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)

        for line in self._lines:
            if not (start_line_num <= line <= end_line_num):
                return False
        return True

    def get_min_parent_ast(self) -> Optional[ast.AST]:
        if len(self._parent_nodes) == 0:
            return None
        else:
            min_parent = min(self._parent_nodes, key=lambda x: self._node_size(x))
            return min_parent

    @staticmethod
    def _node_size(node) -> int:
        start_line_num = node.lineno
        end_line_num = node.end_lineno

        if (isinstance(node, ast.FunctionDef) or
                isinstance(node, ast.AsyncFunctionDef) or
                isinstance(node, ast.ClassDef)):
            start_line_num, end_line_num = get_function_class_ast_node_start_end_lines(node)

        node_size = end_line_num - start_line_num + 1

        return node_size
