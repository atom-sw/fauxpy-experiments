import csv
import shutil
from pathlib import Path
from string import Template

TEMPLATE_DIR = Path("template")
TEMPLATE_BODY = TEMPLATE_DIR / Path("faux-in-py-body-template.sh")
TEMPLATE_SBFL = TEMPLATE_DIR / Path("faux-in-py-sbfl-template.sh")
TEMPLATE_MBFL = TEMPLATE_DIR / Path("faux-in-py-mbfl-template.sh")
TEMPLATE_PS = TEMPLATE_DIR / Path("faux-in-py-ps-template.sh")
TEMPLATE_ST = TEMPLATE_DIR / Path("faux-in-py-st-template.sh")

INFO_DIR = Path("info")
SUBJECT_INFO_FILE = INFO_DIR / Path("subject_info.csv")
TIMEOUT_FILE = INFO_DIR / Path("timeout_info.csv")

MEMORY = 32

SBFL = "sbfl"
MBFL = "mbfl"
PS = "ps"
ST = "st"

STATEMENT = "statement"
FUNCTION = "function"

OUTPUT_DIRECTORY = Path("scripts")


def read_template_to_string(template_path):
    with template_path.open("r") as file:
        script_content = file.read()

    return script_content


def read_csv_as_dict_list(file_path):
    subject_info_table = []
    with open(file_path, "r") as file:
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
                               subject: dict,
                               family: str,
                               granularity: str):
    t = Template(script_template)
    script = t.safe_substitute({
        'PLACE_HOLDER_PYTHON_V': wrap_item_in_double_quotes(subject["PYTHON_V"]),
        'PLACE_HOLDER_BENCHMARK_NAME': wrap_item_in_double_quotes(subject["BENCHMARK_NAME"]),
        'PLACE_HOLDER_BUG_NUMBER': wrap_item_in_double_quotes(subject["BUG_NUMBER"]),
        'PLACE_HOLDER_TARGET_DIR': wrap_item_in_double_quotes(subject["TARGET_DIR"]),
        'PLACE_HOLDER_TEST_SUITE': info_list_to_bash_list_items(subject["TEST_SUITE"]),
        'PLACE_HOLDER_EXCLUDE': info_list_to_bash_list_items(subject["EXCLUDE"]),
        'PLACE_HOLDER_TARGET_FAILING_TESTS': info_list_to_bash_list_items(subject["TARGET_FAILING_TESTS"]),
        'PLACE_HOLDER_EXPERIMENT': run_script,
        'PLACE_HOLDER_FAMILY': wrap_item_in_double_quotes(family),
        'PLACE_HOLDER_GRANULARITY': wrap_item_in_double_quotes(granularity)
    })
    return script


def get_script(family, subject_info):
    if family == SBFL:
        family_template_path = TEMPLATE_SBFL
    elif family == MBFL:
        family_template_path = TEMPLATE_MBFL
    elif family == PS:
        family_template_path = TEMPLATE_PS
    elif family == ST:
        family_template_path = TEMPLATE_ST
    else:
        raise Exception()

    body_template = read_template_to_string(TEMPLATE_BODY)
    run_template = read_template_to_string(family_template_path)
    t = Template(run_template)
    run_statement = t.safe_substitute({
        'PLACE_HOLDER_GRANULARITY': STATEMENT
    })
    run_function = t.safe_substitute({
        'PLACE_HOLDER_GRANULARITY': FUNCTION
    })

    statement_script = produce_script_for_subject(body_template, run_statement, subject_info, family, STATEMENT)
    function_script = produce_script_for_subject(body_template, run_function, subject_info, family, FUNCTION)

    return statement_script, function_script


def get_experiment_timeout(subject_info, family):
    timeout_info = read_csv_as_dict_list(TIMEOUT_FILE)
    benchmark_name = subject_info["BENCHMARK_NAME"]

    benchmark_timeout_info = list(filter(lambda x: x["BENCHMARK_NAME"] == benchmark_name, timeout_info))[0]
    experiment_timeout = benchmark_timeout_info[family]

    return experiment_timeout


def save_script(script: str,
                subject_info: dict,
                family: str,
                granularity: str,
                index: int):
    # N_Th_Mg_script_name.sh
    # N is a unique numerical identifier
    # T is the timeout we should use for that experiment (in hours).
    # T can be anything between 1 and 48 hours
    # M is the amount of memory we should allocate.
    # M is 16 GB by default, and can be incremented up to 64 GB

    timeout = get_experiment_timeout(subject_info, family)
    file_name = (f"{subject_info['#']}{index}_"
                 f"{timeout}h_"
                 f"{MEMORY}g_"
                 f"{subject_info['BENCHMARK_NAME']}_"
                 f"{subject_info['BUG_NUMBER']}_"
                 f"{family}_"
                 f"{granularity}.sh")

    if not OUTPUT_DIRECTORY.exists():
        OUTPUT_DIRECTORY.mkdir()

    file_path = OUTPUT_DIRECTORY / Path(file_name)
    file_path.write_text(script)


def remove_output():
    if OUTPUT_DIRECTORY.exists():
        shutil.rmtree(OUTPUT_DIRECTORY.absolute().resolve())


def main():
    remove_output()
    subject_info_table = read_csv_as_dict_list(SUBJECT_INFO_FILE)
    for item in subject_info_table:
        statement, function = get_script(SBFL, item)
        index = 0
        save_script(statement, item, SBFL, STATEMENT, index)
        index += 1
        # save_script(function, item, SBFL, FUNCTION, index)

        statement, function = get_script(MBFL, item)
        index += 1
        save_script(statement, item, MBFL, STATEMENT, index)
        index += 1
        # save_script(function, item, MBFL, FUNCTION, index)

        statement, function = get_script(PS, item)
        index += 1
        save_script(statement, item, PS, STATEMENT, index)
        index += 1
        # save_script(function, item, PS, FUNCTION, index)

        _, function = get_script(ST, item)
        index += 1
        save_script(function, item, ST, FUNCTION, index)


if __name__ == '__main__':
    main()
