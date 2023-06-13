import json
import os.path

Data_Dir_Name = "data"


def _split_dictionary(input_dict, chunk_size):
    """
    https://gist.github.com/nz-angel/31890d2c6cb1c9105e677cacc83a1ffd
    """

    res = []
    new_dict = {}
    for k, v in input_dict.items():
        if len(new_dict) < chunk_size:
            new_dict[k] = v
        else:
            res.append(new_dict)
            new_dict = {k: v}
    res.append(new_dict)
    return res


def load_json_to_dict(file_path):
    with open(file_path) as file_handle:
        content_dict = json.load(file_handle)
    return content_dict


def save_dict_to_json(dict_obj, file_path):
    string_object = json.dumps(dict_obj, indent=5)
    with open(file_path, "w") as file_handle:
        file_handle.write(string_object)


def split_java_all_release_json_file():
    java_all_release_json_file_path = os.path.join(Data_Dir_Name, "release.json")
    content_dict = load_json_to_dict(java_all_release_json_file_path)

    number_of_bugs = len(content_dict)
    number_of_files = 10
    number_of_bugs_in_file = int(number_of_bugs / number_of_files) + 1

    java_all_release_dict_list = _split_dictionary(content_dict, number_of_bugs_in_file)

    for index, item in enumerate(java_all_release_dict_list):
        current_file_name = "java_release_" + str(index) + ".json"
        current_file_path = os.path.join(Data_Dir_Name, current_file_name)
        save_dict_to_json(item, current_file_path)


if __name__ == '__main__':
    split_java_all_release_json_file()
