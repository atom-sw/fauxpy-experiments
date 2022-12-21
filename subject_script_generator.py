import csv
from pathlib import Path

SCRIPT_FILE_NAME = "faux-in-py.sh"
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


def produce_script_for_subject(script_template: str,
                               subject: dict):
    script_subject = script_template
    for key, value in subject.items():
        if key != "#":
            script_subject = script_subject.replace(f"####{key}####", value)

    return script_subject


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
