
---

### Phase 1: Core Mechanics & Visuals

#### **v0.1: The "Hello World" Pipeline (CLI Core)**
*   **Goal:** Prove the OpenCode engine works with your API key and can execute a basic sequence autonomously.
*   **Infrastructure:** 
    *   OpenCode CLI installed on your laptop.
    *   Direct OpenRouter API key configured in OpenCode (No LiteLLM proxy yet).
*   **The Pipeline:** A condensed **3-pass pipeline**.
    1.  Pass 1: Core Implementation (DeepSeek v4).
    2.  Pass 2: Tests (DeepSeek v4).
    3.  Pass 3: Docs (DeepSeek v4).
*   **Deliverable:** You can run a terminal command, and OpenCode successfully edits a file, writes a test, and writes a comment using OpenRouter.

#### **v0.2: IDE Integration & Strict Personas (The UX Upgrade)**
*   **Goal:** Move out of the terminal, get visual diffs, and introduce XML boundaries to stop agent hallucinations.
*   **Infrastructure:**
    *   Install the **OpenCode VS Code Extension**.
    *   Create your first `.opencode/agents.xml` file with strict XML boundaries for the agents.
*   **The Pipeline:** Still 3-4 passes, but now executed via the VS Code "Plan Viewer".
*   **Deliverable:** You can click "Approve" in VS Code to accept code diffs between passes. You no longer have to manually check Git to see what the agent changed.

---

### Phase 2: The Architecture & Intelligence

#### **v0.3: The Artifacts & The Gateway (Local Routing)**
*   **Goal:** Introduce Mermaid diagrams (TDD constraint) and set up the local proxy to enable multi-model routing.
*   **Infrastructure:**
    *   Run **LiteLLM** locally via a simple `docker run` command (No SSO, no Postgres, just local SQLite and a personal master key).
    *   Configure OpenCode to point to `localhost:4000` (LiteLLM) instead of OpenRouter directly.
*   **The Pipeline:** Expand to a **5-pass pipeline** (Adding Design and Contracts).
    *   Pass 0: Design (`.mmd` Mermaid generation using Claude 3.7 via local LiteLLM).
    *   Pass 1-4: The rest of the workflow.
*   **Deliverable:** The AI generates a flowchart *before* writing code, and your local proxy successfully routes the Mermaid task to Claude and the Coding task to DeepSeek.

#### **v0.4: Global Context & Verification (The "Brain" Upgrade)**
*   **Goal:** Stop the AI from hallucinating internal APIs by giving it cross-repo search, and enforce the "Red/Green" test gates.
*   **Infrastructure:**
    *   Install **Bloop** locally (Desktop app or local Docker container) and point it at your local `~/Projects` folder.
    *   Configure the OpenCode orchestrator to pause and run `npm test` or `pytest` locally after Pass 3 (Core).
*   **Deliverable:** The agent can now successfully query Bloop for an interface in another folder, use it, write code, and automatically run your local unit tests to verify it works.

---

### Phase 3: The Complete Local Factory

#### **v1.0: The Complete Personal Setup (Feature Complete)**
*   **Goal:** The full 8-pass enterprise pipeline running flawlessly on your local machine with automated atomic Git commits.
*   **Infrastructure:** 
    *   Integrate local **Semgrep** (Static analysis hard-fail gate).
    *   Fully flesh out `.opencode/agents.xml` for all 8 passes.
*   **The Pipeline:** The complete 8-pass pipeline: Design -> Contracts -> Tests -> Core -> Refactor -> Security -> Observability -> Docs.
*   **Automation:** The orchestrator script is finalized. It runs a pass, runs the tests, and if successful, executes `git commit -m "chore(ai): pass name"` autonomously.
*   **Deliverable:** You drop a Jira ticket summary into your IDE, approve the Mermaid diagram, and the system autonomously loops through 7 more passes, creating 7 clean Git commits on your local branch.

---

### Phase 4: The Enterprise Rollout (Future)

#### **v2.0: The Enterprise Server Setup (Out of Scope for Laptop)**
*   **Infrastructure:** Move LiteLLM to a central server.
*   **Governance:** Connect LiteLLM to O365/GSuite SSO. Spin up Postgres for departmental budget rationing.
*   **Execution:** Move Passes 4–7 off the local laptop and into GitHub Actions / GitLab CI asynchronous runners.

---
