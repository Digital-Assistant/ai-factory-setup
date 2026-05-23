# Example: Basic Addition

This directory is a **verified integration test** for the `ai-factory-setup` pipeline. It proves that the full 8-pass agentic workflow runs correctly end-to-end on a simple arithmetic module.

## What's in here

| File | Role |
|------|------|
| `basic_addition.py` | The target source file — pure arithmetic functions |
| `basic_addition_test.py` | The pipeline-generated test suite (324 tests, TDD Red→Green) |
| `design.mmd` | Pass 0 output — Mermaid state diagram of the module |
| `spec.gherkin` | Pass 0 output — Gherkin behavioural specification |

## Why this example exists

When you clone this repo and want to understand "does this pipeline actually work?", run this:

```bash
# From the repo root
python src/pipeline_v3_1.py examples/basic-addition/basic_addition.py
```

The orchestrator will run all 8 passes against `basic_addition.py`, using `design.mmd` and `spec.gherkin` as the frozen architectural anchors.

To just run the tests directly (skip the pipeline):

```bash
pytest examples/basic-addition/ -v
```

## What the pipeline produces

After a full run, the pipeline will have:
1. Type-annotated the function signatures (Pass 1)
2. Generated a comprehensive test suite (Pass 2)
3. Verified the implementation passes all tests (Pass 3)
4. Refactored for readability and DRY principles (Pass 4)
5. Hardened against OWASP edge cases (Pass 5)
6. Added structured logging (Pass 6)
7. Generated full docstrings with traceability links (Pass 7)

Each pass produces an atomic `git commit` — run `git log --oneline` after the pipeline to see the full trail.
