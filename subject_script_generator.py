import csv
from pathlib import Path
from string import Template

SCRIPT_FILE_NAME = "faux-in-py-template.sh"
SUBJECT_INFO_FILE_NAME = "subject_info.csv"


def read_template_script_to_string():
    with open(SCRIPT_FILE_NAME, "r") as file:
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
                               subject: dict):
    t = Template(script_template)
    script = t.safe_substitute({
        'PLACE_HOLDER_PYTHON_V': wrap_item_in_double_quotes(subject["PYTHON_V"]),
        'PLACE_HOLDER_BENCHMARK_NAME': wrap_item_in_double_quotes(subject["BENCHMARK_NAME"]),
        'PLACE_HOLDER_BUG_NUMBER': wrap_item_in_double_quotes(subject["BUG_NUMBER"]),
        'PLACE_HOLDER_TARGET_DIR': wrap_item_in_double_quotes(subject["TARGET_DIR"]),
        'PLACE_HOLDER_TEST_SUITE': info_list_to_bash_list_items(subject["TEST_SUITE"]),
        'PLACE_HOLDER_EXCLUDE': info_list_to_bash_list_items(subject["EXCLUDE"]),
        'PLACE_HOLDER_TARGET_FAILING_TESTS': info_list_to_bash_list_items(subject["TARGET_FAILING_TESTS"])
    })
    return script


def save_script_string(file_name, script_string):
    scripts_dir_path = Path("scripts")

    if not scripts_dir_path.exists():
        scripts_dir_path.mkdir()

    file_path = scripts_dir_path / Path(file_name)
    file_path.write_text(script_string)


def main():
    template_script_content = read_template_script_to_string()
    subject_info_table = read_subject_info()
    for item in subject_info_table:
        script_string = produce_script_for_subject(template_script_content, item)
        file_name = f"{item['BENCHMARK_NAME']}_{item['BUG_NUMBER']}.sh"
        save_script_string(file_name, script_string)


if __name__ == '__main__':
    main()
