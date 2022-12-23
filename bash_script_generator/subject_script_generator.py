import csv
from pathlib import Path
from string import Template

TEMPLATE_DIR = Path("template")
TEMPLATE_BODY = TEMPLATE_DIR / Path("faux-in-py-body-template.sh")
TEMPLATE_SBFL = TEMPLATE_DIR / Path("faux-in-py-sbfl-template.sh")
TEMPLATE_MBFL = TEMPLATE_DIR / Path("faux-in-py-mbfl-template.sh")
TEMPLATE_PS = TEMPLATE_DIR / Path("faux-in-py-ps-template.sh")
TEMPLATE_ST = TEMPLATE_DIR / Path("faux-in-py-st-template.sh")
SUBJECT_INFO_FILE_NAME = Path("subject_info.csv")

SBFL = "sbfl"
MBFL = "mbfl"
PS = "ps"
ST = "st"

STATEMENT = "statement"
FUNCTION = "function"

SCRIPT_DIRECTORY = "scripts"


def read_template_to_string(template_path):
    with template_path.open("r") as file:
        script_content = file.read()

    return script_content


def read_subject_info():
    subject_info_table = []
    with open(SUBJECT_INFO_FILE_NAME, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            subject_info_table.append(row)

    return subject_info_table


def wrap_item_in_double_quotes(item):
    return f'"{item}"'


def info_list_to_bash_list_items(info_list: str):
    if info_list.strip() == "-":
        return ""

    items = info_list.split(";")
    bash_list = ""
    for item in items:
        bash_list += f'"{item.strip()}"\n'

    return bash_list.strip()


def produce_script_for_subject(script_template: str,
                               run_script: str,
                               subject: dict):
    t = Template(script_template)
    script = t.safe_substitute({
        'PLACE_HOLDER_PYTHON_V': wrap_item_in_double_quotes(subject["PYTHON_V"]),
        'PLACE_HOLDER_BENCHMARK_NAME': wrap_item_in_double_quotes(subject["BENCHMARK_NAME"]),
        'PLACE_HOLDER_BUG_NUMBER': wrap_item_in_double_quotes(subject["BUG_NUMBER"]),
        'PLACE_HOLDER_TARGET_DIR': wrap_item_in_double_quotes(subject["TARGET_DIR"]),
        'PLACE_HOLDER_TEST_SUITE': info_list_to_bash_list_items(subject["TEST_SUITE"]),
        'PLACE_HOLDER_EXCLUDE': info_list_to_bash_list_items(subject["EXCLUDE"]),
        'PLACE_HOLDER_TARGET_FAILING_TESTS': info_list_to_bash_list_items(subject["TARGET_FAILING_TESTS"]),
        'PLACE_HOLDER_EXPERIMENT': run_script
    })
    return script


def get_script(family_template_path, subject_info):
    body_template = read_template_to_string(TEMPLATE_BODY)
    run_template = read_template_to_string(family_template_path)
    t = Template(run_template)
    run_statement = t.safe_substitute({
        'PLACE_HOLDER_GRANULARITY': STATEMENT
    })
    run_function = t.safe_substitute({
        'PLACE_HOLDER_GRANULARITY': FUNCTION
    })

    statement_script = produce_script_for_subject(body_template, run_statement, subject_info)
    function_script = produce_script_for_subject(body_template, run_function, subject_info)

    return statement_script, function_script


def save_script(script: str,
                subject_info: dict,
                family: str,
                granularity: str):
    file_name = f"{subject_info['BENCHMARK_NAME']}_{subject_info['BUG_NUMBER']}_{family}_{granularity}.sh"
    scripts_dir_path = Path(SCRIPT_DIRECTORY)

    if not scripts_dir_path.exists():
        scripts_dir_path.mkdir()

    file_path = scripts_dir_path / Path(file_name)
    file_path.write_text(script)


def main():
    subject_info_table = read_subject_info()
    for item in subject_info_table:
        statement, function = get_script(TEMPLATE_SBFL, item)
        save_script(statement, item, SBFL, STATEMENT)
        save_script(function, item, SBFL, FUNCTION)

        statement, function = get_script(TEMPLATE_MBFL, item)
        save_script(statement, item, MBFL, STATEMENT)
        save_script(function, item, MBFL, FUNCTION)

        statement, function = get_script(TEMPLATE_PS, item)
        save_script(statement, item, PS, STATEMENT)
        save_script(function, item, PS, FUNCTION)

        _, function = get_script(TEMPLATE_ST, item)
        save_script(function, item, ST, FUNCTION)


if __name__ == '__main__':
    main()
