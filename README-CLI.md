# agentic-tdd — CLI Installation & Usage Guide

> **Package version:** 0.1.0  
> **Pipeline version:** v0.3.3  
> **Entrypoint:** `agentic-tdd`

---

## Overview

`agentic-tdd` is the globally-installable CLI that drives the **8-pass AI factory pipeline**. Once installed, any developer can run it from any project root without manually invoking `python src/pipeline_v3_1.py`.

The CLI is CWD-aware: it always executes `opencode` in the directory from which you invoked `agentic-tdd`, picks up `.env` from there, and resolves all file paths relative to that location — regardless of where the package is installed.

---

## Installation

### Option A — `pipx` (recommended for global, isolated install)

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Clone the repo (or cd into your local copy)
git clone https://github.com/Digital-Assistant/ai-factory-setup.git
cd ai-factory-setup

# Install the CLI globally in its own virtualenv
pipx install .
```

After install, `agentic-tdd` is on your `PATH` permanently. Upgrades:

```bash
pipx upgrade agentic-tdd
```

### Option B — `pip install -e .` (editable dev install)

```bash
# Inside your active virtualenv or venv
pip install -e .

# Verify
agentic-tdd --help
```

Editable mode means any local edits to `src/agentic_tdd/cli.py` are reflected immediately without reinstalling.

---

## Prerequisites

Before running the pipeline, ensure:

| Requirement | How to get it |
|---|---|
| Python ≥ 3.11 | [python.org](https://www.python.org) |
| `opencode` CLI | `npm install -g opencode-ai` |
| `OPENROUTER_API_KEY` | Add to `.env` in your project root |
| `git` initialised | `git init` in your project directory |
| Agent files | `.opencode/agent/*.md` in your project |

---

## Usage

```
agentic-tdd INPUT_SOURCE [options]
```

### Positional argument

| Argument | Description |
|---|---|
| `INPUT_SOURCE` | The pipeline input. Meaning depends on `--source-type` (default: a file path). |

### Options

| Flag | Default | Description |
|---|---|---|
| `--source-type TYPE` | `file` | How to interpret `INPUT_SOURCE`. Choices: `file` \| `string` \| `github`. |
| `--test-cmd CMD` | auto-inferred | Shell command to run the test suite after each guarded pass. |
| `--skip-hitl` | `false` | Skip the human approval gate after Pass 0 (for CI/CD). |
| `--issue REF` | — | Issue ref (e.g. `123` or `PAY-404`) to auto-create a feature branch. |
| `--base-branch NAME` | — | Base branch for auto-branching (bypasses the `main` guardrail). |
| `--log-level LEVEL` | `INFO` | Logging verbosity. Choices: `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL`. |

---

## Examples

### Run the full pipeline against a Python file

```bash
cd /path/to/my-project
agentic-tdd src/calculator.py
```

### Skip the HITL gate (CI mode)

```bash
agentic-tdd src/calculator.py --skip-hitl
```

### Custom test command

```bash
agentic-tdd src/calculator.py --test-cmd "pytest tests/ -k calculator -x -v"
```

### Auto-create a feature branch from an issue reference

```bash
# branches from HEAD (must not be `main`)
agentic-tdd src/payments.py --issue "PAY-404"

# branch from a specific base, bypassing the main guardrail
agentic-tdd src/payments.py --issue "PAY-404" --base-branch dev
```

### Enable debug logging

```bash
agentic-tdd src/calculator.py --log-level DEBUG
```

### Future: string or GitHub issue input *(not yet implemented)*

```bash
# Placeholder — will materialise the feature description as a temp file
agentic-tdd "Add OAuth2 login flow" --source-type string

# Placeholder — will fetch the issue body via the GitHub API
agentic-tdd https://github.com/org/repo/issues/42 --source-type github
```

---

## The 8-Pass Pipeline

```
Pass 0  Design & Architecture   ->  design.mmd + spec.gherkin  [HITL gate]
Pass 1  Contracts & Types       ->  type stubs in target file
Pass 2  TDD Test Generation     ->  test file                   [Red Phase]
Pass 3  Core Implementation     ->  logic                       [Green Phase + SC]
Pass 4  Refactor & Optimise     ->  complexity/DRY              [SC]
Pass 5  Security Hardening      ->  OWASP Top-10               [SC]
Pass 6  Observability & Logs    ->  logging + error classes     [SC]
Pass 7  Documentation           ->  docstrings + @see links

SC   = Self-correction loop (max 2 retries, then abort with diagnostics)
HITL = Human-in-the-Loop review gate
```

Each guarded pass (3–6) automatically runs your test suite and retries up to 2 times if tests fail. Every pass produces an **atomic git commit**, so you can `git revert` a single step if something goes wrong.

---

## Package Structure

```
ai-factory-setup/
├── src/
│   └── agentic_tdd/
│       ├── __init__.py       # Package marker; exports __version__
│       └── cli.py            # All pipeline logic + argparse entrypoint
├── pyproject.toml            # Build system (hatchling) + project metadata
├── README.md                 # Project overview
└── README-CLI.md             # This file — install & usage guide
```

---

## Development

```bash
# Clone and install in editable mode
git clone https://github.com/Digital-Assistant/ai-factory-setup.git
cd ai-factory-setup
pip install -e ".[dev]"

# Run the test suite
pytest

# Verify the CLI is wired correctly
agentic-tdd --help
```

---

## Uninstall

```bash
# pipx
pipx uninstall agentic-tdd

# pip
pip uninstall agentic-tdd
```
