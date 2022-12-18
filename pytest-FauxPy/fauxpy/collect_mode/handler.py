from enum import Enum
from typing import List

from . import database, report
from .. import common


class CollectMode(Enum):
    MBFL = 1
    PSINFO = 2
    PSRUN = 3


_Src: str
_Exclude: List[str]
_Family: str
_CurrentTest: str


def handlerConfigure(src, exclude, family):
    global _Src
    global _Exclude
    global _Family

    _Src = src
    _Exclude = exclude

    if family == "collectmbfl":
        _Family = CollectMode.MBFL
    elif family == "collectpsinfo":
        _Family = CollectMode.PSINFO
    elif family == "collectpsrun":
        _Family = CollectMode.PSRUN

    database.init()


def handlerRuntestCall(item):
    """
    Runs before the execution of the current test.
    """

    global _CurrentTest

    if _Family in [CollectMode.PSINFO, CollectMode.PSRUN]:
        _CurrentTest = common.getTestName(item.location[0], item.location[1], item.location[2])


def handlerRuntestMakereport(item, call):
    """
    Runs after the execution of the current test.
    """

    if call.when == "call":
        if _Family in [CollectMode.PSINFO, CollectMode.PSRUN]:

            testName = common.getTestName(item.location[0], item.location[1], item.location[2])
            if testName != _CurrentTest:
                raise Exception(f"Starting coverage for {_CurrentTest}. But closing coverage for {testName}.")

            if _Family == CollectMode.PSINFO:
                predicateSequence = common.loadInCollectModeExecutedPredicateSequenceAndRemoveFile()
                if predicateSequence is not None:
                    database.insertPredicateSequence(testName, predicateSequence)

            if _Family == CollectMode.PSRUN:
                seenExceptionsSequence = common.loadInCollectModeSeenExceptionSequenceAndRemoveFile()
                if seenExceptionsSequence is not None:
                    database.insertSeenExceptionSequence(testName, seenExceptionsSequence)

                common.inCollectModeRemoveEvaluationCounterFile()


def handlerTerminalSummary(terminalreporter):
    """
    Runs after the execution of all tests.
    """

    if _Family in [CollectMode.MBFL, CollectMode.PSRUN]:
        for key, value in terminalreporter.stats.items():
            if key in ["passed", "failed"]:
                for testReport in value:
                    testName = common.getTestName(testReport.location[0], testReport.location[1],
                                                  testReport.location[2])
                    testTraceBack = ""
                    timeoutStat = -1
                    if key == "failed":
                        reprTraceback = testReport.longrepr.reprtraceback
                        testTraceBack = common.getShortTraceBackInfo(reprTraceback)
                        # TODO: probably not needed anymore as --timeout_method is set to thread
                        if common.hasTimeoutHappened(testReport.longreprtext):
                            timeoutStat = 1

                    database.insertTestCase(testName=testName, testType=key, shortTraceback=testTraceBack,
                                            timeoutStat=timeoutStat)

        report.saveTestCases()

    if _Family == CollectMode.PSINFO:
        report.saveTestPredicateSequenceTable()

    if _Family == CollectMode.PSRUN:
        report.saveSeenExceptionSequenceTable()

    database.end()

    return {"Default": []}
