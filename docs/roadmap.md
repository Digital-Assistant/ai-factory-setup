# Roadmap

Items in no particular order of priority. Contributions welcome — see the [architecture manifesto](architecture-manifesto.md) for design context.

## Planned

- [ ] Modularise `pipeline_v3_1.py` into a proper Python package with a clean CLI entry point
- [ ] Run a full pipeline against a real-world feature and document the results
- [ ] Figure out how to invoke the pipeline from a ticket/issue (GitHub Actions integration)
- [ ] Dev mode vs. debug mode — should there be separate verbosity levels and dry-run support?
- [ ] Handling agent failures and infinite loops. Further enhancement - Orchestrator captures the stdout/stderr, saves it to logs/pass_n_failures.txt. Orchestrator prompts the agent again, appending the failure log. This will ensure agents try new approaches different from what they tried before.  
- [ ] Better LiteLLM config using Postgres for budget tracking (see `infra/` for current setup)
- [ ] Bloop integration for cross-repo semantic context retrieval
- [ ] VS Code extension / cleaner HITL flow for reviewing and editing artifact files (`.mmd`, `.gherkin`) during the Pass 0 gate. 
- [ ] Better HITL overall - this will keep improving once we start using this tool in real projects and tickets.
- [ ] Semgrep integration as a hard-fail gate between passes (see architecture manifesto § 4.3)
- [ ] DevContainer / Nix flake for deterministic agent sandboxing (see architecture manifesto § 2.3)
- [ ] Benchmarking: quantify token savings from Static Prefix caching across model providers
- [ ] Improve security agent - input sanitisation, zip bombs, size restrictions etc. Do we need different frameworks for frontend, backend and desktop apps ?
- [ ] Pass 0 - better workflow - make a git branch before working on the problem.
- [ ] Have a maker-checker pattern for soem critical parts like specs and mmd. 
- [ ] Can I make this harness into a plugin to claude code ?

## Other architectural debates and discussions

- [ ] Swap Pass 5 and Pass 6.
    - [ ] New Pass 5: Observability & Error Handling. The agent builds the try/catch blocks, defines the error classes, and drops in the log statements.
    - [ ] New Pass 6: Security Hardening (The Final Gate). The Security agent now reviews the complete feature—including the error handlers. It will see the raw logger.error from Pass 5 and correctly modify it to mask PII, and it will sanitize the API response so the stack trace isn't leaked to the client.
- [ ] The "Security Orchestrator" Pattern
    - [ ] Instead of one massive security prompt, Pass 6 should invoke a Security Orchestrator Agent. This agent reads the design.mmd to figure out what type of code it is looking at, and then delegates to specialized experts:
        - [ ] Sub-Agent 1: The Payload Specialist (Checks for Zip Bombs/Decompression attacks, JSON size limits, XML External Entities).
        - [ ] Sub-Agent 2: The Data Sanitizer (Checks Regex constraints, SQL Injection, Prototype Pollution).
        - [ ] Sub-Agent 3: The Context Expert (Frontend vs. Backend)
          - [ ] If the code is React/Next.js, it looks for XSS and missing CSRF tokens.
          - [ ] If the code is Node/Python backend, it looks for SSRF and broken access control. 
- [ ] When implementing a security fix or a feature, we will enforce a strict resolution heirarchy. AI agent may generate code by importing random libraries (e.g., pulling in DOMPurify when you already use xss, or adding Joi when your project uses Zod
  - [ ] Heirarchy - 
    1. CURRENT PATTERNS: Look at the existing codebase context (via Bloop/imports). Does the team already have a custom utility for this? (e.g., `src/utils/sanitizer.ts`). If yes, use it.
    2. CURRENT LIBRARIES: Look at the `package.json` / `requirements.txt`. Do we already have an installed library capable of this? (e.g., Zod, DOMPurify). If yes, use it.
    3. FRAMEWORK NATIVE: Can this be solved using the native standard library or framework defaults without adding dependencies? (e.g., Django's built-in validators, Python's native `json` limits). If yes, use it.
    4. NEW DEPENDENCY: ONLY if 1, 2, and 3 fail, propose adding a highly standard, vetted enterprise library (and flag it for human review).  


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

