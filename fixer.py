import shutil
import sys
from pathlib import Path


def httpie_fixer():
    file_name = "pytest.ini"
    pytest_ini = Path(file_name)

    if pytest_ini.exists():
        shutil.copy(file_name, f"{file_name}.bak")
        with pytest_ini.open() as file:
            oldLines = file.readlines()

        newLines = []
        for line in oldLines:
            if "--tb=native" in line and not line.strip().startswith("#"):
                newLines.append(f"# {line}")
            else:
                newLines.append(line)

        with open(file_name, "w") as file:
            file.writelines(newLines)


def main():
    benchmark_name = sys.argv[1]
    if benchmark_name == "httpie":
        httpie_fixer()
