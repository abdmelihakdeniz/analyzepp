# AnalyzePP

`analyzepp` is an intelligent CLI tool that compiles C++ files, executes them under **Valgrind Memcheck** for dynamic runtime analysis, parses the generated XML diagnostic logs, and leverages **Google Gemini AI** to produce concise memory and performance reviews.

## Requirements

- **Python >= 3.12**
- **uv** (recommended) or **pip**
- **g++** (GNU C++ compiler)
- **Valgrind** (for dynamic memory analysis)
- **Gemini API Key** (get one at [Google AI Studio](https://aistudio.google.com/apikey))

## Installation

### With uv

```bash
uv sync
```

### With pip

```bash
pip install .
```

## .env Setup

Create a local `.env` file to store your Gemini API credentials safely:

```bash
cp .env.example .env
```

Open the newly created `.env` file and insert your API key:

```bash
GEMINI_API_KEY=AIzaSyYourRealGeminiApiKeyHere...
```

> **Security Warning:** Never share this file or commit it to version control.

## Usage

### Run directly with uv (no install needed)

```bash
uv run python -m analyzepp -f path/to/file.cpp
```

### Run after pip install

```bash
analyzepp -f path/to/file.cpp
```

### Arguments

| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `--file` | `-f` | *(required)* | Path to the target `.cpp` source file |
| `--output` | `-o` | `tempbin` | Name of the compiled binary |
| `--model` | `-m` | `flash` | Gemini model: `flash` or `pro` |
| `--report` | `-r` | *(optional)* | Save the AI analysis to a Markdown file (e.g. `-r report.md`) |
| `--keep` | — | `False` | Preserve binary and Valgrind XML after analysis |
| `--verbose` | `-v` | `False` | Enable debug-level log output |
| `--quiet` | `-q` | `False` | Suppress informational log output |

### Examples

```bash
# Basic analysis
analyzepp -f test.cpp

# Use Pro model, keep temp files, save a Markdown report
analyzepp -f test.cpp -m flash --keep -r report.md
```
