# pip install python-scalpel
# pip install packaging
import signal
from pathlib import Path
from typing import List

from scalpel.call_graph.pycg import CallGraphGenerator


def module_path_to_import(src_module: str):
    temp = src_module.replace(".py", "")
    parts = temp.strip().split("/")
    import_format_module = ".".join(parts)
    return import_format_module


def get_call_graph_edges(test_module: str,
                         source_code_package: str,
                         timeout: int):
    # def handler(signum, frame):
    #     raise TimeoutError()

    # signal.signal(signal.SIGALRM, handler)
    # signal.alarm(timeout)

    cg_generator = CallGraphGenerator([test_module], source_code_package, max_iter=1)
    cg_generator.analyze()
    edges = cg_generator.output_edges()

    # signal.alarm(0)

    return edges


def is_affecting_test_module(test_module: str,
                             source_code_packages: List[str],
                             changed_modules: List[str],
                             timeout: int):
    for src_package in source_code_packages:
        # print("Source package", src_package)
        try:
            edges = get_call_graph_edges(test_module, src_package, timeout)
        except Exception:
            # If call graph cannot be made,
            # let's keep the test module to stay on
            # the safe side.
            print("Unable to make call graph for: ", test_module)
            return True

        # unique_edge_destinations = set()
        # unique_edge_destinations.update(map(lambda x: x[1], edges))

        for src_module in changed_modules:
            # print("Source module: ", src_module)
            src_import_format = module_path_to_import(src_module)
            test_module_name = test_module.split("/")[-1].replace(".py", "")
            for source, destination in edges:
                if test_module_name in source and src_import_format in destination:
                    return True

    return False


def call_graph():
    # test_suite_path = Path("/home/moe/BugsInPyExp/7.keras/bug20/buggy/keras/tests")
    # source_code_packages = ["/home/moe/BugsInPyExp/7.keras/bug20/buggy/keras/keras",
    #                         "/home/moe/BugsInPyExp/7.keras/bug20/buggy/keras/docs",
    #                         "/home/moe/BugsInPyExp/7.keras/bug20/buggy/keras/examples"]
    # changed_modules = ["keras/backend/cntk_backend.py",
    #                    "keras/backend/tensorflow_backend.py",
    #                    "keras/backend/theano_backend.py",
    #                    "keras/layers/convolutional.py",
    #                    "keras/utils/conv_utils.py"]
    #
    # test_module_paths = list(test_suite_path.rglob("test_*.py")) + list(test_suite_path.rglob("*_test.py"))

    source_code_packages = ["/media/moe/ext4Drive/workspace/fastapi/bug2/buggy/fastapi"]
    changed_modules = ["fastapi/routing.py"]
    test_module_paths = [
        Path("/media/moe/ext4Drive/workspace/fastapi/bug2/buggy/fastapi/tests/test_custom_route_class.py")]

    print("Number of test modules: ", len(test_module_paths))

    selected_test_modules = []
    for item in test_module_paths:
        print("Analyzing test module: ", item)
        keep_it = is_affecting_test_module(str(item.absolute().resolve()), source_code_packages, changed_modules, 10)
        if keep_it:
            selected_test_modules.append(item)

    print("Number of selected test modules: ", len(selected_test_modules))
    for item in selected_test_modules:
        print(item)


def main():
    # z = importlib.import_module("/media/moe/ext4Drive/workspace/fastapi/bug2/buggy/fastapi/tests/test_custom_route_class.py")
    # x = inspect.getfile(z)
    # print(x)

    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("fastapi",
                                                  "/media/moe/ext4Drive/workspace/fastapi/bug2/buggy/fastapi/fastapi/__init__.py")
    foo = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = foo
    spec.loader.exec_module(foo)
    x = foo.app


if __name__ == '__main__':
    # main()
    call_graph()
