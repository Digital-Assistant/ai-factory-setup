#!/usr/bin/env python3
"""
pipeline_v3.py — v0.3 AI Factory Pipeline Orchestrator
=======================================================

Executes the full 8-pass AI-native development pipeline against a single
target source file, using OpenCode CLI as the agent runner.

State machine overview
----------------------
  Pass 0  Design & Architecture  (claude-sonnet-4.6)
          → Produces design.mmd + spec.gherkin
          → HUMAN-IN-THE-LOOP gate before any code is written

  Pass 1  Contracts & Types      (claude-3.7-sonnet)
          → Adds Pydantic models / TypedDicts / interfaces to target file
          → git commit after completion

  Pass 2  TDD Test Generation    (deepseek-v4-pro)   [Red Phase]
          → Creates test file from spec.gherkin; tests are EXPECTED to fail
          → git commit after completion

  Pass 3  Core Implementation    (deepseek-v4-pro)   [Green Phase]
          → Writes logic to make Pass 2 tests pass
          → Self-correction loop (max 2 retries) if tests fail
          → git commit after tests pass

  Pass 4  Refactor & Optimise    (deepseek-coder-v4)
          → Reduces complexity, enforces DRY, improves Big-O
          → Self-correction loop (max 2 retries) if tests break
          → git commit after tests pass

  Pass 5  Security Hardening     (gpt-4.5-turbo)
          → OWASP Top-10 mitigations, input validation
          → Self-correction loop (max 2 retries) if tests break
          → git commit after tests pass

  Pass 6  Observability & Logs   (deepseek-coder-v4)
          → Structured JSON logging, custom error classes, try/except
          → Self-correction loop (max 2 retries) if tests break
          → git commit after tests pass

  Pass 7  Documentation          (deepseek-v4-pro)
          → JSDoc / Python docstrings, @see links to design.mmd
          → git commit after completion

Self-correction loop
--------------------
  For Passes 3-6 only:
    Attempt 1 : initial agent run → run tests
    Attempt 2 : if failed → agent re-run with error log → run tests  (retry 1)
    Attempt 3 : if failed → agent re-run with error log → run tests  (retry 2)
    Abort     : if all 3 attempts fail, pipeline halts for human review

Git integration
---------------
  After each pass (1-7), the orchestrator runs:
    git add <relevant_file(s)>
    git commit -m "chore(ai): completed Pass X — <pass name>"
  If nothing changed (the agent chose not to edit), the commit is skipped
  gracefully rather than crashing.

Usage
-----
  python pipeline_v3.py <target_file> [options]

  python pipeline_v3.py src/calculator.py
  python pipeline_v3.py src/calculator.py --test-cmd "pytest src/ -x -v"
  python pipeline_v3.py src/calculator.py --skip-hitl   # CI / automated use

Prerequisites
-------------
  - opencode CLI on $PATH  (npm install -g opencode-ai)
  - OPENROUTER_API_KEY in .env or already exported to the shell
  - Agent files present in .opencode/agent/
  - git initialised in the working directory (for atomic commits)
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

PIPELINE_VERSION = "0.3"

# opencode CLI binary name — must be on $PATH
OPENCODE_CMD = "opencode"

# Maximum number of ADDITIONAL attempts after the first failure.
# Total agent invocations per guarded pass = MAX_CORRECTION_RETRIES + 1 (= 3).
MAX_CORRECTION_RETRIES = 2

# Maps pass numbers to their agent IDs.
# Agent IDs must match filenames under .opencode/agent/<id>.md
# The agent file's YAML frontmatter declares the model — the orchestrator
# never hard-codes a model; all model routing lives in the agent files.
AGENTS: dict[int, str] = {
    0: "pass-0-design-agent",
    1: "pass-1-contracts-agent",
    2: "test-generation-agent",
    3: "core-implementation-agent",
    4: "pass-4-refactor-agent",
    5: "pass-5-security-agent",
    6: "pass-6-observability-agent",
    7: "documentation-agent",
}

# Human-readable labels used in headers, commit messages, and log output
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

# Width for box-drawing in terminal output
_W = 68


# ─────────────────────────────────────────────────────────────────────────────
# Environment helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_dot_env(env_path: Path = Path(".env")) -> None:
    """Parse a .env file and populate os.environ.

    Variables already present in the environment take precedence
    (shell-level overrides are not clobbered).  Blank lines and lines
    starting with '#' are silently skipped.  Inline comments (# …) and
    surrounding quotes on values are stripped.

    Args:
        env_path: Path to the .env file.  Defaults to ./.env
    """
    if not env_path.is_file():
        return

    with env_path.open() as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            clean_value = raw_value.split("#")[0].strip().strip("'\"")
            os.environ.setdefault(key.strip(), clean_value)


def preflight_checks(target: Path) -> None:
    """Validate all prerequisites before any pipeline pass runs.

    Aborts with a descriptive error message if any check fails,
    preventing a partially-run pipeline with misleading side-effects.

    Args:
        target: Resolved path to the target source file.

    Raises:
        SystemExit(1): On any failed check.
    """
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


# ─────────────────────────────────────────────────────────────────────────────
# Terminal output helpers
# ─────────────────────────────────────────────────────────────────────────────

def _banner(target: Path, test_cmd: list[str], skip_hitl: bool) -> None:
    """Print the v0.3 pipeline startup banner."""
    print()
    print("┌" + "─" * _W + "┐")
    print(f"│  ai-factory-setup  •  v{PIPELINE_VERSION} Pipeline  •  8-Pass State Machine"
          + " " * (_W - 55) + "│")
    print("└" + "─" * _W + "┘")
    print()
    print(f"  Target     : {target}")
    print(f"  Test cmd   : {' '.join(test_cmd)}")
    print(f"  HITL gate  : {'disabled (--skip-hitl)' if skip_hitl else 'enabled'}")
    print(f"  Max retries: {MAX_CORRECTION_RETRIES} (per guarded pass)")
    print()
    print("  Pass schedule:")
    for num, label in PASS_LABELS.items():
        gate = "  ← self-correction + git commit" if num in (3, 4, 5, 6) else \
               "  ← git commit" if num in (1, 2, 7) else \
               "  ← HITL gate"
        print(f"    {num}  {label:<36}{gate}")
    print()


def _pass_header(label: str) -> None:
    """Print a visually distinct header for each pipeline pass."""
    print()
    print("━" * _W)
    print(f"  {label}")
    print("━" * _W)
    print()


def _pass_ok(label: str) -> None:
    """Print a pass-completion confirmation."""
    print(f"\n  ✓  {label} — complete.\n")


def _warn(lines: list[str]) -> None:
    """Print a loud, boxed warning block that does NOT abort the pipeline.

    Args:
        lines: Individual lines of the warning message body.
    """
    print()
    print("┌" + "─" * _W + "┐")
    print("│  ⚠  WARNING" + " " * (_W - 12) + "│")
    print("│" + " " * _W + "│")
    for line in lines:
        padded = f"│  {line}"
        print(padded + " " * max(0, _W + 1 - len(padded)) + "│")
    print("│" + " " * _W + "│")
    print("└" + "─" * _W + "┘")
    print()


def _die(msg: str) -> None:
    """Print a fatal error message and exit with code 1.

    Args:
        msg: Error description.  May contain newlines for multiline output.
    """
    print(f"\n[FATAL]  {msg}\n", file=sys.stderr)
    sys.exit(1)


def _git_info(msg: str) -> None:
    """Print a formatted git-operation status line."""
    print(f"  [git]  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# OpenCode runner
# ─────────────────────────────────────────────────────────────────────────────

def run_opencode(agent: str, prompt: str, files: list[Path]) -> None:
    """Invoke `opencode run` for a single pipeline pass.

    Streams all output directly to the terminal so the developer sees
    live diffs and agent reasoning as they happen.  The model is NOT
    specified here — each agent's frontmatter owns its model declaration,
    ensuring the agent file is the single source of truth for model routing.

    Args:
        agent:  Agent ID matching .opencode/agent/<agent>.md
        prompt: The user-turn message sent to the agent.
        files:  Source files to attach via repeated --file flags.

    Raises:
        subprocess.CalledProcessError: If opencode exits with a non-zero code.
    """
    cmd = [OPENCODE_CMD, "run", "--agent", agent]

    # Attach every file with its own --file flag (opencode supports repeats)
    for f in files:
        cmd += ["--file", str(f)]

    # Auto-approve file read/write permissions that aren't explicitly denied in
    # the agent's frontmatter.  All agents deny bash and webfetch — those
    # restrictions are enforced even with this flag.
    cmd.append("--dangerously-skip-permissions")

    # The prompt is the final positional argument
    cmd.append(prompt)

    # Stream output live — no stdout/stderr capture here
    subprocess.run(cmd, check=True)


# ─────────────────────────────────────────────────────────────────────────────
# Git integration — atomic commits
# ─────────────────────────────────────────────────────────────────────────────

def git_commit(files: list[Path], message: str) -> None:
    """Stage specific files and create an atomic git commit.

    This is the "Atomic Commits" strategy from the architecture manifesto
    (§3.3): one commit per pass makes regressions easy to pinpoint and
    revert.  Each commit represents a discrete, verified state.

    Graceful no-op cases (not errors):
      - File wasn't modified by the agent → "nothing to commit" → skip commit.
      - git is not initialised in the project → warn and skip (don't crash).

    Args:
        files:   List of file paths to stage with `git add`.
        message: The commit message (use 'chore(ai): ...' convention).
    """
    # ── Sanity-check: is git available? ─────────────────────────────────────
    if not shutil.which("git"):
        _warn([
            "git not found on PATH — skipping atomic commit.",
            f"  Message: {message}",
            "  Install git and ensure the project is initialised (git init).",
        ])
        return

    # ── Stage all relevant files for this pass ───────────────────────────────
    # We stage each file individually so a missing file (agent didn't create
    # it yet) does not cause `git add` to fail the entire batch.
    for f in files:
        result = subprocess.run(
            ["git", "add", str(f)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Non-fatal: the file might not exist yet or might be ignored.
            _warn([
                f"git add failed for: {f}",
                result.stderr.strip() or result.stdout.strip(),
                "Continuing — this file will be absent from the commit.",
            ])

    # ── Attempt the commit ────────────────────────────────────────────────────
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Success — print the one-line commit summary (e.g. "[main abc1234] ...")
        summary = result.stdout.strip().splitlines()[0] if result.stdout else message
        _git_info(f"Committed → {summary}")
        return

    # ── Handle the "nothing to commit" case gracefully ───────────────────────
    # git exits 1 with this message when the staging area has no new content.
    # This happens legitimately when the agent determined no changes were needed
    # (e.g. the Refactor agent finds the code is already optimal).
    combined_output = (result.stdout + result.stderr).lower()
    if "nothing to commit" in combined_output or "nothing added to commit" in combined_output:
        _git_info(
            f"No changes to stage for: '{message}'  "
            "(agent made no edits — skipping commit)"
        )
        return

    # ── Any other git failure is surfaced as a warning (not a fatal error) ───
    # We don't abort the pipeline over a git failure — the code changes exist
    # on disk and the developer can commit manually.
    _warn([
        f"git commit failed: {message}",
        result.stderr.strip() or result.stdout.strip(),
        "Pipeline continues. Run 'git status' to inspect the working tree.",
    ])


# ─────────────────────────────────────────────────────────────────────────────
# Human-in-the-Loop gate
# ─────────────────────────────────────────────────────────────────────────────

def hitl_gate(design_mmd: Path, spec_gherkin: Path) -> None:
    """Block pipeline execution until the developer explicitly approves.

    This is the primary hallucination-prevention checkpoint described in
    the architecture manifesto (§1.2 — Artifact-Driven Development).
    The developer should:
      1. Open design.mmd in a Mermaid viewer (VS Code + 'Mermaid Preview',
         or mermaid.live) and verify the diagram is architecturally correct.
      2. Open spec.gherkin and confirm the BDD scenarios are exhaustive.
      3. Press Enter only when satisfied.

    Pressing Ctrl+C triggers a clean, zero-error abort so the developer
    can edit the design artefacts manually before re-running Pass 0.

    Args:
        design_mmd:   Path to the generated Mermaid diagram file.
        spec_gherkin: Path to the generated Gherkin specification file.
    """
    _max = _W - 10

    def _fmt(p: Path) -> str:
        s = str(p)
        return ("…" + s[-(_max - 1):]) if len(s) > _max else s

    print()
    print("┌" + "─" * _W + "┐")
    print("│  HUMAN-IN-THE-LOOP GATE (After Pass 0)                        │")
    print("│  Review the design artefacts before any code is written.      │")
    print("│" + " " * _W + "│")
    print(f"│  1. Mermaid diagram  →  {_fmt(design_mmd):<{_max}}│")
    print(f"│  2. Gherkin spec     →  {_fmt(spec_gherkin):<{_max}}│")
    print("│" + " " * _W + "│")
    print("│  Tip: VS Code + 'Mermaid Preview' extension to render .mmd    │")
    print("│  Press Ctrl+C to abort — no code will be written.             │")
    print("└" + "─" * _W + "┘")
    print()

    try:
        input("  Press Enter to approve and advance to Pass 1 (Contracts)…  ")
    except KeyboardInterrupt:
        # Clean exit — developer wants to edit artefacts and re-run
        print("\n\n  Pipeline aborted at HITL gate.  No code was written.\n")
        sys.exit(0)

    print("\n  Design approved.  Continuing to Pass 1 (Contracts & Types)…\n")


# ─────────────────────────────────────────────────────────────────────────────
# Test runner — captures output for the self-correction loop
# ─────────────────────────────────────────────────────────────────────────────

def run_tests_with_capture(test_cmd: list[str]) -> tuple[bool, str]:
    """Run the local test suite and capture its output.

    Unlike the v0.2 simple run_tests(), this version captures stdout and
    stderr so the orchestrator can extract the failure log and feed it back
    to the agent during the self-correction loop (Passes 3-6).

    Output is printed to the terminal in real-time (via the print calls after
    capture) so the developer can follow along.

    Args:
        test_cmd: Fully-resolved command as a list (e.g. ['pytest', 'src/', '-v']).

    Returns:
        tuple[bool, str]:
            - bool  : True if the suite exited zero (all tests passed).
            - str   : Combined stdout + stderr from the test run.
              Used as the error payload in self-correction prompts.
    """
    print(f"  Running: {' '.join(test_cmd)}\n")

    try:
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
        )

        # Print captured output so the developer can read it in the terminal
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        combined_output = result.stdout + "\n" + result.stderr
        return result.returncode == 0, combined_output

    except FileNotFoundError:
        # The test runner binary (pytest, npm, …) is not on PATH.
        msg = (
            f"Test runner not found: '{test_cmd[0]}'\n"
            f"Install it or supply a valid command with --test-cmd.\n"
            f"  Python:  pip install pytest\n"
            f"  JS/TS:   npm install"
        )
        _warn(msg.splitlines())
        return False, msg


def infer_test_command(target_file: Path) -> list[str]:
    """Return a sensible default test command based on the file extension.

    Args:
        target_file: Resolved path to the target source file.

    Returns:
        List of command tokens ready to pass to subprocess.run().
    """
    ext = target_file.suffix.lower()

    if ext == ".py":
        # pytest discovers test_*.py / *_test.py automatically in the dir.
        # --tb=short keeps failure output dense enough for the correction prompt.
        return ["pytest", str(target_file.parent), "--tb=short", "-v"]

    if ext in (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts"):
        return ["npm", "test"]

    # Generic fallback
    return ["pytest", str(target_file.parent), "--tb=short"]


# ─────────────────────────────────────────────────────────────────────────────
# Self-correction loop — the "Actor-Critic" inner loop
# ─────────────────────────────────────────────────────────────────────────────

def run_pass_with_self_correction(
    pass_num: int,
    agent: str,
    initial_prompt: str,
    files: list[Path],
    target: Path,
    test_cmd: list[str],
    max_retries: int = MAX_CORRECTION_RETRIES,
) -> None:
    """Execute an agent pass backed by a test-verification gate.

    This implements the "Verification Gate" loop from the architecture
    manifesto (§1.1 — The Multi-Pass Pipeline):

        SubAgent → Gate (tests) → Fail: feed error logs back → SubAgent
                               → Pass: yield control to Orchestrator

    Flow:
      1. Run the agent with initial_prompt.
      2. Run the test suite (attempt 1).
      3. If tests fail and retries remain:
           a. Build a correction prompt that embeds the raw failure log.
           b. Re-run the agent with the correction prompt (attempt N).
           c. Re-run the test suite.
      4. After max_retries correction cycles, if tests still fail → abort.

    Why embed raw test output?
      The failure log contains the exact stack trace, assertion values, and
      diff.  Feeding it directly (not summarised) minimises hallucination:
      the agent sees the same information a human developer would see when
      debugging a failing test in their IDE.

    Args:
        pass_num:        Integer pass number (e.g. 3 for Core Implementation).
        agent:           Agent ID string (key in AGENTS dict).
        initial_prompt:  The first user-turn message for this pass.
        files:           Files attached to every agent invocation.
        target:          The target source file (used in correction prompts).
        test_cmd:        The test command to run after each agent invocation.
        max_retries:     Number of additional attempts after the first failure.
                         Default: MAX_CORRECTION_RETRIES (2), meaning 3 total.

    Raises:
        SystemExit(1): If all attempts are exhausted and tests still fail.
    """
    pass_label = PASS_LABELS[pass_num]
    total_attempts = max_retries + 1  # e.g. 3 attempts: initial + 2 corrections

    # ── Attempt 0: initial agent invocation ──────────────────────────────────
    print(f"\n  → Invoking {agent} (initial run)…\n")
    run_opencode(agent=agent, prompt=initial_prompt, files=files)

    # ── Verification + correction loop ───────────────────────────────────────
    # attempt_idx tracks how many test runs have been attempted (0-indexed).
    # The loop runs at most (max_retries + 1) times.
    for attempt_idx in range(total_attempts):
        human_attempt_num = attempt_idx + 1  # 1-based for human-readable output

        _pass_header(
            f"Verification Gate — Pass {pass_num}: {pass_label}"
            f"  [attempt {human_attempt_num}/{total_attempts}]"
        )

        passed, error_output = run_tests_with_capture(test_cmd)

        if passed:
            # ── Happy path: tests green ──────────────────────────────────────
            print(f"  ✓  Tests passed on attempt {human_attempt_num}/{total_attempts}.\n")
            return  # Exit the correction loop; control returns to main()

        # ── Tests failed ─────────────────────────────────────────────────────
        if attempt_idx == max_retries:
            # This was the last allowed attempt.  Abort the pipeline so a human
            # can inspect the failure, manually fix the issue, and re-run.
            # We print the tail of the error log so the developer has immediate
            # context without having to scroll.
            tail_chars = 2000
            error_tail = (
                error_output[-tail_chars:] if len(error_output) > tail_chars
                else error_output
            )
            _die(
                f"Pass {pass_num} ({pass_label}) FAILED after {total_attempts} attempt(s).\n\n"
                f"  The test suite still fails after {max_retries} self-correction "
                f"retries.\n"
                f"  Human intervention is required.\n\n"
                f"  Suggested actions:\n"
                f"    1. Run: {' '.join(test_cmd)}\n"
                f"    2. Inspect the failure and edit {target.name} manually.\n"
                f"    3. Re-run the pipeline from this pass with --skip-hitl.\n\n"
                f"  Last {min(tail_chars, len(error_output))} chars of test output:\n"
                f"{'─' * 60}\n"
                f"{error_tail}\n"
                f"{'─' * 60}"
            )

        # ── Still have retries — trigger self-correction ──────────────────────
        retries_remaining = max_retries - attempt_idx
        print(
            f"\n  Tests FAILED (attempt {human_attempt_num}/{total_attempts}).\n"
            f"  Triggering self-correction — {retries_remaining} "
            f"{'retry' if retries_remaining == 1 else 'retries'} remaining.\n"
        )

        # Build the correction prompt.  We inject the raw failure log inside
        # XML tags so the agent cannot confuse test output with pipeline
        # instructions (per manifesto §4.1 — XML Prompting over Markdown).
        correction_prompt = (
            f"You are running as Pass {pass_num} ({pass_label}) "
            f"of the v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
            f"SELF-CORRECTION CYCLE {human_attempt_num} of {max_retries}.\n\n"
            f"Your previous edit to '{target.name}' caused the test suite to fail.\n"
            f"Diagnose the root cause by reading the test failure log below,\n"
            f"then fix '{target.name}' to make the tests pass.\n\n"
            f"STRICT RULES:\n"
            f"  - Modify ONLY '{target.name}'.\n"
            f"  - Do NOT modify test files, design.mmd, spec.gherkin, or any other file.\n"
            f"  - Do NOT change test assertions to match broken logic — fix the logic.\n"
            f"  - Do NOT add new public functions or change existing signatures.\n"
            f"  - Fix the ROOT CAUSE of the failure, not just the symptom.\n\n"
            f"<test_failure_log>\n"
            f"{error_output}\n"
            f"</test_failure_log>"
        )

        print(f"  → Invoking {agent} (self-correction cycle {human_attempt_num}/{max_retries})…\n")
        run_opencode(
            agent=agent,
            prompt=correction_prompt,
            files=files,
        )
        # Loop continues → test suite is re-run at the top of the next iteration


# ─────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def _build_arg_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipeline_v3.py",
        description=(
            f"v{PIPELINE_VERSION} AI Factory Pipeline — Full 8-pass state machine\n"
            "\n"
            "Passes:\n"
            "  0  Design        (claude-sonnet)      → design.mmd + spec.gherkin\n"
            "     [HUMAN-IN-THE-LOOP gate]\n"
            "  1  Contracts     (claude-3.7-sonnet)  → type stubs in target file\n"
            "  2  Tests         (deepseek-v4-pro)    → test file  [Red Phase]\n"
            "  3  Core Logic    (deepseek-v4-pro)    → implementation [Green Phase]\n"
            "     [self-correction loop: max 2 retries]\n"
            "  4  Refactor      (deepseek-coder-v4)  → complexity/DRY cleanup\n"
            "     [self-correction loop: max 2 retries]\n"
            "  5  Security      (gpt-4.5-turbo)      → OWASP mitigations\n"
            "     [self-correction loop: max 2 retries]\n"
            "  6  Observability (deepseek-coder-v4)  → logging + error classes\n"
            "     [self-correction loop: max 2 retries]\n"
            "  7  Docs          (deepseek-v4-pro)    → docstrings + @see links\n\n"
            "  git commit fired after every pass (1-7)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "target_file",
        metavar="TARGET_FILE",
        type=Path,
        help="Source file to run the pipeline against.  Example: src/calculator.py",
    )

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


# ─────────────────────────────────────────────────────────────────────────────
# Main pipeline — the state machine
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point — orchestrate all 8 pipeline passes end-to-end.

    The function is one long sequential state machine.  Each block is labelled
    with its pass number, agent, and rationale from the architecture manifesto.
    Heavy commenting is intentional: the developer should be able to read this
    function top-to-bottom and understand exactly what each AI agent is doing
    and why it is doing it.
    """

    # ── Parse CLI arguments ──────────────────────────────────────────────────
    args = _build_arg_parser().parse_args()

    target: Path = args.target_file.resolve()
    target_dir: Path = target.parent

    # ── Derive artefact paths —————————————————————————────————————————————————
    # Design artefacts (from Pass 0) live alongside the target for discoverability.
    design_mmd:    Path = target_dir / "design.mmd"
    spec_gherkin:  Path = target_dir / "spec.gherkin"

    # Test file follows language conventions:
    #   Python:     calculator_test.py
    #   JS/TS:      calculator.test.ts
    _stem = target.stem
    _ext  = target.suffix
    _test_name = (
        f"{_stem}_test{_ext}" if _ext == ".py"
        else f"{_stem}.test{_ext}"
    )
    test_file: Path = target_dir / _test_name

    # ── Environment setup ────────────────────────────────────────────────────
    load_dot_env()
    preflight_checks(target)

    # ── Resolve test command ─────────────────────────────────────────────────
    if args.test_cmd:
        test_cmd: list[str] = shlex.split(args.test_cmd)
    else:
        test_cmd = infer_test_command(target)

    # ── Print startup banner ─────────────────────────────────────────────────
    _banner(target, test_cmd, args.skip_hitl)

    # ════════════════════════════════════════════════════════════════════════
    # PASS 0 — Design & Architecture  (claude-sonnet-4.6)
    #
    # Goal:
    #   Analyse the target source file and produce two human-reviewable
    #   artefacts that serve as the architectural source of truth for every
    #   subsequent pass:
    #     design.mmd    — Mermaid state/sequence/flowchart diagram
    #     spec.gherkin  — BDD Given/When/Then scenarios
    #
    # Why Claude?
    #   Per manifesto §3.2: "Claude is the industry leader in Constitutional
    #   Adherence and Systems Design. It excels at reading messy tickets and
    #   translating them into flawless Mermaid boundaries without hallucinating
    #   premature code."
    #
    # Gate:
    #   Human-in-the-Loop review before any code is written (see §1.2).
    #   No git commit at Pass 0 — the commit happens at Pass 1 after HITL.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 0 — {PASS_LABELS[0]}  [{AGENTS[0]}]")

    design_prompt = (
        f"You are running as Pass 0 (Design & Architecture) of the v{PIPELINE_VERSION} "
        f"AI Factory pipeline.\n\n"
        f"Analyse the attached source file and produce exactly two artefact files.\n\n"
        f"ARTEFACT 1 — Mermaid diagram\n"
        f"  Write to: {design_mmd}\n"
        f"  Use stateDiagram-v2, sequenceDiagram, or flowchart TD — whichever best\n"
        f"  represents the logic.  Include a header comment block:\n"
        f"    %% Module: {target.name}\n"
        f"    %% Generated by: {AGENTS[0]}  Pipeline: v{PIPELINE_VERSION}\n\n"
        f"ARTEFACT 2 — Gherkin specification\n"
        f"  Write to: {spec_gherkin}\n"
        f"  One Feature block.  Minimum three Scenarios: happy path, edge case,\n"
        f"  error/exception case.  Use concrete values (no <placeholder> tokens).\n\n"
        f"STRICT RULES:\n"
        f"  - Do NOT modify {target.name}.\n"
        f"  - Do NOT write executable code of any kind.\n"
        f"  - Output ONLY {design_mmd.name} and {spec_gherkin.name}.\n"
        f"  - Mermaid syntax must be valid and renderable by mermaid.js v10+."
    )

    run_opencode(
        agent=AGENTS[0],
        prompt=design_prompt,
        files=[target],
    )
    _pass_ok(f"Pass 0 — {PASS_LABELS[0]}")

    # ════════════════════════════════════════════════════════════════════════
    # HUMAN-IN-THE-LOOP GATE
    #
    # The developer reviews design.mmd and spec.gherkin before a single line
    # of production code is written or modified.
    #
    # This is the primary checkpoint against LLM hallucination (manifesto §1.2):
    #   - A 50-token diagram is far easier to verify than 500 lines of code.
    #   - Forcing AI to map a state machine first enforces Architectural
    #     Chain-of-Thought and virtually eliminates logical hallucinations.
    #
    # Ctrl+C → clean exit with zero error code.  No code is written.
    # Enter  → pipeline advances to Pass 1.
    # ════════════════════════════════════════════════════════════════════════
    if not args.skip_hitl:
        hitl_gate(design_mmd, spec_gherkin)
    else:
        print("  [--skip-hitl]  Skipping human approval gate.\n")

    # ════════════════════════════════════════════════════════════════════════
    # PASS 1 — Contracts & Types  (claude-3.7-sonnet)
    #
    # Goal:
    #   Define the strict API boundaries for the module.  For Python: Pydantic
    #   models, TypedDicts, dataclasses, Protocols.  For TypeScript: interfaces,
    #   types, enums.  These become the binding contract that Pass 3 implements.
    #
    # Why Claude?
    #   Contracts require precise reasoning about Mermaid state transitions and
    #   Gherkin scenarios simultaneously.  Claude's constitutional adherence
    #   minimises schema hallucination.
    #
    # Gate: none (no tests expected to pass at this stage)
    # Git:  commit after completion.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 1 — {PASS_LABELS[1]}  [{AGENTS[1]}]")

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
        f"  - Do NOT write business logic — stubs only.\n"
        f"  - Do NOT modify {design_mmd.name} or {spec_gherkin.name}."
    )

    run_opencode(
        agent=AGENTS[1],
        prompt=contracts_prompt,
        files=[target, design_mmd, spec_gherkin],
    )
    _pass_ok(f"Pass 1 — {PASS_LABELS[1]}")

    # Atomic commit: the target file now contains the type contract baseline.
    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 1 — {PASS_LABELS[1]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # PASS 2 — TDD Test Generation  (deepseek-v4-pro)  [Red Phase]
    #
    # Goal:
    #   Write a comprehensive, failing test suite derived from spec.gherkin
    #   and the Pass 1 type contracts.  The tests are the executable constraints
    #   for the implementation pass.  They are EXPECTED to fail at this stage —
    #   that failure is proof the constraints are real (Red Phase).
    #
    # Why DeepSeek?
    #   Structured code generation at algorithmic precision; matches frontier
    #   models for this task at ~10% of the cost (manifesto §3.2).
    #
    # Convention: test file is co-located with the target:
    #   Python →  <stem>_test.py
    #   JS/TS  →  <stem>.test.ts
    #
    # Gate: no test gate here — tests are EXPECTED to fail (Red Phase)
    # Git:  commit the new test file after generation.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 2 — {PASS_LABELS[2]}  [{AGENTS[2]}]")

    test_gen_prompt = (
        f"You are running as Pass 2 (TDD Test Generation — Red Phase) of the "
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
        f"  - Create ONLY '{_test_name}' — no other files."
    )

    run_opencode(
        agent=AGENTS[2],
        prompt=test_gen_prompt,
        files=[target, design_mmd, spec_gherkin],
    )
    _pass_ok(f"Pass 2 — {PASS_LABELS[2]}")

    # Atomic commit: the test file captures the Red Phase constraints.
    # Note: we commit the TEST file here, not the target file, because the
    # target was not modified by the test-generation agent.
    git_commit(
        files=[test_file],
        message=f"chore(ai): completed Pass 2 — {PASS_LABELS[2]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # PASS 3 — Core Implementation  (deepseek-v4-pro)  [Green Phase]
    #
    # Goal:
    #   Write the algorithmic logic that makes the Pass 2 tests pass.
    #   design.mmd is the binding architectural contract — the agent must
    #   implement exactly the state machine depicted there.
    #
    # Gate:
    #   LOCAL TEST SUITE — run via subprocess, deterministic, unfakeable.
    #   Self-correction loop: up to MAX_CORRECTION_RETRIES retries.
    #   If all attempts fail → pipeline aborts for human review.
    #
    # Git:  commit after tests pass.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 3 — {PASS_LABELS[3]}  [{AGENTS[3]}]")

    impl_prompt = (
        f"You are running as Pass 3 (Core Implementation — Green Phase) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached files:\n"
        f"  Source file to implement:  {target}\n"
        f"  Architecture constraint:   {design_mmd}\n"
        f"  Behavioural specification: {spec_gherkin}\n\n"
        f"Your task:\n"
        f"  Implement the business logic in '{target.name}' so all tests in\n"
        f"  '{_test_name}' pass.  The diagram in '{design_mmd.name}' is your\n"
        f"  binding architectural contract — deviate from it only if the test\n"
        f"  failures prove the diagram is wrong (and leave a comment explaining).\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT modify the test file, {design_mmd.name}, or {spec_gherkin.name}.\n"
        f"  - Do NOT add documentation blocks — that is Pass 7's job.\n"
        f"  - Do NOT add logging — that is Pass 6's job.\n"
        f"  - Do NOT deviate from the type contracts established in Pass 1."
    )

    # This pass uses the self-correction loop: agent is called, tests are run,
    # and on failure the agent is re-invoked with the error log.
    run_pass_with_self_correction(
        pass_num=3,
        agent=AGENTS[3],
        initial_prompt=impl_prompt,
        files=[target, design_mmd, spec_gherkin],
        target=target,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 3 — {PASS_LABELS[3]}")

    # Atomic commit: the target file now has passing core logic.
    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 3 — {PASS_LABELS[3]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # PASS 4 — Refactor & Optimise  (deepseek-coder-v4)
    #
    # Goal:
    #   Reduce cyclomatic complexity, enforce DRY, and improve algorithmic
    #   efficiency WITHOUT changing observable behaviour.  The test suite is
    #   the behavioral contract — it must still pass after every change.
    #
    # Gate:  Local test suite + self-correction loop (max 2 retries).
    # Git:   Commit after tests pass.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 4 — {PASS_LABELS[4]}  [{AGENTS[4]}]")

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
        pass_num=4,
        agent=AGENTS[4],
        initial_prompt=refactor_prompt,
        files=[target],
        target=target,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 4 — {PASS_LABELS[4]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 4 — {PASS_LABELS[4]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # PASS 5 — Security Hardening  (gpt-4.5-turbo)
    #
    # Goal:
    #   Add input sanitisation, OWASP Top-10 mitigations, and boundary
    #   validation.  GPT-4.5 is selected for its deep RLHF-based red-team
    #   mindset (manifesto §3.2): "We pay the premium token cost here to
    #   leverage its deep red-teaming mindset to spot injection flaws."
    #
    # Gate:  Local test suite + self-correction loop (max 2 retries).
    # Git:   Commit after tests pass.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 5 — {PASS_LABELS[5]}  [{AGENTS[5]}]")

    security_prompt = (
        f"You are running as Pass 5 (Security Hardening) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached file (the ONLY file you may modify): {target}\n\n"
        f"The code has passed Tests (Pass 3) and Refactor (Pass 4). Your task:\n"
        f"  Apply your security_checklist (OWASP Top-10) to '{target.name}'.\n"
        f"  Add input validation, sanitisation, and boundary checks.\n"
        f"  Mark every change with an inline comment: '# SEC: <category> — <reason>'.\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY '{target.name}'.\n"
        f"  - Do NOT change business logic or function signatures.\n"
        f"  - Do NOT modify test files or design artefacts.\n"
        f"  - All new validation must raise descriptive exceptions (not swallow them)."
    )

    run_pass_with_self_correction(
        pass_num=5,
        agent=AGENTS[5],
        initial_prompt=security_prompt,
        files=[target],
        target=target,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 5 — {PASS_LABELS[5]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 5 — {PASS_LABELS[5]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # PASS 6 — Observability & Logging  (deepseek-coder-v4)
    #
    # Goal:
    #   Add structured JSON logging, try/except error handling, and custom
    #   exception classes.  Every public function must have entry/exit log
    #   lines and a top-level error-catching wrapper.
    #
    # Gate:  Local test suite + self-correction loop (max 2 retries).
    # Git:   Commit after tests pass.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 6 — {PASS_LABELS[6]}  [{AGENTS[6]}]")

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
        f"  - Do NOT use print() — use the logging module (Python) or a logger.\n"
        f"  - Do NOT modify test files or design artefacts.\n"
        f"  - Custom exception classes must be defined in this file, not imported."
    )

    run_pass_with_self_correction(
        pass_num=6,
        agent=AGENTS[6],
        initial_prompt=observability_prompt,
        files=[target],
        target=target,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 6 — {PASS_LABELS[6]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 6 — {PASS_LABELS[6]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # PASS 7 — Documentation  (deepseek-v4-pro)
    #
    # Goal:
    #   Add complete JSDoc / Python docstrings to the finalised implementation.
    #   Crucially, every public function must include a @see / See Also link
    #   back to design.mmd — this is the Traceability Matrix requirement from
    #   manifesto §1.3 (Eliminating Specification Drift).
    #   "By utilizing @see links pointing directly to local .mmd files, human
    #   developers can instantly trace complex AI-generated code back to the
    #   exact state transition diagram that dictated it."
    #
    # Gate: no test gate (docs-only pass, no logic changes)
    # Git:  commit after completion.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(f"Pass 7 — {PASS_LABELS[7]}  [{AGENTS[7]}]")

    docs_prompt = (
        f"You are running as Pass 7 (Documentation) of the "
        f"v{PIPELINE_VERSION} AI Factory pipeline.\n\n"
        f"Attached file (the ONLY file you may modify): {target}\n\n"
        f"This is the finalised implementation after TDD, Refactor, Security,\n"
        f"and Observability passes.  Your task — add complete documentation:\n"
        f"  1. A module-level docstring describing the purpose, architecture,\n"
        f"     and the pipeline version that produced this file.\n"
        f"  2. JSDoc (JS/TS) or Python docstrings for every public function/class.\n"
        f"  3. @param / Args, @returns / Returns, @throws / Raises sections.\n"
        f"  4. An @see / See Also link pointing to '{design_mmd.name}' on\n"
        f"     every public function — this is the Traceability Matrix link.\n"
        f"     It lets any developer navigate from code to the architectural\n"
        f"     diagram that dictated it.  This is MANDATORY.\n\n"
        f"STRICT RULES:\n"
        f"  - Edit ONLY '{target.name}' — comments and docstrings ONLY.\n"
        f"  - Do NOT change any logic, variable names, or control flow.\n"
        f"  - Do NOT modify the test file, {design_mmd.name}, or {spec_gherkin.name}."
    )

    run_opencode(
        agent=AGENTS[7],
        prompt=docs_prompt,
        files=[target],
    )
    _pass_ok(f"Pass 7 — {PASS_LABELS[7]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 7 — {PASS_LABELS[7]}",
    )

    # ════════════════════════════════════════════════════════════════════════
    # Final summary
    # ════════════════════════════════════════════════════════════════════════
    _max_path = _W - 22

    def _fp(p: Path) -> str:
        """Truncate a path for display in the summary box."""
        s = str(p)
        return ("…" + s[-(_max_path - 1):]) if len(s) > _max_path else s

    print()
    print("┌" + "─" * _W + "┐")
    print(f"│  v{PIPELINE_VERSION} Pipeline complete — all 8 passes ran successfully."
          + " " * (_W - 55) + "│")
    print("│" + " " * _W + "│")
    print(f"│  Target file    : {_fp(target):<{_max_path}}│")
    print("│" + " " * _W + "│")
    print("│  Artefacts:" + " " * (_W - 11) + "│")
    print(f"│    design.mmd   : {_fp(design_mmd):<{_max_path}}│")
    print(f"│    spec.gherkin : {_fp(spec_gherkin):<{_max_path}}│")
    print(f"│    test file    : {_fp(test_file):<{_max_path}}│")
    print(f"│    source file  : {_fp(target):<{_max_path}}│")
    print("│" + " " * _W + "│")
    print("│  Git:  7 atomic commits created (Passes 1–7)." + " " * (_W - 47) + "│")
    print("│  Next: git log --oneline  to review the commit trail." + " " * (_W - 54) + "│")
    print("│        Open a PR when satisfied." + " " * (_W - 33) + "│")
    print("└" + "─" * _W + "┘")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C outside the HITL gate (e.g. during an opencode pass).
        # Partial changes may exist on disk — inform the developer.
        print(
            "\n\n  Pipeline interrupted by user.\n"
            "  Partial changes may exist — run:  git diff\n"
            "  To resume from a specific pass, re-run with --skip-hitl.\n"
        )
        sys.exit(0)
    except subprocess.CalledProcessError as exc:
        # opencode exited non-zero — surface the command that failed.
        # This is distinct from a test failure: it means the agent CLI itself
        # crashed, not that the tests failed.
        cmd_str = " ".join(str(a) for a in exc.cmd)
        print(
            f"\n[FATAL]  opencode exited with code {exc.returncode}.\n"
            f"  Command: {cmd_str}\n"
            f"  Check the terminal output above for details.\n",
            file=sys.stderr,
        )
        sys.exit(1)
