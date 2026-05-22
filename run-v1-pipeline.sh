#!/usr/bin/env bash
# =============================================================================
# run-v1-pipeline.sh — v0.1 "Hello World" Pipeline Orchestrator
#
# Usage:
#   ./run-v1-pipeline.sh <target_file>
#
# Example:
#   ./run-v1-pipeline.sh src/calculator.py
#
# What it does:
#   Sequentially invokes OpenCode CLI with three scoped sub-agents against
#   the given target file:
#     Pass 1 — core-implementation-agent  (writes/improves core logic)
#     Pass 2 — test-generation-agent      (generates the test suite)
#     Pass 3 — documentation-agent        (adds JSDoc / docstrings)
#
# Prerequisites:
#   - opencode CLI installed and on $PATH
#   - OPENROUTER_API_KEY set in .env (or already exported in your shell)
#   - Agent files present in .opencode/agent/
#
# Note on the model ID:
#   The model below uses the OpenRouter provider prefix that OpenCode expects.
#   If your OpenRouter account uses a different model slug, update MODEL below.
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL="openrouter/deepseek/deepseek-v4-pro"

AGENTS=(
  "core-implementation-agent"
  "test-generation-agent"
  "documentation-agent"
)

PASS_LABELS=(
  "Pass 1 — Core Implementation"
  "Pass 2 — Test Generation"
  "Pass 3 — Documentation"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
print_banner() {
  echo ""
  echo "┌─────────────────────────────────────────────────────────┐"
  echo "│  ai-factory-setup  •  v0.1 Hello World Pipeline         │"
  echo "└─────────────────────────────────────────────────────────┘"
  echo ""
}

print_pass_header() {
  local label="$1"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  $label"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

die() {
  echo ""
  echo "[ERROR] $*" >&2
  exit 1
}

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
TARGET_FILE="${1:-}"

[[ -n "$TARGET_FILE" ]] || die "No target file specified.\n\nUsage: $0 <target_file>"
[[ -f "$TARGET_FILE" ]] || die "Target file not found: '$TARGET_FILE'"

# Load .env if present (OpenCode also reads this automatically, but we need
# the key for our preflight check below).
if [[ -f ".env" ]]; then
  # Export variables without executing arbitrary code
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

[[ -n "${OPENROUTER_API_KEY:-}" ]] || \
  die "OPENROUTER_API_KEY is not set. Add it to your .env file:\n  OPENROUTER_API_KEY=sk-or-..."

command -v opencode >/dev/null 2>&1 || \
  die "'opencode' CLI not found on PATH. Install it with: npm install -g opencode-ai"

# ---------------------------------------------------------------------------
# Pipeline prompts (one per pass)
# ---------------------------------------------------------------------------
PROMPTS=(
  # Pass 1 — Core Implementation
  "You are running as Pass 1 of the v0.1 pipeline. Review the attached file and implement its core logic. Write clean, functional code that fulfils the module's apparent purpose. Focus exclusively on algorithmic correctness. Do NOT add tests or documentation."

  # Pass 2 — Test Generation
  "You are running as Pass 2 of the v0.1 pipeline. The attached file is a completed implementation. Create a co-located test file (e.g. <name>.test.py or <name>.test.js) with comprehensive unit tests covering happy paths, edge cases, and error conditions. Do NOT modify the source file."

  # Pass 3 — Documentation
  "You are running as Pass 3 of the v0.1 pipeline. The attached file is a completed implementation. Add JSDoc (JS/TS) or docstring (Python) documentation to every public function and class, plus a module-level header comment. Do NOT change any logic, variable names, or test code."
)

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------
print_banner
echo "  Target : $TARGET_FILE"
echo "  Model  : $MODEL"
echo "  Agents : ${#AGENTS[@]} passes"
echo ""

PASS_COUNT=${#AGENTS[@]}

for (( i=0; i<PASS_COUNT; i++ )); do
  agent="${AGENTS[$i]}"
  label="${PASS_LABELS[$i]}"
  prompt="${PROMPTS[$i]}"

  print_pass_header "$label  [agent: $agent]"

  opencode run \
    --agent  "$agent"  \
    --model  "$MODEL"  \
    --file   "$TARGET_FILE" \
    --dangerously-skip-permissions \
    "$prompt"

  echo ""
  echo "  ✓ $label complete."
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│  v0.1 Pipeline finished successfully.                   │"
echo "│                                                         │"
echo "│  Artifacts produced for: $TARGET_FILE"
echo "│    Pass 1 → core logic implemented                      │"
echo "│    Pass 2 → test file created alongside source          │"
echo "│    Pass 3 → JSDoc / docstrings added                    │"
echo "│                                                         │"
echo "│  Run 'git diff' to review all agent changes.            │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
