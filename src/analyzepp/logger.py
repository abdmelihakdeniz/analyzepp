"""Colored terminal logger backed by Python logging module."""

import logging
import sys
from typing import ClassVar

SUCCESS_LEVEL = 25
SECTION_LEVEL = 35
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(SECTION_LEVEL, "SECTION")


class _ColoredFormatter(logging.Formatter):
    """Format log records with ANSI color codes."""

    _COLORS: ClassVar[dict[str, str]] = {
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "SUCCESS": "\033[92m",
        "INFO": "\033[94m",
        "BOLD": "\033[1m",
        "END": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        level = record.levelname
        colors = self._COLORS

        if level == "ERROR":
            return f"{colors['ERROR']}{colors['BOLD']}[ERROR]{colors['END']} {colors['ERROR']}{msg}{colors['END']}"
        if level == "WARNING":
            return f"{colors['WARNING']}[WARNING]{colors['END']} {msg}"
        if level == "SUCCESS":
            return f"{colors['SUCCESS']}[SUCCESS]{colors['END']} {msg}"
        if level == "SECTION":
            return f"\n{colors['INFO']}{colors['BOLD']}=== {msg} ==={colors['END']}"
        return f"{colors['INFO']}[INFO]{colors['END']} {msg}"


class Logger:
    """Colored terminal logger.

    Usage:
        Logger.setup(logging.DEBUG)  # optional, INFO is default
        Logger.info("message")
        Logger.success("message")
        Logger.warn("message")
        Logger.error("message")
        Logger.section("title")
    """

    _logger: logging.Logger = logging.getLogger("analyzepp")
    _is_setup: bool = False

    @classmethod
    def setup(cls, level: int = logging.INFO) -> None:
        """Configure the logger once."""
        if cls._is_setup:
            return
        cls._is_setup = True
        cls._logger.setLevel(level)
        cls._logger.handlers.clear()
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(_ColoredFormatter())
        cls._logger.addHandler(handler)

    @classmethod
    def set_level(cls, level: int) -> None:
        """Change the logging level at runtime."""
        cls._logger.setLevel(level)

    @classmethod
    def error(cls, message: str) -> None:
        cls._logger.error(message)

    @classmethod
    def success(cls, message: str) -> None:
        cls._logger.log(SUCCESS_LEVEL, message)

    @classmethod
    def warn(cls, message: str) -> None:
        cls._logger.warning(message)

    @classmethod
    def info(cls, message: str) -> None:
        cls._logger.info(message)

    @classmethod
    def section(cls, title: str) -> None:
        cls._logger.log(SECTION_LEVEL, title)
