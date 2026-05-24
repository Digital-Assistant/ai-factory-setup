#!/usr/bin/env python3
"""
agentic_tdd.cli -- v0.3.3 AI Factory Pipeline Orchestrator
===========================================================

Packaged as a globally-installable CLI tool: ``agentic-tdd``.

Install
-------
  pipx install .                  # globally, in isolation (recommended)
  pip install -e .                # editable dev install

Invoke
------
  agentic-tdd path/to/feature.md            # default: --source-type file
  agentic-tdd path/to/src/calculator.py --source-type file
  agentic-tdd "Add OAuth2 login" --source-type string    # (placeholder)
  agentic-tdd https://github.com/org/repo/issues/42 --source-type github  # (placeholder)

Changes from v0.3.1
-------------------
  - Moved into installable Python package ``agentic_tdd``
  - Entrypoint: ``agentic_tdd.cli:main`` (mapped to ``agentic-tdd`` command)
  - New positional argument ``input_source`` replaces ``target_file``
  - New ``--source-type`` flag: file | string | github (extensible)
  - All subprocess calls execute inside ``os.getcwd()`` (the caller's project
    root), not the directory where the package is installed
  - Logging, git-branching, and self-correction logic unchanged

Three cost-critical invariants (unchanged)
------------------------------------------
  1. "Static Prefix"     -- locked --file order maximises cache hits
  2. "Context Compaction"-- error logs deleted the moment tests pass
  3. "Single-Model Lock" -- model declared in agent YAML, never overridden

State machine
-------------
  Pass 0  Design & Architecture  -> design.mmd + spec.gherkin  [HITL gate]
  Pass 1  Contracts & Types      -> type stubs in target file
  Pass 2  TDD Test Generation    -> test file                   [Red Phase]
  Pass 3  Core Implementation    -> logic                       [Green Phase + SC]
  Pass 4  Refactor & Optimise    -> complexity/DRY              [SC]
  Pass 5  Security Hardening     -> OWASP Top-10                [SC]
  Pass 6  Observability & Logs   -> logging + error classes     [SC]
  Pass 7  Documentation          -> docstrings + @see links

  [SC]   = Self-correction loop (max 2 retries, then abort)
  [HITL] = Human-in-the-Loop review gate

Prerequisites
-------------
  - opencode CLI on $PATH  (npm install -g opencode-ai)
  - OPENROUTER_API_KEY in .env or exported to the shell
  - Agent files present in .opencode/agent/
  - git initialised in the working directory
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIPELINE_VERSION = "0.3.3"
logger = logging.getLogger(__name__)

OPENCODE_CMD = "opencode"

MAX_CORRECTION_RETRIES = 2

AGENTS: dict[int, str] = {
    0: "pass-0-design-agent",
    1: "pass-1-contracts-agent",
    2: "pass-2-test-generation-agent",
    3: "pass-3-core-implementation-agent",
    4: "pass-4-refactor-agent",
    5: "pass-5-security-agent",
    6: "pass-6-observability-agent",
    7: "pass-7-documentation-agent",
}

PASS_LABELS: dict[int, str] = {
    0: "Design & Architecture",
    1: "Contracts & Types",
    2: "Test Generation (Red Phase)",
    3: "Core Implementation (Green Phase)",
    4: "Refactor & Optimise",
    5: "Security Hardening",
    6: "Observability & Logging",
    7: "Documentation",
}

_W = 68

# ---------------------------------------------------------------------------
# Static Prefix -- Immutable File Ordering
# ---------------------------------------------------------------------------
#
# THE RULE: The `--file` arguments appended to every `opencode run` invocation
# MUST appear in a hardcoded, unchanging sequence.  Never re-order them.
#
# File ordering:
#   - design.mmd          -- FIRST, immutable architectural source of truth
#   - spec.gherkin        -- SECOND, immutable behavioural specification
#   - target source       -- THIRD, the file being modified (can change)
#   - .opencode_error.log -- OPTIONAL, only during self-correction retries
# ---------------------------------------------------------------------------

# Canonical artefact filenames -- hardcoded so the orchestrator can always
# locate them relative to the target file's directory.
ARTEFACT_DESIGN = "design.mmd"
ARTEFACT_GHERKIN = "spec.gherkin"

# Disposable error log attached during self-correction retries.
# Deleted immediately once tests pass (Context Compaction).
ERROR_LOG_STUB = ".opencode_error.log"


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

class _PipelineFormatter(logging.Formatter):
    """INFO records are emitted raw (no timestamp/level prefix) so the
    ASCII banner boxes are not polluted.  DEBUG/WARNING/ERROR records carry
    the full structured prefix for diagnostics."""

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno == logging.INFO:
            return record.getMessage()
        return super().format(record)


def setup_logging(level_name: str) -> None:
    """Configure the root pipeline logger.

    Called once at startup after argparse resolves ``--log-level``.
    Clears any existing handlers to stay idempotent on repeated calls
    (e.g. during tests).
    """
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        _PipelineFormatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)


# ---------------------------------------------------------------------------
# Terminal output helpers
# ---------------------------------------------------------------------------

def _banner(target: Path, test_cmd: list[str], skip_hitl: bool, source_type: str) -> None:
    """Print the pipeline startup banner."""
    logger.info("")
    logger.info("┌" + "─" * _W + "┐")
    logger.info(
        f"│  agentic-tdd  •  v{PIPELINE_VERSION} Pipeline  •  8-Pass State Machine"
        + " " * (_W - 57) + "│"
    )
    logger.info("└" + "─" * _W + "┘")
    logger.info("")
    logger.info(f"  Input source : {target}")
    logger.info(f"  Source type  : {source_type}")
    logger.info(f"  Test cmd     : {' '.join(test_cmd)}")
    logger.info(f"  HITL gate    : {'disabled (--skip-hitl)' if skip_hitl else 'enabled'}")
    logger.info(f"  Max retries  : {MAX_CORRECTION_RETRIES} (per guarded pass)")
    logger.info(f"  CWD          : {os.getcwd()}")
    logger.info("")
    logger.info("  Cache strategy: Static Prefix  +  Context Compaction")
    logger.info("")
    logger.info("  Pass schedule:")
    for num, label in PASS_LABELS.items():
        gate = (
            "  <- self-correction + git commit" if num in (3, 4, 5, 6) else
            "  <- git commit"                   if num in (1, 2, 7)     else
            "  <- HITL gate"
        )
        logger.info(f"    {num}  {label:<36}{gate}")
    logger.info("")


def _pass_header(label: str) -> None:
    logger.info("")
    logger.info("━" * _W)
    logger.info(f"  {label}")
    logger.info("━" * _W)
    logger.info("")


def _pass_ok(label: str) -> None:
    logger.info(f"\n  ✓  {label} — complete.\n")


def _warn(lines: list[str]) -> None:
    logger.warning("")
    logger.warning("┌" + "─" * _W + "┐")
    logger.warning("│  ⚠  WARNING" + " " * (_W - 12) + "│")
    logger.warning("│" + " " * _W + "│")
    for line in lines:
        padded = f"│  {line}"
        logger.warning(padded + " " * max(0, _W + 1 - len(padded)) + "│")
    logger.warning("│" + " " * _W + "│")
    logger.warning("└" + "─" * _W + "┘")
    logger.warning("")


def _die(msg: str) -> None:
    logger.error(f"\n[FATAL]  {msg}\n")
    sys.exit(1)


def _git_info(msg: str) -> None:
    logger.info(f"  [git]  {msg}")


# ---------------------------------------------------------------------------
# OpenCode runner
# ---------------------------------------------------------------------------

def build_opencode_command(
    agent_name: str,
    prompt: str,
    target_file: Path,
    artefact_dir: Path,
    error_log: Path | None = None,
) -> list[str]:
    """Construct a strictly-ordered ``opencode run`` command list.

    Enforces the Static Prefix invariant: design.mmd → spec.gherkin →
    target_file → error_log (optional) → prompt.  No argument is ever
    re-ordered or overridden by this function.

    Args:
        agent_name:   Agent ID matching ``.opencode/agent/<id>.md``.
        prompt:       User-turn instruction (varies per pass/retry).
        target_file:  Absolute path to the source file under modification.
        artefact_dir: Directory containing design.mmd and spec.gherkin.
        error_log:    Optional path to a self-correction failure log.

    Returns:
        A complete subprocess-ready command list.
    """
    cmd = [OPENCODE_CMD, "run", "--agent", agent_name]

    # Static Prefix — immutable order
    design_path = artefact_dir / ARTEFACT_DESIGN
    if design_path.is_file():
        cmd += ["--file", str(design_path)]

    gherkin_path = artefact_dir / ARTEFACT_GHERKIN
    if gherkin_path.is_file():
        cmd += ["--file", str(gherkin_path)]

    cmd += ["--file", str(target_file)]

    # Error log sits last — variable content, must not pollute the prefix
    if error_log is not None and error_log.is_file():
        cmd += ["--file", str(error_log)]

    cmd.append("--dangerously-skip-permissions")
    cmd.append(prompt)

    return cmd


def run_opencode(cmd: list[str]) -> None:
    """Execute a pre-built opencode command, streaming output to the terminal.

    Runs in the caller's CWD (``os.getcwd()``), which is the project root
    where ``agentic-tdd`` was invoked — not the package installation directory.

    Args:
        cmd: Full subprocess command list from :func:`build_opencode_command`.

    Raises:
        subprocess.CalledProcessError: If opencode exits non-zero.
    """
    logger.debug(f"Running opencode command: {shlex.join(cmd)}")
    logger.debug(f"CWD for opencode: {os.getcwd()}")
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def load_dot_env(env_path: Path | None = None) -> None:
    """Parse a .env file in the caller's CWD and populate os.environ.

    Resolves relative to the caller's current working directory so that
    the API key is picked up from the *project* being processed, not the
    package installation directory.
    """
    if env_path is None:
        env_path = Path(os.getcwd()) / ".env"

    if not env_path.is_file():
        logger.debug(f"No .env found at {env_path} — skipping")
        return

    logger.debug(f"Loading environment from {env_path}")
    with env_path.open() as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            clean_value = raw_value.split("#")[0].strip().strip("'\"")
            os.environ.setdefault(key.strip(), clean_value)


def preflight_checks(target: Path) -> None:
    """Validate prerequisites before pipeline execution."""
    logger.debug(f"Preflight check: target={target}")

    if not target.is_file():
        _die(f"Target file not found: '{target}'")

    if not os.environ.get("OPENROUTER_API_KEY"):
        _die(
            "OPENROUTER_API_KEY is not set.\n"
            "  Add it to your .env file:  OPENROUTER_API_KEY=sk-or-..."
        )

    if not shutil.which(OPENCODE_CMD):
        _die(
            f"'{OPENCODE_CMD}' CLI not found on PATH.\n"
            "  Install it with:  npm install -g opencode-ai"
        )

    logger.debug("Preflight checks passed.")


# ---------------------------------------------------------------------------
# Git integration -- atomic commits & branching
# ---------------------------------------------------------------------------

def get_current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    return result.stdout.strip()


def is_working_directory_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def branch_exists(branch_name: str) -> bool:
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"]
    )
    return result.returncode == 0


def ensure_branch_is_synced(branch_name: str) -> None:
    _git_info("Fetching latest from origin...")
    subprocess.run(["git", "fetch", "-q"], check=False)


def sanitize_to_git_branch(issue_ref: str) -> str:
    """Produce a valid, sanitized Git branch name from a free-form issue ref.

    Examples:
        "123"          -> "ai/issue-123"
        "PAY-404"      -> "feat/pay-404"
        "Add OAuth2"   -> "feat/add-oauth2"
    """
    s = str(issue_ref).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"ai/issue-{s}" if s.isdigit() else f"feat/{s}"


def setup_feature_branch(
    issue_ref: str, base_branch: str | None, skip_hitl: bool
) -> None:
    """Resolve base branch and checkout a new feature branch for the pipeline.

    Safety guardrails:
      - Aborts if the working directory has uncommitted changes.
      - Aborts if HEAD is ``main`` (unless ``--base-branch`` overrides).
      - Prompts before appending commits to an existing branch (unless
        ``--skip-hitl`` is active).
    """
    if not shutil.which("git"):
        _warn(["git not found on PATH -- skipping branch setup."])
        return

    if is_working_directory_dirty():
        _die(
            "Working directory is dirty. "
            "Please commit or stash your changes before running the pipeline."
        )

    current = get_current_branch()
    if base_branch:
        base = base_branch
    else:
        if current == "main":
            _die(
                "Hygiene Error: Cannot automatically branch from 'main'. "
                "Please switch to a working branch or use --base-branch override."
            )
        base = current

    ensure_branch_is_synced(base)
    branch_name = sanitize_to_git_branch(issue_ref)
    logger.debug(f"Resolved feature branch: {branch_name} (base: {base})")

    if branch_exists(branch_name):
        if skip_hitl:
            _git_info(f"Branch '{branch_name}' already exists. Checking out... (--skip-hitl)")
            subprocess.run(["git", "checkout", branch_name], check=True)
        else:
            logger.info("")
            ans = input(
                f"  [git]  Branch '{branch_name}' already exists. "
                "Append commits to existing branch? [Y/n] "
            )
            if ans.lower() not in ("", "y", "yes"):
                _die("Aborted by user.")
            subprocess.run(["git", "checkout", branch_name], check=True)
    else:
        _git_info(f"Creating and checking out new branch: {branch_name} from {base}")
        subprocess.run(["git", "checkout", "-b", branch_name, base], check=True)


def git_commit(files: list[Path], message: str) -> None:
    """Stage specific files and create an atomic git commit.

    Implements the Atomic Commits strategy: one commit per pass for precise
    regression pinpointing.  Gracefully skips if there is nothing to commit
    or if git is not available.

    Args:
        files:   File paths to stage with ``git add``.
        message: Commit message (``chore(ai): ...`` convention).
    """
    if not shutil.which("git"):
        _warn([
            "git not found on PATH -- skipping atomic commit.",
            f"  Message: {message}",
            "  Install git and ensure the project is initialised (git init).",
        ])
        return

    for f in files:
        result = subprocess.run(
            ["git", "add", str(f)], capture_output=True, text=True
        )
        if result.returncode != 0:
            _warn([
                f"git add failed for: {f}",
                result.stderr.strip() or result.stdout.strip(),
                "Continuing -- this file will be absent from the commit.",
            ])

    result = subprocess.run(
        ["git", "commit", "-m", message], capture_output=True, text=True
    )

    if result.returncode == 0:
        summary = result.stdout.strip().splitlines()[0] if result.stdout else message
        _git_info(f"Committed -> {summary}")
        return

    combined = (result.stdout + result.stderr).lower()
    if "nothing to commit" in combined or "nothing added to commit" in combined:
        _git_info(
            f"No changes to stage for: '{message}'  "
            "(agent made no edits -- skipping commit)"
        )
        return

    _warn([
        f"git commit failed: {message}",
        result.stderr.strip() or result.stdout.strip(),
        "Pipeline continues. Run 'git status' to inspect the working tree.",
    ])


# ---------------------------------------------------------------------------
# Human-in-the-Loop gate
# ---------------------------------------------------------------------------

def hitl_gate(design_mmd: Path, spec_gherkin: Path) -> None:
    """Block pipeline execution until the developer explicitly approves."""
    _max = _W - 10

    def _fmt(p: Path) -> str:
        s = str(p)
        return ("..." + s[-(_max - 1):]) if len(s) > _max else s

    logger.info("")
    logger.info("┌" + "─" * _W + "┐")
    logger.info("│  HUMAN-IN-THE-LOOP GATE (After Pass 0)                        │")
    logger.info("│  Review the design artefacts before any code is written.      │")
    logger.info("│" + " " * _W + "│")
    logger.info(f"│  1. Mermaid diagram  ->  {_fmt(design_mmd):<{_max}}│")
    logger.info(f"│  2. Gherkin spec     ->  {_fmt(spec_gherkin):<{_max}}│")
    logger.info("│" + " " * _W + "│")
    logger.info("│  Tip: VS Code + 'Mermaid Preview' extension to render .mmd    │")
    logger.info("│  Press Ctrl+C to abort -- no code will be written.             │")
    logger.info("└" + "─" * _W + "┘")
    logger.info("")

    try:
        input("  Press Enter to approve and advance to Pass 1 (Contracts)...  ")
    except KeyboardInterrupt:
        logger.info("\n\n  Pipeline aborted at HITL gate.  No code was written.\n")
        sys.exit(0)

    logger.info("\n  Design approved.  Continuing to Pass 1 (Contracts & Types)...\n")


# ---------------------------------------------------------------------------
# Test runner -- captures output for the self-correction loop
# ---------------------------------------------------------------------------

def run_tests_with_capture(test_cmd: list[str]) -> tuple[bool, str]:
    """Run the local test suite and capture its output.

    Args:
        test_cmd: Fully-resolved command list (e.g. ``['pytest', 'src/', '-v']``).

    Returns:
        Tuple of (passed: bool, combined_output: str).
    """
    logger.info(f"  Running: {' '.join(test_cmd)}\n")

    try:
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.stdout:
            logger.debug(result.stdout)
        if result.stderr:
            logger.debug(result.stderr)

        combined = result.stdout + "\n" + result.stderr
        return result.returncode == 0, combined

    except FileNotFoundError:
        msg = (
            f"Test runner not found: '{test_cmd[0]}'\n"
            "Install it or supply a valid command with --test-cmd.\n"
            "  Python:  pip install pytest\n"
            "  JS/TS:   npm install"
        )
        _warn(msg.splitlines())
        return False, msg


def infer_test_command(target_file: Path) -> list[str]:
    """Return a sensible default test command based on the file extension."""
    ext = target_file.suffix.lower()
    if ext == ".py":
        return ["pytest", str(target_file.parent), "--tb=short", "-v"]
    if ext in (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts"):
        return ["npm", "test"]
    return ["pytest", str(target_file.parent), "--tb=short"]


# ---------------------------------------------------------------------------
# Self-correction loop (Actor-Critic inner loop)
# ---------------------------------------------------------------------------

def run_pass_with_self_correction(
    pass_num: int,
    agent: str,
    initial_prompt: str,
    target: Path,
    artefact_dir: Path,
    test_cmd: list[str],
    max_retries: int = MAX_CORRECTION_RETRIES,
) -> None:
    """Execute an agent pass backed by a test-verification gate.

    Flow:
      1. Run the agent with ``initial_prompt``.
      2. Run the test suite.
      3. If tests fail and retries remain:
           a. Write raw error output to ``.opencode_error.log`` (Context Compaction).
           b. Re-run the agent with the error log attached as a ``--file``.
           c. Re-run the test suite.
           d. If tests pass: DELETE ``.opencode_error.log`` immediately.
      4. If max retries exhausted -> abort.

    Args:
        pass_num:       Pass number (e.g. 3 for Core Implementation).
        agent:          Agent ID string (key in AGENTS dict).
        initial_prompt: First user-turn message.
        target:         The target source file path.
        artefact_dir:   Directory containing design.mmd and spec.gherkin.
        test_cmd:       Test command to run after each agent invocation.
        max_retries:    Additional correction attempts (default 2 -> 3 total).

    Raises:
        SystemExit(1): If all attempts are exhausted and tests still fail.
    """
    pass_label = PASS_LABELS[pass_num]
    total_attempts = max_retries + 1
    error_log_path = artefact_dir / ERROR_LOG_STUB

    logger.info(f"\n  -> Invoking {agent} (initial run)...\n")
    initial_cmd = build_opencode_command(
        agent_name=agent,
        prompt=initial_prompt,
        target_file=target,
        artefact_dir=artefact_dir,
    )
    run_opencode(initial_cmd)

    for attempt_idx in range(total_attempts):
        human_attempt_num = attempt_idx + 1

        _pass_header(
            f"Verification Gate -- Pass {pass_num}: {pass_label}"
            f"  [attempt {human_attempt_num}/{total_attempts}]"
        )

        passed, error_output = run_tests_with_capture(test_cmd)

        if passed:
            # Context Compaction: flush stale error log
            if error_log_path.exists():
                error_log_path.unlink()
                logger.info(f"  [compaction]  Deleted {error_log_path} -- context reset.\n")
            logger.info(f"  ✓  Tests passed on attempt {human_attempt_num}/{total_attempts}.\n")
            return

        # Tests failed
        if attempt_idx == max_retries:
            if error_log_path.exists():
                error_log_path.unlink()

            tail_chars = 2000
            error_tail = (
                error_output[-tail_chars:] if len(error_output) > tail_chars
                else error_output
            )
            _die(
                f"Pass {pass_num} ({pass_label}) FAILED after {total_attempts} attempt(s).\n\n"
                f"  The test suite still fails after {max_retries} self-correction retries.\n"
                f"  Human intervention is required.\n\n"
                f"  Suggested actions:\n"
                f"    1. Run: {' '.join(test_cmd)}\n"
                f"    2. Inspect the failure and edit {target.name} manually.\n"
                f"    3. Re-run the pipeline from this pass with --skip-hitl.\n\n"
                f"  Last {min(tail_chars, len(error_output))} chars of test output:\n"
                f"{'-' * 60}\n"
                f"{error_tail}\n"
                f"{'-' * 60}"
            )

        retries_remaining = max_retries - attempt_idx
        logger.info(
            f"\n  Tests FAILED (attempt {human_attempt_num}/{total_attempts}).\n"
            f"  Triggering self-correction -- {retries_remaining} "
            f"{'retry' if retries_remaining == 1 else 'retries'} remaining.\n"
        )

        # Context Compaction: write error to a disposable file
        error_log_path.write_text(error_output, encoding="utf-8")
        logger.info(
            f"  [compaction]  Error log written to {error_log_path} "
            f"({len(error_output)} bytes)\n"
        )

        correction_prompt = (
            f"You are running as Pass {pass_num} ({pass_label}) "
            f"of the v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
            f"SELF-CORRECTION CYCLE {human_attempt_num} of {max_retries}.\n\n"
            f"Your previous edit to '{target.name}' caused the test suite to fail.\n"
            f"The complete failure log is attached as '{ERROR_LOG_STUB}'.\n"
            f"Read that file to diagnose the root cause, then fix '{target.name}'\n"
            f"to make the tests pass.\n\n"
            f"STRICT RULES:\n"
            f"  - Modify ONLY '{target.name}'.\n"
            f"  - Do NOT modify test files, design.mmd, spec.gherkin, or any other file.\n"
            f"  - Do NOT change test assertions to match broken logic -- fix the logic.\n"
            f"  - Do NOT add new public functions or change existing signatures.\n"
            f"  - Fix the ROOT CAUSE of the failure, not just the symptom."
        )

        logger.info(
            f"  -> Invoking {agent} "
            f"(self-correction cycle {human_attempt_num}/{max_retries})...\n"
        )

        correction_cmd = build_opencode_command(
            agent_name=agent,
            prompt=correction_prompt,
            target_file=target,
            artefact_dir=artefact_dir,
            error_log=error_log_path,
        )
        run_opencode(correction_cmd)


# ---------------------------------------------------------------------------
# Input resolution
# ---------------------------------------------------------------------------

def resolve_input_source(input_source: str, source_type: str) -> Path:
    """Validate and resolve the pipeline input to a concrete file path.

    Supports three source types:
      ``file``   -- a local file path (validated immediately).
      ``string`` -- a raw feature description string (future).
      ``github`` -- a GitHub issue URL (future).

    Args:
        input_source: Raw value of the positional CLI argument.
        source_type:  One of ``file``, ``string``, ``github``.

    Returns:
        Resolved absolute Path to the target source file.

    Raises:
        SystemExit(1): If the source cannot be resolved or is not yet supported.
    """
    if source_type == "file":
        # Resolve relative to the caller's CWD, not the install location.
        path = Path(os.getcwd()) / input_source
        path = path.resolve()
        if not path.is_file():
            _die(
                f"Input file not found: '{path}'\n"
                f"  Ensure the path is correct relative to your current directory:\n"
                f"  CWD: {os.getcwd()}"
            )
        logger.debug(f"Resolved target file: {path}")
        return path

    if source_type == "string":
        _die(
            "source-type 'string' is not yet implemented.\n"
            "  Planned for a future release: the raw string will be written to a\n"
            "  temporary feature file before Pass 0 begins.\n\n"
            "  NotImplementedError: string input source"
        )

    if source_type == "github":
        _die(
            "source-type 'github' is not yet implemented.\n"
            "  Planned for a future release: the GitHub issue body will be fetched\n"
            "  via the API and materialised as a local feature file.\n\n"
            "  NotImplementedError: github input source"
        )

    _die(f"Unknown source-type: '{source_type}'")
    # Unreachable; satisfies type checker
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentic-tdd",
        description=(
            f"agentic-tdd v{PIPELINE_VERSION} -- Multi-Pass Agentic TDD Pipeline\n"
            "\n"
            "Runs an 8-pass AI factory pipeline against a target source file.\n"
            "Install globally:  pipx install .\n"
            "Install for dev:   pip install -e .\n"
            "\n"
            "v0.3.3 adds:\n"
            "  - Packaged as an installable CLI (agentic-tdd)\n"
            "  - Flexible --source-type flag (file | string | github)\n"
            "  - CWD-aware execution (runs in your project root)\n"
            "\n"
            "Passes:\n"
            "  0  Design        -> design.mmd + spec.gherkin  [HITL gate]\n"
            "  1  Contracts     -> type stubs in target file\n"
            "  2  Tests         -> test file                   [Red Phase]\n"
            "  3  Core Logic    -> implementation              [Green Phase + SC]\n"
            "  4  Refactor      -> complexity/DRY cleanup      [SC]\n"
            "  5  Security      -> OWASP mitigations           [SC]\n"
            "  6  Observability -> logging + error classes     [SC]\n"
            "  7  Docs          -> docstrings + @see links\n\n"
            "  git commit fired after every pass (1-7)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ----- Positional --------------------------------------------------------
    parser.add_argument(
        "input_source",
        metavar="INPUT_SOURCE",
        type=str,
        help=(
            "The pipeline input. Interpretation depends on --source-type:\n"
            "  file   : path to the source file to process  (default)\n"
            "  string : raw feature description string      (future)\n"
            "  github : GitHub issue URL                    (future)\n"
            "Example: agentic-tdd src/calculator.py"
        ),
    )

    # ----- Source type -------------------------------------------------------
    parser.add_argument(
        "--source-type",
        dest="source_type",
        metavar="TYPE",
        choices=["file", "string", "github"],
        default="file",
        help=(
            "How to interpret INPUT_SOURCE.  Choices: file | string | github.\n"
            "Default: file\n"
            "  file   -- INPUT_SOURCE is a path to the target source file.\n"
            "  string -- INPUT_SOURCE is a raw feature description (future).\n"
            "  github -- INPUT_SOURCE is a GitHub issue URL (future)."
        ),
    )

    # ----- Logging -----------------------------------------------------------
    parser.add_argument(
        "--log-level",
        dest="log_level",
        metavar="LEVEL",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging verbosity (default: INFO).",
    )

    # ----- Git branching -----------------------------------------------------
    parser.add_argument(
        "--issue",
        dest="issue",
        metavar="REF",
        type=str,
        default=None,
        help=(
            "Issue reference (e.g. '123' or 'PAY-404') to auto-create and\n"
            "checkout an isolated feature branch before any passes run."
        ),
    )

    parser.add_argument(
        "--base-branch",
        dest="base_branch",
        metavar="NAME",
        type=str,
        default=None,
        help=(
            "Base branch to branch from (e.g. 'dev').  Bypasses the 'main'\n"
            "hygiene check.  Requires --issue."
        ),
    )

    # ----- Pipeline control --------------------------------------------------
    parser.add_argument(
        "--test-cmd",
        dest="test_cmd",
        metavar="CMD",
        type=str,
        default=None,
        help=(
            "Shell command to verify the test suite after each guarded pass.\n"
            "Defaults: 'pytest <dir> --tb=short -v'  (.py files)\n"
            "          'npm test'                     (.js/.ts files)\n"
            "Example:  --test-cmd 'pytest tests/ -k calculator -x'"
        ),
    )

    parser.add_argument(
        "--skip-hitl",
        dest="skip_hitl",
        action="store_true",
        default=False,
        help=(
            "Skip the human approval gate after Pass 0.\n"
            "Intended for CI/CD contexts.  Not recommended for local dev."
        ),
    )

    return parser


# ---------------------------------------------------------------------------
# Main pipeline -- the 8-pass state machine
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entrypoint.  Mapped to ``agentic-tdd`` by pyproject.toml.

    Orchestrates all 8 pipeline passes end-to-end.  Execution always runs in
    ``os.getcwd()`` -- the directory from which the developer invoked the
    command -- so that relative file paths and .env lookups behave correctly
    regardless of where the package is installed.
    """
    args = _build_arg_parser().parse_args()

    setup_logging(args.log_level)

    logger.debug(f"agentic-tdd v{PIPELINE_VERSION} starting")
    logger.debug(f"CWD: {os.getcwd()}")
    logger.debug(f"args: {args}")

    # --- Git branch setup (if requested) ------------------------------------
    if args.issue:
        setup_feature_branch(args.issue, args.base_branch, args.skip_hitl)

    # --- Resolve the input source -------------------------------------------
    target: Path = resolve_input_source(args.input_source, args.source_type)
    target_dir: Path = target.parent

    # Artefact paths co-located with the target file
    design_mmd:   Path = target_dir / ARTEFACT_DESIGN
    spec_gherkin: Path = target_dir / ARTEFACT_GHERKIN

    # Test file naming follows language conventions
    _stem = target.stem
    _ext  = target.suffix
    _test_name = (
        f"{_stem}_test{_ext}" if _ext == ".py"
        else f"{_stem}.test{_ext}"
    )
    test_file: Path = target_dir / _test_name

    # --- Environment & preflight -------------------------------------------
    load_dot_env()          # resolves to CWD/.env
    preflight_checks(target)

    if args.test_cmd:
        test_cmd: list[str] = shlex.split(args.test_cmd)
    else:
        test_cmd = infer_test_command(target)

    _banner(target, test_cmd, args.skip_hitl, args.source_type)

    # ====================================================================
    # PASS 0 -- Design & Architecture
    # ====================================================================
    _pass_header(f"Pass 0 -- {PASS_LABELS[0]}  [{AGENTS[0]}]")

    design_prompt = (
        f"You are running as Pass 0 (Design & Architecture) of the v{PIPELINE_VERSION} "
        f"AI Factory pipeline.\n\n"
        f"Analyse the attached source file and produce exactly two artefact files.\n\n"
        f"ARTEFACT 1 -- Mermaid diagram\n"
        f"  Write to: {design_mmd}\n"
        f"  Use stateDiagram-v2, sequenceDiagram, or flowchart TD -- whichever best\n"
        f"  represents the logic.  Include a header comment block:\n"
        f"    %% Module: {target.name}\n"
        f"    %% Generated by: {AGENTS[0]}  Pipeline: v{PIPELINE_VERSION}\n\n"
        f"ARTEFACT 2 -- Gherkin specification\n"
        f"  Write to: {spec_gherkin}\n"
        f"  One Feature block.  Minimum three Scenarios: happy path, edge case,\n"
        f"  error/exception case.  Use concrete values (no <placeholder> tokens).\n\n"
        f"STRICT RULES:\n"
        f"  - Do NOT modify {target.name}.\n"
        f"  - Do NOT write executable code of any kind.\n"
        f"  - Output ONLY {design_mmd.name} and {spec_gherkin.name}.\n"
        f"  - Mermaid syntax must be valid and renderable by mermaid.js v10+."
    )

    run_opencode(build_opencode_command(
        agent_name=AGENTS[0],
        prompt=design_prompt,
        target_file=target,
        artefact_dir=target_dir,
    ))
    _pass_ok(f"Pass 0 -- {PASS_LABELS[0]}")

    if not args.skip_hitl:
        hitl_gate(design_mmd, spec_gherkin)
    else:
        logger.info("  [--skip-hitl]  Skipping human approval gate.\n")

    # ====================================================================
    # PASS 1 -- Contracts & Types
    # ====================================================================
    _pass_header(f"Pass 1 -- {PASS_LABELS[1]}  [{AGENTS[1]}]")

    contracts_prompt = (
        f"You are running as Pass 1 (Contracts & Types) of the v{PIPELINE_VERSION} "
        f"AI Factory pipeline.\n\n"
        f"Attached files:\n"
        f"  Source file (the ONLY file you may modify): {target}\n"
        f"  Architecture constraint:                    {design_mmd}\n"
        f"  Behavioural specification:                  {spec_gherkin}\n\n"
        f"Your task:\n"
        f"  Read all three files.  Add type contracts to '{target.name}':\n"
        f"    1. Identify every entity, input type, output type, and error condition\n"
        f"       described in {design_mmd.name} and {spec_gherkin.name}.\n"
        f"    2. Define a strict type for each (Pydantic BaseModel / TypedDict /\n"
        f"       dataclass / Protocol for Python; interface / type / enum for TS).\n"
        f"    3. Add full type annotations to all existing function signatures.\n"
        f"    4. Function bodies must remain as stubs (raise NotImplementedError).\n"
        f"    5. Place all new type definitions in a clearly labelled section at\n"
        f"       the top of the file.\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT write business logic -- stubs only.\n"
        f"  - Do NOT modify {design_mmd.name} or {spec_gherkin.name}."
    )

    run_opencode(build_opencode_command(
        agent_name=AGENTS[1],
        prompt=contracts_prompt,
        target_file=target,
        artefact_dir=target_dir,
    ))
    _pass_ok(f"Pass 1 -- {PASS_LABELS[1]}")
    git_commit(files=[target], message=f"chore(ai): completed Pass 1 -- {PASS_LABELS[1]}")

    # ====================================================================
    # PASS 2 -- TDD Test Generation  [Red Phase]
    # ====================================================================
    _pass_header(f"Pass 2 -- {PASS_LABELS[2]}  [{AGENTS[2]}]")

    test_gen_prompt = (
        f"You are running as Pass 2 (TDD Test Generation -- Red Phase) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached files:\n"
        f"  Source file (DO NOT modify):      {target}\n"
        f"  Architecture constraint:          {design_mmd}\n"
        f"  Behavioural specification:        {spec_gherkin}\n\n"
        f"Your task:\n"
        f"  Create a test file at:\n"
        f"    {test_file}\n\n"
        f"  The tests must:\n"
        f"    1. Mirror every Scenario in {spec_gherkin.name} as a named test case.\n"
        f"    2. Cover all type contracts defined in {target.name} (Pass 1 output).\n"
        f"    3. Cover happy paths, edge cases, boundary conditions, and errors.\n"
        f"    4. Use pytest (Python) or Jest (TypeScript/JavaScript).\n"
        f"    5. Be independent, deterministic, and idempotent.\n\n"
        f"  NOTE: These tests are EXPECTED to fail right now (Red Phase).\n"
        f"  The function bodies are stubs.  Write the tests against the CONTRACT,\n"
        f"  not the current (stub) implementation.\n\n"
        f"STRICT RULES:\n"
        f"  - Do NOT modify '{target.name}'.\n"
        f"  - Create ONLY '{_test_name}' -- no other files."
    )

    run_opencode(build_opencode_command(
        agent_name=AGENTS[2],
        prompt=test_gen_prompt,
        target_file=target,
        artefact_dir=target_dir,
    ))
    _pass_ok(f"Pass 2 -- {PASS_LABELS[2]}")
    git_commit(files=[test_file], message=f"chore(ai): completed Pass 2 -- {PASS_LABELS[2]}")

    # ====================================================================
    # PASS 3 -- Core Implementation  [Green Phase + self-correction]
    # ====================================================================
    _pass_header(f"Pass 3 -- {PASS_LABELS[3]}  [{AGENTS[3]}]")

    impl_prompt = (
        f"You are running as Pass 3 (Core Implementation -- Green Phase) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached files:\n"
        f"  Source file to implement:  {target}\n"
        f"  Architecture constraint:   {design_mmd}\n"
        f"  Behavioural specification: {spec_gherkin}\n\n"
        f"Your task:\n"
        f"  Implement the business logic in '{target.name}' so all tests in\n"
        f"  '{_test_name}' pass.  The diagram in '{design_mmd.name}' is your\n"
        f"  binding architectural contract -- deviate from it only if the test\n"
        f"  failures prove the diagram is wrong (and leave a comment explaining).\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT modify the test file, {design_mmd.name}, or {spec_gherkin.name}.\n"
        f"  - Do NOT add documentation blocks -- that is Pass 7's job.\n"
        f"  - Do NOT add logging -- that is Pass 6's job.\n"
        f"  - Do NOT deviate from the type contracts established in Pass 1."
    )

    run_pass_with_self_correction(
        pass_num=3, agent=AGENTS[3], initial_prompt=impl_prompt,
        target=target, artefact_dir=target_dir, test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 3 -- {PASS_LABELS[3]}")
    git_commit(files=[target], message=f"chore(ai): completed Pass 3 -- {PASS_LABELS[3]}")

    # ====================================================================
    # PASS 4 -- Refactor & Optimise  [self-correction]
    # ====================================================================
    _pass_header(f"Pass 4 -- {PASS_LABELS[4]}  [{AGENTS[4]}]")

    refactor_prompt = (
        f"You are running as Pass 4 (Refactor & Optimise) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached file (the ONLY file you may modify): {target}\n\n"
        f"The file has just passed all tests in Pass 3. Your task:\n"
        f"  Apply the refactor_checklist from your agent instructions to '{target.name}'.\n"
        f"  Improve structure, readability, and performance WITHOUT changing any\n"
        f"  observable behaviour.  The test suite is the binding behavioural contract.\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT change public function signatures, names, or return types.\n"
        f"  - Do NOT add new features or fix out-of-scope bugs.\n"
        f"  - Do NOT modify test files or design artefacts.\n"
        f"  - If no improvement is possible, return the file unchanged."
    )

    run_pass_with_self_correction(
        pass_num=4, agent=AGENTS[4], initial_prompt=refactor_prompt,
        target=target, artefact_dir=target_dir, test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 4 -- {PASS_LABELS[4]}")
    git_commit(files=[target], message=f"chore(ai): completed Pass 4 -- {PASS_LABELS[4]}")

    # ====================================================================
    # PASS 5 -- Security Hardening  [self-correction]
    # ====================================================================
    _pass_header(f"Pass 5 -- {PASS_LABELS[5]}  [{AGENTS[5]}]")

    security_prompt = (
        f"You are running as Pass 5 (Security Hardening) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached file (the ONLY file you may modify): {target}\n\n"
        f"The code has passed Tests (Pass 3) and Refactor (Pass 4). Your task:\n"
        f"  Apply your security_checklist (OWASP Top-10) to '{target.name}'.\n"
        f"  Add input validation, sanitisation, and boundary checks.\n"
        f"  Mark every change with an inline comment: '# SEC: <category> -- <reason>'.\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT change business logic or function signatures.\n"
        f"  - Do NOT modify test files or design artefacts.\n"
        f"  - All new validation must raise descriptive exceptions (not swallow them)."
    )

    run_pass_with_self_correction(
        pass_num=5, agent=AGENTS[5], initial_prompt=security_prompt,
        target=target, artefact_dir=target_dir, test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 5 -- {PASS_LABELS[5]}")
    git_commit(files=[target], message=f"chore(ai): completed Pass 5 -- {PASS_LABELS[5]}")

    # ====================================================================
    # PASS 6 -- Observability & Logging  [self-correction]
    # ====================================================================
    _pass_header(f"Pass 6 -- {PASS_LABELS[6]}  [{AGENTS[6]}]")

    observability_prompt = (
        f"You are running as Pass 6 (Observability & Logging) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached file (the ONLY file you may modify): {target}\n\n"
        f"The code has passed Tests, Refactor, and Security passes.  Your task:\n"
        f"  Add structured logging and error handling to '{target.name}' following\n"
        f"  your agent's observability_checklist.\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT change business logic, function signatures, or security code.\n"
        f"  - Do NOT use print() -- use the logging module (Python) or a logger.\n"
        f"  - Do NOT modify test files or design artefacts.\n"
        f"  - Custom exception classes must be defined in this file, not imported."
    )

    run_pass_with_self_correction(
        pass_num=6, agent=AGENTS[6], initial_prompt=observability_prompt,
        target=target, artefact_dir=target_dir, test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 6 -- {PASS_LABELS[6]}")
    git_commit(files=[target], message=f"chore(ai): completed Pass 6 -- {PASS_LABELS[6]}")

    # ====================================================================
    # PASS 7 -- Documentation
    # ====================================================================
    _pass_header(f"Pass 7 -- {PASS_LABELS[7]}  [{AGENTS[7]}]")

    docs_prompt = (
        f"You are running as Pass 7 (Documentation) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached file (the ONLY file you may modify): {target}\n\n"
        f"This is the finalised implementation after TDD, Refactor, Security,\n"
        f"and Observability passes.  Your task -- add complete documentation:\n"
        f"  1. A module-level docstring describing the purpose, architecture,\n"
        f"     and the pipeline version that produced this file.\n"
        f"  2. JSDoc (JS/TS) or Python docstrings for every public function/class.\n"
        f"  3. @param / Args, @returns / Returns, @throws / Raises sections.\n"
        f"  4. An @see / See Also link pointing to '{design_mmd.name}' on\n"
        f"     every public function -- this is the Traceability Matrix link.\n"
        f"     It lets any developer navigate from code to the architectural\n"
        f"     diagram that dictated it.  This is MANDATORY.\n\n"
        f"STRICT RULES:\n"
        f"  - Edit ONLY '{target.name}' -- comments and docstrings ONLY.\n"
        f"  - Do NOT change any logic, variable names, or control flow.\n"
        f"  - Do NOT modify the test file, {design_mmd.name}, or {spec_gherkin.name}."
    )

    run_opencode(build_opencode_command(
        agent_name=AGENTS[7],
        prompt=docs_prompt,
        target_file=target,
        artefact_dir=target_dir,
    ))
    _pass_ok(f"Pass 7 -- {PASS_LABELS[7]}")
    git_commit(files=[target], message=f"chore(ai): completed Pass 7 -- {PASS_LABELS[7]}")

    # ====================================================================
    # Final summary
    # ====================================================================
    _max_path = _W - 22

    def _fp(p: Path) -> str:
        s = str(p)
        return ("..." + s[-(_max_path - 1):]) if len(s) > _max_path else s

    logger.info("")
    logger.info("┌" + "─" * _W + "┐")
    logger.info(
        f"│  v{PIPELINE_VERSION} Pipeline complete -- all 8 passes ran successfully."
        + " " * (_W - 60) + "│"
    )
    logger.info("│" + " " * _W + "│")
    logger.info(f"│  Target file    : {_fp(target):<{_max_path}}│")
    logger.info("│" + " " * _W + "│")
    logger.info("│  Artefacts:" + " " * (_W - 11) + "│")
    logger.info(f"│    design.mmd   : {_fp(design_mmd):<{_max_path}}│")
    logger.info(f"│    spec.gherkin : {_fp(spec_gherkin):<{_max_path}}│")
    logger.info(f"│    test file    : {_fp(test_file):<{_max_path}}│")
    logger.info(f"│    source file  : {_fp(target):<{_max_path}}│")
    logger.info("│" + " " * _W + "│")
    logger.info("│  Git:  7 atomic commits created (Passes 1-7)." + " " * (_W - 47) + "│")
    logger.info("│  Next: git log --oneline  to review the commit trail." + " " * (_W - 54) + "│")
    logger.info("│        Open a PR when satisfied." + " " * (_W - 33) + "│")
    logger.info("└" + "─" * _W + "┘")
    logger.info("")


# ---------------------------------------------------------------------------
# Entry point (for direct script execution; preferred path is via pipx/pip)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info(
            "\n\n  Pipeline interrupted by user.\n"
            "  Partial changes may exist -- run:  git diff\n"
            "  To resume from a specific pass, re-run with --skip-hitl.\n"
        )
        sys.exit(0)
    except subprocess.CalledProcessError as exc:
        cmd_str = " ".join(str(a) for a in exc.cmd)
        logger.error(
            f"\n[FATAL]  opencode exited with code {exc.returncode}.\n"
            f"  Command: {cmd_str}\n"
            f"  Check the terminal output above for details.\n"
        )
        sys.exit(1)
