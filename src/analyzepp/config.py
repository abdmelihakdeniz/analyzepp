"""Application configuration with environment variable overrides."""

import os

from dotenv import load_dotenv

load_dotenv()

# Compiler configuration
CXX: str = os.environ.get("ANALYZEPP_CXX", "g++")
CXX_DEBUG_FLAG: str = os.environ.get("ANALYZEPP_CXX_FLAGS", "-g")

# Valgrind configuration
VALGRIND_BIN: str = os.environ.get("ANALYZEPP_VALGRIND", "valgrind")
VALGRIND_TOOL: str = os.environ.get("ANALYZEPP_VALGRIND_TOOL", "memcheck")
VALGRIND_LEAK_CHECK: str = os.environ.get("ANALYZEPP_VALGRIND_LEAK_CHECK", "full")

# Subprocess timeout (seconds)
SUBPROCESS_TIMEOUT: int = int(os.environ.get("ANALYZEPP_TIMEOUT", "120"))

# Default AI model
DEFAULT_MODEL: str = os.environ.get("ANALYZEPP_DEFAULT_MODEL", "flash")
