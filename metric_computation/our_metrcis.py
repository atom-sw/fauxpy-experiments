from typing import List

from entity_type import ScoredStatement


class ProgramLocation:
    def __init__(self,
                 package: str,
                 module: str,
                 line: int):
        self._package = package
        self._module = module
        self._line = line

    def _pretty_representation(self):
        return f"<{self._package}, {self._module}, {self._line}>"

    def __str__(self):
        return self._pretty_representation()

    def __repr__(self):
        return self._pretty_representation()

    @staticmethod
    def from_scored_statement(scored_statement: ScoredStatement):
        file_path_parts = scored_statement.get_file_path().split("/")
        package_path = "/".join(file_path_parts[:-1])
        module_path = file_path_parts[-1]
        line_number = scored_statement.get_line_number()
        location_object = ProgramLocation(package_path, module_path, line_number)
        return location_object


def scored_statements_to_program_locations(scored_statements: List[ScoredStatement]):
    program_locations = []
    for scored_statement in scored_statements:
        assert isinstance(scored_statement, ScoredStatement)
        current = ProgramLocation.from_scored_statement(scored_statement)
        program_locations.append(current)
    return program_locations

