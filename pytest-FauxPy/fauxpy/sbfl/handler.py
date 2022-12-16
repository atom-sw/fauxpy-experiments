from typing import List

import coverage

from . import database, ranking_metric, covered_function
from .. import common

_Granularity: str
_Src: str
_Exclude: List[str]
_TopN: int
_Cov: coverage.Coverage
_CurrentTest: str
_TargetFailingTests: common.TargetFailingTests


def handlerConfigure(granularity, src, exclude, topN, targetFailingTests):
    global _Granularity, _Src, _Exclude, _TopN, _Cov, _TargetFailingTests

    _Granularity = granularity
    _Src = src
    _Exclude = exclude
    _TopN = int(topN)
    _TargetFailingTests = targetFailingTests
    _Cov = coverage.Coverage()
    database.init()


def handlerRuntestCall(item):
    """
    Runs before the execution of the current test.
    """

    global _Cov
    global _CurrentTest

    _CurrentTest = common.getTestName(item.location[0], item.location[1], item.location[2])
    _Cov.start()


def handlerRuntestMakereport(item, call):
    """
    Runs after the execution of the current test.
    """

    global _Cov, _CurrentTest

    if call.when == "call":
        testName = common.getTestName(item.location[0], item.location[1], item.location[2])
        if testName != _CurrentTest:
            raise Exception(f"Starting coverage for {_CurrentTest}. But closing coverage for {testName}.")
        _Cov.stop()
        covDat = _Cov.get_data()
        coveredStatements = []
        filesCov = covDat.measured_files()

        for file in filesCov:
            if common.pathShouldBeLocalized(_Src, _Exclude, file):
                lines = covDat.lines(file)
                for line in lines:
                    coveredStatements.append((file, line))
        if len(coveredStatements) == 0:
            database.insertEmptyTest(testName)
        else:
            if _Granularity == "statement":
                coveredStatementNames = [common.getStatementName(x[0], x[1]) for x in coveredStatements]
                database.insertExecutionTrace(testName, coveredStatementNames)
            elif _Granularity == "function":
                coveredFunctionNames = covered_function.getCoveredFunctionNames(coveredStatements)
                database.insertExecutionTrace(testName, coveredFunctionNames)
            else:
                raise Exception(f"Granularity {_Granularity} is not supported.")

        _Cov.erase()


def handlerTerminalSummary(terminalreporter):
    """
    Runs after the execution of all tests.
    """

    global _TargetFailingTests

    for key, value in terminalreporter.stats.items():
        if key in ["passed", "failed"]:
            for testReport in value:
                testPath = testReport.location[0]
                testLineNumber = testReport.location[1]
                testMethodName = testReport.location[2]

                target = False
                if _TargetFailingTests is not None and key == "failed":
                    target = _TargetFailingTests.isTargetTest(testPath, testMethodName)
                elif _TargetFailingTests is None and key == "failed":
                    target = True

                testName = common.getTestName(testPath, testLineNumber, testMethodName)
                database.insertTestCase(testName, key, target)

    scoreEntities = ranking_metric.computeSortedScores(_TopN)

    database.end()

    return scoreEntities
