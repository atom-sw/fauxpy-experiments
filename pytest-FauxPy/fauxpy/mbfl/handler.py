from typing import List

import coverage
# from fauxpy import program_tracer

from . import database, mutation, runner, mutant_score, entity_score
from .. import common

_Granularity: str
_Src: str
_Exclude: List[str]
_TopN: int
_Cov: coverage.Coverage
_CurrentTest: str
_FileOrDir: List[str]
_TargetFailingTests: common.TargetFailingTests

_CurrentTestTimer = common.Timer()


def handlerConfigure(granularity, src, exclude, topN, fileOrDir, targetFailingTests):
    global _Granularity, _Src, _Exclude, _TopN, _FileOrDir, _TargetFailingTests
    global _Cov

    _Granularity = granularity
    _Src = src
    _Exclude = exclude
    _TopN = int(topN)
    _Cov = coverage.Coverage()
    _FileOrDir = fileOrDir
    _TargetFailingTests = targetFailingTests
    database.init()


def handlerRuntestCall(item):
    """
    Runs before the execution of the current test.
    """

    global _Cov
    global _CurrentTest

    _CurrentTestTimer.startTimer()

    _CurrentTest = common.getTestName(item.location[0], item.location[1], item.location[2])
    # program_tracer.start(isWanted=lambda x: common.pathShouldBeLocalized(_Src, _Exclude, x))
    _Cov.start()


def handlerRuntestMakereport(item, call):
    """
    Runs after the execution of the current test.
    """

    global _Cov
    global _CurrentTest

    # TODO: Replace custom tracer with coverage library (commented code). Coverage tool does not
    #  work on cookiecutter project. Not found the reason. Probably timeout is the problem
    #  and the project having only one mutant. Increasing the
    #  timeout solved the problem for now.

    if call.when == "call":
        testName = common.getTestName(item.location[0], item.location[1], item.location[2])
        if testName != _CurrentTest:
            raise Exception(f"Starting coverage for {_CurrentTest}. But closing coverage for {testName}.")

        # program_tracer.stop()
        # executionTrace = program_tracer.getExecutionTrace()
        # executedLines = executionTrace.getExecutedLinesNoOrder()
        # if len(executedLines) == 0:
        #     database.insertEmptyTest(testName)
        # else:
        #     coveredStatementNames = [common.getStatementName(x[0], x[1]) for x in executedLines]
        #     database.insertExecutionTrace(testName, coveredStatementNames)

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
            coveredStatementNames = [common.getStatementName(x[0], x[1]) for x in coveredStatements]
            database.insertExecutionTrace(testName, coveredStatementNames)
        _Cov.erase()

        # # Lets give more time to mutants by putting these lines after
        currentTestTime = _CurrentTestTimer.endTimer()
        database.insertTestTime(testName, currentTestTime)


def handlerTerminalSummary(terminalreporter):
    """
    Runs after the execution of all tests.
    """

    for key, value in terminalreporter.stats.items():
        if key in ["passed", "failed"]:
            for testReport in value:
                testPath = testReport.location[0]
                testLineNumber = testReport.location[1]
                testMethodName = testReport.location[2]
                testName = common.getTestName(testPath, testLineNumber, testMethodName)
                testTraceBack = ""
                timeoutStat = -1
                target = False
                if key == "failed":
                    if _TargetFailingTests is not None:
                        target = _TargetFailingTests.isTargetTest(testPath, testMethodName)
                    elif _TargetFailingTests is None:
                        target = True
                    reprTraceback = testReport.longrepr.reprtraceback
                    testTraceBack = common.getShortTraceBackInfo(reprTraceback)
                    if common.hasTimeoutHappened(testReport.longreprtext):
                        timeoutStat = 1

                database.insertTestCaseRun(testName, key, testTraceBack, timeoutStat, target)

    failingLineNumbers = database.selectDistinctLineNumbersCoveredByFailingTests()
    mutants = mutation.getAllMutantsForFailingLineNumbers(failingLineNumbers)

    # Storing mutants for possible further analysis (can be removed)
    for mutant in mutants:
        database.insertMutant(mutant.getId(),
                              mutant.getModulePath(),
                              mutant.getLineNumber(),
                              mutant.getModuleOperator(),
                              mutant.getModuleDiffAsText(),
                              mutant.getStartPos(),
                              mutant.getEndPos())

    # TODO: Get time from passing tests and target failing tests.
    maxTestTime = database.selectMaxTestTime()
    timeoutLimit = common.getTimeout(maxTestTime)
    numPassed, numFailed = database.selectNumberOfTests()
    numAllTests = numPassed + numFailed
    processTimeout = common.getProcessTimeout(numAllTests, timeoutLimit)
    runner.runAllMutantsStoreDb(mutants, _FileOrDir, _Granularity, _Src, _Exclude, timeoutLimit, _TargetFailingTests, numAllTests, processTimeout)
    mutant_score.computeMutantScoresStoreDb()
    entityScores = entity_score.computeEntityScoresStoreDb(_TopN)

    database.end()
    return entityScores
