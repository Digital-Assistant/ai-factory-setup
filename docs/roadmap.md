# Roadmap

Items in no particular order of priority. Contributions welcome — see the [architecture manifesto](architecture-manifesto.md) for design context.

## Planned

- [ ] Modularise `pipeline_v3_1.py` into a proper Python package with a clean CLI entry point
- [ ] Run a full pipeline against a real-world feature and document the results
- [ ] Figure out how to invoke the pipeline from a ticket/issue (GitHub Actions integration)
- [ ] Dev mode vs. debug mode — should there be separate verbosity levels and dry-run support?
- [ ] Better LiteLLM config using Postgres for budget tracking (see `infra/` for current setup)
- [ ] Bloop integration for cross-repo semantic context retrieval
- [ ] VS Code extension / cleaner HITL flow for reviewing and editing artifact files (`.mmd`, `.gherkin`) during the Pass 0 gate
- [ ] Semgrep integration as a hard-fail gate between passes (see architecture manifesto § 4.3)
- [ ] DevContainer / Nix flake for deterministic agent sandboxing (see architecture manifesto § 2.3)
- [ ] Benchmarking: quantify token savings from Static Prefix caching across model providers

## Completed

- [x] 8-pass pipeline orchestrator (`src/pipeline_v3_1.py`)
- [x] Static Prefix anchoring (immutable file ordering for cache hits)
- [x] Context Compaction (disposable error logs, clean pass starts)
- [x] Self-correction loop (max 2 retries per guarded pass)
- [x] Human-in-the-Loop gate after Pass 0
- [x] Atomic git commits per pass
- [x] Agent guardrails via `.opencode/agents.xml` and per-agent `.md` files
- [x] OpenRouter + LiteLLM proxy configuration (`infra/`)
- [x] Verified integration example (`examples/basic-addition/`)