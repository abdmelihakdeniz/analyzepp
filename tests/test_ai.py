import os
from unittest.mock import MagicMock

import pytest

from analyzepp.ai import generate_analysis, get_ai_client, write_report
from analyzepp.exceptions import AiApiError


def test_generate_analysis_no_issues(mock_ai_client: MagicMock) -> None:
    result = generate_analysis(mock_ai_client, [], "flash")
    assert result == "## CLEAN REPORT\n\nNo memory leaks detected."
    mock_ai_client.models.generate_content.assert_called_once()


def test_generate_analysis_with_issues(mock_ai_client: MagicMock) -> None:
    issues = [{"Kind": "Leak_DefinitelyLost", "Description": "test", "Function": "f", "File": "a.cpp", "Line": "5"}]
    result = generate_analysis(mock_ai_client, issues, "flash")
    assert result == "## CLEAN REPORT\n\nNo memory leaks detected."
    mock_ai_client.models.generate_content.assert_called_once()


def test_generate_analysis_model_mapping(mock_ai_client: MagicMock) -> None:
    generate_analysis(mock_ai_client, [], "pro")
    call_args = mock_ai_client.models.generate_content.call_args
    assert call_args[1]["model"] == "gemini-2.5-pro"


def test_generate_analysis_uses_correct_prompt(mock_ai_client: MagicMock) -> None:
    issues = [{"Kind": "Leak_DefinitelyLost", "Description": "100 bytes lost"}]
    generate_analysis(mock_ai_client, issues, "flash", source_name="test.cpp")
    call_args = mock_ai_client.models.generate_content.call_args
    prompt = call_args[1]["contents"]
    assert "100 bytes lost" in prompt
    assert "test.cpp" in prompt


def test_generate_analysis_default_source_name(mock_ai_client: MagicMock) -> None:
    generate_analysis(mock_ai_client, [], "flash")
    call_args = mock_ai_client.models.generate_content.call_args
    prompt = call_args[1]["contents"]
    assert "unknown.cpp" in prompt


def test_generate_analysis_api_error_fallback(mock_ai_client: MagicMock) -> None:
    from google.genai import errors

    mock_ai_client.models.generate_content.side_effect = [
        errors.APIError(503, {"error": {"message": "Service Unavailable"}}),
        MagicMock(text="Fallback response"),
    ]

    result = generate_analysis(mock_ai_client, [], "flash")
    assert result == "Fallback response"
    assert mock_ai_client.models.generate_content.call_count == 2


def test_generate_analysis_both_models_fail(mock_ai_client: MagicMock) -> None:
    from google.genai import errors

    mock_ai_client.models.generate_content.side_effect = [
        errors.APIError(503, {"error": {"message": "Service Unavailable"}}),
        errors.APIError(503, {"error": {"message": "Still unavailable"}}),
    ]

    with pytest.raises(AiApiError):
        generate_analysis(mock_ai_client, [], "flash")
    assert mock_ai_client.models.generate_content.call_count == 2


def test_get_ai_client_no_api_key() -> None:
    key = os.environ.pop("GEMINI_API_KEY", None)
    try:
        with pytest.raises(AiApiError):
            get_ai_client()
    finally:
        if key is not None:
            os.environ["GEMINI_API_KEY"] = key


def test_write_report_creates_file(tmp_path: str) -> None:
    report_path = os.path.join(str(tmp_path), "report.md")
    write_report("Analysis content", report_path, source_file="test.cpp", model="flash")

    assert os.path.exists(report_path)
    with open(report_path) as f:
        content = f.read()

    assert "# AnalyzePP Report" in content
    assert "**Source:** `test.cpp`" in content
    assert "**Model:** `gemini-2.5-flash`" in content
    assert "Analysis content" in content


def test_write_report_custom_path(tmp_path: str) -> None:
    report_path = os.path.join(str(tmp_path), "custom", "rapor.md")
    os.makedirs(os.path.dirname(report_path))
    write_report("test", report_path, source_file="a.cpp", model="pro")

    assert os.path.exists(report_path)
    with open(report_path) as f:
        content = f.read()
    assert "**Model:** `gemini-2.5-pro`" in content
