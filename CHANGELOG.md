# Changelog

## [0.1.0] - 2025-06-18

### Added
- C++ compilation with `g++ -g` and Valgrind Memcheck execution.
- XML report parsing for memory leaks, invalid writes, and uninitialized values.
- AI-powered analysis via Google Gemini (`flash` / `pro`) with automatic model fallback.
- Colored terminal logger with `--verbose` / `--quiet` flags.
- `--version` CLI flag.
- Test suite: 17 tests (pytest), ruff linting, mypy type checking.
- Pre-commit hooks and GitHub Actions CI.
- `.editorconfig`, `LICENSE` (MIT), `CHANGELOG.md`.
- Modular architecture: `cli`, `logger`, `config`, `valgrind`, `parser`, `ai`.
- Environment variable configuration (`ANALYZEPP_*`, `GEMINI_API_KEY`).
- `uv` and `pip install` support via PEP 517 packaging.
