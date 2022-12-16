import os
import pathlib
import shutil
import tempfile
import time
from typing import List

ProjectWorkingDirectory: str


def init():
    global ProjectWorkingDirectory

    ProjectWorkingDirectory = os.getcwd()


def _notStartsWith(exclude: List[str], path: str):
    for exld in exclude:
        absExld = str(pathlib.Path(exld).resolve())
        if path.startswith(absExld):
            return False
    return True


def pathShouldBeLocalized(src: str, exclude: List[str], path: str):
    """
    The parameter src is a relative path.
    The parameter path is an absolute path.
    """
    absSrc = relativePathToAbsPath(src)
    if path.startswith(absSrc) and _notStartsWith(exclude, path):
        return True
    else:
        return False


def relativePathToAbsPath(relPath):
    global ProjectWorkingDirectory

    absSrc = pathlib.Path(ProjectWorkingDirectory) / relPath
    return str(absSrc.resolve())


def absolutePathToRelativePath(absPath: str) -> str:
    global ProjectWorkingDirectory

    relPath = os.path.relpath(absPath, ProjectWorkingDirectory)
    return relPath


def convertArgumentListStringToList(excludeString: str) -> List[str]:
    strippedString = excludeString.strip()
    bracketsRemoved = strippedString[1:-1]
    if bracketsRemoved == "":
        return []
    else:
        items = bracketsRemoved.split(",")
        itemsStripped = [x.strip() for x in items]

        return itemsStripped


def convertListToString(listObj: List[str]) -> str:
    listContentAsStr = ",".join(listObj)
    listString = "[" + listContentAsStr + "]"
    return listString


def _getCurrentWorkingDirectory() -> str:
    return ProjectWorkingDirectory


def _getUniqueTemporaryDirectoryPath() -> str:
    tmp = tempfile.gettempdir()
    currentTimeInt = time.time()
    tmpDir = pathlib.Path(tmp) / str(currentTimeInt)
    tmpDir = str(tmpDir.resolve())
    return tmpDir


def _copyDir(source: str, destination: str):
    shutil.copytree(source, destination, symlinks=True)


def makeProjectCopyInTemp() -> str:
    tempDir = _getUniqueTemporaryDirectoryPath()
    projectDir = _getCurrentWorkingDirectory()
    _copyDir(projectDir, tempDir)

    return tempDir


def runCommand(command: List[str], workingDir: str):
    import subprocess
    print("--------------------HERE_BEGIN---------------------")
    print("Command to run: ", " ".join(command))
    execOut = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             cwd=workingDir)

    print(execOut.stdout)
    print(execOut.stderr)
    print("--------------------HERE_END---------------------")


def csvRowToList(csvRow: str) -> List[str]:
    csvComps = csvRow.split(",")
    return csvComps


def listToCsvRow(listItem: List[str]) -> str:
    csvRow = ",".join(listItem)
    return csvRow
