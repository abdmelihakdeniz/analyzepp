"""Gemini AI client and analysis orchestration."""

import os
from datetime import datetime
from typing import Any

from google import genai
from google.genai import errors

from analyzepp.config import DEFAULT_MODEL
from analyzepp.exceptions import AiApiError
from analyzepp.logger import Logger

PROMPT_TEMPLATE = """
You are an expert C++ memory debugging engineer. Produce a thorough Markdown analysis report.

## INPUT

Source file: {source_name}

Valgrind Memcheck findings:
{issues_str}

## RULES

- Use ONLY the information present in the Valgrind report.
- Do not assume access to the source code beyond what is shown.
- If the root cause cannot be determined exactly, state the most likely causes.
- Use technical English. Do NOT use emoji.
- Output MUST be valid Markdown.

## OUTPUT FORMAT

# Memory Analysis Report

## Issues (sorted by severity — Critical first)

For each distinct issue:

### N. [Severity] Kind

| Field | Detail |
|-------|--------|
| **Description** | ... |
| **Location** | `file.cpp:line` in `function()` |
| **Severity** | Critical / High / Medium / Low |
| **Leak Size** | N bytes in N blocks _(if applicable)_ |
| **Impact** | What happens at runtime (crash, slowdown, undefined behavior) |
| **Likely Cause** | ... |
| **Suggested Fix** |
```cpp
  // short code snippet showing the fix
  ```
| **Prevention Tip** | How to avoid this class of bug |

## Summary

| Metric | Value |
|--------|-------|
| **Total Issues** | N |
| **Total Leaked** | N bytes _(if applicable)_ |
| **Highest Severity** | Critical / High / Medium / Low |
| **Overall Memory Safety** | Poor / Fair / Good / Excellent |
| **Recommended Fix Order** | ... _(list issues by priority)_ |

## Notes

- Memory safety appears acceptable based on this run _(if no issues)_.
- Additional tools such as AddressSanitizer, UBSan, or clang-tidy may still reveal issues not detected by Valgrind.
"""


_MODEL_MAP: dict[str, tuple[str, str]] = {
    "pro": ("gemini-2.5-pro", "gemini-2.5-flash"),
    "flash": ("gemini-2.5-flash", "gemini-2.5-pro"),
}


def get_ai_client() -> genai.Client:
    """Initialize the Gemini AI client using the API key from the environment.

    Returns:
        A configured genai.Client instance.

    Raises:
        AiApiError: If GEMINI_API_KEY is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise AiApiError(
            "GEMINI_API_KEY environment variable is not set.\n"
            "Create a .env file from .env.example and set GEMINI_API_KEY there."
        )
    return genai.Client(api_key=api_key)


def generate_analysis(
    client: genai.Client,
    issues: list[dict[str, Any]],
    model_choice: str | None = None,
    source_name: str = "unknown.cpp",
) -> str:
    """Send Valgrind findings to Gemini AI and return a human-readable analysis.

    Falls back to a secondary model if the primary returns a 503 or 429 error.

    Args:
        client: An initialized genai.Client instance.
        issues: List of parsed Valgrind issues (from parse_valgrind_report).
        model_choice: Model preference ("flash" or "pro"). Defaults to config value.
        source_name: Name of the analyzed source file (for report context).

    Returns:
        The AI-generated analysis text.

    Raises:
        AiApiError: If all models fail or the response is empty.
    """
    Logger.info("Generating AI report...")
    issues_str = str(issues) if issues else "No memory leaks or errors detected by Valgrind."
    prompt = PROMPT_TEMPLATE.format(issues_str=issues_str, source_name=source_name)

    model_choice = model_choice or DEFAULT_MODEL
    primary_model, fallback_model = _MODEL_MAP.get(model_choice, _MODEL_MAP["flash"])

    def _generate_with_model(model_name: str) -> str:
        response = client.models.generate_content(model=model_name, contents=prompt)
        if response.text is None:
            raise AiApiError("AI returned empty response.")
        return response.text

    try:
        Logger.info(f"Sending request to primary model ({primary_model})...")
        return _generate_with_model(primary_model)
    except errors.APIError as e:
        if e.code in (503, 429):
            Logger.warn(f"Primary model failed (Code {e.code}). Switching to fallback ({fallback_model})...")
            try:
                return _generate_with_model(fallback_model)
            except errors.APIError as fallback_err:
                raise AiApiError(
                    f"Fallback model also failed (Code {fallback_err.code}): {fallback_err.message}"
                ) from fallback_err
        else:
            raise AiApiError(f"Gemini API Error (Code {e.code}): {e.message}") from e
    except AiApiError:
        raise
    except Exception as e:
        raise AiApiError(f"Unexpected connection or system error: {e}") from e


def write_report(report_text: str, report_path: str, source_file: str = "unknown.cpp", model: str = "flash") -> None:
    """Write the AI analysis report to a Markdown file with metadata header.

    Args:
        report_text: The AI-generated analysis content.
        report_path: Filesystem path for the output report.
        source_file: Name of the analyzed C++ source file.
        model: Gemini model used for analysis.

    Raises:
        OSError: If the file cannot be written.
    """
    header = (
        f"# AnalyzePP Report\n\n"
        f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"- **Source:** `{source_file}`\n"
        f"- **Model:** `gemini-2.5-{model}`\n"
        f"- **Tool:** Valgrind Memcheck\n\n"
        f"---\n\n"
    )

    with open(report_path, "w") as f:
        f.write(header)
        f.write(report_text.strip())
        f.write("\n")

    Logger.success(f"Report saved to {report_path}")
