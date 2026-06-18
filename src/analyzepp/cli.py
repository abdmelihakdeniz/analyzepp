import argparse
import logging
import os
import shutil
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from analyzepp.ai import generate_analysis, get_ai_client, write_report
from analyzepp.exceptions import AnalyzeppError
from analyzepp.logger import Logger
from analyzepp.parser import parse_valgrind_report
from analyzepp.runner import compile_cpp, run_valgrind


def _get_version() -> str:
    try:
        return version("analyzepp")
    except PackageNotFoundError:
        return "0.1.0"


def _resolve_log_level(args: argparse.Namespace) -> int:
    if args.verbose:
        return logging.DEBUG
    if args.quiet:
        return logging.WARNING
    return logging.INFO


def _check_environment() -> None:
    """Verify that the host OS and required tools are available.

    Raises:
        AnalyzeppError: If the environment is not supported.
    """
    if not sys.platform.startswith("linux"):
        raise AnalyzeppError(
            f"analyzepp currently supports Linux only (detected: {sys.platform})"
        )

    missing = []
    if not shutil.which("g++"):
        missing.append("g++")
    if not shutil.which("valgrind"):
        missing.append("valgrind")

    if missing:
        raise AnalyzeppError(
            "Required tools not found in PATH: " + ", ".join(missing)
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="C++ performance and memory leak analyzer",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_get_version()}")
    parser.add_argument("-f", "--file", required=True, help="Path to the C++ source file")
    parser.add_argument("-o", "--output", default="tempbin", help="Name of the compiled binary")
    parser.add_argument("--keep", action="store_true", help="Keep generated binary and XML report")
    parser.add_argument(
        "-m", "--model", choices=["flash", "pro"], default="flash", help="Gemini model choice (default: flash)"
    )
    parser.add_argument("-r", "--report", nargs="?", const="report.md", default=None,
                        help="Save AI analysis report to a Markdown file (default: report.md)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (debug) output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress informational output")

    args = parser.parse_args()

    Logger.setup(_resolve_log_level(args))

    _check_environment()

    binary_file = args.output
    report_file = f"{binary_file}_report.xml"

    if not os.path.exists(args.file):
        Logger.error(f"No such file: {args.file}")
        sys.exit(1)

    source_name = Path(args.file).name
    client = get_ai_client()

    try:
        compile_cpp(args.file, binary_file)
        run_valgrind(binary_file, report_file)
        findings = parse_valgrind_report(report_file)
        ai_report = generate_analysis(client, findings, args.model, source_name=source_name)

        Logger.section("AI ANALYSIS REPORT")
        print(ai_report.strip())
        print(f"\033[96m\033[1m{'=' * 50}\033[0m")

        if args.report:
            write_report(ai_report, args.report, source_file=source_name, model=args.model)

    except AnalyzeppError as e:
        Logger.error(str(e))
        sys.exit(1)

    finally:
        if not args.keep:
            for file in [binary_file, report_file]:
                path = Path(file)
                if path.exists():
                    path.unlink()
            Logger.info("Temporary files removed. Cleanup done.")
        else:
            Logger.info(f"Kept files: {binary_file} and {report_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        Logger.warn("Operation cancelled by user. Exiting...")
        sys.exit(0)
