from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from analyzepp.parser import parse_valgrind_report

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


@pytest.fixture
def sample_valgrind_xml() -> str:
    return str(SAMPLES_DIR / "valgrind_report.xml")


@pytest.fixture
def parsed_findings() -> list[dict[str, Any]]:
    xml_path = SAMPLES_DIR / "valgrind_report.xml"
    return parse_valgrind_report(str(xml_path))


@pytest.fixture
def mock_ai_client() -> MagicMock:
    client = MagicMock()
    response = MagicMock()
    response.text = "## CLEAN REPORT\n\nNo memory leaks detected."
    client.models.generate_content.return_value = response
    return client
