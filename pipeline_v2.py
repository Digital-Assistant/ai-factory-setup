#!/usr/bin/env python3
"""
pipeline_v2.py — v0.2 AI Factory Pipeline Orchestrator
=======================================================

Executes a four-pass AI-native development pipeline against a single
target source file, using OpenCode CLI as the agent runner.

Pipeline passes
---------------
  Pass 0  Design & Architecture  (Claude Sonnet 4.5)
          → Produces design.mmd + spec.gherkin
          → Human-in-the-Loop gate before any code is written

  Pass 1  Test Generation        (DeepSeek v4-pro)   [Red Phase]
          → Writes a test file derived from the Gherkin scenarios

  Pass 2  Core Implementation    (DeepSeek v4-pro)   [Green Phase]
          → Writes/improves source logic to satisfy Pass 1 tests
          → Verification gate: runs the local test suite via subprocess

  Pass 3  Documentation          (DeepSeek v4-pro)
          → Adds JSDoc / Python docstrings (no logic changes)

Usage
-----
  python pipeline_v2.py <target_file> [options]

  python pipeline_v2.py src/calculator.py
  python pipeline_v2.py src/calculator.py --test-cmd "pytest src/ -k calculator -v"
  python pipeline_v2.py src/calculator.py --skip-hitl   # CI / automated use

Prerequisites
-------------
  - opencode CLI on $PATH  (npm install -g opencode-ai)
  - OPENROUTER_API_KEY in .env or already exported to the shell
  - Agent files present in .opencode/agent/
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

PIPELINE_VERSION = "0.2"

# opencode CLI binary name — must be on $PATH
OPENCODE_CMD = "opencode"

# Maps logical pass names to agent IDs.
# Agent IDs must match filenames under .opencode/agent/<id>.md
AGENTS = {
    "design":     "pass-0-design-agent",
    "tests":      "test-generation-agent",
    "implement":  "core-implementation-agent",
    "docs":       "documentation-agent",
}

# Width for decorative box-drawing in terminal output
_W = 64


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

            # Skip blank lines and comments
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, _, raw_value = line.partition("=")

            # Strip inline comment, then surrounding quotes
            clean_value = raw_value.split("#")[0].strip().strip("'\"")

            # setdefault: shell env overrides .env
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
    """Print the pipeline startup banner."""
    print()
    print("┌" + "─" * _W + "┐")
    print(f"│  ai-factory-setup  •  v{PIPELINE_VERSION} Pipeline" + " " * (_W - 33) + "│")
    print("└" + "─" * _W + "┘")
    print()
    print(f"  Target     : {target}")
    print(f"  Test cmd   : {' '.join(test_cmd)}")
    print(f"  HITL gate  : {'disabled (--skip-hitl)' if skip_hitl else 'enabled'}")
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
    print(f"\n[ERROR]  {msg}\n", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# OpenCode runner
# ─────────────────────────────────────────────────────────────────────────────

def run_opencode(
    agent: str,
    prompt: str,
    files: list[Path],
) -> None:
    """Invoke `opencode run` for a single pipeline pass.

    Streams all output directly to the terminal so the developer sees
    live diffs and agent reasoning as they happen.  The model is NOT
    specified here — each agent's frontmatter owns its model declaration.
    This keeps model selection co-located with agent definitions and
    ensures `agents.xml` remains the single source of truth.

    Args:
        agent:  Agent ID matching .opencode/agent/<agent>.md
        prompt: The user-turn message sent to the agent.
        files:  Source files to attach to the message via repeated --file flags.

    Raises:
        subprocess.CalledProcessError: If opencode exits with a non-zero code.
        KeyboardInterrupt: Propagated as-is; handled by the caller.
    """
    cmd = [OPENCODE_CMD, "run", "--agent", agent]

    # Attach every file with its own --file flag (opencode supports repeats)
    for f in files:
        cmd += ["--file", str(f)]

    # Auto-approve permissions that aren't explicitly denied in the agent's
    # frontmatter.  Safe here because all agents deny bash and webfetch.
    cmd.append("--dangerously-skip-permissions")

    # The prompt is a positional argument(s) at the end of the command
    cmd.append(prompt)

    # Stream output live — no stdout/stderr capture
    subprocess.run(cmd, check=True)


# ─────────────────────────────────────────────────────────────────────────────
# Human-in-the-Loop gate
# ─────────────────────────────────────────────────────────────────────────────

def hitl_gate(design_mmd: Path, spec_gherkin: Path) -> None:
    """Block pipeline execution until the developer explicitly approves.

    This is the primary hallucination-prevention checkpoint.  The
    developer should:
      1. Open design.mmd in a Mermaid viewer (e.g. VS Code +
         'Mermaid Preview' extension, or mermaid.live).
      2. Verify the diagram accurately reflects the intended architecture.
      3. Open spec.gherkin and confirm the BDD scenarios are exhaustive.
      4. Press Enter only when satisfied.

    Pressing Ctrl+C triggers a clean, zero-error abort so the developer
    can edit the design artefacts manually before re-running.

    Args:
        design_mmd:   Path to the generated Mermaid diagram file.
        spec_gherkin: Path to the generated Gherkin specification file.
    """
    # Truncate long paths to fit in the box without wrapping
    _max = _W - 8

    def _fmt(p: Path) -> str:
        s = str(p)
        return ("…" + s[-(  _max - 1):]) if len(s) > _max else s

    print()
    print("┌" + "─" * _W + "┐")
    print("│  HUMAN-IN-THE-LOOP GATE                               │")
    print("│  Pass 0 is complete. Review before code is written.   │")
    print("│" + " " * _W + "│")
    print(f"│  1. Mermaid diagram  →  {_fmt(design_mmd):<{_max}}│")
    print(f"│  2. Gherkin spec     →  {_fmt(spec_gherkin):<{_max}}│")
    print("│" + " " * _W + "│")
    print("│  Tip: VS Code + 'Mermaid Preview' to render design.mmd│")
    print("└" + "─" * _W + "┘")
    print()

    try:
        input("  Press Enter to approve and continue, or Ctrl+C to abort: ")
    except KeyboardInterrupt:
        # Clean exit — not an error; developer chose to review/edit
        print("\n\n  Pipeline aborted at HITL gate.  No code was written.\n")
        sys.exit(0)

    print("\n  Approved. Continuing to Pass 1 (Test Generation)…\n")


# ─────────────────────────────────────────────────────────────────────────────
# Verification gate — local test runner
# ─────────────────────────────────────────────────────────────────────────────

def run_tests(test_cmd: list[str]) -> bool:
    """Run the local test suite via subprocess.

    Deliberately does NOT abort the pipeline on failure.  Failed tests
    are surfaced as a loud warning so the documentation pass can still
    run.  The developer reviews and iterates.

    Test output is streamed live (no capture) so failures are immediately
    visible in the terminal.

    Args:
        test_cmd: Fully-resolved command as a list (e.g. ['pytest', 'src/', '-v']).

    Returns:
        True if the suite exited zero (all tests passed), False otherwise.
    """
    print(f"  Running: {' '.join(test_cmd)}\n")

    try:
        result = subprocess.run(test_cmd)  # No check=True — we handle non-zero ourselves
        return result.returncode == 0
    except FileNotFoundError:
        # The test runner binary (pytest, npm, …) is not on PATH.
        # Surface this as a warning rather than crashing — the pipeline is
        # otherwise complete and the user can install the runner and re-test.
        _warn([
            f"Test runner not found: '{test_cmd[0]}'",
            "",
            "Install it or supply a valid command with --test-cmd.",
            f"  For Python:  pip install pytest",
            f"  For JS/TS:   npm install",
            "",
            f"Then re-run the suite manually:  {' '.join(test_cmd)}",
        ])
        return False


def infer_test_command(target_file: Path) -> list[str]:
    """Return a sensible default test command based on the file extension.

    The default pytest invocation runs the whole directory and uses
    short tracebacks so failures are easy to scan.  For JS/TS projects
    we delegate to npm test (which reads the project's package.json).

    Callers can always override this with --test-cmd.

    Args:
        target_file: Resolved path to the target source file.

    Returns:
        List of command components ready to pass to subprocess.run().
    """
    ext = target_file.suffix.lower()

    if ext == ".py":
        # pytest discovers test_*.py / *_test.py automatically in the dir
        return ["pytest", str(target_file.parent), "--tb=short", "-v"]

    if ext in (".js", ".mjs", ".cjs", ".jsx"):
        return ["npm", "test"]

    if ext in (".ts", ".tsx", ".mts"):
        return ["npm", "test"]

    # Generic fallback
    return ["pytest", str(target_file.parent), "--tb=short"]


# ─────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def _build_arg_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pipeline_v2.py",
        description=(
            "v0.2 AI Factory Pipeline — 4-pass pipeline with HITL gate\n"
            "\n"
            "Passes:\n"
            "  0  Design        (Claude Sonnet 4.5) → design.mmd + spec.gherkin\n"
            "  1  Tests         (DeepSeek v4-pro)   → test file  [Red Phase]\n"
            "  2  Impl          (DeepSeek v4-pro)   → core logic [Green Phase]\n"
            "     Verification gate: local test suite via subprocess\n"
            "  3  Docs          (DeepSeek v4-pro)   → docstrings"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "target_file",
        metavar="TARGET_FILE",
        type=Path,
        help=(
            "Source file to run the pipeline against.\n"
            "Example: src/calculator.py"
        ),
    )

    parser.add_argument(
        "--test-cmd",
        dest="test_cmd",
        metavar="CMD",
        type=str,
        default=None,
        help=(
            "Shell command to run the test suite after Pass 2.\n"
            "Defaults: 'pytest <dir> --tb=short -v' (.py files)\n"
            "          'npm test'                   (.js/.ts files)\n"
            "Example: --test-cmd 'pytest tests/ -k calculator -x'"
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
# Main pipeline
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point — orchestrate all pipeline passes end-to-end."""

    # ── Parse CLI arguments ──────────────────────────────────────────────────
    args = _build_arg_parser().parse_args()

    target: Path = args.target_file.resolve()
    target_dir: Path = target.parent

    # Design artefacts live alongside the target file for easy discoverability
    design_mmd   : Path = target_dir / "design.mmd"
    spec_gherkin : Path = target_dir / "spec.gherkin"

    # ── Environment setup ────────────────────────────────────────────────────
    # Load .env before preflight so checks can read OPENROUTER_API_KEY
    load_dot_env()
    preflight_checks(target)

    # ── Resolve test command ─────────────────────────────────────────────────
    if args.test_cmd:
        # User supplied a string — split it safely (handles quotes, spaces)
        test_cmd: list[str] = shlex.split(args.test_cmd)
    else:
        test_cmd = infer_test_command(target)

    # ── Print startup banner ─────────────────────────────────────────────────
    _banner(target, test_cmd, args.skip_hitl)

    # ════════════════════════════════════════════════════════════════════════
    # STEP A — Pass 0: Design & Architecture  (Claude Sonnet 4.5)
    #
    # Goal:
    #   Analyse the target file and produce two human-reviewable artefacts
    #   that act as the architectural source of truth for all subsequent passes:
    #     design.mmd    — Mermaid state/sequence/flowchart diagram
    #     spec.gherkin  — Gherkin BDD feature file (Given/When/Then)
    #
    # Why Claude here?
    #   Per the architecture manifesto (§3.2), Claude excels at Constitutional
    #   Adherence and Systems Design — translating existing code into precise
    #   Mermaid and Gherkin without hallucinating premature implementation details.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(
        "Pass 0 — Design & Architecture"
        "  [pass-0-design-agent / claude-sonnet-4.5]"
    )

    design_prompt = (
        f"You are running as Pass 0 (Design & Architecture) of the v0.2 AI Factory pipeline.\n\n"
        f"Analyse the attached source file and produce exactly two artefact files.\n\n"
        f"ARTEFACT 1 — Mermaid diagram\n"
        f"  Write to: {design_mmd}\n"
        f"  Use stateDiagram-v2, sequenceDiagram, or flowchart TD — whichever best\n"
        f"  represents the logic. Include a header comment block:\n"
        f"    %% Module: {target.name}\n"
        f"    %% Generated by: pass-0-design-agent  Pipeline: v0.2\n\n"
        f"ARTEFACT 2 — Gherkin specification\n"
        f"  Write to: {spec_gherkin}\n"
        f"  One Feature block. Minimum three Scenarios: happy path, edge case,\n"
        f"  error/exception case. Use concrete values (no <placeholder> tokens).\n\n"
        f"STRICT RULES:\n"
        f"  - Do NOT modify {target.name}.\n"
        f"  - Do NOT write executable code of any kind.\n"
        f"  - Output ONLY {design_mmd.name} and {spec_gherkin.name}.\n"
        f"  - Mermaid syntax must be valid and renderable by mermaid.js v10+."
    )

    run_opencode(
        agent=AGENTS["design"],
        prompt=design_prompt,
        files=[target],
    )
    _pass_ok("Pass 0 — Design & Architecture")

    # ════════════════════════════════════════════════════════════════════════
    # STEP B — Human-in-the-Loop Gate
    #
    # The developer reviews design.mmd and spec.gherkin before any code is
    # written or modified.  This is the primary checkpoint against LLM
    # hallucination: a 50-token diagram is far easier to verify than 500
    # lines of generated code (see manifesto §1.2 — Artifact-Driven Dev).
    #
    # Ctrl+C → clean exit, no code written.
    # Enter  → pipeline continues to Pass 1.
    # ════════════════════════════════════════════════════════════════════════
    if not args.skip_hitl:
        # STEP B (interactive)
        hitl_gate(design_mmd, spec_gherkin)
    else:
        print("  [--skip-hitl]  Skipping human approval gate.\n")

    # ════════════════════════════════════════════════════════════════════════
    # STEP C — Pass 1: Test Generation  (DeepSeek v4-pro)  [Red Phase]
    #
    # Goal:
    #   Write a failing test suite derived from spec.gherkin and design.mmd.
    #   Tests are the executable constraints for the implementation pass.
    #   The agent must NOT write the implementation — only the expectations.
    #
    # Why DeepSeek here?
    #   Per the manifesto (§3.2): DeepSeek v4 is an algorithmic powerhouse
    #   that matches frontier models for structured code tasks at ~10% of
    #   the cost.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(
        "Pass 1 — Test Generation"
        "  [test-generation-agent / deepseek-v4-pro]  🔴 Red Phase"
    )

    # Derive test file name conventions by extension
    _stem = target.stem
    _ext  = target.suffix
    _test_name = (
        f"{_stem}_test{_ext}"   if _ext == ".py"
        else f"{_stem}.test{_ext}"
    )

    test_prompt = (
        f"You are running as Pass 1 (Test Generation — Red Phase) of the v0.2 AI Factory pipeline.\n\n"
        f"Attached source file:      {target}\n"
        f"Architecture constraint:   {design_mmd}\n"
        f"Behavioural specification: {spec_gherkin}\n\n"
        f"Your task:\n"
        f"  Read all three files. Create a test file at:\n"
        f"    {target_dir / _test_name}\n\n"
        f"  The tests must:\n"
        f"    1. Directly reflect the Scenarios in {spec_gherkin.name}.\n"
        f"    2. Cover happy paths, edge cases, and error conditions.\n"
        f"    3. Use pytest (Python) or Jest (JS/TS).\n"
        f"    4. Be independent, deterministic, and idempotent.\n\n"
        f"STRICT RULES:\n"
        f"  - Do NOT modify {target.name}.\n"
        f"  - Create only {_test_name} — no other files."
    )

    run_opencode(
        agent=AGENTS["tests"],
        prompt=test_prompt,
        files=[target, design_mmd, spec_gherkin],
    )
    _pass_ok("Pass 1 — Test Generation")

    # ════════════════════════════════════════════════════════════════════════
    # STEP D — Pass 2: Core Implementation  (DeepSeek v4-pro)  [Green Phase]
    #
    # Goal:
    #   Write or improve the source file's logic so the Pass 1 tests pass.
    #   design.mmd is the binding architectural constraint — the agent must
    #   not deviate from the state machine depicted there.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(
        "Pass 2 — Core Implementation"
        "  [core-implementation-agent / deepseek-v4-pro]  🟢 Green Phase"
    )

    impl_prompt = (
        f"You are running as Pass 2 (Core Implementation — Green Phase) of the v0.2 AI Factory pipeline.\n\n"
        f"Attached source file to implement: {target}\n"
        f"Architecture constraint:           {design_mmd}\n"
        f"Behavioural specification:         {spec_gherkin}\n\n"
        f"Your task:\n"
        f"  Implement or improve {target.name} so its logic satisfies the test suite\n"
        f"  written in Pass 1.  The diagram in {design_mmd.name} is your binding\n"
        f"  architectural contract — implement exactly what is diagrammed there.\n\n"
        f"STRICT RULES:\n"
        f"  - Modify ONLY {target.name}.\n"
        f"  - Do NOT modify the test file or artefact files.\n"
        f"  - Do NOT add documentation blocks — that is Pass 3's job.\n"
        f"  - Do NOT deviate from the logic flow in {design_mmd.name}."
    )

    run_opencode(
        agent=AGENTS["implement"],
        prompt=impl_prompt,
        files=[target, design_mmd, spec_gherkin],
    )
    _pass_ok("Pass 2 — Core Implementation")

    # ════════════════════════════════════════════════════════════════════════
    # STEP E — Verification Gate: local test suite
    #
    # This is a direct subprocess call — NOT an OpenCode agent.
    # Running tests outside the LLM loop gives a deterministic, unambiguous
    # pass/fail signal that no amount of prompt engineering can fake.
    #
    # Non-zero exit → loud warning block printed but pipeline continues.
    # The documentation pass is still useful even against failing code, and
    # the developer will see the failures and can iterate.
    # ════════════════════════════════════════════════════════════════════════
    _pass_header("Verification Gate — Local Test Suite")

    tests_passed: bool = run_tests(test_cmd)

    if tests_passed:
        print("  ✓  All tests passed.  Proceeding to documentation pass.\n")
    else:
        _warn([
            "Test suite FAILED after Pass 2 (Core Implementation).",
            "",
            "The pipeline will continue to the documentation pass,",
            "but you should resolve failing tests before merging.",
            "",
            f"Re-run tests:  {' '.join(test_cmd)}",
            "",
            "Iteration tip: check design.mmd for logic gaps, then re-run:",
            "  python pipeline_v2.py <target> --skip-hitl",
        ])

    # ════════════════════════════════════════════════════════════════════════
    # STEP F — Pass 3: Documentation  (DeepSeek v4-pro)
    #
    # Goal:
    #   Add JSDoc / Python docstrings to the finalised implementation.
    #   Includes an @see link back to design.mmd per the manifesto's
    #   Traceability Matrix requirement (§1.3 — Eliminating Spec Drift).
    # ════════════════════════════════════════════════════════════════════════
    _pass_header(
        "Pass 3 — Documentation"
        "  [documentation-agent / deepseek-v4-pro]"
    )

    docs_prompt = (
        f"You are running as Pass 3 (Documentation) of the v0.2 AI Factory pipeline.\n\n"
        f"The attached file is the finalised implementation after the TDD cycle.\n\n"
        f"Your task — add complete documentation to {target.name}:\n"
        f"  1. A module-level docstring/comment describing purpose and architecture.\n"
        f"  2. JSDoc (JS/TS) or Python docstrings for every public function/class.\n"
        f"  3. @param / Args, @returns / Returns, @throws / Raises sections.\n"
        f"  4. An @see / See Also link pointing to '{design_mmd.name}' so humans\n"
        f"     can navigate from code to the architectural diagram.\n\n"
        f"STRICT RULES:\n"
        f"  - Edit ONLY {target.name} — comments and docstrings only.\n"
        f"  - Do NOT change any logic, variable names, or control flow.\n"
        f"  - Do NOT modify the test file, {design_mmd.name}, or {spec_gherkin.name}."
    )

    run_opencode(
        agent=AGENTS["docs"],
        prompt=docs_prompt,
        files=[target],
    )
    _pass_ok("Pass 3 — Documentation")

    # ════════════════════════════════════════════════════════════════════════
    # Final summary
    # ════════════════════════════════════════════════════════════════════════
    test_badge = "✓ PASSED" if tests_passed else "✗ FAILED  (see warnings above)"

    _max_path = _W - 20   # max chars for path display in the summary box

    def _fp(p: Path) -> str:
        s = str(p)
        return ("…" + s[-(_max_path - 1):]) if len(s) > _max_path else s

    print()
    print("┌" + "─" * _W + "┐")
    print("│  v0.2 Pipeline complete." + " " * (_W - 25) + "│")
    print("│" + " " * _W + "│")
    print(f"│  Target file    : {_fp(target):<{_max_path}}│")
    print(f"│  Test suite     : {test_badge:<{_max_path}}│")
    print("│" + " " * _W + "│")
    print("│  Artefacts:" + " " * (_W - 11) + "│")
    print(f"│    design.mmd   : {_fp(design_mmd):<{_max_path}}│")
    print(f"│    spec.gherkin : {_fp(spec_gherkin):<{_max_path}}│")
    print("│    test file    : co-located alongside source" + " " * (_W - 46) + "│")
    print("│    source file  : implemented + documented" + " " * (_W - 43) + "│")
    print("│" + " " * _W + "│")
    print("│  Next: git diff — review all agent changes." + " " * (_W - 44) + "│")
    print("└" + "─" * _W + "┘")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Catch Ctrl+C outside the HITL gate (e.g. during an opencode pass)
        print("\n\n  Pipeline interrupted by user.  Partial changes may exist — run git diff.\n")
        sys.exit(0)
    except subprocess.CalledProcessError as exc:
        # opencode exited non-zero — surface the command that failed
        _die(
            f"opencode exited with code {exc.returncode}.\n"
            f"  Command: {' '.join(str(a) for a in exc.cmd)}\n"
            f"  Check the output above for details."
        )
