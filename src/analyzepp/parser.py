"""Valgrind XML report parser."""

import os
import xml.etree.ElementTree as ET
from typing import Any

from analyzepp.exceptions import XmlParseError
from analyzepp.logger import Logger


def _frame_text(frame: ET.Element | None, tag: str, default: str = "Unknown") -> str:
    return frame.findtext(tag, default=default) if frame is not None else default


def parse_valgrind_report(xml_path: str) -> list[dict[str, Any]]:
    """Parse a Valgrind XML report and extract memory issues.

    Args:
        xml_path: Path to the Valgrind Memcheck XML report.

    Returns:
        List of dicts with keys: Kind, Description, Function, File, Line.
        Returns an empty list if the file is missing or contains no relevant issues.

    Raises:
        XmlParseError: If the XML file exists but cannot be parsed.
    """
    Logger.info("Parsing XML report...")
    if not os.path.exists(xml_path):
        return []

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise XmlParseError(f"Failed to parse Valgrind XML report: {xml_path}") from e

    issues: list[dict[str, Any]] = []
    for error in root.findall(".//error"):
        error_kind = error.findtext("kind", default="Unknown error")
        if any(keyword in error_kind for keyword in ["Leak", "Invalid", "Uninit"]):
            description = error.findtext("what", default="No description available")
            frame = error.find(".//stack/frame")
            if frame is None:
                frame = error.find(".//frame")

            issues.append(
                {
                    "Kind": error_kind,
                    "Description": description,
                    "Function": _frame_text(frame, "fn"),
                    "File": _frame_text(frame, "file"),
                    "Line": _frame_text(frame, "line"),
                }
            )

    Logger.success(f"Found {len(issues)} potential issues.")
    return issues
