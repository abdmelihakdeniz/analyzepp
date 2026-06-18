import logging

from analyzepp.logger import SECTION_LEVEL, SUCCESS_LEVEL, Logger


def test_logger_methods_exist() -> None:
    Logger.setup(logging.WARNING)
    assert hasattr(Logger, "error")
    assert hasattr(Logger, "success")
    assert hasattr(Logger, "warn")
    assert hasattr(Logger, "info")
    assert hasattr(Logger, "section")
    assert hasattr(Logger, "set_level")


def test_logger_levels() -> None:
    assert SUCCESS_LEVEL == 25
    assert SECTION_LEVEL == 35
    assert logging.getLevelName(SUCCESS_LEVEL) == "SUCCESS"
    assert logging.getLevelName(SECTION_LEVEL) == "SECTION"


def test_logger_set_level() -> None:
    Logger.setup(logging.DEBUG)
    Logger.set_level(logging.ERROR)
    assert Logger._logger.level == logging.ERROR
