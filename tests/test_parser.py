import os
import tempfile
import xml.etree.ElementTree as ET

import pytest

from analyzepp.exceptions import XmlParseError
from analyzepp.parser import parse_valgrind_report


def test_parse_valgrind_report_returns_issues(sample_valgrind_xml: str) -> None:
    issues = parse_valgrind_report(sample_valgrind_xml)

    assert len(issues) == 2
    assert issues[0]["Kind"] == "Leak_DefinitelyLost"
    assert issues[0]["Description"] == "100 bytes in 1 blocks are definitely lost in loss record 1 of 1"
    assert issues[0]["Function"] == "leakFunction()"
    assert issues[0]["File"] == "test.cpp"
    assert issues[0]["Line"] == "5"

    assert issues[1]["Kind"] == "InvalidWrite"
    assert issues[1]["Function"] == "main"
    assert issues[1]["File"] == "test.cpp"
    assert issues[1]["Line"] == "11"


def test_parse_valgrind_report_missing_file(tmp_path: str) -> None:
    missing = str(tmp_path) + "/nonexistent.xml"
    issues = parse_valgrind_report(missing)
    assert issues == []


def test_parse_valgrind_report_invalid_xml(tmp_path: str) -> None:
    bad_file = str(tmp_path) + "/bad.xml"
    with open(bad_file, "w") as f:
        f.write("not xml content")

    with pytest.raises(XmlParseError):
        parse_valgrind_report(bad_file)


def test_parse_valgrind_report_empty(sample_valgrind_xml: str) -> None:
    tree = ET.parse(sample_valgrind_xml)
    root = tree.getroot()
    for error in root.findall(".//error"):
        kind_el = error.find("kind")
        if kind_el is not None and kind_el.text in ("Leak_DefinitelyLost", "InvalidWrite"):
            kind_el.text = "SomeOtherKind"

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="wb") as f:
        tree.write(f.name)
        modified_path = f.name

    try:
        issues = parse_valgrind_report(modified_path)
        assert issues == []
    finally:
        os.unlink(modified_path)
