import io
import json
import os
from enum import Enum

import common

Data_dir_name = "data"
Experiment_file_name = "exp_info.json"


class ExperimentType(Enum):
    PythonAll = 0
    PythonSimilar = 1
    JavaAll = 2
    JavaSimilar = 3


def load_json_release_files_to_dict(experiment_type):
    if experiment_type in [ExperimentType.PythonAll, ExperimentType.PythonSimilar]:
        name_prefix = "python_release_"
        language_name = "python"
    elif experiment_type in [ExperimentType.JavaAll, ExperimentType.JavaSimilar]:
        name_prefix = "java_release_"
        language_name = "java"
    else:
        raise Exception()

    granularity_name = "statement"

    experiment_file_path = os.path.join(Data_dir_name, Experiment_file_name)
    experiment_info = {
        "language": language_name,
        "granularity": granularity_name
    }
    common.save_object_to_json(experiment_info, experiment_file_path)

    num_files = 10
    json_release_dict = {}
    for index_item in range(0, num_files):
        current_file = os.path.join("data", name_prefix + str(index_item) + ".json")
        with io.open(current_file) as f:
            current_release_dict = json.load(f)
            json_release_dict.update(current_release_dict)
    return json_release_dict


def load_techniques_to_set(experiment_type):
    if experiment_type == ExperimentType.PythonAll:
        techniques = {
            'DStar',
            'Metallaxis',
            'Muse',
            'Ochiai',
            'PS',
            'ST',
            'Tarantula'
        }
    elif experiment_type == ExperimentType.PythonSimilar:
        techniques = {
            'DStar',
            'Metallaxis',
            'Muse',
            'Ochiai',
            'PS',
            'ST'
        }
    elif experiment_type == ExperimentType.JavaAll:
        techniques = {
            'ochiai',
            'dstar',
            'metallaxis',
            'muse',
            'slicing',
            'slicing_count',
            'slicing_intersection',
            'stacktrace',
            'predicateswitching'
        }
    elif experiment_type == ExperimentType.JavaSimilar:
        techniques = {
            'ochiai',
            'dstar',
            'metallaxis',
            'muse',
            'stacktrace',
            'predicateswitching'
        }
    else:
        raise Exception()
    return techniques


def load_projects_to_list(experiment_type):
    if experiment_type in [ExperimentType.PythonAll, ExperimentType.PythonSimilar]:
        projects = [
            ('black', 13),
            ('cookiecutter', 4),
            ('fastapi', 13),
            ('httpie', 4),
            ('keras', 18),
            # ('luigi', 13),
            ('pandas', 18),
            ('sanic', 3),
            ('spacy', 6),
            ('thefuck', 16),
            ('tornado', 4),
            ('tqdm', 6),
            ('youtube-dl', 16)
        ]
    elif experiment_type in [ExperimentType.JavaAll, ExperimentType.JavaSimilar]:
        projects = [
            ('Math', 106),
            ('Closure', 133),
            ('Time', 27),
            ('Chart', 26),
            ('Lang', 65)
        ]
    else:
        raise Exception()

    return projects


def load_qid_lines_csv_file_name():
    experiment_file_path = os.path.join(Data_dir_name, Experiment_file_name)
    experiment_info_dict = common.load_json_file_to_object(experiment_file_path)
    language_name = experiment_info_dict["language"]
    granularity_name = experiment_info_dict["granularity"]

    if language_name == "python":
        qid_lines_csv_file_name = "python_qid-lines.csv"
    elif language_name == "java":
        qid_lines_csv_file_name = "java_qid-lines.csv"
    else:
        raise Exception()

    return qid_lines_csv_file_name
