from typing import Tuple


def _quoteFreeTestMethodName(methodName: str):
    qftm = methodName.replace("'", "XquoteX").replace('"', "XdoubleQuoteX")
    return qftm


def getTestName(path: str, lineNumber: int, methodName: str):
    testName = path + "::" + str(lineNumber) + "::" + _quoteFreeTestMethodName(methodName)
    return testName


def convertTestNameToComponents(testName: str) -> Tuple[str, int, str]:
    components = testName.split("::")
    return components[0], int(components[1]), components[2]


def getStatementName(path: str, lineNumber: int):
    statementName = path + "::" + str(lineNumber)
    return statementName


def convertStatementNameToComponents(statementName: str) -> Tuple[str, int]:
    components = statementName.split("::")
    return components[0], int(components[1])


def getCoveredFunctionName(path: str, functionName: str, lineStart: int, lineEnd: int):
    covFuncName = path + "::" + functionName + "::" + str(lineStart) + "::" + str(lineEnd)
    return covFuncName


def testNameToFileName(testName: str):
    qftm = testName.replace("/", "_").replace("/", "_").replace(":", "_")
    return qftm
