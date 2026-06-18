import os
import shutil

import pytest

from analyzepp.exceptions import CompilationError, ValgrindError
from analyzepp.runner import compile_cpp, run_valgrind

valgrind_available = shutil.which("valgrind") is not None


def test_compile_cpp_creates_binary(tmp_path: str) -> None:
    source = os.path.join(os.path.dirname(__file__), "..", "test.cpp")
    binary = os.path.join(str(tmp_path), "testbin")

    compile_cpp(source, binary)

    assert os.path.exists(binary)


def test_compile_cpp_fails_on_missing_file(tmp_path: str) -> None:
    missing = os.path.join(str(tmp_path), "nonexistent.cpp")
    binary = os.path.join(str(tmp_path), "testbin")

    with pytest.raises(CompilationError):
        compile_cpp(missing, binary)


@pytest.mark.skipif(not valgrind_available, reason="valgrind not installed")
def test_run_valgrind_creates_xml(tmp_path: str) -> None:
    source = os.path.join(os.path.dirname(__file__), "..", "test.cpp")
    binary = os.path.join(str(tmp_path), "testbin")
    xml_out = os.path.join(str(tmp_path), "report.xml")

    compile_cpp(source, binary)
    run_valgrind(binary, xml_out)

    assert os.path.exists(xml_out)


def test_run_valgrind_tool_not_found(tmp_path: str) -> None:
    with pytest.raises(ValgrindError):
        run_valgrind("nonexistent_binary", str(tmp_path) + "/out.xml")
