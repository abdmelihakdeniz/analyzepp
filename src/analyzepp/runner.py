"""C++ compilation and Valgrind execution."""

import os
import subprocess

from analyzepp.config import CXX, CXX_DEBUG_FLAG, SUBPROCESS_TIMEOUT, VALGRIND_BIN, VALGRIND_LEAK_CHECK, VALGRIND_TOOL
from analyzepp.exceptions import CompilationError, ValgrindError
from analyzepp.logger import Logger


def compile_cpp(source_file: str, binary_output: str) -> None:
    """Compile a C++ source file with debug symbols.

    Args:
        source_file: Path to the C++ source file.
        binary_output: Desired path for the compiled binary.

    Raises:
        CompilationError: If compilation fails or g++ is not found.
    """
    Logger.info(f"Compiling {source_file}...")
    command = [CXX, CXX_DEBUG_FLAG, source_file, "-o", binary_output]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        raise CompilationError(f"Compilation timed out after {SUBPROCESS_TIMEOUT} seconds.") from e
    except FileNotFoundError as e:
        raise CompilationError(f"{CXX} not found. Please install g++ and ensure it is in your PATH.") from e

    if result.returncode != 0:
        raise CompilationError(f"Compilation failed:\n{result.stderr}")
    Logger.success("Compilation completed successfully.")


def run_valgrind(binary_path: str, xml_output: str) -> None:
    """Run Valgrind Memcheck on a binary and produce an XML report.

    Args:
        binary_path: Path to the compiled binary.
        xml_output: Desired path for the Valgrind XML report.

    Raises:
        ValgrindError: If Valgrind fails or is not found.
    """
    Logger.info(f"Running Valgrind on {binary_path}...")
    binary_arg = binary_path if os.sep in binary_path else f"./{binary_path}"
    command = [
        VALGRIND_BIN,
        f"--tool={VALGRIND_TOOL}",
        f"--leak-check={VALGRIND_LEAK_CHECK}",
        "--xml=yes",
        f"--xml-file={xml_output}",
        binary_arg,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        raise ValgrindError(f"Valgrind timed out after {SUBPROCESS_TIMEOUT} seconds.") from e
    except FileNotFoundError as e:
        raise ValgrindError(f"{VALGRIND_BIN} not found. Please install valgrind and ensure it is in your PATH.") from e

    if not os.path.exists(xml_output):
        detail = result.stderr or ""
        raise ValgrindError(f"Valgrind did not generate an XML report.\n{detail}")
    Logger.success(f"Analysis completed. Report saved to {xml_output}.")
