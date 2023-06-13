import io
import json
import os
from enum import Enum

import common

Language_python = "python"
Language_java = "java"
Granularity_statement = "statement"
Granularity_function = "function"
Granularity_module = "module"
Combination_alfa = "alfa"
Combination_sbst = "sbst"

Data_dir_name = "data"
Experiment_file_name = "exp_info.json"


class ExperimentType(Enum):
    PythonAlfaStatement = 0
    PythonAlfaFunction = 1
    PythonAlfaModule = 2
    PythonSbstStatement = 3
    PythonSbstFunction = 4
    PythonSbstModule = 5
    JavaAlfaStatement = 6
    JavaSbstStatement = 7


def load_json_release_files_to_dict(experiment_type):
    if experiment_type in [ExperimentType.PythonAlfaStatement,
                           ExperimentType.PythonSbstStatement]:
        name_prefix = "python_statement_release_"
        language_name = Language_python
        granularity_name = Granularity_statement
    elif experiment_type in [ExperimentType.PythonAlfaFunction,
                             ExperimentType.PythonSbstFunction]:
        name_prefix = "python_function_release_"
        language_name = Language_python
        granularity_name = Granularity_function
    elif experiment_type in [ExperimentType.PythonAlfaModule,
                             ExperimentType.PythonSbstModule]:
        name_prefix = "python_module_release_"
        language_name = Language_python
        granularity_name = Granularity_module
    elif experiment_type in [ExperimentType.JavaAlfaStatement,
                             ExperimentType.JavaSbstStatement]:
        name_prefix = "java_release_"
        language_name = Language_java
        granularity_name = Granularity_statement
    else:
        raise Exception()

    if experiment_type in [ExperimentType.PythonAlfaStatement,
                           ExperimentType.PythonAlfaFunction,
                           ExperimentType.PythonAlfaModule,
                           ExperimentType.JavaAlfaStatement]:
        combination_name = Combination_alfa
    elif experiment_type in [ExperimentType.PythonSbstStatement,
                             ExperimentType.PythonSbstFunction,
                             ExperimentType.PythonSbstModule,
                             ExperimentType.JavaSbstStatement]:
        combination_name = Combination_sbst
    else:
        raise Exception()

    experiment_file_path = os.path.join(Data_dir_name, Experiment_file_name)
    experiment_info = {
        "language": language_name,
        "granularity": granularity_name,
        "combination": combination_name
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
    if experiment_type in [ExperimentType.PythonAlfaStatement,
                           ExperimentType.PythonAlfaFunction,
                           ExperimentType.PythonAlfaModule]:
        techniques = {
            'DStar',
            'Metallaxis',
            'Muse',
            'Ochiai',
            'PS',
            'ST'
        }
    elif experiment_type in [ExperimentType.PythonSbstStatement,
                             ExperimentType.PythonSbstFunction,
                             ExperimentType.PythonSbstModule]:
        techniques = {
            'DStar',
            'Ochiai',
            'ST'
        }
    elif experiment_type == ExperimentType.JavaAlfaStatement:
        techniques = {
            'ochiai',
            'dstar',
            'metallaxis',
            'muse',
            'stacktrace',
            'predicateswitching'
        }
    elif experiment_type == ExperimentType.JavaSbstStatement:
        techniques = {
            'ochiai',
            'dstar',
            'stacktrace',
        }
    else:
        raise Exception()

    return techniques


def load_projects_to_list(experiment_type):
    if experiment_type in [ExperimentType.PythonAlfaStatement,
                           ExperimentType.PythonAlfaFunction,
                           ExperimentType.PythonAlfaModule,
                           ExperimentType.PythonSbstStatement,
                           ExperimentType.PythonSbstFunction,
                           ExperimentType.PythonSbstModule
                           ]:
        projects = [
            ('black', 13),
            ('cookiecutter', 4),
            ('fastapi', 13),
            ('httpie', 4),
            ('keras', 18),
            ('luigi', 13),
            ('pandas', 18),
            ('sanic', 3),
            ('spacy', 6),
            ('thefuck', 16),
            ('tornado', 4),
            ('tqdm', 7),
            ('youtube-dl', 16)
        ]
    elif experiment_type in [ExperimentType.JavaAlfaStatement,
                             ExperimentType.JavaSbstStatement]:
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

    if language_name == Language_python:
        if granularity_name == Granularity_statement:
            qid_lines_csv_file_name = "python_statement_qid-lines.csv"
        elif granularity_name == Granularity_function:
            qid_lines_csv_file_name = "python_function_qid-lines.csv"
        elif granularity_name == Granularity_module:
            qid_lines_csv_file_name = "python_module_qid-lines.csv"
        else:
            raise Exception()
    elif language_name == Language_java:
        qid_lines_csv_file_name = "java_qid-lines.csv"
    else:
        raise Exception()

    return qid_lines_csv_file_name


def get_results_file_name():
    experiment_file_path = os.path.join(Data_dir_name, Experiment_file_name)
    experiment_info_dict = common.load_json_file_to_object(experiment_file_path)
    language_name = experiment_info_dict["language"]
    granularity_name = experiment_info_dict["granularity"]
    combination_name = experiment_info_dict["combination"]
    file_name = ("results_" +
                 language_name +
                 "_" +
                 granularity_name +
                 "_" +
                 combination_name +
                 ".json")

    return file_name


def get_experiment_file_info():
    experiment_file_path = os.path.join(Data_dir_name, Experiment_file_name)
    experiment_info_dict = common.load_json_file_to_object(experiment_file_path)
    language_name = experiment_info_dict["language"]
    granularity_name = experiment_info_dict["granularity"]
    combination_name = experiment_info_dict["combination"]

    return language_name, granularity_name, combination_name


def load_ground_truth_num_items():
    (language_name,
     granularity_name,
     combination_name) = get_experiment_file_info()

    assert language_name == Language_python

    if granularity_name == Granularity_statement:
        ground_truth_dict_file_name = "python_statement_qid_ground_truth_number_of_items.json"
    elif granularity_name == Granularity_function:
        ground_truth_dict_file_name = "python_function_qid_ground_truth_number_of_items.json"
    elif granularity_name == Granularity_module:
        ground_truth_dict_file_name = "python_module_qid_ground_truth_number_of_items.json"
    else:
        raise Exception()

    ground_truth_dict_file_path = os.path.join(Data_dir_name, ground_truth_dict_file_name)
    ground_truth_dict_content = common.load_json_file_to_object(ground_truth_dict_file_path)

    return ground_truth_dict_content
