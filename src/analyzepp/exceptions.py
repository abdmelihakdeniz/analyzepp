"""Custom exception hierarchy for analyzepp."""


class AnalyzeppError(Exception):
    """Base exception for all analyzepp errors."""


class CompilationError(AnalyzeppError):
    """Raised when C++ compilation fails."""


class ValgrindError(AnalyzeppError):
    """Raised when Valgrind execution fails."""


class XmlParseError(AnalyzeppError):
    """Raised when the Valgrind XML report cannot be parsed."""


class AiApiError(AnalyzeppError):
    """Raised when the Gemini AI API fails."""
