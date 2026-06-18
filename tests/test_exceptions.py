from analyzepp.exceptions import (
    AiApiError,
    AnalyzeppError,
    CompilationError,
    ValgrindError,
    XmlParseError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(CompilationError, AnalyzeppError)
    assert issubclass(ValgrindError, AnalyzeppError)
    assert issubclass(XmlParseError, AnalyzeppError)
    assert issubclass(AiApiError, AnalyzeppError)
    assert issubclass(AnalyzeppError, Exception)


def test_exception_message() -> None:
    err = CompilationError("test message")
    assert str(err) == "test message"
