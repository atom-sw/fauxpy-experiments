import json
import collections


def results_to_dictionary_object(top_n, top_n_percent, avg_exam):
    results_dict = {
        "@1": top_n[0],
        "@3": top_n[1],
        "@5": top_n[2],
        "@10": top_n[3],

        "@1%": top_n_percent[0],
        "@3%": top_n_percent[1],
        "@5%": top_n_percent[2],
        "@10%": top_n_percent[3],

        "java_exam": avg_exam
    }

    return results_dict


def save_object_to_json(obj, file_name):
    string_object = json.dumps(obj, indent=5)
    save_string_to_file(string_object, file_name)


def save_string_to_file(content_str, file_name):
    with open(file_name, "w") as file_han:
        file_han.write(content_str)


def load_file_to_string(file_name):
    with open(file_name, "r") as file_han:
        content = file_han.read()
    return content


def load_json_file_to_object(file_path):
    content = load_file_to_string(file_path)
    object_file = json.loads(content)
    return object_file
