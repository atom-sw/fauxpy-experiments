import ast

from fauxpy.predicate_switching import ast_manager
from tests.common import getDataPath
from fauxpy.predicate_switching.ast_manager import instrumentation


def test_instrumentOneLineIfMinimal():
    filePath = str(getDataPath("predicate_switching", "one_line_if.pyt").absolute())
    candidatePredicates = [(1, 1, "pred_1")]
    seenExceptions = []
    instFileContent = ast_manager.instrumentCurrentFilePath(filePath,
                                                            candidatePredicates,
                                                            seenExceptions)
    expectedString = "from fauxpy import fauxpy_inst\nif fauxpy_inst.wrap_pred_to_switch(not line, 'pred_1'):\n    break\n"
    assert instFileContent == expectedString


def test_instrumentNormalIfMinimal():
    filePath = str(getDataPath("predicate_switching", "normal_if.pyt").absolute())
    candidatePredicates = [(1, 1, "pred_2")]
    seenExceptions = []
    instFileContent = ast_manager.instrumentCurrentFilePath(filePath,
                                                            candidatePredicates,
                                                            seenExceptions)
    expectedString = "from fauxpy import fauxpy_inst\nif fauxpy_inst.wrap_pred_to_switch(not line, 'pred_2'):\n    raise TokenError('EOF in multi-line string', strstart)\n"
    assert instFileContent == expectedString


def test_instrumentMultilinePredicateNormalIf():
    filePath = str(getDataPath("predicate_switching", "multiline_predicate_normal_if.pyt").absolute())
    candidatePredicates = [(1, 3, "pred_3")]
    seenExceptions = []
    instFileContent = ast_manager.instrumentCurrentFilePath(filePath,
                                                            candidatePredicates,
                                                            seenExceptions)
    expectedString = """from fauxpy import fauxpy_inst
if fauxpy_inst.wrap_pred_to_switch(not line or x > 12 and y <= z, 'pred_3'):
    raise TokenError('EOF in multi-line string', strstart)
"""
    assert instFileContent == expectedString


def test_instrumentOneLineIfBlack14():
    filePath = str(getDataPath("predicate_switching", "tokenize.pyt").absolute())
    candidatePredicates = [(395, 395, "pred_20")]
    seenExceptions = []
    instFileContent = ast_manager.instrumentCurrentFilePath(filePath,
                                                            candidatePredicates,
                                                            seenExceptions)
    instrumentationString = "if fauxpy_inst.wrap_pred_to_switch(not line, 'pred_20'):"
    assert instrumentationString in instFileContent


def test_instrumentNormalIfBlack14():
    filePath = str(getDataPath("predicate_switching", "tokenize.pyt").absolute())
    candidatePredicates = [(374, 374, "pred_18")]
    seenExceptions = []
    instFileContent = ast_manager.instrumentCurrentFilePath(filePath,
                                                            candidatePredicates,
                                                            seenExceptions)
    instrumentationString = "if fauxpy_inst.wrap_pred_to_switch(not line, 'pred_18'):"
    assert instrumentationString in instFileContent


def test__addInstrumentationImport():
    filePath = str(getDataPath("predicate_switching", "future_import.py").absolute())
    with open(filePath, "r") as source:
        treeObj = ast.parse(source.read())

    instrumentation._addInstrumentationImport(treeObj)

    def isFromFuture(x) -> bool:
        if isinstance(x, ast.ImportFrom):
            return x.module == "__future__"
        return False

    for index, item in enumerate(treeObj.body):
        if isFromFuture(item):
            beforeFromFuture = list(map(isFromFuture, treeObj.body[0:index]))
            assert len(beforeFromFuture) == 0 or any(beforeFromFuture)
