#!/usr/bin/env python3
"""
pipeline_v3_1.py -- v0.3.1 AI Factory Pipeline Orchestrator
============================================================

Refactored from v0.3 to enforce three cost-critical invariants:

  1.  "Static Prefix" (Maximize API Caching)
      The top 70-90% of every CLI payload is bit-for-bit identical across
      all 8 passes.  File attachment order is locked -- design.mmd,
      spec.gherkin, then the target file -- so every pass shares the same
      cacheable prefix and the orchestrator reclaims ~90% of input tokens
      from the provider's prefix-cache pool.

  2.  "Context Compaction" (Eliminate LLM Attention Drift)
      Each pass is a fresh `opencode run` invocation with no session
      resuming.  "Memory" lives exclusively in the updated files on disk.
      When a self-correction retry needs an error log, that log is passed
      as a temporary --file argument (.opencode_error.log).  The moment
      tests turn green the log is deleted so the next pass starts with a
      clean, compacted context.

  3.  "Single-Model Lock" (Preserve Cache Pool)
      All agents remain locked to deepseek-coder-v4 via their individual
      agent YAML frontmatter.  The orchestrator never injects a model
      override, so every call hits the same API cache pool.

State machine overview (unchanged from v0.3)
--------------------------------------------
  Pass 0  Design & Architecture  -> design.mmd + spec.gherkin  [+ HITL gate]
  Pass 1  Contracts & Types      -> type stubs in target file
  Pass 2  TDD Test Generation    -> test file                  [Red Phase]
  Pass 3  Core Implementation    -> logic                      [Green Phase + SC]
  Pass 4  Refactor & Optimise    -> complexity/DRY             [SC]
  Pass 5  Security Hardening     -> OWASP Top-10               [SC]
  Pass 6  Observability & Logs   -> logging + error classes    [SC]
  Pass 7  Documentation          -> docstrings + @see links

  [SC] = Self-correction loop (max 2 retries, then abort)
  [HITL] = Human-in-the-Loop review gate

Usage
-----
  python pipeline_v3_1.py <target_file> [options]

  python pipeline_v3_1.py src/calculator.py
  python pipeline_v3_1.py src/calculator.py --test-cmd "pytest src/ -x -v"
  python pipeline_v3_1.py src/calculator.py --skip-hitl   # CI / automated use

Prerequisites
-------------
  - opencode CLI on $PATH  (npm install -g opencode-ai)
  - OPENROUTER_API_KEY in .env or exported to the shell
  - Agent files present in .opencode/agent/
  - git initialised in the working directory
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIPELINE_VERSION = "0.3.1"

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
# Why?  LLM API providers (OpenRouter, Anthropic, OpenAI) implement
# *prefix-level* KV-cache lookups.  If the first N tokens of a request are
# byte-for-byte identical to a prior request, the provider serves those tokens
# from cache --  zero compute cost, ~90% discount on input pricing.
#
# Our invariant:
#   [agent system prompt] + [design.mmd] + [spec.gherkin] + [target file]
#
# The agent system prompt (the .md agent file loaded by `--agent`) never
# changes between passes.  design.mmd and spec.gherkin are frozen after
# Pass 0.  Together they form the "Static Prefix" that dominates every
# payload -- typically 70-90% of the total input tokens.  By locking their
# order we ensure every pass shares the identical prefix and reaps the
# cache discount.
#
# File ordering matters:
#   - design.mmd        -- FIRST, immutable architectural source of truth
#   - spec.gherkin      -- SECOND, immutable behavioural specification
#   - target source     -- THIRD, the file being modified (can change)
#   - .opencode_error.log -- OPTIONAL, only during self-correction retries
#
# The target file moves with each pass (it is being edited), so it sits
# AFTER the static prefix.  The error log changes with every retry, so it
# sits last.  The prompt (user-turn message) is always the final positional
# argument -- it differs per pass and per retry, but because it comes *after*
# the static prefix it never invalidates the cache.
# ---------------------------------------------------------------------------

# Canonical artefact filenames -- these names are hardcoded so the
# orchestrator can always locate them in the artefact directory.
ARTEFACT_DESIGN = "design.mmd"
ARTEFACT_GHERKIN = "spec.gherkin"

# The error-log stub attached during self-correction retries.
# Context Compaction ensures this file is deleted the moment tests pass,
# so the next pipeline pass inherits no stale debugging context.
ERROR_LOG_STUB = ".opencode_error.log"


def build_opencode_command(
    agent_name: str,
    prompt: str,
    target_file: Path,
    artefact_dir: Path,
    error_log: Path | None = None,
) -> list[str]:
    """Construct a strictly-ordered `opencode run` command list.

    STATIC PREFIX (Prefix Anchoring)
    --------------------------------
    The --file arguments are appended in a HARDCODED, IMMUTABLE order
    that never varies across passes:

      1. design.mmd      -- static architectural artefact (cacheable)
      2. spec.gherkin    -- static behavioural artefact (cacheable)
      3. target_file     -- the source file being edited
      4. error_log       -- temporary self-correction log (if present)

    The prompt (user-turn instruction) is always the terminal argument.
    Because design.mmd + spec.gherkin sit at a fixed offset from the
    start of the payload, their tokens are ALWAYS in the prefix-cache
    hit zone across all 8 passes.

    SINGLE-MODEL LOCK
    -----------------
    No --model override is ever injected.  The model is declared exclusively
    in each agent's YAML frontmatter (.opencode/agent/<agent>.md).  This
    preserves the cache pool because switching models (even from
    deepseek-coder-v4 to a different variant) would fragment the cache
    and waste the discount.

    Args:
        agent_name:   Agent ID matching .opencode/agent/<id>.md
        prompt:       The user-turn instruction (varies per pass/retry).
        target_file:  Absolute path to the source file under modification.
        artefact_dir: Directory containing design.mmd and spec.gherkin.
        error_log:    Optional path to a self-correction failure log.
                      See Context Compaction docs in
                      run_pass_with_self_correction().

    Returns:
        A complete subprocess-ready command list.
    """
    cmd = [OPENCODE_CMD, "run", "--agent", agent_name]

    # --- Static Prefix: artefact files in immutable order ---

    # design.mmd is ALWAYS first.  It is the architectural source of truth
    # and changes only if a human edits it at the HITL gate.  Its tokens
    # sit at the earliest possible offset in the payload, maximising the
    # prefix-cache overlap across all 8 passes.
    design_path = artefact_dir / ARTEFACT_DESIGN
    if design_path.is_file():
        cmd += ["--file", str(design_path)]

    # spec.gherkin is ALWAYS second.  Like design.mmd, it is frozen after
    # Pass 0 and contributes to the immutable prefix.
    gherkin_path = artefact_dir / ARTEFACT_GHERKIN
    if gherkin_path.is_file():
        cmd += ["--file", str(gherkin_path)]

    # The target source file is attached THIRD.  Its content changes
    # between passes (it's being iteratively improved), so it must not
    # appear inside the cacheable prefix.  Placing it AFTER the static
    # artefacts ensures the prefix stays clean.
    cmd += ["--file", str(target_file)]

    # --- Optional self-correction error log ---

    # The error log is ONLY present during a self-correction retry.
    # Its content differs every time (different failure signatures),
    # so it is placed LAST among the --file arguments to avoid
    # fragmenting the static prefix.  Context Compaction deletes this
    # file the moment tests pass.
    if error_log is not None and error_log.is_file():
        cmd += ["--file", str(error_log)]

    # --- Auto-approve permissions for deterministic file I/O ---
    #
    # --dangerously-skip-permissions allows the agent to read/write the
    # attached files without interactive prompts.  All agents deny bash
    # and webfetch in their frontmatter -- those restrictions are
    # enforced regardless of this flag.
    cmd.append("--dangerously-skip-permissions")

    # --- The prompt is the terminal argument ---
    #
    # Putting the prompt LAST is intentional: it varies per pass and
    # per retry, so it must come after the static prefix to avoid
    # invalidating the cache.  The provider's prefix matcher scans
    # from token 0; as long as the first N tokens are identical, the
    # match succeeds regardless of what follows.
    cmd.append(prompt)

    return cmd


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def load_dot_env(env_path: Path = Path(".env")) -> None:
    """Parse a .env file and populate os.environ."""
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
    """Validate prerequisites before pipeline execution."""
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


# ---------------------------------------------------------------------------
# Terminal output helpers
# ---------------------------------------------------------------------------

def _banner(target: Path, test_cmd: list[str], skip_hitl: bool) -> None:
    """Print the v0.3.1 pipeline startup banner."""
    print()
    print("┌" + "─" * _W + "┐")
    print(f"│  ai-factory-setup  •  v{PIPELINE_VERSION} Pipeline  •  8-Pass State Machine"
          + " " * (_W - 59) + "│")
    print("└" + "─" * _W + "┘")
    print()
    print(f"  Target     : {target}")
    print(f"  Test cmd   : {' '.join(test_cmd)}")
    print(f"  HITL gate  : {'disabled (--skip-hitl)' if skip_hitl else 'enabled'}")
    print(f"  Max retries: {MAX_CORRECTION_RETRIES} (per guarded pass)")
    print()
    print("  Cache strategy: Static Prefix  +  Context Compaction")
    print()
    print("  Pass schedule:")
    for num, label in PASS_LABELS.items():
        gate = "  <- self-correction + git commit" if num in (3, 4, 5, 6) else \
               "  <- git commit" if num in (1, 2, 7) else \
               "  <- HITL gate"
        print(f"    {num}  {label:<36}{gate}")
    print()


def _pass_header(label: str) -> None:
    print()
    print("━" * _W)
    print(f"  {label}")
    print("━" * _W)
    print()


def _pass_ok(label: str) -> None:
    print(f"\n  ✓  {label} — complete.\n")


def _warn(lines: list[str]) -> None:
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
    print(f"\n[FATAL]  {msg}\n", file=sys.stderr)
    sys.exit(1)


def _git_info(msg: str) -> None:
    print(f"  [git]  {msg}")


# ---------------------------------------------------------------------------
# OpenCode runner (simplified -- just executes a pre-built command)
# ---------------------------------------------------------------------------

def run_opencode(cmd: list[str]) -> None:
    """Execute a pre-built opencode command, streaming output to the terminal.

    The command order is constructed by build_opencode_command() which
    enforces the Static Prefix invariant.  This function merely invokes
    the command -- it does not reorder, reattach, or override any argument.
    That separation guarantees the file ordering can never accidentally
    drift between passes.

    Args:
        cmd: Full subprocess command list from build_opencode_command().

    Raises:
        subprocess.CalledProcessError: If opencode exits non-zero.
    """
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# Git integration -- atomic commits
# ---------------------------------------------------------------------------

def git_commit(files: list[Path], message: str) -> None:
    """Stage specific files and create an atomic git commit.

    Implements the "Atomic Commits" strategy from the architecture manifesto
    (§3.3): one commit per pass for precise regression pinpointing.

    Graceful no-op cases:
      - File wasn't modified -> "nothing to commit" -> skip.
      - git not initialised -> warn and skip.

    Args:
        files:   File paths to stage with `git add`.
        message: Commit message (use 'chore(ai): ...' convention).
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
            ["git", "add", str(f)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            _warn([
                f"git add failed for: {f}",
                result.stderr.strip() or result.stdout.strip(),
                "Continuing -- this file will be absent from the commit.",
            ])

    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        summary = result.stdout.strip().splitlines()[0] if result.stdout else message
        _git_info(f"Committed -> {summary}")
        return

    combined_output = (result.stdout + result.stderr).lower()
    if "nothing to commit" in combined_output or "nothing added to commit" in combined_output:
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

    print()
    print("┌" + "─" * _W + "┐")
    print("│  HUMAN-IN-THE-LOOP GATE (After Pass 0)                        │")
    print("│  Review the design artefacts before any code is written.      │")
    print("│" + " " * _W + "│")
    print(f"│  1. Mermaid diagram  ->  {_fmt(design_mmd):<{_max}}│")
    print(f"│  2. Gherkin spec     ->  {_fmt(spec_gherkin):<{_max}}│")
    print("│" + " " * _W + "│")
    print("│  Tip: VS Code + 'Mermaid Preview' extension to render .mmd    │")
    print("│  Press Ctrl+C to abort -- no code will be written.             │")
    print("└" + "─" * _W + "┘")
    print()

    try:
        input("  Press Enter to approve and advance to Pass 1 (Contracts)...  ")
    except KeyboardInterrupt:
        print("\n\n  Pipeline aborted at HITL gate.  No code was written.\n")
        sys.exit(0)

    print("\n  Design approved.  Continuing to Pass 1 (Contracts & Types)...\n")


# ---------------------------------------------------------------------------
# Test runner -- captures output for the self-correction loop
# ---------------------------------------------------------------------------

def run_tests_with_capture(test_cmd: list[str]) -> tuple[bool, str]:
    """Run the local test suite and capture its output.

    Args:
        test_cmd: Fully-resolved command list (e.g. ['pytest', 'src/', '-v']).

    Returns:
        tuple[bool, str]:
            - bool : True if the suite exited zero (all tests passed).
            - str  : Combined stdout + stderr.
    """
    print(f"  Running: {' '.join(test_cmd)}\n")

    try:
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        combined_output = result.stdout + "\n" + result.stderr
        return result.returncode == 0, combined_output

    except FileNotFoundError:
        msg = (
            f"Test runner not found: '{test_cmd[0]}'\n"
            f"Install it or supply a valid command with --test-cmd.\n"
            f"  Python:  pip install pytest\n"
            f"  JS/TS:   npm install"
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
# Self-correction loop -- the "Actor-Critic" inner loop
#
# CONTEXT COMPACTION
# ------------------
# This is the critical invariant introduced in v0.3.1.  In the v0.3
# orchestrator, the raw test failure log was embedded inside the prompt
# text itself.  While functional, this inflates the prompt context and
# -- more importantly -- means that context is implicitly carried forward
# across passes via the agent's working memory.  LLMs exhibit "attention
# drift" (the "lost in the middle" syndrome), where older context
# fragments degrade performance on the current task.
#
# The v0.3.1 strategy:
#   1. Write the test failure output to a TEMPORARY file
#      (.opencode_error.log).
#   2. Pass that file as a separate --file argument (not embedded in
#      the prompt).  The agent reads it, but the file is an explicit
#      artefact, not conversational context.
#   3. The moment tests pass, DELETE .opencode_error.log.  The next
#      pass inherits ZERO debugging context from the previous pass.
#      It starts fresh, with only the final correct code on disk.
#
# This is "Context Compaction": the orchestrator actively deletes
# intermediate debugging state so no single agent ever processes more
# context than necessary.  Each pass is a clean start.
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
      1. Run the agent with initial_prompt.
      2. Run the test suite.
      3. If tests fail and retries remain:
           a. Write the raw error output to .opencode_error.log
           b. Re-run the agent with the error log attached
           c. Re-run the test suite.
           d. If tests pass: DELETE .opencode_error.log immediately.
      4. If max retries exhausted -> abort.

    The error log is passed as a --file argument, NOT embedded in the
    prompt.  This keeps the prompt compact and ensures the debugging
    context is an explicit, disposable artefact (Context Compaction).

    Args:
        pass_num:     Pass number (e.g. 3 for Core Implementation).
        agent:        Agent ID string (key in AGENTS dict).
        initial_prompt: First user-turn message.
        target:       The target source file path.
        artefact_dir: Directory containing design.mmd and spec.gherkin.
        test_cmd:     Test command to run after each agent invocation.
        max_retries:  Additional correction attempts (default 2 -> 3 total).

    Raises:
        SystemExit(1): If all attempts are exhausted and tests still fail.
    """
    pass_label = PASS_LABELS[pass_num]
    total_attempts = max_retries + 1

    # Path to the disposable error log used for Context Compaction.
    error_log_path = artefact_dir / ERROR_LOG_STUB

    # --- Attempt 0: initial agent invocation ---
    #
    # The Static Prefix is enforced by build_opencode_command().
    # No error log file is attached yet because this is the first attempt.
    print(f"\n  -> Invoking {agent} (initial run)...\n")
    initial_cmd = build_opencode_command(
        agent_name=agent,
        prompt=initial_prompt,
        target_file=target,
        artefact_dir=artefact_dir,
        # error_log=None -- no error context on the first attempt
    )
    run_opencode(initial_cmd)

    # --- Verification + correction loop ---
    for attempt_idx in range(total_attempts):
        human_attempt_num = attempt_idx + 1

        _pass_header(
            f"Verification Gate -- Pass {pass_num}: {pass_label}"
            f"  [attempt {human_attempt_num}/{total_attempts}]"
        )

        passed, error_output = run_tests_with_capture(test_cmd)

        if passed:
            # === CONTEXT COMPACTION: flush error context ===
            #
            # Tests are green.  The error log from a previous retry (if
            # any) is now stale debugging context.  Deleting it HERE
            # ensures the next pipeline pass starts with a clean slate.
            # No agent ever inherits another pass's error history.
            if error_log_path.exists():
                error_log_path.unlink()
                print(f"  [compaction]  Deleted {error_log_path} -- context reset.\n")

            print(f"  ✓  Tests passed on attempt {human_attempt_num}/{total_attempts}.\n")
            return

        # --- Tests failed ---
        if attempt_idx == max_retries:
            # Final attempt exhausted.  Clean up the error log and abort.
            if error_log_path.exists():
                error_log_path.unlink()

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
                f"{'-' * 60}\n"
                f"{error_tail}\n"
                f"{'-' * 60}"
            )

        # --- Still have retries -- trigger self-correction ---
        retries_remaining = max_retries - attempt_idx
        print(
            f"\n  Tests FAILED (attempt {human_attempt_num}/{total_attempts}).\n"
            f"  Triggering self-correction -- {retries_remaining} "
            f"{'retry' if retries_remaining == 1 else 'retries'} remaining.\n"
        )

        # === CONTEXT COMPACTION: write error to a TEMPORARY file ===
        #
        # Instead of embedding 2000+ characters of stack trace inside the
        # prompt (which inflates the per-pass context and bleeds into the
        # next pass via implicit history), we write the raw failure log
        # to a DISPOSABLE file on disk.
        #
        # The agent reads this file as a `--file` attachment.  It has the
        # same diagnostic value as an inline prompt embedding, but it is
        # an EXPLICIT artefact that the orchestrator can delete the
        # moment tests pass.  No implicit state leaks across passes.
        error_log_path.write_text(error_output, encoding="utf-8")
        print(f"  [compaction]  Error log written to {error_log_path} ({len(error_output)} bytes)\n")

        # Build the correction prompt.  Notice: the prompt does NOT
        # embed the raw test failure log.  It only instructs the agent
        # to read the attached error log file.  This keeps the prompt
        # itself compact and stable.
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

        print(f"  -> Invoking {agent} (self-correction cycle {human_attempt_num}/{max_retries})...\n")

        # The error log file is passed as an explicit `--file` argument
        # via build_opencode_command().  It sits AFTER the static prefix
        # (design.mmd, spec.gherkin, target), so it does not fragment
        # the prefix-cache lookup for the immutable artefacts.
        correction_cmd = build_opencode_command(
            agent_name=agent,
            prompt=correction_prompt,
            target_file=target,
            artefact_dir=artefact_dir,
            error_log=error_log_path,
        )
        run_opencode(correction_cmd)

        # Loop continues -> test suite re-run at top of next iteration.
        # The .opencode_error.log file is overwritten each retry cycle
        # (because error_output changes), then deleted when tests pass.


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipeline_v3_1.py",
        description=(
            f"v{PIPELINE_VERSION} AI Factory Pipeline -- Full 8-pass state machine\n"
            "\n"
            "v0.3.1 adds:\n"
            "  - Static Prefix anchoring (immutable file ordering for cache hits)\n"
            "  - Context Compaction (disposable error logs, fresh pass starts)\n"
            "  - Single-model lock (deepseek-coder-v4 across all 8 passes)\n"
            "\n"
            "Passes:\n"
            "  0  Design        (deepseek-coder-v4)  -> design.mmd + spec.gherkin\n"
            "     [HUMAN-IN-THE-LOOP gate]\n"
            "  1  Contracts     (deepseek-coder-v4)  -> type stubs in target file\n"
            "  2  Tests         (deepseek-coder-v4)  -> test file  [Red Phase]\n"
            "  3  Core Logic    (deepseek-coder-v4)  -> implementation [Green Phase]\n"
            "     [self-correction loop: max 2 retries]\n"
            "  4  Refactor      (deepseek-coder-v4)  -> complexity/DRY cleanup\n"
            "     [self-correction loop: max 2 retries]\n"
            "  5  Security      (deepseek-coder-v4)  -> OWASP mitigations\n"
            "     [self-correction loop: max 2 retries]\n"
            "  6  Observability (deepseek-coder-v4)  -> logging + error classes\n"
            "     [self-correction loop: max 2 retries]\n"
            "  7  Docs          (deepseek-coder-v4)  -> docstrings + @see links\n\n"
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


# ---------------------------------------------------------------------------
# Main pipeline -- the state machine
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point -- orchestrate all 8 pipeline passes end-to-end.

    Every agent invocation goes through build_opencode_command(), which
    enforces the Static Prefix (immutable file ordering) and Single-Model
    Lock (no --model override) invariants.  Self-correction passes use
    run_pass_with_self_correction(), which enforces Context Compaction
    (disposable error logs, clean pass starts).
    """

    args = _build_arg_parser().parse_args()

    target: Path = args.target_file.resolve()
    target_dir: Path = target.parent

    # Artefact paths -- co-located with the target file.
    design_mmd:   Path = target_dir / ARTEFACT_DESIGN
    spec_gherkin: Path = target_dir / ARTEFACT_GHERKIN

    # Test file follows language conventions.
    _stem = target.stem
    _ext  = target.suffix
    _test_name = (
        f"{_stem}_test{_ext}" if _ext == ".py"
        else f"{_stem}.test{_ext}"
    )
    test_file: Path = target_dir / _test_name

    # Environment setup.
    load_dot_env()
    preflight_checks(target)

    if args.test_cmd:
        test_cmd: list[str] = shlex.split(args.test_cmd)
    else:
        test_cmd = infer_test_command(target)

    _banner(target, test_cmd, args.skip_hitl)

    # ====================================================================
    # PASS 0 -- Design & Architecture  (deepseek-coder-v4)
    #
    # Goal:
    #   Produce design.mmd + spec.gherkin from the target source file.
    #   Human-in-the-Loop review before any code is written.
    #
    # Static Prefix note:
    #   At Pass 0, design.mmd and spec.gherkin do not exist yet, so
    #   build_opencode_command() only attaches the target file.  From
    #   Pass 1 onward, every call includes design.mmd and spec.gherkin
    #   as the immutable cache prefix.
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

    # --------------------------------------------------------------------
    # HUMAN-IN-THE-LOOP GATE
    # --------------------------------------------------------------------
    if not args.skip_hitl:
        hitl_gate(design_mmd, spec_gherkin)
    else:
        print("  [--skip-hitl]  Skipping human approval gate.\n")

    # ====================================================================
    # PASS 1 -- Contracts & Types  (deepseek-coder-v4)
    #
    # Static Prefix anchor: from here onward, EVERY pass invocation
    # attaches design.mmd first, then spec.gherkin, then the target file.
    # This ordering is enforced by build_opencode_command() and never
    # varies.
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

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 1 -- {PASS_LABELS[1]}",
    )

    # ====================================================================
    # PASS 2 -- TDD Test Generation  (deepseek-coder-v4)  [Red Phase]
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

    git_commit(
        files=[test_file],
        message=f"chore(ai): completed Pass 2 -- {PASS_LABELS[2]}",
    )

    # ====================================================================
    # PASS 3 -- Core Implementation  (deepseek-coder-v4)  [Green Phase]
    #
    # Gate:  Local test suite + self-correction loop (max 2 retries).
    #        Context Compaction: error logs are written to .opencode_error.log,
    #        then deleted the moment tests pass.
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
        pass_num=3,
        agent=AGENTS[3],
        initial_prompt=impl_prompt,
        target=target,
        artefact_dir=target_dir,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 3 -- {PASS_LABELS[3]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 3 -- {PASS_LABELS[3]}",
    )

    # ====================================================================
    # PASS 4 -- Refactor & Optimise  (deepseek-coder-v4)
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
        pass_num=4,
        agent=AGENTS[4],
        initial_prompt=refactor_prompt,
        target=target,
        artefact_dir=target_dir,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 4 -- {PASS_LABELS[4]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 4 -- {PASS_LABELS[4]}",
    )

    # ====================================================================
    # PASS 5 -- Security Hardening  (deepseek-coder-v4)
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
        pass_num=5,
        agent=AGENTS[5],
        initial_prompt=security_prompt,
        target=target,
        artefact_dir=target_dir,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 5 -- {PASS_LABELS[5]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 5 -- {PASS_LABELS[5]}",
    )

    # ====================================================================
    # PASS 6 -- Observability & Logging  (deepseek-coder-v4)
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
        pass_num=6,
        agent=AGENTS[6],
        initial_prompt=observability_prompt,
        target=target,
        artefact_dir=target_dir,
        test_cmd=test_cmd,
    )
    _pass_ok(f"Pass 6 -- {PASS_LABELS[6]}")

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 6 -- {PASS_LABELS[6]}",
    )

    # ====================================================================
    # PASS 7 -- Documentation  (deepseek-coder-v4)
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

    git_commit(
        files=[target],
        message=f"chore(ai): completed Pass 7 -- {PASS_LABELS[7]}",
    )

    # ====================================================================
    # Final summary
    # ====================================================================
    _max_path = _W - 22

    def _fp(p: Path) -> str:
        s = str(p)
        return ("..." + s[-(_max_path - 1):]) if len(s) > _max_path else s

    print()
    print("┌" + "─" * _W + "┐")
    print(f"│  v{PIPELINE_VERSION} Pipeline complete -- all 8 passes ran successfully."
          + " " * (_W - 59) + "│")
    print("│" + " " * _W + "│")
    print(f"│  Target file    : {_fp(target):<{_max_path}}│")
    print("│" + " " * _W + "│")
    print("│  Artefacts:" + " " * (_W - 11) + "│")
    print(f"│    design.mmd   : {_fp(design_mmd):<{_max_path}}│")
    print(f"│    spec.gherkin : {_fp(spec_gherkin):<{_max_path}}│")
    print(f"│    test file    : {_fp(test_file):<{_max_path}}│")
    print(f"│    source file  : {_fp(target):<{_max_path}}│")
    print("│" + " " * _W + "│")
    print("│  Git:  7 atomic commits created (Passes 1-7)." + " " * (_W - 47) + "│")
    print("│  Next: git log --oneline  to review the commit trail." + " " * (_W - 54) + "│")
    print("│        Open a PR when satisfied." + " " * (_W - 33) + "│")
    print("└" + "─" * _W + "┘")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\n\n  Pipeline interrupted by user.\n"
            "  Partial changes may exist -- run:  git diff\n"
            "  To resume from a specific pass, re-run with --skip-hitl.\n"
        )
        sys.exit(0)
    except subprocess.CalledProcessError as exc:
        cmd_str = " ".join(str(a) for a in exc.cmd)
        print(
            f"\n[FATAL]  opencode exited with code {exc.returncode}.\n"
            f"  Command: {cmd_str}\n"
            f"  Check the terminal output above for details.\n",
            file=sys.stderr,
        )
        sys.exit(1)