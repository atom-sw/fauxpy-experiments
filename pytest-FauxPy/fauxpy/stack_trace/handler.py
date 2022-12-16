from typing import List

from _pytest._code.code import ReprTraceback

from . import parse, ranking, database
from .. import common

_Src: str
_Exclude: List[str]
_TopN: int
_CurrentTest: str
_TargetFailingTests: common.TargetFailingTests


def handlerConfigure(src, exclude, topN, targetFailingTests):
    global _Src, _Exclude, _TopN, _TargetFailingTests

    _Src = src
    _Exclude = exclude
    _TopN = int(topN)
    _TargetFailingTests = targetFailingTests
    database.init()


def handlerRuntestCall(item):
    """
    Runs before the execution of the current test.
    """

    global _CurrentTest
    _CurrentTest = common.getTestName(item.location[0], item.location[1], item.location[2])


def handlerRuntestMakereport(item, call):
    """
    Runs after the execution of the current test.
    """

    global _CurrentTest

    if call.when == "call":
        testName = common.getTestName(item.location[0], item.location[1], item.location[2])
        if testName != _CurrentTest:
            raise Exception(f"Starting coverage for {_CurrentTest}. But closing coverage for {testName}.")


def handlerTerminalSummary(terminalreporter):
    """
    Runs after the execution of all tests.
    """
    global _Src, _Exclude, _TargetFailingTests

    for key, value in terminalreporter.stats.items():
        if key in ["failed"]:
            for testReport in value:
                testPath = testReport.location[0]
                testLineNumber = testReport.location[1]
                testMethodName = testReport.location[2]

                if ((_TargetFailingTests is not None and _TargetFailingTests.isTargetTest(testPath, testMethodName))
                        or _TargetFailingTests is None):
                    currentTest = common.getTestName(testPath, testLineNumber, testMethodName)
                    reprTraceback: ReprTraceback = testReport.longrepr.reprtraceback
                    tracebackFunctionNames = parse.getOrderedTracebackFunctionNames(_Src, _Exclude, reprTraceback)
                    currentTestScores = ranking.computeScores(tracebackFunctionNames)
                    database.insertTracebackScores(currentTest, currentTestScores)

    scores = ranking.getSortedScores(_TopN)

    database.end()

    return {"default": scores}
