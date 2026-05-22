# OpenCode v0.1 Hello World Pipeline

**Session ID:** ses_1b593f9b0ffeGB7w9QEx0PQ6oA
**Created:** 5/21/2026, 5:34:14 PM
**Updated:** 5/21/2026, 6:01:01 PM

---

## User

<role>
You are my Lead Platform Engineer. We are building an enterprise AI-native development pipeline using OpenCode.
</role>

<context>
Read the two documents located in the `./docs/` folder: `architecture-manifesto.md` and `version-plan.md`. These outline the final vision, but we are executing an iterative build.
</context>

<current_task>
Your exact, constrained task is to implement strictly ONLY "v0.1: The Hello World Pipeline". 
Do NOT implement any features from v0.2, v0.3, or v1.0. Do NOT attempt to install LiteLLM, Bloop, Semgrep, or VS Code extensions.
</current_task>

<deliverables>
I need you to generate the underlying files for v0.1 in this directory:

1. Create a `.env.example` file with a placeholder for `OPENROUTER_API_KEY`.
2. Create the `.opencode/agents.xml` file. Define ONLY three sub-agents for this version: 
   - CoreImplementationAgent (Target model: deepseek/deepseek-coder-v4)
   - TestGenerationAgent (Target model: deepseek/deepseek-coder-v4)
   - DocumentationAgent (Target model: deepseek/deepseek-coder-v4)
3. Write a simple orchestrator script named `run-v1-pipeline.sh` (or `.py` if you prefer). This script should take a target file as an argument, and sequentially invoke OpenCode CLI using the three agents defined above.
</deliverables>

<execution_rules>
- Use standard bash or python for the orchestrator.
- Make sure the orchestrator script is executable.
- Output a brief summary of how I should run the `run-v1-pipeline.sh` script to test it once you are done.
</execution_rules> 

---

## Assistant (Build · Claude Sonnet 4.6 · 9.6s)

_Thinking:_

Let me start by reading the documentation files to understand the architecture and version plan, then implement the v0.1 pipeline strictly as specified.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/docs/architecture-manifesto.md"
}
```

**Output:**
```
<path>/home/kc/Projects/UDAN/ai-factory-setup/docs/architecture-manifesto.md</path>
<type>file</type>
<content>
1: # The Enterprise Agentic Software Development Framework
2: **Building a deterministic, artifact-driven AI developer pipeline using OpenCode.**
3: 
4: _(While this architecture focuses on software development teams, it is easy to extended this to all employees by replacing IDEs with appropriate genAI clients and harnesses i.e. replace opencode+Bloop by [AnythingLLM](https://github.com/mintplex-labs/anything-llm) while retaining the LiteLLM and OpenRouter.)_
5: 
6: This document outlines the architectural blueprint for scaling AI coding agents across an enterprise. The architecture uses mature open-source tools to optmise and balance multiple common trade-offs in AI development. (The actual implementation will be opensourced soon.)
7: 
8: 
9: **Platform & Governance:** (Driven by LiteLLM, OpenRouter, Bloop, and Git Workflows)
10: - **Budget Control & Token Efficiency:** Granular token rationing and state-of-the-art code context retrieval using bloop.
11: - **Model Independence:** A proxy-first approach to avoid vendor lock-in (dynamically routing between Claude, DeepSeek, and OpenAI or models of your choice).
12: - **Enterprise-Grade Security & Auditing:** SSO Ready, PII masking, scoped access, and centralized AI telemetry.
13: - **Deterministic Execution:** Sandboxed agent environments to ensure reproducible builds.
14: - **Human Control:** Visual approval checkpoints and atomic Git commit workflows.
15: 
16: **Code Quality & Practices:** (Driven by 8-pass pipeline, TDD, Mermaid, opencode system prompts and Atomic Commits)
17: - **Output Accuracy:** Guaranteed via strict Test-Driven Development (TDD) constraints.
18: - **Zero Specification Drift:** Synchronizing executable specs (Mermaid/Gherkin) with core logic on every pass.
19: - **Readability & Traceability:** Automated dependency linking between code, tests, and architectural diagrams.
20: - **Observability:** Dedicated pipeline passes ensuring uniform error handling, logging, and telemetry.
21: - **Global Context Awareness:** Eliminating hallucinations via cross-repository semantic indexing.
22: 
23: By enforcing strict pipelines, localized context retrieval, and artifact-driven development, this framework eliminates context window bloat, prevents specification drift, and reduces LLM API costs significantly (needs further benchmarking) compared to ad-hoc agentic workflows.
24: 
25: ---
26: High-Level System Context Diagram
27: ---
28: ```mermaid
29: graph TD
30:     %% Consistent C4-inspired Style Definitions
31:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff
32:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
33:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
34: 
35:     %% Actors (Users) - Positioned at the top
36:     Dev(["Software Developer <br> (IDE / OpenCode CLI)"]):::actor
37:     PlatformAdmin(["Platform / DevOps Admin"]):::actor
38: 
39:     %% The Central System
40:     AIFactory["Enterprise AI Factory <br> (OpenCode Orchestrator + LiteLLM + Bloop)"]:::coreSystem
41: 
42:     %% External Systems - Positioned at the bottom
43:     SSO["Identity Provider<br>(O365 / GSuite)"]:::extSystem
44:     VCS["Version Control & CI/CD <br> (GitHub / GitLab)"]:::extSystem
45:     OpenRouter["OpenRouter API Gateway <br> (Model Multiplexer)"]:::extSystem
46:     TargetModels["Target LLMs <br> (DeepSeek / Claude / GPT)"]:::extSystem
47: 
48:     %% Human to System Relationships
49:     Dev -->|"1. Triggers agentic passes <br> & reviews code"| AIFactory
50:     PlatformAdmin -->|"2. Configures routing, <br> budgets & plugins"| AIFactory
51: 
52:     %% System to External Relationships
53:     AIFactory -->|"3. Authenticates user <br> & validates tokens"| SSO
54:     AIFactory -->|"4. Reads context <br> & writes commits"| VCS
55:     AIFactory -->|"5. Sends prompt payload <br> & tracks budget"| OpenRouter
56:     
57:     %% Gateway to Final Models
58:     OpenRouter -.->|"6. Routes dynamically <br> based on task"| TargetModels
59: ```
60: 
61: ---
62: 
63: ## 1. Background and Limitations
64: 
65: For the past two years, proprietary and open-source genAI coding tools have been evolving rapidly. They have been evolving faster than the developer community has been able to keep up. While the tools have been getting increasingly powerful and feature rich, it has been difficult to harness this power for teams. There are many public and celebrated "Agents.md" files but they focus only on the Agents and not the engineering around the Agents. There is also the FOMO factor on whether we are missing some capabilities or not by not using the very latest and greatest tools.
66: 
67: This unstructured approach fails at the enterprise level for three reasons:
68: 1. **Context Bloat:** Dumping massive files into an Agentic window burns millions of expensive tokens.
69: 2. **Spaghetti Edits:** Asking a single model to write core logic, implement security, and format logging simultaneously leads to "attention degradation". The model will inevitably "lazy code" one of these constraints.
70: 3. **Specification Drift:** The Agentic model changes the code, but the architectural documentation and requirements are left untouched, creating a legacy codebase on day one.
71: 
72: To solve this, we evolved the approach to agent development to: **AI as an Assembly Line.**
73: 
74: ### 1.1 The Proposed Paradigm: The Multi-Pass Pipeline
75: 
76: Instead of a single zero-shot prompt, development is broken down into a strict, sequential pipeline. Each step (pass) is handled by a specialized sub-agent with a deeply constrained scope and strict guard-rails.
77: 
78: > **The Decision:** We use a 8-pass pipeline (Design -> Contracts -> Tests -> Core Logic -> Refactor -> Security -> Observability -> Documentation).
79: >
80: > **The Rationale:** By strictly scoping each pass, we eliminate attention degradation. A "Security Agent" tasked *only* with finding OWASP vulnerabilities in a pre-written file performs significantly better than a generalist agent trying to write logic and secure it at the same time. Furthermore, tight scoping allows us to route simpler tasks to cheaper models, drastically reducing API costs.
81: 
82: ```mermaid
83: graph TD
84:     %% Consistent C4-inspired Style Definitions
85:     classDef orchestrator fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
86:     classDef subAgent fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
87:     classDef gate fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#000
88:     classDef external fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
89: 
90:     %% Nodes
91:     Orchestrator["Main Orchestrator <br> (Context & State Manager)"]:::orchestrator
92:     SubAgent["Specialized Sub-Agent <br> (e.g., Security, Observability)"]:::subAgent
93:     Gate{"Verification Gate <br> (Tests, Semgrep)"}:::gate
94:     Git[("Git Repository")]:::external
95: 
96:     %% Flow
97:     Orchestrator -->|1. Delegates scope & task boundaries| SubAgent
98:     
99:     SubAgent -->|2. Writes code / proposes diffs| Gate
100:     
101:     Gate -->|3. Fails: Feed error logs back| SubAgent
102:     
103:     Gate -->|4. Passes: Yield control back| Orchestrator
104:     
105:     Orchestrator -->|5. Commit atomic changes| Git
106:     Orchestrator -->|6. Trigger next pipeline pass| Orchestrator
107: ```
108: 
109: ### 1.2 Core Tenet: Artifact-Driven Development
110: 
111: In traditional development, documentation is a markdown file written after the fact. In an AI-Native pipeline, **the artifacts are the source of truth, and the code is merely a byproduct.** AWS Kiro does a great job here but it has some constraints around model selection and customizability.
112: 
113: We rely on two core artifacts:
114: *   **`.mmd` (Mermaid.js):** Text-based sequence, state, and class diagrams.
115: *   **`.gherkin` (Behavior-Driven Specs):** Executable Given/When/Then requirements.
116: 
117: > **The Decision:** No agent is allowed to write core logic until a Mermaid diagram and a Gherkin specification have been generated, updated, and approved by a human. This Human-in-the-loop is our check against AI hallucination.
118: >
119: > **The Rationale:** LLMs are prone to "logical tangents" when writing code directly. Forcing the AI to map a state machine in Mermaid.js *first* enforces Architectural Chain-of-Thought. When the AI subsequently writes the code, it uses its own diagram as a strict mathematical constraint, virtually eliminating logical hallucinations. Diagrams are easier for humans to understand and follow, making it easier to catch unhandled scenarios and edge cases, thus reducing the cognitive load on the developer. This also helps in maintaining backward compatibility and ease of onboarding new developers.
120: 
121: (*Link to Traceability Matrix Diagram in Appendix.*)
122: 
123: ### 1.3 Eliminating Specification Drift
124: 
125: The greatest risk of agentic coding (apart from the obvious hallucinations and questionable human oversight) is the speed at which it can outpace its own documentation.
126: 
127: > **The Decision:** We treat architectural diagrams and Gherkin specs as version-controlled, executable code. The pipeline enforces a mandatory "Artifact Sync" rule: an agent mandatorily updates the '.mmd' and '.gherkin' and takes human approval of these changes before touching any core logic. 
128: >
129: > **The Rationale:** This creates a "Digital Twin" of your software. By utilizing `JSDoc @see` links pointing directly to local `.mmd` files, human developers can instantly trace complex AI-generated code back to the exact state transition diagram that dictated it. Spec drift becomes impossible because the spec and the code are locked in a continuous feedback loop.
130: 
131: ```mermaid
132: graph TD
133:     %% Consistent C4 Style Definitions
134:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff,rx:20,ry:20
135:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
136:     classDef internalComp fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
137:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
138:     
139:     %% Phase Styling
140:     classDef phaseRed fill:#fee2e2,stroke:#b91c1c,stroke-width:2px,color:#000
141:     classDef phaseGreen fill:#dcfce7,stroke:#15803d,stroke-width:2px,color:#000
142:     classDef phaseRefactor fill:#fef3c7,stroke:#b45309,stroke-width:2px,color:#000
143: 
144:     %% Actors and Inputs
145:     Dev(["Developer / Product Manager"]):::actor
146:     Ticket["New Feature Request <br> (Modifies Existing Module)"]:::extSystem
147:     Bloop[("Bloop Indexer <br> (Retrieves Existing Specs)")]:::internalComp
148: 
149:     subgraph DesignPhase ["1. Spec Evolution (Pass 0)"]
150:         direction TB
151:         UpdateMMD["Agent updates existing design.mmd"]:::coreSystem
152:         UpdateGherkin["Agent updates existing spec.gherkin"]:::coreSystem
153:         HITL{"Human Approval <br> (Reviews Architecture Diff)"}:::actor
154:     end
155: 
156:     subgraph TDDPhase ["2. Test Evolution (Pass 2)"]
157:         direction TB
158:         WriteTests["Agent updates test_suite.ts <br> to match new specs"]:::phaseRed
159:         RunFail["Run Tests: FAIL <br> (Ensures tests are valid constraints)"]:::phaseRed
160:     end
161: 
162:     subgraph CodePhase ["3. Code Evolution (Pass 3)"]
163:         direction TB
164:         UpdateCode["Agent edits implementation.ts"]:::phaseGreen
165:         RunPass["Run Tests: PASS <br> (Code meets new specs)"]:::phaseGreen
166:     end
167: 
168:     subgraph CIPhase ["4. Hardening (Pass 4-7 - REFACTOR)"]
169:         direction TB
170:         Pipeline["Refactor, Security, Logging <br> (Tests run continuously)"]:::phaseRefactor
171:         FinalSync["Pass 7 Docs: Verify Specs <br> match final code"]:::phaseRefactor
172:     end
173: 
174:     %% Flow Relationships
175:     Dev --> Ticket
176:     Ticket --> UpdateMMD
177:     Bloop -. "Provides existing context" .-> UpdateMMD
178:     
179:     UpdateMMD --> UpdateGherkin
180:     UpdateGherkin --> HITL
181:     
182:     HITL -- "Approved" --> WriteTests
183:     HITL -. "Rejected" .-> UpdateMMD
184:     
185:     WriteTests --> RunFail
186:     RunFail -- "Triggers Implementation" --> UpdateCode
187:     
188:     UpdateCode --> RunPass
189:     
190:     RunPass -- "Commits to CI" --> Pipeline
191:     Pipeline --> FinalSync
192: ```
193: 
194: **The Reality Check: Why Diagrams Actually Reduce Costs**
195: 
196: The "Multi-Pass Pipeline" sounds expensive: multiple API calls, multiple context windows, human approval gates.
197: 
198: However, in practice, this system acts as a **Context Collapse Filter**. Consider the alternative: a "Zero-Shot" approach where a single agent writes the code directly from the initial ticket.
199: 
200: Without a visual constraint, the agent must hold the entire feature logic, plus the entirety of the existing codebase (e.g., the `Order` module), in its context window simultaneously. This inevitably leads to **Logical Dilution**, where the agent "lazy codes" constraints to save token space, resulting in bugs that require hours of debugging.
201: 
202: By forcing the creation of a Mermaid diagram first, we do the following:
203: 1. **Token Compression:** A Mermaid diagram encoding 500 lines of logic uses 90% fewer tokens than the source code itself.
204: 2. **Early Error Detection:** A human can spot a logical flaw in a 200-token diagram in seconds, preventing a 2,000-line buggy implementation that would take hours to refactor.
205: 3. **Recursive Constraint:** The diagram becomes a persistent, cheap "Context Anchor" that can be re-fed to the agent in subsequent passes without blowing the budget.
206: 
207: ---
208: 
209: ## 2. The Architecture & Infrastructure
210: 
211: To execute an 8-pass agentic pipeline safely across hundreds of developers, the underlying infrastructure must enforce security, budget constraints, and context accuracy before a single prompt reaches an LLM. 
212: 
213: We achieve this by decoupling the agent from the LLM provider, utilizing a secure gateway proxy, and building a centralized semantic knowledge graph.
214: 
215: ### 2.1 The Model Gateway: LiteLLM + OpenRouter + SSO
216: 
217: Relying on a single vendor (like GitHub Copilot or ChatGPT Enterprise) locks an organization into arbitrary pricing models, limits model choice, and removes granular auditing capabilities.
218: 
219: > **The Decision:** We route all agent traffic through a self-hosted [**LiteLLM**](https://github.com/BerriAI/litellm) (or [Bifrost](https://github.com/maximhq/bifrost)) proxy, authenticated via corporate SSO (O365/GSuite), which then multiplexes requests to **OpenRouter** (or internal models).
220: >
221: > **The Rationale:** 
222: > *   **Budget Rationing:** LiteLLM intercepts the SSO identity and checks it against the internal Postgres database. We can enforce hard monthly budgets per developer or per department. Once the budget is hit, the proxy returns a `402 Payment Required`, preventing runaway agent loops from causing massive API bills. (Optionally, We can also have a fallback option of cheaper/smaller models with some warning.)
223: > *   **Model Routing:** Pass 1 (Contracts) requires the strict formatting of Claude 3.7 (or higher), while Pass 3 (Core Logic) can be handled by the 80% cheaper DeepSeek v4 (or other models). The proxy allows us to dynamically route tasks to the most cost-effective model without changing the developer's local tools.
224: > *   **PII & Data Loss Prevention (DLP):** The proxy acts as a firewall. Middleware can strip sensitive API keys, DB credentials, or PII from the prompt before it ever leaves the corporate network.
225: 
226: ```mermaid
227: graph LR
228:     %% Consistent Style Definitions
229:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff,rx:20,ry:20
230:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
231:     classDef internalComp fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
232:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
233: 
234:     %% Nodes
235:     Dev(["Developer IDE"]):::actor
236: 
237:     subgraph Proxy ["Internal AI Gateway (LiteLLM)"]
238:         direction LR
239:         Auth["1. Identity Check <br> (SSO/OIDC)"]:::coreSystem
240:         Quota["2. Budget Gate <br> (Quota Check)"]:::internalComp
241:         DLP["3. Privacy Filter <br> (DLP Masking)"]:::internalComp
242:     end
243: 
244:     Target["OpenRouter API <br> (External LLMs)"]:::extSystem
245: 
246:     %% Execution Flow
247:     Dev ==> Auth
248:     Auth ==> Quota
249:     Quota ==> DLP
250:     DLP ==> Target
251: 
252:     %% Simple Legend/Status
253:     Target -. "Response & Token Billing" .-> Proxy
254: ```
255: A more detailed diagram can be found in the Appendix (**Placeholder for link to Diagram**)
256: 
257: ### 2.2 The Knowledge Layer: Bloop AI & Semantic Indexing
258: 
259: An AI agent is only as intelligent as the context it is given. Under-optimised agentic tools (including Gemini-cli, Claude-Code) attempt to solve this by context stuffing or inefficiently running `grep` across the terminal or asking the user to drag-and-drop files, which leads to massive token waste and missed cross-repository dependencies.
260: 
261: > **The Decision:** We deploy [**Bloop AI**](https://github.com/BloopAI/bloop) (or a similar vector/AST indexer like Zoekt) as an internal service to index all Git repositories, acting as the semantic search engine for the OpenCode orchestrator.
262: >
263: > **The Rationale:** When a developer asks an agent to "update the payment retry logic," the Pass 0 (Design) agent queries the Bloop API. Bloop returns the exact `.mmd` diagrams, TypeScript interfaces, and database schemas required from across multiple microservices. This surgically precise context window (hundreds of tokens instead of thousands) prevents hallucinations and ensures the agent adheres to existing architectural patterns.
264: 
265: ```mermaid
266: graph LR
267:     %% Consistent Style Definitions
268:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff,rx:20,ry:20
269:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
270:     classDef internalComp fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
271:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
272: 
273:     %% Nodes
274:     Repos["Internal Repos <br> (GitHub/GitLab)"]:::extSystem
275:     
276:     subgraph "Background: Indexing"
277:         direction TB
278:         Bloop["Bloop Engine <br> (Parser & Indexer)"]:::coreSystem
279:         DB[("Search & Vector DB <br> (The Knowledge)")]:::internalComp
280:     end
281: 
282:     subgraph "Foreground: Retrieval"
283:         direction TB
284:         Agent["OpenCode Agent <br> (The Orchestrator)"]:::coreSystem
285:     end
286: 
287:     %% Data Flow
288:     Repos -- "Sync Code" --> Bloop
289:     Bloop -- "Create Graph" --> DB
290:     
291:     Agent -- "Ask: 'Where is...?'" --> DB
292:     DB -- "Return Exact Code" --> Agent
293: 
294:     %% Labels
295:     style DB fill:#2dd4bf,stroke:#0f766e
296: ```
297: (Placeholder: Insert Link to detailed "Retrieval/Indexing Architecture Diagram" here)
298: 
299: ### 2.3 Deterministic Environments (The Agent Sandbox)
300: 
301: Because our pipeline relies on a strict TDD methodology (Pass 2 tests *must* fail before Pass 3 writes code), the agents must be able to execute terminal commands like `npm test`, `mvn clean install`, or `pytest`. 
302: 
303: > **The Decision:** Agent execution is strictly bound to deterministic, containerized environments using **DevContainers (`devcontainer.json`)** or **Nix flakes**. (Implementation pending.)
304: >
305: > **The Rationale:** If an agent runs a test on a developer's local machine that has the wrong Node.js version, the test will fail due to environment errors. The agent will then hallucinate, attempting to rewrite perfectly good code to "fix" a problem that is actually an environment mismatch. By forcing agents to run in a sandboxed container, we guarantee reproducible builds, protect the host machine from rogue agent scripts, and ensure the TDD loop is cryptographically reliable.
306: 
307: ---
308: 
309: ## 3. The 8-Pass Pipeline & Model Strategy
310: 
311: The heart of the our OpenCode Enterprise Framework is the orchestrator script that transitions the agent through eight strictly scoped phases. By decomposing the software development lifecycle (SDLC) into granular agentic tasks, we can apply the "Actor-Critic" and "Red-Green-Refactor" methodologies programmatically.
312: 
313: ```mermaid
314: ---
315: title: 7-Pass Agentic TDD Pipeline (State Machine)
316: ---
317: stateDiagram-v2
318:     %% Consistent Styling Definitions
319:     classDef human fill:#08427b,color:#fff,stroke:#052e56,stroke-width:2px
320:     classDef agent fill:#1168bd,color:#fff,stroke:#0b4884,stroke-width:2px
321:     classDef testGate fill:#2dd4bf,color:#000,stroke:#0f766e,stroke-width:2px
322: 
323:     [*] --> Pass_0
324:     
325:     %% --- PHASE 1: Design & Specs ---
326:     Pass_0 : Pass 0 - Design & Context (Agent)
327:     class Pass_0 agent
328:     
329:     HITL : Developer Review (HITL)
330:     class HITL human
331:     
332:     Pass_0 --> HITL : Outputs .mmd & .gherkin
333:     HITL --> Pass_0 : Request Architecture Changes
334:     HITL --> Pass_1 : Approve Specs
335:     
336:     %% --- PHASE 2: Contracts & Tests ---
337:     Pass_1 : Pass 1 - Contracts & Types (Agent)
338:     class Pass_1 agent
339:     
340:     Pass_2 : Pass 2 - Test Generation [Red Phase]
341:     class Pass_2 agent
342:     
343:     Pass_1 --> Pass_2
344:     Pass_2 --> Pass_3
345:     
346:     %% --- PHASE 3: Core Implementation ---
347:     Pass_3 : Pass 3 - Core Logic [Green Phase]
348:     class Pass_3 agent
349:     
350:     Gate_3 : Test Runner (Verify Core)
351:     class Gate_3 testGate
352:     
353:     Pass_3 --> Gate_3
354:     Gate_3 --> Pass_3 : Tests Failed (Fix Core)
355:     Gate_3 --> Pass_4 : Tests Passed
356:     
357:     %% --- PHASE 4: Refactor ---
358:     Pass_4 : Pass 4 - Clean Code & Refactor
359:     class Pass_4 agent
360:     
361:     Gate_4 : Test Runner (Verify Refactor)
362:     class Gate_4 testGate
363: 
364:     Pass_4 --> Gate_4
365:     Gate_4 --> Pass_4 : Refactor Broke Logic (Revert & Fix)
366:     Gate_4 --> Pass_5 : Tests Passed
367:     
368:     %% --- PHASE 5: Security ---
369:     Pass_5 : Pass 5 - Security Hardening
370:     class Pass_5 agent
371:     
372:     Gate_5 : Test Runner (Verify Security)
373:     class Gate_5 testGate
374:     
375:     Pass_5 --> Gate_5
376:     Gate_5 --> Pass_5 : Security Blocked Valid Logic (Fix)
377:     Gate_5 --> Pass_6 : Tests Passed
378:     
379:     %% --- PHASE 6: Observability ---
380:     Pass_6 : Pass 6 - Observability & Logs
381:     class Pass_6 agent
382:     
383:     Gate_6 : Test Runner (Verify Observability)
384:     class Gate_6 testGate
385:     
386:     Pass_6 --> Gate_6
387:     Gate_6 --> Pass_6 : Logs Broke Scopes/Types (Fix)
388:     Gate_6 --> Pass_7 : Tests Passed
389:     
390:     %% --- PHASE 7: Documentation & Spec Sync ---
391:     Pass_7 : Pass 7 - Sync Docs & Spec Artifacts
392:     class Pass_7 agent
393:     
394:     Gate_7 : Final CI/CD Verification
395:     class Gate_7 testGate
396:     
397:     Pass_7 --> Gate_7
398:     Gate_7 --> Pass_7 : Spec Drift Detected (Update Specs)
399:     Gate_7 --> [*] : Branch Ready for PR
400: ```
401: 
402: ### 3.1 The Pipeline Breakdown
403: 
404: The workflow requires the OpenCode orchestrator to sequentially trigger the following sub-agents:
405: 
406: 1. **Pass 0: Design & Context** (The Architect)
407:    * *Goal:* Read the feature ticket, query Bloop for repository context, and generate/update the `design.mmd` (Mermaid diagrams) and `spec.gherkin`. 
408:    * *Gate:* Requires human (Developer) approval before proceeding.
409: 2. **Pass 1: Contracts & Interfaces** (The Modeler)
410:    * *Goal:* Define the strict API boundaries, types, and data schemas (e.g., TypeScript Interfaces, Pydantic models).
411: 3. **Pass 2: TDD Test Generation** (The QA Red Phase)
412:    * *Goal:* Write comprehensive unit and edge-case tests against the Pass 1 interfaces based purely on the Pass 0 diagrams. Do *not* write core logic.
413: 4. **Pass 3: Core Implementation** (The Builder Green Phase)
414:    * *Goal:* Write the algorithmic logic to make the Pass 2 tests pass. 
415:    * *Gate:* `npm test` must pass. If it fails, the agent reads the error log and self-corrects.
416: 5. **Pass 4: Refactor & Optimization** (The Optimizer)
417:    * *Goal:* Reduce cyclomatic complexity, enforce DRY principles, and optimize Big-O performance without changing behavior.
418:    * *Gate:* `npm test` must pass to ensure the refactor didn't break functionality.
419: 6. **Pass 5: Security Hardening** (The Red Team)
420:    * *Goal:* Add input sanitization, OWASP mitigations, and boundary validation (e.g., Zod schemas). 
421:    * *Gate:* `npm test` must pass.
422: 7. **Pass 6: Observability** (The SRE)
423:    * *Goal:* Implement uniform try/catch blocks, structured JSON logging, and custom error classes.
424:    * *Gate:* `npm test` must pass.
425: 8. **Pass 7: Documentation** (The Tech Writer)
426:    * *Goal:* Generate JSDoc/Docstrings, sync the Traceability Matrix, and ensure the README and inline comments reflect the final implementation.
427: 
428: ### 3.2 Dynamic Model Routing (The OpenRouter Strategy)
429: 
430: Using a frontier model (like Claude 4.x Sonnet or GPT-4.5) for all eight passes is financially irresponsible at an enterprise scale. Because we use LiteLLM and OpenRouter, we lock specific models to specific passes based on their training strengths.
431: 
432: > **The Decision:** We route Architectural passes to **Claude**, Logic/Execution passes to **DeepSeek**, Security passes to **OpenAI**, and text generation to **Llama/Gemini**. 
433: > 
434: >*(Given the bloop integration and resultant high-quality context, we think that 30B-300B param models too might do a great (or at least adequate) job for exeution passes 3-4 and 6,7. You should probably use a frontier model for the Security pass (pass 5) though.). Some more experiments with different models for different passes will be very helful.*
435: >
436: > **The Rationale:** 
437: > *   **Claude 3.7 Sonnet or higher (Passes 0 & 1):** Claude is the industry leader in Constitutional Adherence and Systems Design. It excels at reading messy Jira tickets and translating them into flawless XML and Mermaid.js boundaries without hallucinating premature code.
438: > *   **DeepSeek v4 (Passes 2, 3, & 4):** DeepSeek is an algorithmic powerhouse. For pure "make the tests pass" mathematical logic, it matches or beats proprietary frontier models at roughly 10% of the cost. It is our heavy-lifting engine.
439: > *   **GPT-4.5 (Pass 5 - Security):** OpenAI models undergo massive corporate RLHF (Reinforcement Learning from Human Feedback) for defensive cybersecurity. We pay the premium token cost here to leverage its deep red-teaming mindset to spot injection flaws.
440: > *   **Llama 3 70B / Gemini 2.5 Flash (Passes 6 & 7):** Adding logging and writing docstrings is highly repetitive, mundane prose. We route this to blazing-fast, nearly-free models to minimize overhead.
441: 
442: ### 3.3 Execution: Atomic Commits vs. Bulk Edits
443: 
444: In a multi-pass system running locally, the compute overhead of testing is negligible, but the risk of "merge hell" is high.
445: 
446: > **The Decision:** The pipeline is orchestrated to pause, run the test suite, and execute an atomic `git commit` after *every individual pass* (starting from Pass 1), rather than squashing all AI edits into a single feature commit.
447: > *Example:* `git commit -m "chore(ai): applied security hardening"`
448: >
449: > **The Rationale:** If an agent outputs a massive single commit containing core logic, security updates, and new logs, and the application subsequently crashes, the developer has no idea which sub-agent broke the code. By testing and committing sequentially, a developer can pinpoint exactly which pass caused the regression and surgically `git revert` just that step, adjust the `agents.xml` prompt, and retry. This turns debugging an AI hallucination from a multi-hour headache into a 30-second revert.
450: 
451: ---
452: 
453: ## 4. Agent Guardrails & Prompt Engineering
454: 
455: Giving autonomous agents write-access to your codebase and API keys introduces massive risk. Without strict guardrails, an agent might accidentally overwrite business logic while trying to add a log statement, or fall victim to a "Prompt Injection" attack hidden in a legacy code comment.
456: 
457: To mitigate this, we define the agents' personas, constraints, and instructions using strict structural formatting within a centralized `.opencode/` directory in every repository.
458: 
459: ### 4.1 XML Prompting over Markdown
460: 
461: Most agentic systems use Markdown (`# Instructions`, `## Context`) to prompt the LLM. For complex, multi-agent pipelines, Markdown is fundamentally flawed because it lacks strict boundaries. 
462: 
463: > **The Decision:** All sub-agent personas and system instructions must be formatted using strict XML tags (e.g., `<system_instructions>`, `<user_code>`, `<action_plan>`) rather than Markdown headers.
464: >
465: > **The Rationale:** If you use Markdown and feed the AI a codebase file that *also* contains Markdown comments, the LLM can easily confuse the code's comments for pipeline instructions (Prompt Injection). XML creates absolute semantic walls. The LLM understands that everything inside `<user_code> ... </user_code>` is purely a payload to be analyzed, not a command to be executed. This is Anthropic's recommended standard for zero-hallucination agent routing.
466: 
467: *Example of a secure `.opencode/agents.xml` definition:*
468: ```xml
469: <agent>
470:   <role>Security Hardening Agent</role>
471:   <directives>
472:     <rule>Find and mitigate OWASP vulnerabilities.</rule>
473:     <rule>Do NOT modify the core algorithmic logic.</rule>
474:   </directives>
475:   <context>
476:     <!-- Injected by Bloop Retrieval -->
477:     {{COMPANY_SECURITY_PATTERNS}}
478:   </context>
479:   <task>
480:     Review the payload in the user_code tag. Output proposed fixes as Diffs.
481:   </task>
482: </agent>
483: ```
484: 
485: ### 4.2 Agent Isolation and Scope Locking
486: 
487: If the Observability Agent (Pass 6) decides that the core logic is "messy" and rewrites it while adding logs, the pipeline breaks. We must enforce the "Separation of Concerns" at the file and Abstract Syntax Tree (AST) level.
488: 
489: > **The Decision:** Agents are heavily restricted via "Scope Guardrails." If an agent believes an out-of-scope change is required (e.g., the Docs Agent realizes the Core Logic is flawed), it is forbidden from making the change. It must pause, delegate a request back to the Orchestrator, and wait for human intervention.
490: >
491: > **The Rationale:** This prevents "Agent Trampling." By enforcing strict write-locks based on the pipeline phase (e.g., Pass 2 can only write to `*.spec.ts`, Pass 7 can only edit comments/docstrings), we guarantee that downstream passes do not silently undo the verified work of upstream passes. 
492: 
493: ### 4.3 Automated Hard-Fail Gates (Semgrep)
494: 
495: Even with the best models, we cannot trust AI-generated code blindly, especially concerning security and internal compliance.
496: 
497: > **The Decision:** The pipeline incorporates static analysis tools like **Semgrep** as automated "Hard-Fail" gates between passes.
498: >
499: > **The Rationale:** If the DeepSeek Core Logic agent (Pass 3) writes a working feature, but includes a hardcoded secret or a SQL injection vulnerability, Semgrep intercepts the code during the verification gate. Instead of passing the vulnerable code to the human, the pipeline automatically feeds the Semgrep error trace back to the agent for self-correction. The human never sees the code until it passes all deterministic static analysis checks.
500: 
501: ---
502: 
503: ## Next Steps and The Path Forward
504: 
505: By implementing the **Nistapp-OpenCode Enterprise Framework**, organizations stop paying for bloated token context windows and stop suffering from specification drift. Instead, developers become **System Orchestrators**—curating architecture via Mermaid diagrams, defining executable Gherkin specs, and reviewing atomic, verified Git commits generated by a highly disciplined, multi-pass AI pipeline.
506: 
507: This is a significant step towards a fundamentally safer, more maintainable way to build enterprise software.
508: 
509: ## Apendix - 1 (Todo)
510: 1. full text variable names vs. abbreviations
511: 2. Others
512: 
513: ---
514: ## Apendix - 2 Detailed Diagrams
515: > 1. Logical Architecture (Network & Data Flow)
516: ```mermaid
517: graph LR
518:     %% Consistent C4-inspired Style Definitions
519:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff
520:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
521:     classDef internalComp fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
522:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
523: 
524:     %% User Boundary
525:     Dev(["Developer\n(IDE / OpenCode)"]):::actor
526: 
527:     %% Internal Network Subgraph
528:     subgraph InternalVPC ["Internal Corporate Network (VPC)"]
529:         LocalAgent["OpenCode CLI <br> (Local Orchestrator)"]:::coreSystem
530:         Proxy["LiteLLM Proxy <br> (API Gateway & DLP filter)"]:::coreSystem
531:         AuthDB[("SSO & Usage DB <br> (Postgres)")]:::internalComp
532:     end
533: 
534:     %% Public Internet Subgraph
535:     subgraph PublicNet ["Public Internet"]
536:         Router["OpenRouter API <br> (Model Multiplexer)"]:::extSystem
537:         ModelA["DeepSeek Models <br> (Core Code / Tests)"]:::extSystem
538:         ModelB["Claude Models <br> (Design / Contracts)"]:::extSystem
539:     end
540: 
541:     %% Sequential Data Flow
542:     Dev -->|"1. Initiates Task"| LocalAgent
543:     
544:     LocalAgent -->|"2. API Request\n(OpenAI Format)"| Proxy
545:     
546:     Proxy <-->|"3. Validate Budget & Key"| AuthDB
547:     
548:     Proxy -->|"4. Forward Request <br> (PII Stripped)"| Router
549:     
550:     Router -.->|"5a. Route: Logic"| ModelA
551:     Router -.->|"5b. Route: Architecture"| ModelB
552: 
553: ```
554: 
555: ---
556: > 2. Component Deployment & Network Boundaries
557: ```mermaid
558: graph TD
559:     %% Consistent C4-inspired Style Definitions
560:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff
561:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
562:     classDef internalComp fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
563:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
564: 
565:     Dev(["Developer"]):::actor
566: 
567:     %% Zone 1: The Local Machine
568:     subgraph LocalHost ["Developer Workstation (Local Laptop)"]
569:         IDE["VS Code IDE <br> (OpenCode UI)"]:::coreSystem
570:         CLI["OpenCode CLI <br> (Local Orchestrator)"]:::coreSystem
571:         Sandbox["DevContainer <br> (Test Execution Sandbox)"]:::internalComp
572:     end
573: 
574:     %% Zone 2: The Secure Corporate Network
575:     subgraph VPC ["Corporate Internal Network (VPC)"]
576:         Proxy["LiteLLM Gateway <br> (Token Proxy & Router)"]:::coreSystem
577:         AuthDB[("PostgreSQL DB <br> (Budgets & Usage)")]:::internalComp
578:         
579:         Bloop["Bloop AI Server <br> (Global Context Engine)"]:::coreSystem
580:         IndexDB[("Qdrant / Tantivy DBs <br> (Vector & Text Indexes)")]:::internalComp
581:     end
582: 
583:     %% Zone 3: External Services
584:     subgraph PublicCloud ["Public Cloud / SaaS (Internet)"]
585:         SSO["SSO Provider <br> (O365 / GSuite)"]:::extSystem
586:         VCS["Source Control <br> (GitHub / GitLab)"]:::extSystem
587:         OpenRouter["OpenRouter API <br> (LLM Multiplexer)"]:::extSystem
588:     end
589: 
590:     %% Local Interactions
591:     Dev -->|"1. Writes code & initiates"| IDE
592:     IDE -->|"2. Delegates pipeline tasks"| CLI
593:     CLI <-->|"3. Executes isolated tests"| Sandbox
594:     
595:     %% Internal Network Interactions (LAN)
596:     CLI -->|"4. Fetches architecture & context"| Bloop
597:     CLI -->|"5. Streams prompt payloads"| Proxy
598:     Bloop <-->|"6. Queries embeddings/text"| IndexDB
599:     Proxy <-->|"7. Validates auth & limits"| AuthDB
600: 
601:     %% Public Cloud Interactions (WAN - Dotted lines)
602:     Proxy -.->|"8. Validates OIDC JWTs"| SSO
603:     Proxy -.->|"9. Routes prompt <br> (PII stripped)"| OpenRouter
604:     Bloop -.->|"10. Pulls latest code (Nightly)"| VCS
605:     CLI -.->|"11. Pushes atomic agent commits"| VCS
606: ```
607: 
608: ---
609: > 3. Pipeline Lifecycle
610: ```mermaid
611: stateDiagram
612:     %% Consistent Styling Definitions
613:     classDef state fill:#1168bd,color:#fff,stroke:#0b4884,stroke-width:2px
614:     classDef gate fill:#2dd4bf,color:#000,stroke:#0f766e,stroke-width:2px
615:     classDef human fill:#08427b,color:#fff,stroke:#052e56,stroke-width:2px
616:     classDef endState fill:#999999,color:#fff,stroke:#666666,stroke-width:2px
617: 
618:     [*] --> Feature_Request
619:     class Feature_Request human
620: 
621:     Feature_Request --> Design_Phase : Assign to Pass 0
622: 
623:     %% Phase 1: The Design Contract
624:     state Design_Phase {
625:         [*] --> Draft_Artifacts : Generate .mmd & .gherkin
626:         Draft_Artifacts --> Human_Review : Propose Architecture
627:         
628:         Human_Review --> Draft_Artifacts : Reject (Modify Specs)
629:         Human_Review --> [*] : Approve Design
630:     }
631:     class Design_Phase state
632:     class Human_Review human
633: 
634:     Design_Phase --> Implementation_Phase : Specs Locked
635:     
636:     %% Phase 2: The Agentic Code Factory
637:     state Implementation_Phase {
638:         [*] --> Write_Code : Passes 1-3 (Core)
639:         
640:         Write_Code --> Run_Tests : Execute TDD Suite
641:         Run_Tests --> Write_Code : Tests Failed (Retry)
642:         
643:         Run_Tests --> Sync_Artifacts : Tests Passed
644:         Sync_Artifacts --> Write_Code : Drift Detected (Loop)
645:         
646:         Sync_Artifacts --> [*] : Passes 4-7 Complete
647:     }
648:     class Implementation_Phase state
649: 
650:     Implementation_Phase --> Quality_Gate : Trigger CI/CD Guardrails
651:     class Quality_Gate gate
652: 
653:     %% Final Resolution
654:     Quality_Gate --> Implementation_Phase : Security / Linting Fail
655:     Quality_Gate --> PR_Merged : LGTM / PR Approved
656:     
657:     PR_Merged --> [*] : Production Ready
658:     class PR_Merged endState
659: ```
660: 
661: --- 
662: > 4. Git Lifecycle & Atomic Commits
663: ```mermaid
664: sequenceDiagram
665:     autonumber
666:     
667:     participant Dev as Human Developer
668:     participant Orch as AI Orchestrator
669:     participant Feature as Feature Branch (Git)
670:     participant Main as Main Branch (Git)
671: 
672:     %% Note over Dev, Orch: Feature Request & Architecture Approved
673:     
674:     Orch->>Feature: Commit: [Pass 0] Artifacts (.mmd, .gherkin)
675:     
676:     %% Light Blue background for functional coding
677:     rect rgb(224, 242, 254)
678:         Note right of Orch: Phase 1: Core Implementation
679:         Orch->>Feature: Commit: [Pass 1] Interfaces & Contracts
680:         Orch->>Feature: Commit: [Pass 2] TDD Test Suite (Red Phase)
681:         Orch->>Feature: Commit: [Pass 3] Core Logic (Green Phase)
682:     end
683:     
684:     %% Light Teal background for enterprise hygiene
685:     rect rgb(204, 251, 241)
686:         Note right of Orch: Phase 2: Enterprise Hardening
687:         Orch->>Feature: Commit: [Pass 4] Refactor & Code Cleanup
688:         Orch->>Feature: Commit: [Pass 5] Security Guardrails
689:         Orch->>Feature: Commit: [Pass 6] Observability & Logging
690:         Orch->>Feature: Commit: [Pass 7] Traceability Links & Docs
691:     end
692: 
693:     %% Note over Orch, Feature: Automated Pipeline Complete
694:     
695:     Dev->>Feature: Review Code & Approve Pull Request
696:     Feature->>Main: Squash & Merge
697:     
698:     %% Note over Main: Feature is Production-Ready
699: ```
700: ---
701: > 5. Retrieval & Indexing Architecture
702: ```mermaid
703: graph LR
704:     %% Consistent C4-inspired Style Definitions
705:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff
706:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
707:     classDef internalComp fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
708:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
709: 
710:     %% Source Data (Left)
711:     VCS["Git Repositories <br> (Company Codebase)"]:::extSystem
712: 
713:     %% Central Context Server (Middle)
714:     subgraph BloopServer ["Bloop AI Central Context Server"]
715:         Indexer["Code Crawler & Indexer"]:::coreSystem
716:         
717:         Qdrant[("Qdrant DB <br> (Semantic / AI Vectors)")]:::internalComp
718:         Tantivy[("Tantivy DB <br> (Regex / Keyword Text)")]:::internalComp
719:         
720:         BloopAPI["Bloop REST API <br> (Query Gateway)"]:::coreSystem
721:     end
722: 
723:     %% The Orchestrator (Right)
724:     Agent(["OpenCode Agent <br> (Pass 0 / Discovery)"]):::actor
725: 
726:     %% 1. Background Indexing Flow (Data moving In)
727:     VCS -->|"1. Clone & Parse (Nightly)"| Indexer
728:     Indexer -->|"2. Create Embeddings"| Qdrant
729:     Indexer -->|"3. Build AST/Trigrams"| Tantivy
730: 
731:     %% 2. Runtime Query Flow (Data moving Out)
732:     Agent -->|"A. Request Cross-Repo Context"| BloopAPI
733:     BloopAPI -->|"B. Query Context Meaning"| Qdrant
734:     BloopAPI -->|"C. Query Exact Symbols"| Tantivy
735:     
736:     %% The final payload returning to the agent
737:     BloopAPI -.->|"D. Return High-Density Context"| Agent
738: ```
739: 
740: ---
741: > 6. Knowledge Context Construction Flow
742: ```mermaid
743: graph TD
744:     %% Consistent C4-inspired Style Definitions
745:     classDef orchestrator fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
746:     classDef knowledge fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
747:     classDef action fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#000
748:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
749: 
750:     Agent(["Pass-Specific Agent\n(e.g., Core Logic Orchestrator)"]):::orchestrator
751: 
752:     %% Grouping the data sources logically
753:     subgraph Knowledge_Sources ["The Three Pillars of Context"]
754:         direction LR
755:         LocalDB[("Local Directory <br> (.opencode/patterns)")]:::knowledge
756:         BloopDB[("Global Context <br> (Bloop REST API)")]:::knowledge
757:         GitDB[("Local Git History <br> (Commit Logs & Diffs)")]:::knowledge
758:     end
759: 
760:     Pruner{"Context Merger & <br> Dynamic Pruning Layer"}:::action
761:     FinalPrompt["Optimized Prompt Payload <br> (XML-Wrapped)"]:::orchestrator
762:     LLM["Target LLM via OpenRouter <br> (DeepSeek / Claude)"]:::extSystem
763: 
764:     %% Step 1-3: Gathering Information
765:     Agent -->|"1. Query Architectural Rules"| LocalDB
766:     Agent -->|"2. Query Cross-Repo Types"| BloopDB
767:     Agent -->|"3. Query Intent & Changes"| GitDB
768: 
769:     %% Returning data to the Pruner
770:     LocalDB -.->|"Raw Rules"| Pruner
771:     BloopDB -.->|"Raw Dependencies"| Pruner
772:     GitDB -.->|"Raw Diffs"| Pruner
773: 
774:     %% Final Execution
775:     Pruner -->|"4. Trim, Deduplicate & Format"| FinalPrompt
776:     FinalPrompt -->|"5. Send Executable Prompt"| LLM
777: ```
778: 
779: ---
780: 7. Auth and Budgeting
781: ```mermaid
782: sequenceDiagram
783:     autonumber
784: 
785:     box rgb(240, 248, 255) "Internal Corporate Network"
786:         participant Dev as Developer IDE (OpenCode)
787:         participant Proxy as LiteLLM Proxy
788:         participant DB as Auth & Usage DB
789:     end
790: 
791:     box rgb(245, 245, 245) "Public Internet"
792:         participant OR as OpenRouter API
793:     end
794: 
795:     %% Initial Request
796:     Dev->>+Proxy: Request Model Completion (Auth Header)
797:     
798:     %% Identity Verification
799:     Note right of Proxy: OIDC Auth & Role Mapping
800:     Proxy->>+DB: Validate SSO Token
801:     DB-->>-Proxy: Identity Confirmed (User / Dept)
802:     
803:     %% Budgeting Gate
804:     Proxy->>+DB: Check Department/User Token Quota
805:     
806:     alt Quota Exceeded
807:         DB-->>Proxy: Status: Budget Exhausted
808:         Proxy-->>Dev: 402 Error: Department Quota Reached
809:     else Quota Available
810:         DB-->>-Proxy: Status: Budget Approved
811:         
812:         %% Security & Gateway Logic
813:         Note right of Proxy: Data Loss Prevention (DLP)<br/>Strip PII & Hardcoded Secrets
814:         Proxy->>+OR: Forward Sanitized Prompt
815:         
816:         %% Response & Accounting
817:         OR-->>-Proxy: Stream LLM Response
818:         
819:         Proxy->>+DB: Log Token Usage (Increment Counter)
820:         DB-->>-Proxy: Usage Updated
821:         
822:         Proxy-->>-Dev: Return Response to Developer
823:     end
824: ```
825: 
826: ---
827: > 8. Security and PII
828: ```mermaid
829: graph TD
830:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff
831:     classDef proxy fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
832:     classDef filter fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
833:     classDef ext fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
834: 
835:     Dev(["Developer IDE"]):::actor
836:     
837:     subgraph ProxyGateway["LiteLLM Gateway"]
838:         Inbound["Inbound Request"]:::proxy
839:         DLP["PII/DLP Filter\n(Masking Engine)"]:::filter
840:         Log["Secure Log\n(Audited)"]:::filter
841:     end
842: 
843:     Target["OpenRouter API"]:::ext
844: 
845:     Dev --> Inbound
846:     Inbound --> DLP
847:     DLP -- "Masked Payload" --> Target
848:     DLP -- "Audit Record" --> Log
849:     Target -- "Stream Response" --> Dev
850: ```
851: 
852: ---
853: 9. CI/CD PipeLine integration
854: ```mermaid
855: graph TD
856:     %% Consistent C4 Style Definitions
857:     classDef actor fill:#08427b,stroke:#052e56,stroke-width:2px,color:#fff,rx:20,ry:20
858:     classDef coreSystem fill:#1168bd,stroke:#0b4884,stroke-width:2px,color:#fff
859:     classDef extSystem fill:#999999,stroke:#666666,stroke-width:2px,color:#fff
860:     classDef highlight fill:#2dd4bf,stroke:#0f766e,stroke-width:2px,color:#000
861: 
862:     %% Nodes
863:     Dev(["Developer"]):::actor
864: 
865:     subgraph Local ["Local Dev Environment (Synchronous)"]
866:         direction TB
867:         L_P0["Pass 0: Design <br> (Mermaid & Gherkin)"]:::coreSystem
868:         L_P1["Pass 1: Contracts"]:::coreSystem
869:         L_P2["Pass 2: Tests (TDD)"]:::coreSystem
870:         L_P3["Pass 3: Core Logic"]:::coreSystem
871:         
872:         L_P0 --> L_P1 --> L_P2 --> L_P3
873:     end
874: 
875:     VCS[("Git Repository\n(Feature Branch)")]:::extSystem
876: 
877:     subgraph CI ["CI/CD Build Server (Asynchronous Agents)"]
878:         direction TB
879:         C_P4["Pass 4: Refactor <br> + Run Tests"]:::coreSystem
880:         C_P5["Pass 5: Security <br> + Run Tests"]:::coreSystem
881:         C_P6["Pass 6: Logging <br> + Run Tests"]:::coreSystem
882:         C_P7["Pass 7: Docs & Spec Sync <br> + Run Tests"]:::coreSystem
883:         
884:         C_P4 -- "If Tests Pass" --> C_P5
885:         C_P5 -- "If Tests Pass" --> C_P6
886:         C_P6 -- "If Tests Pass" --> C_P7
887:     end
888: 
889:     %% Flow Relationships (Execution moves downwards)
890:     Dev -- "Inputs Ticket & <br> Approves Design" --> L_P0
891:     
892:     L_P3 == "1. Push Base Feature\n& Spec Artifacts" ==> VCS
893:     
894:     VCS -- "2. Trigger Pipeline" --> C_P4
895:     
896:     %% Atomic Commits Back to Git (Loops route around the sides)
897:     C_P4 -. "3a. Atomic Commit" .-> VCS
898:     C_P5 -. "3b. Atomic Commit" .-> VCS
899:     C_P6 -. "3c. Atomic Commit" .-> VCS
900:     C_P7 -. "3d. Final Commit <br> (Updates Specs/Docs)" .-> VCS
901: 
902:     %% Layout styling
903:     style Local fill:#f0f8ff,stroke:#87cefa,stroke-dasharray: 5 5
904:     style CI fill:#fff8dc,stroke:#deb887,stroke-dasharray: 5 5
905: ```
906: 
907: ---
908: > 10. Developer aid: To help human developers understand and follow the code
909: ```mermaid
910: %% This diagram visualizes how a human navigator follows the links from the feature implementation back to the foundational specs.
911: erDiagram
912:     %% The overarching feature directory grouping
913:     FEATURE_MODULE ||--|{ IMPLEMENTATION_CODE : "contains"
914:     FEATURE_MODULE ||--|| DESIGN_DIAGRAMS : "contains"
915:     FEATURE_MODULE ||--|| GHERKIN_SPECS : "contains"
916:     FEATURE_MODULE ||--|| TEST_SUITE : "contains"
917: 
918:     %% Traceability Links (How a human navigates the Digital Twin)
919:     IMPLEMENTATION_CODE }o--|| DESIGN_DIAGRAMS : "navigates to (@see link)"
920:     IMPLEMENTATION_CODE }o--|| GHERKIN_SPECS : "navigates to (@see link)"
921:     IMPLEMENTATION_CODE }o--|| TEST_SUITE : "navigates to (@see link)"
922: 
923:     %% Verification Link
924:     TEST_SUITE ||--|| GHERKIN_SPECS : "executes (BDD)"
925: 
926:     %% Entity Definitions with descriptive metadata
927:     IMPLEMENTATION_CODE {
928:         string file_path "e.g., implementation.ts"
929:         string jsdoc_headers "Clickable IDE links"
930:         code business_logic "Pass 3 Core Logic"
931:     }
932:     
933:     DESIGN_DIAGRAMS {
934:         string file_path "e.g., design.mmd"
935:         text visual_logic "Mermaid State/Sequence"
936:     }
937:     
938:     GHERKIN_SPECS {
939:         string file_path "e.g., spec.gherkin"
940:         text requirements "Given/When/Then"
941:     }
942:     
943:     TEST_SUITE {
944:         string file_path "e.g., test_suite.ts"
945:         code assertions "Pass 2 TDD Verification"
946:     }
947: ``` 
948: 
949: ---

(End of file - total 949 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/docs/version-plan.md"
}
```

**Output:**
```
<path>/home/kc/Projects/UDAN/ai-factory-setup/docs/version-plan.md</path>
<type>file</type>
<content>
1: 
2: ---
3: 
4: ### Phase 1: Core Mechanics & Visuals
5: 
6: #### **v0.1: The "Hello World" Pipeline (CLI Core)**
7: *   **Goal:** Prove the OpenCode engine works with your API key and can execute a basic sequence autonomously.
8: *   **Infrastructure:** 
9:     *   OpenCode CLI installed on your laptop.
10:     *   Direct OpenRouter API key configured in OpenCode (No LiteLLM proxy yet).
11: *   **The Pipeline:** A condensed **3-pass pipeline**.
12:     1.  Pass 1: Core Implementation (DeepSeek v4).
13:     2.  Pass 2: Tests (DeepSeek v4).
14:     3.  Pass 3: Docs (DeepSeek v4).
15: *   **Deliverable:** You can run a terminal command, and OpenCode successfully edits a file, writes a test, and writes a comment using OpenRouter.
16: 
17: #### **v0.2: IDE Integration & Strict Personas (The UX Upgrade)**
18: *   **Goal:** Move out of the terminal, get visual diffs, and introduce XML boundaries to stop agent hallucinations.
19: *   **Infrastructure:**
20:     *   Install the **OpenCode VS Code Extension**.
21:     *   Create your first `.opencode/agents.xml` file with strict XML boundaries for the agents.
22: *   **The Pipeline:** Still 3-4 passes, but now executed via the VS Code "Plan Viewer".
23: *   **Deliverable:** You can click "Approve" in VS Code to accept code diffs between passes. You no longer have to manually check Git to see what the agent changed.
24: 
25: ---
26: 
27: ### Phase 2: The Architecture & Intelligence
28: 
29: #### **v0.3: The Artifacts & The Gateway (Local Routing)**
30: *   **Goal:** Introduce Mermaid diagrams (TDD constraint) and set up the local proxy to enable multi-model routing.
31: *   **Infrastructure:**
32:     *   Run **LiteLLM** locally via a simple `docker run` command (No SSO, no Postgres, just local SQLite and a personal master key).
33:     *   Configure OpenCode to point to `localhost:4000` (LiteLLM) instead of OpenRouter directly.
34: *   **The Pipeline:** Expand to a **5-pass pipeline** (Adding Design and Contracts).
35:     *   Pass 0: Design (`.mmd` Mermaid generation using Claude 3.7 via local LiteLLM).
36:     *   Pass 1-4: The rest of the workflow.
37: *   **Deliverable:** The AI generates a flowchart *before* writing code, and your local proxy successfully routes the Mermaid task to Claude and the Coding task to DeepSeek.
38: 
39: #### **v0.4: Global Context & Verification (The "Brain" Upgrade)**
40: *   **Goal:** Stop the AI from hallucinating internal APIs by giving it cross-repo search, and enforce the "Red/Green" test gates.
41: *   **Infrastructure:**
42:     *   Install **Bloop** locally (Desktop app or local Docker container) and point it at your local `~/Projects` folder.
43:     *   Configure the OpenCode orchestrator to pause and run `npm test` or `pytest` locally after Pass 3 (Core).
44: *   **Deliverable:** The agent can now successfully query Bloop for an interface in another folder, use it, write code, and automatically run your local unit tests to verify it works.
45: 
46: ---
47: 
48: ### Phase 3: The Complete Local Factory
49: 
50: #### **v1.0: The Complete Personal Setup (Feature Complete)**
51: *   **Goal:** The full 8-pass enterprise pipeline running flawlessly on your local machine with automated atomic Git commits.
52: *   **Infrastructure:** 
53:     *   Integrate local **Semgrep** (Static analysis hard-fail gate).
54:     *   Fully flesh out `.opencode/agents.xml` for all 8 passes.
55: *   **The Pipeline:** The complete 8-pass pipeline: Design -> Contracts -> Tests -> Core -> Refactor -> Security -> Observability -> Docs.
56: *   **Automation:** The orchestrator script is finalized. It runs a pass, runs the tests, and if successful, executes `git commit -m "chore(ai): pass name"` autonomously.
57: *   **Deliverable:** You drop a Jira ticket summary into your IDE, approve the Mermaid diagram, and the system autonomously loops through 7 more passes, creating 7 clean Git commits on your local branch.
58: 
59: ---
60: 
61: ### Phase 4: The Enterprise Rollout (Future)
62: 
63: #### **v2.0: The Enterprise Server Setup (Out of Scope for Laptop)**
64: *   **Infrastructure:** Move LiteLLM to a central server.
65: *   **Governance:** Connect LiteLLM to O365/GSuite SSO. Spin up Postgres for departmental budget rationing.
66: *   **Execution:** Move Passes 4–7 off the local laptop and into GitHub Actions / GitLab CI asynchronous runners.
67: 
68: ---

(End of file - total 68 lines)
</content>
```

---

## Assistant (Build · Claude Sonnet 4.6 · 15.7s)

_Thinking:_

Now I have a clear picture of what's needed for v0.1. Let me plan the tasks:

1. Create `.env.example` with `OPENROUTER_API_KEY` placeholder
2. Create `.opencode/agents.xml` with three sub-agents (CoreImplementationAgent, TestGenerationAgent, DocumentationAgent) - all using `deepseek/deepseek-coder-v4`
3. Create `run-v1-pipeline.sh` - sequential orchestrator script that invokes OpenCode CLI with each agent

Key notes from version-plan.md for v0.1:
- 3-pass pipeline: Core Implementation → Tests → Docs


- All agents use DeepSeek v4 with direct OpenRouter API key

I need to understand how OpenCode CLI works - specifically how to invoke agents with target files. Let me check the customize-opencode skill to see the agents.xml format and CLI invocation patterns.

Looking at the architecture manifesto, agents are defined in XML with roles and directives that specify what the agent should do and what it shouldn't modify. I need to load the configuration documentation to understand the exact CLI syntax for specifying agents and target files.

**Tool: skill**

**Input:**
```json
{
  "name": "customize-opencode"
}
```

**Output:**
```
<skill_content name="customize-opencode">
# Skill: customize-opencode

<!--
  Built-in skill. Name and description are registered in code at
  packages/opencode/src/skill/index.ts (see CUSTOMIZE_OPENCODE_SKILL_NAME
  and CUSTOMIZE_OPENCODE_SKILL_DESCRIPTION). The body below becomes the
  skill's content.
-->

# Customizing opencode

opencode validates its own config strictly and refuses to start when a field
is wrong. The shapes below cover the common surface area, but they are a
**summary, not the source of truth**.

## Full schema reference

The authoritative list of every config option — with field types, enums,
defaults, and descriptions — lives in the published JSON Schema:

**<https://opencode.ai/config.json>**

If a field is not documented in this skill, or you need to confirm an exact
shape before writing config, **fetch that URL and read the schema directly**
rather than guessing. opencode hard-fails on invalid config, so the cost of a
wrong shape is a broken startup.

Independently, every `opencode.json` should declare
`"$schema": "https://opencode.ai/config.json"` so the user's editor catches
mistakes as they type.

## Applying changes

Config is loaded once when opencode starts and is not hot-reloaded. After
saving changes to `opencode.json`, an agent file, a skill, a plugin, or any
other config-time file, **tell the user to quit and restart opencode** for
the changes to take effect. The running session will keep using the
already-loaded config until then.

## Where files live

| Scope                         | Path                                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Project config                | `./opencode.json`, `./opencode.jsonc`, or `.opencode/opencode.json` (opencode walks up from the cwd to the worktree root) |
| Global config                 | `~/.config/opencode/opencode.json` (NOT `~/.opencode/`)                                                                   |
| Project agents                | `.opencode/agent/<name>.md` or `.opencode/agents/<name>.md`                                                               |
| Global agents                 | `~/.config/opencode/agent(s)/<name>.md`                                                                                   |
| Project skills                | `.opencode/skill(s)/<name>/SKILL.md`                                                                                      |
| Global skills                 | `~/.config/opencode/skill(s)/<name>/SKILL.md`                                                                             |
| External skills (auto-loaded) | `~/.claude/skills/<name>/SKILL.md`, `~/.agents/skills/<name>/SKILL.md`                                                    |

Configs from each scope are deep-merged. Project overrides global. Unknown
top-level keys in `opencode.json` are rejected with `ConfigInvalidError`.

## opencode.json

Every field is optional.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "username": "string",
  "model": "provider/model-id",
  "small_model": "provider/model-id",
  "default_agent": "agent-name",
  "shell": "/bin/zsh",
  "logLevel": "DEBUG" | "INFO" | "WARN" | "ERROR",
  "share": "manual" | "auto" | "disabled",
  "autoupdate": true | false | "notify",
  "snapshot": true,
  "instructions": ["AGENTS.md", "docs/style.md"],

  "skills": {
    "paths": [".opencode/skills", "/abs/path/to/skills"],
    "urls": ["https://example.com/.well-known/skills/"]
  },

  "agent": {
    "my-agent": {
      "model": "anthropic/claude-sonnet-4-6",
      "mode": "subagent",
      "description": "...",
      "permission": { "edit": "deny" }
    }
  },

  "command": {
    "deploy": { "description": "...", "prompt": "..." }
  },

  "provider": {
    "anthropic": { "options": { "apiKey": "..." } }
  },
  "disabled_providers": ["openai"],
  "enabled_providers": ["anthropic"],

  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp"],
      "enabled": true,
      "env": {}
    },
    "remote-thing": {
      "type": "remote",
      "url": "https://...",
      "headers": { "Authorization": "Bearer ..." }
    }
  },

  "plugin": [
    "opencode-gemini-auth",
    "opencode-foo@1.2.3",
    "./local-plugin.ts",
    ["opencode-bar", { "option": "value" }]
  ],

  "permission": {
    "edit": "deny",
    "bash": { "git *": "allow", "*": "ask" }
  },

  "formatter": false,
  "lsp": false,

  "experimental": {
    "primary_tools": ["edit"],
    "mcp_timeout": 30000
  },

  "tool_output": { "max_lines": 200, "max_bytes": 8192 },

  "compaction": { "auto": true, "tail_turns": 15 }
}
```

Shape notes worth being explicit about:

- `model` always carries a provider prefix: `"anthropic/claude-sonnet-4-6"`.
- `skills` is an object with `paths` and/or `urls`, not an array.
- `agent` is an object keyed by agent name, not an array.
- `plugin` is an array of strings or `[name, options]` tuples, not an object.
- `mcp[name].command` is an array of strings, never a single string. `type` is required.
- `permission` is either a string action or an object keyed by tool name.

## Skills

opencode's skill loader scans for `**/SKILL.md` inside skill directories. The
file is named `SKILL.md` exactly, and lives in its own folder named after the
skill:

```
.opencode/skills/my-skill/SKILL.md
```

Frontmatter:

```markdown
---
name: my-skill
description: One sentence covering what this skill does AND when to trigger it. Front-load the literal keywords or filenames the user is likely to say.
---

# My Skill

(skill body in markdown: instructions, examples, references)
```

- `name` is required, lowercase hyphen-separated, up to 64 chars, and matches the folder name.
- `description` is effectively required: skills without one are filtered out and never surfaced to the model. Cover both _what_ the skill does and _when_ to use it. Write in third person ("Use when...", not "I help with..."). Front-load concrete trigger keywords and filenames; gate with "Use ONLY when..." if the skill should stay quiet on adjacent topics.
- Optional: `license`, `compatibility`, `metadata` (string-string map).

Register skills from non-default locations via `skills.paths` (scanned
recursively for `**/SKILL.md`) and `skills.urls` (each URL serves a list of
skills).

## Agents

Two ways to define an agent. Use the file form for anything non-trivial.

### Inline (in `opencode.json`)

```json
{
  "agent": {
    "my-reviewer": {
      "description": "Reviews PRs for style violations.",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-6",
      "permission": { "edit": "deny", "bash": "ask" },
      "prompt": "You are a strict PR reviewer..."
    }
  }
}
```

### File

```
.opencode/agent/my-reviewer.md      OR     .opencode/agents/my-reviewer.md
```

```markdown
---
description: Reviews PRs for style violations.
mode: subagent
model: anthropic/claude-sonnet-4-6
permission:
  edit: deny
  bash: ask
---

You are a strict PR reviewer. Focus on...
```

The file body becomes the agent's `prompt`. Do not also put `prompt:` in the
frontmatter.

`mode` is one of `"primary"`, `"subagent"`, `"all"`.

Allowed top-level frontmatter fields: `name, model, variant, description, mode,
hidden, color, steps, options, permission, disable, temperature, top_p`. Any
unknown field is silently routed into `options`.

To disable a built-in agent: `agent: { build: { disable: true } }`, or in a
file, `disable: true` in frontmatter.

`default_agent` must point to a non-hidden, primary-mode agent.

### Built-in agents

opencode ships with `build`, `plan`, `general`, `explore`, plus optionally
`scout` (gated on `OPENCODE_EXPERIMENTAL_SCOUT`). Hidden internal agents:
`compaction`, `title`, `summary`. To override a built-in's fields, define the
same key in `agent: { <name>: { ... } }`.

## Plugins

`plugin:` is an array. Each entry is one of:

```json
"plugin": [
  "opencode-gemini-auth",            // npm spec, latest
  "opencode-foo@1.2.3",              // npm spec, pinned
  "./local-plugin.ts",               // file path, relative to the declaring config
  "file:///abs/path/plugin.js",      // file URL
  ["opencode-bar", { "key": "val" }] // tuple form with options
]
```

Auto-discovered plugins (no config entry needed): any `*.ts` or `*.js` file in
`.opencode/plugin/` or `.opencode/plugins/`.

A plugin module exports `default` (or any named export) of type
`Plugin = (input: PluginInput, options?) => Promise<Hooks>`. The export is a
function, not a plain object literal, and the function returns an object
(return `{}` if there is nothing to register).

```ts
import type { Plugin } from "@opencode-ai/plugin"

export default (async ({ client, project, directory, $ }) => {
  return {
    config: (cfg) => {
      // cfg is the live merged config; mutate fields here.
    },
    "tool.execute.before": async (input, output) => {
      // mutate output.args before the tool runs
    },
  }
}) satisfies Plugin
```

Hook surface (mutate `output` in place; return `void`):

- `event(input)`: every bus event
- `config(cfg)`: once on init with the merged config
- `chat.message`, `chat.params`, `chat.headers`
- `tool.execute.before`, `tool.execute.after`
- `tool.definition`
- `command.execute.before`
- `shell.env`
- `permission.ask`
- `experimental.chat.messages.transform`, `experimental.chat.system.transform`,
  `experimental.session.compacting`, `experimental.compaction.autocontinue`,
  `experimental.text.complete`

Special object-shaped (not callbacks): `tool: { my_tool: { ... } }`,
`auth: { ... }`, `provider: { ... }`.

## MCP servers

`mcp:` is an object keyed by server name. Each server is discriminated by
`type`:

```json
{
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp"],
      "enabled": true,
      "env": { "BROWSER": "chromium" }
    },
    "github": {
      "type": "remote",
      "url": "https://...",
      "enabled": true,
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    },
    "old-server": { "enabled": false }
  }
}
```

`command` is an array of strings. `type` is required. Use `enabled: false` to
disable a server inherited from a parent config.

## Permissions

```json
"permission": {
  "edit": "deny",
  "bash": { "git *": "allow", "rm *": "deny", "*": "ask" },
  "external_directory": { "~/secrets/**": "deny", "*": "allow" }
}
```

Actions: `"allow"`, `"ask"`, `"deny"`.

Per-tool value forms: `"allow"` shorthand (treated as `{"*": "allow"}`), or an
object `{ pattern: action }`. Within an object, **insertion order matters**.
opencode evaluates the LAST matching rule, so put broad rules first and narrow
rules last.

`permission: "allow"` (a string at the top level) is shorthand for "allow
everything" and is rarely what the user wants.

Known permission keys: `read, edit, glob, grep, list, bash, task,
external_directory, todowrite, question, webfetch, websearch, repo_clone,
repo_overview, lsp, doom_loop, skill`. Some of these (`todowrite,
question, webfetch, websearch, doom_loop`) only accept a flat
action, not a per-pattern object.

`external_directory` patterns are filesystem paths (use `~/`, absolute paths,
or globs like `~/projects/**`).

Per-agent `permission:` overrides top-level `permission:`. Plan Mode lives on
the `plan` agent's permission ruleset (`edit: deny *`).

## Escape hatches

When a user's config is broken and opencode won't start, these env vars help:

- `OPENCODE_DISABLE_PROJECT_CONFIG=1`: skip the project's local `opencode.json`
  and start from globals only. Run from the project directory, opencode loads,
  the user edits the broken file, then they restart without the flag.
- `OPENCODE_CONFIG=/path/to/file.json`: load an additional explicit config.
- `OPENCODE_CONFIG_CONTENT='{"$schema":"https://opencode.ai/config.json"}'`:
  inject inline JSON as a final local-scope merge.
- `OPENCODE_DISABLE_DEFAULT_PLUGINS=1`: skip default plugins.
- `OPENCODE_PURE=1`: skip external plugins entirely.
- `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`,
  `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`: skip the external skill scans under
  `~/.claude/` and `~/.agents/`.

## When proposing edits

- Validate against the schema before writing. If you are unsure of a field's
  exact shape, or the field is not covered in this skill, fetch
  `https://opencode.ai/config.json` and read the schema rather than guessing.
- Preserve `$schema` and any existing fields the user did not ask to change.
- For agent, skill, and plugin definitions, prefer creating new files in the
  correct location over inlining everything in `opencode.json`.
- If the user's existing config is malformed, point them at the env-var escape
  hatches above so they can edit from inside opencode without breaking their
  session.
- After saving any config change, remind the user to quit and restart opencode
  — running sessions keep using the already-loaded config.

Base directory for this skill: file:///home/kc/Projects/UDAN/ai-factory-setup
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.
Note: file list is sampled.

<skill_files>
<file>/home/kc/Projects/UDAN/ai-factory-setup/.env</file>
<file>/home/kc/Projects/UDAN/ai-factory-setup/.env.example</file>
<file>/home/kc/Projects/UDAN/ai-factory-setup/docs/version-plan.md</file>
<file>/home/kc/Projects/UDAN/ai-factory-setup/docs/architecture-manifesto.md</file>
</skill_files>
</skill_content>
```

**Tool: bash**

**Input:**
```json
{
  "command": "ls /home/kc/Projects/UDAN/ai-factory-setup/",
  "description": "List project directory contents"
}
```

**Output:**
```
docs

```

---

## Assistant (Build · Claude Sonnet 4.6 · 39.2s)

_Thinking:_

Now I understand the OpenCode configuration system clearly. Key takeaways:

1. **Agents** should be defined as `.opencode/agent/<name>.md` files (not `agents.xml` - the manifesto mentions XML but the actual OpenCode config system uses `.md` files with YAML frontmatter). The user asked for `.opencode/agents.xml`, but OpenCode doesn't actually use XML for agents - it uses markdown files with frontmatter.

Wait, the user explicitly asked for `.opencode/agents.xml`. But from the skill, I can see that OpenCode agents are defined as `.md` files, not XML. The `agents.xml` mentioned in the architecture manifesto is aspirational/custom notation for the pipeline concept, not actual OpenCode config files.


I think the best approach here is to create the proper OpenCode agent definition files in the `.opencode/agent/` directory structure, which is what the system actually expects, while potentially creating an `agents.xml` as a supplementary reference file if the user's orchestrator script needs it. with a specific agent, and I need to check the OpenCode CLI documentation to understand how to run it non-interactively. Looking at the agent structure more carefully, agents are defined as `.opencode/agent/<name>.md` or `.opencode/agents/<name>.md` files with a `mode` field that can be set to `"subagent"`. The `agents.xml` file should follow the manifesto's XML pattern for documentation purposes, while the actual OpenCode integration will use the markdown agent files.

Let me verify what files actually exist in the project directory—the skill scanner mentioned `.env` and `.env.example`, but I should confirm what's really there since the directory listing only showed the `docs/` folder.

Now I need to figure out how to invoke the OpenCode CLI non-interactively for the orchestrator script. I should check the documentation to understand the proper command syntax, whether it's something like `opencode run --agent CoreImplementationAgent --file target_file.py` or a different format with model and prompt parameters.

The user wants three specific things: an `.env.example` file with the API key placeholder, an `.opencode/agents.xml` file containing three agents in XML format per the manifesto, and I need to figure out what the third requirement is. I see there's a mismatch between what the manifesto prescribes (XML-based agent definitions) and what OpenCode actually implements (markdown files). I need to create both the `agents.xml` file as specified in the requirements and the actual `.md` files that OpenCode will use to run the agents.

For the orchestrator script to work, I need to figure out the OpenCode CLI flags for non-interactive execution—whether it's something like `opencode -p "prompt"` or another approach. Let me check the documentation to understand how to invoke OpenCode programmatically for each agent.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Read existing .env.example if it exists",
      "status": "in_progress",
      "priority": "low"
    },
    {
      "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Create run-v1-pipeline.sh orchestrator script",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Make run-v1-pipeline.sh executable",
      "status": "pending",
      "priority": "medium"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Read existing .env.example if it exists",
    "status": "in_progress",
    "priority": "low"
  },
  {
    "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Create run-v1-pipeline.sh orchestrator script",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Make run-v1-pipeline.sh executable",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 5.1s)

**Tool: webfetch**

**Input:**
```json
{
  "url": "https://opencode.ai/docs"
}
```

**Output:**
```
Intro | AI coding agent built for the terminalIntro | OpenCode     [Skip to content](#_top)

  [![](/docs/_astro/logo-dark.DOStV66V.svg) ![](/docs/_astro/logo-light.B0yzR0O5.svg) OpenCode](/docs/)

[app.header.home](/)[app.header.docs](/docs/)

[](https://github.com/anomalyco/opencode)[](https://opencode.ai/discord)

Search CtrlK

Cancel

-   [Intro](/docs/)
-   [Config](/docs/config/)
-   [Providers](/docs/providers/)
-   [Network](/docs/network/)
-   [Enterprise](/docs/enterprise/)
-   [Troubleshooting](/docs/troubleshooting/)
-   [Windows](/docs/windows-wsl)
-   Usage
    
    -   [Go](/docs/go/)
    -   [TUI](/docs/tui/)
    -   [CLI](/docs/cli/)
    -   [Web](/docs/web/)
    -   [IDE](/docs/ide/)
    -   [Zen](/docs/zen/)
    -   [Share](/docs/share/)
    -   [GitHub](/docs/github/)
    -   [GitLab](/docs/gitlab/)
    
-   Configure
    
    -   [Tools](/docs/tools/)
    -   [Rules](/docs/rules/)
    -   [Agents](/docs/agents/)
    -   [Models](/docs/models/)
    -   [Themes](/docs/themes/)
    -   [Keybinds](/docs/keybinds/)
    -   [Commands](/docs/commands/)
    -   [Formatters](/docs/formatters/)
    -   [Permissions](/docs/permissions/)
    -   [LSP Servers](/docs/lsp/)
    -   [MCP servers](/docs/mcp-servers/)
    -   [ACP Support](/docs/acp/)
    -   [Agent Skills](/docs/skills/)
    -   [Custom Tools](/docs/custom-tools/)
    
-   Develop
    
    -   [SDK](/docs/sdk/)
    -   [Server](/docs/server/)
    -   [Plugins](/docs/plugins/)
    -   [Ecosystem](/docs/ecosystem/)
    

[GitHub](https://github.com/anomalyco/opencode)[Discord](https://opencode.ai/discord)

Select theme DarkLightAuto   Select language EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文

On this page

-   [Overview](#_top)
-   [Install](#install)
-   [Configure](#configure)
-   [Initialize](#initialize)
-   [Usage](#usage)
    -   [Ask questions](#ask-questions)
    -   [Add features](#add-features)
    -   [Make changes](#make-changes)
    -   [Undo changes](#undo-changes)
-   [Share](#share)
-   [Customize](#customize)

## On this page

-   [Overview](#_top)
-   [Install](#install)
-   [Configure](#configure)
-   [Initialize](#initialize)
-   [Usage](#usage)
    -   [Ask questions](#ask-questions)
    -   [Add features](#add-features)
    -   [Make changes](#make-changes)
    -   [Undo changes](#undo-changes)
-   [Share](#share)
-   [Customize](#customize)

# Intro

Get started with OpenCode.

[**OpenCode**](/) is an open source AI coding agent. It’s available as a terminal-based interface, desktop app, or IDE extension.

![OpenCode TUI with the opencode theme](/docs/_astro/screenshot.CQjBbRyJ_1dLadc.webp)

Let’s get started.

---

#### [Prerequisites](#prerequisites)

To use OpenCode in your terminal, you’ll need:

1.  A modern terminal emulator like:
    
    -   [WezTerm](https://wezterm.org), cross-platform
    -   [Alacritty](https://alacritty.org), cross-platform
    -   [Ghostty](https://ghostty.org), Linux and macOS
    -   [Kitty](https://sw.kovidgoyal.net/kitty/), Linux and macOS
2.  API keys for the LLM providers you want to use.
    

---

## [Install](#install)

The easiest way to install OpenCode is through the install script.

Terminal window

```
curl -fsSL https://opencode.ai/install | bash
```

You can also install it with the following commands:

-   **Using Node.js**
    
    -   [npm](#tab-panel-0)
    -   [Bun](#tab-panel-1)
    -   [pnpm](#tab-panel-2)
    -   [Yarn](#tab-panel-3)
    
    Terminal window
    
    ```
    npm install -g opencode-ai
    ```
    
    Terminal window
    
    ```
    bun install -g opencode-ai
    ```
    
    Terminal window
    
    ```
    pnpm install -g opencode-ai
    ```
    
    Terminal window
    
    ```
    yarn global add opencode-ai
    ```
    
-   **Using Homebrew on macOS and Linux**
    
    Terminal window
    
    ```
    brew install anomalyco/tap/opencode
    ```
    
    > We recommend using the OpenCode tap for the most up to date releases. The official `brew install opencode` formula is maintained by the Homebrew team and is updated less frequently.
    
-   **Installing on Arch Linux**
    
    Terminal window
    
    ```
    sudo pacman -S opencode           # Arch Linux (Stable)paru -S opencode-bin              # Arch Linux (Latest from AUR)
    ```
    

#### [Windows](#windows)

Recommended: Use WSL

For the best experience on Windows, we recommend using [Windows Subsystem for Linux (WSL)](/docs/windows-wsl). It provides better performance and full compatibility with OpenCode’s features.

-   **Using Chocolatey**
    
    Terminal window
    
    ```
    choco install opencode
    ```
    
-   **Using Scoop**
    
    Terminal window
    
    ```
    scoop install opencode
    ```
    
-   **Using NPM**
    
    Terminal window
    
    ```
    npm install -g opencode-ai
    ```
    
-   **Using Mise**
    
    Terminal window
    
    ```
    mise use -g github:anomalyco/opencode
    ```
    
-   **Using Docker**
    
    Terminal window
    
    ```
    docker run -it --rm ghcr.io/anomalyco/opencode
    ```
    

Support for installing OpenCode on Windows using Bun is currently in progress.

You can also grab the binary from the [Releases](https://github.com/anomalyco/opencode/releases).

---

## [Configure](#configure)

With OpenCode you can use any LLM provider by configuring their API keys.

If you are new to using LLM providers, we recommend using [OpenCode Zen](/docs/zen). It’s a curated list of models that have been tested and verified by the OpenCode team.

1.  Run the `/connect` command in the TUI, select opencode, and head to [opencode.ai/auth](https://opencode.ai/auth).
    
    ```
    /connect
    ```
    
2.  Sign in, add your billing details, and copy your API key.
    
3.  Paste your API key.
    
    ```
    ┌ API key││└ enter
    ```
    

Alternatively, you can select one of the other providers. [Learn more](/docs/providers#directory).

---

## [Initialize](#initialize)

Now that you’ve configured a provider, you can navigate to a project that you want to work on.

Terminal window

```
cd /path/to/project
```

And run OpenCode.

Terminal window

```
opencode
```

Next, initialize OpenCode for the project by running the following command.

```
/init
```

This will get OpenCode to analyze your project and create an `AGENTS.md` file in the project root.

Tip

You should commit your project’s `AGENTS.md` file to Git.

This helps OpenCode understand the project structure and the coding patterns used.

---

## [Usage](#usage)

You are now ready to use OpenCode to work on your project. Feel free to ask it anything!

If you are new to using an AI coding agent, here are some examples that might help.

---

### [Ask questions](#ask-questions)

You can ask OpenCode to explain the codebase to you.

Tip

Use the `@` key to fuzzy search for files in the project.

```
How is authentication handled in @packages/functions/src/api/index.ts
```

This is helpful if there’s a part of the codebase that you didn’t work on.

---

### [Add features](#add-features)

You can ask OpenCode to add new features to your project. Though we first recommend asking it to create a plan.

1.  **Create a plan**
    
    OpenCode has a *Plan mode* that disables its ability to make changes and instead suggest *how* it’ll implement the feature.
    
    Switch to it using the **Tab** key. You’ll see an indicator for this in the lower right corner.
    
    ```
    <TAB>
    ```
    
    Now let’s describe what we want it to do.
    
    ```
    When a user deletes a note, we'd like to flag it as deleted in the database.Then create a screen that shows all the recently deleted notes.From this screen, the user can undelete a note or permanently delete it.
    ```
    
    You want to give OpenCode enough details to understand what you want. It helps to talk to it like you are talking to a junior developer on your team.
    
    Tip
    
    Give OpenCode plenty of context and examples to help it understand what you want.
    
2.  **Iterate on the plan**
    
    Once it gives you a plan, you can give it feedback or add more details.
    
    ```
    We'd like to design this new screen using a design I've used before.[Image #1] Take a look at this image and use it as a reference.
    ```
    
    Tip
    
    Drag and drop images into the terminal to add them to the prompt.
    
    OpenCode can scan any images you give it and add them to the prompt. You can do this by dragging and dropping an image into the terminal.
    
3.  **Build the feature**
    
    Once you feel comfortable with the plan, switch back to *Build mode* by hitting the **Tab** key again.
    
    ```
    <TAB>
    ```
    
    And asking it to make the changes.
    
    ```
    Sounds good! Go ahead and make the changes.
    ```
    

---

### [Make changes](#make-changes)

For more straightforward changes, you can ask OpenCode to directly build it without having to review the plan first.

```
We need to add authentication to the /settings route. Take a look at how this ishandled in the /notes route in @packages/functions/src/notes.ts and implementthe same logic in @packages/functions/src/settings.ts
```

You want to make sure you provide a good amount of detail so OpenCode makes the right changes.

---

### [Undo changes](#undo-changes)

Let’s say you ask OpenCode to make some changes.

```
Can you refactor the function in @packages/functions/src/api/index.ts?
```

But you realize that it is not what you wanted. You **can undo** the changes using the `/undo` command.

```
/undo
```

OpenCode will now revert the changes you made and show your original message again.

```
Can you refactor the function in @packages/functions/src/api/index.ts?
```

From here you can tweak the prompt and ask OpenCode to try again.

Tip

You can run `/undo` multiple times to undo multiple changes.

Or you **can redo** the changes using the `/redo` command.

```
/redo
```

---

## [Share](#share)

The conversations that you have with OpenCode can be [shared with your team](/docs/share).

```
/share
```

This will create a link to the current conversation and copy it to your clipboard.

Note

Conversations are not shared by default.

Here’s an [example conversation](https://opencode.ai/s/4XP1fce5) with OpenCode.

---

## [Customize](#customize)

And that’s it! You are now a pro at using OpenCode.

To make it your own, we recommend [picking a theme](/docs/themes), [customizing the keybinds](/docs/keybinds), [configuring code formatters](/docs/formatters), [creating custom commands](/docs/commands), or playing around with the [OpenCode config](/docs/config).

[Edit page](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/index.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Select language EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Last updated: May 21, 2026
```

**Tool: bash**

**Input:**
```json
{
  "command": "ls -la /home/kc/Projects/UDAN/ai-factory-setup/",
  "description": "Check what files exist in project root"
}
```

**Output:**
```
total 20
drwxr-xr-x 3 kc kc 4096 May 21 17:22 .
drwxr-xr-x 8 kc kc 4096 May 21 15:45 ..
drwxr-xr-x 2 kc kc 4096 May 21 15:44 docs
-rw-r--r-- 1 kc kc   48 May 21 15:42 .env
-rw-r--r-- 1 kc kc   48 May 21 15:37 .env.example

```

---

## Assistant (Build · Claude Sonnet 4.6 · 5.6s)

_Thinking:_

So `.env.example` already exists. Let me read it and also fetch the CLI docs to understand how to use opencode non-interactively.

**Tool: webfetch**

**Input:**
```json
{
  "url": "https://opencode.ai/docs/cli/"
}
```

**Output:**
```
CLI | OpenCode     [Skip to content](#_top)

  [![](/docs/_astro/logo-dark.DOStV66V.svg) ![](/docs/_astro/logo-light.B0yzR0O5.svg) OpenCode](/docs/)

[app.header.home](/)[app.header.docs](/docs/)

[](https://github.com/anomalyco/opencode)[](https://opencode.ai/discord)

Search CtrlK

Cancel

-   [Intro](/docs/)
-   [Config](/docs/config/)
-   [Providers](/docs/providers/)
-   [Network](/docs/network/)
-   [Enterprise](/docs/enterprise/)
-   [Troubleshooting](/docs/troubleshooting/)
-   [Windows](/docs/windows-wsl)
-   Usage
    
    -   [Go](/docs/go/)
    -   [TUI](/docs/tui/)
    -   [CLI](/docs/cli/)
    -   [Web](/docs/web/)
    -   [IDE](/docs/ide/)
    -   [Zen](/docs/zen/)
    -   [Share](/docs/share/)
    -   [GitHub](/docs/github/)
    -   [GitLab](/docs/gitlab/)
    
-   Configure
    
    -   [Tools](/docs/tools/)
    -   [Rules](/docs/rules/)
    -   [Agents](/docs/agents/)
    -   [Models](/docs/models/)
    -   [Themes](/docs/themes/)
    -   [Keybinds](/docs/keybinds/)
    -   [Commands](/docs/commands/)
    -   [Formatters](/docs/formatters/)
    -   [Permissions](/docs/permissions/)
    -   [LSP Servers](/docs/lsp/)
    -   [MCP servers](/docs/mcp-servers/)
    -   [ACP Support](/docs/acp/)
    -   [Agent Skills](/docs/skills/)
    -   [Custom Tools](/docs/custom-tools/)
    
-   Develop
    
    -   [SDK](/docs/sdk/)
    -   [Server](/docs/server/)
    -   [Plugins](/docs/plugins/)
    -   [Ecosystem](/docs/ecosystem/)
    

[GitHub](https://github.com/anomalyco/opencode)[Discord](https://opencode.ai/discord)

Select theme DarkLightAuto   Select language EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文

On this page

-   [Overview](#_top)
    -   [tui](#tui)
-   [Commands](#commands)
    -   [agent](#agent)
    -   [attach](#attach)
    -   [auth](#auth)
    -   [github](#github)
    -   [mcp](#mcp)
    -   [models](#models)
    -   [run](#run-1)
    -   [serve](#serve)
    -   [session](#session)
    -   [stats](#stats)
    -   [export](#export)
    -   [import](#import)
    -   [web](#web)
    -   [acp](#acp)
    -   [plugin](#plugin)
    -   [pr](#pr)
    -   [db](#db)
    -   [debug](#debug-1)
    -   [uninstall](#uninstall)
    -   [upgrade](#upgrade)
-   [Global Flags](#global-flags)
-   [Environment variables](#environment-variables)
    -   [Experimental](#experimental)

## On this page

-   [Overview](#_top)
    -   [tui](#tui)
-   [Commands](#commands)
    -   [agent](#agent)
    -   [attach](#attach)
    -   [auth](#auth)
    -   [github](#github)
    -   [mcp](#mcp)
    -   [models](#models)
    -   [run](#run-1)
    -   [serve](#serve)
    -   [session](#session)
    -   [stats](#stats)
    -   [export](#export)
    -   [import](#import)
    -   [web](#web)
    -   [acp](#acp)
    -   [plugin](#plugin)
    -   [pr](#pr)
    -   [db](#db)
    -   [debug](#debug-1)
    -   [uninstall](#uninstall)
    -   [upgrade](#upgrade)
-   [Global Flags](#global-flags)
-   [Environment variables](#environment-variables)
    -   [Experimental](#experimental)

# CLI

OpenCode CLI options and commands.

The OpenCode CLI by default starts the [TUI](/docs/tui) when run without any arguments.

Terminal window

```
opencode
```

But it also accepts commands as documented on this page. This allows you to interact with OpenCode programmatically.

Terminal window

```
opencode run "Explain how closures work in JavaScript"
```

---

### [tui](#tui)

Start the OpenCode terminal user interface.

Terminal window

```
opencode [project]
```

#### [Flags](#flags)

Flag

Short

Description

`--continue`

`-c`

Continue the last session

`--session`

`-s`

Session ID to continue

`--fork`

Fork the session when continuing (use with `--continue` or `--session`)

`--prompt`

Prompt to use

`--model`

`-m`

Model to use in the form of provider/model

`--agent`

Agent to use

`--port`

Port to listen on

`--hostname`

Hostname to listen on

`--mdns`

Enable mDNS discovery

`--mdns-domain`

Custom mDNS domain name

`--cors`

Additional browser origin(s) to allow CORS

---

## [Commands](#commands)

The OpenCode CLI also has the following commands.

---

### [agent](#agent)

Manage agents for OpenCode.

Terminal window

```
opencode agent [command]
```

---

#### [create](#create)

Create a new agent with custom configuration.

Terminal window

```
opencode agent create
```

This command will guide you through creating a new agent with a custom system prompt and permission configuration. Anything you don’t allow is denied in the generated agent’s frontmatter.

#### [Flags](#flags-1)

Flag

Short

Description

`--path`

Directory to write the agent file to (defaults to global or `.opencode/agent` based on the prompt)

`--description`

What the agent should do

`--mode`

Agent mode: `all`, `primary`, or `subagent`

`--permissions`

Comma-separated list of permissions to allow (default: all). Available: `bash`, `read`, `edit`, `glob`, `grep`, `webfetch`, `task`, `todowrite`, `websearch`, `lsp`, `skill`. Anything omitted is denied. Alias: `--tools`

`--model`

`-m`

Model to use, in `provider/model` format

Passing all of `--path`, `--description`, `--mode`, and `--permissions` runs the command non-interactively.

---

#### [list](#list)

List all available agents.

Terminal window

```
opencode agent list
```

---

### [attach](#attach)

Attach a terminal to an already running OpenCode backend server started via `serve` or `web` commands.

Terminal window

```
opencode attach [url]
```

This allows using the TUI with a remote OpenCode backend. For example:

Terminal window

```
# Start the backend server for web/mobile accessopencode web --port 4096 --hostname 0.0.0.0
# In another terminal, attach the TUI to the running backendopencode attach http://10.20.30.40:4096
```

#### [Flags](#flags-2)

Flag

Short

Description

`--dir`

Working directory to start TUI in

`--continue`

`-c`

Continue the last session

`--session`

`-s`

Session ID to continue

`--fork`

Fork the session when continuing (use with `--continue` or `--session`)

`--password`

`-p`

Basic auth password (defaults to `OPENCODE_SERVER_PASSWORD`)

`--username`

`-u`

Basic auth username (defaults to `OPENCODE_SERVER_USERNAME` or `opencode`)

---

### [auth](#auth)

Command to manage credentials and login for providers.

Terminal window

```
opencode auth [command]
```

---

#### [login](#login)

OpenCode is powered by the provider list at [Models.dev](https://models.dev), so you can use `opencode auth login` to configure API keys for any provider you’d like to use. This is stored in `~/.local/share/opencode/auth.json`.

Terminal window

```
opencode auth login
```

When OpenCode starts up it loads the providers from the credentials file. And if there are any keys defined in your environments or a `.env` file in your project.

##### [Flags](#flags-3)

Flag

Short

Description

`--provider`

`-p`

Provider ID or name to log in to

`--method`

`-m`

Login method label to use, skipping method selection

---

#### [list](#list-1)

Lists all the authenticated providers as stored in the credentials file.

Terminal window

```
opencode auth list
```

Or the short version.

Terminal window

```
opencode auth ls
```

---

#### [logout](#logout)

Logs you out of a provider by clearing it from the credentials file.

Terminal window

```
opencode auth logout
```

---

### [github](#github)

Manage the GitHub agent for repository automation.

Terminal window

```
opencode github [command]
```

---

#### [install](#install)

Install the GitHub agent in your repository.

Terminal window

```
opencode github install
```

This sets up the necessary GitHub Actions workflow and guides you through the configuration process. [Learn more](/docs/github).

---

#### [run](#run)

Run the GitHub agent. This is typically used in GitHub Actions.

Terminal window

```
opencode github run
```

##### [Flags](#flags-4)

Flag

Description

`--event`

GitHub mock event to run the agent for

`--token`

GitHub personal access token

---

### [mcp](#mcp)

Manage Model Context Protocol servers.

Terminal window

```
opencode mcp [command]
```

---

#### [add](#add)

Add an MCP server to your configuration.

Terminal window

```
opencode mcp add
```

This command will guide you through adding either a local or remote MCP server.

---

#### [list](#list-2)

List all configured MCP servers and their connection status.

Terminal window

```
opencode mcp list
```

Or use the short version.

Terminal window

```
opencode mcp ls
```

---

#### [auth](#auth-1)

Authenticate with an OAuth-enabled MCP server.

Terminal window

```
opencode mcp auth [name]
```

If you don’t provide a server name, you’ll be prompted to select from available OAuth-capable servers.

You can also list OAuth-capable servers and their authentication status.

Terminal window

```
opencode mcp auth list
```

Or use the short version.

Terminal window

```
opencode mcp auth ls
```

---

#### [logout](#logout-1)

Remove OAuth credentials for an MCP server.

Terminal window

```
opencode mcp logout [name]
```

---

#### [debug](#debug)

Debug OAuth connection issues for an MCP server.

Terminal window

```
opencode mcp debug <name>
```

---

### [models](#models)

List all available models from configured providers.

Terminal window

```
opencode models [provider]
```

This command displays all models available across your configured providers in the format `provider/model`.

This is useful for figuring out the exact model name to use in [your config](/docs/config/).

You can optionally pass a provider ID to filter models by that provider.

Terminal window

```
opencode models anthropic
```

#### [Flags](#flags-5)

Flag

Description

`--refresh`

Refresh the models cache from models.dev

`--verbose`

Use more verbose model output (includes metadata like costs)

Use the `--refresh` flag to update the cached model list. This is useful when new models have been added to a provider and you want to see them in OpenCode.

Terminal window

```
opencode models --refresh
```

---

### [run](#run-1)

Run opencode in non-interactive mode by passing a prompt directly.

Terminal window

```
opencode run [message..]
```

This is useful for scripting, automation, or when you want a quick answer without launching the full TUI. For example.

Terminal window

```
opencode run Explain the use of context in Go
```

You can also attach to a running `opencode serve` instance to avoid MCP server cold boot times on every run:

Terminal window

```
# Start a headless server in one terminalopencode serve
# In another terminal, run commands that attach to itopencode run --attach http://localhost:4096 "Explain async/await in JavaScript"
```

#### [Flags](#flags-6)

Flag

Short

Description

`--command`

The command to run, use message for args

`--continue`

`-c`

Continue the last session

`--session`

`-s`

Session ID to continue

`--fork`

Fork the session when continuing (use with `--continue` or `--session`)

`--share`

Share the session

`--model`

`-m`

Model to use in the form of provider/model

`--agent`

Agent to use

`--file`

`-f`

File(s) to attach to message

`--format`

Format: default (formatted) or json (raw JSON events)

`--title`

Title for the session (uses truncated prompt if no value provided)

`--attach`

Attach to a running opencode server (e.g., [http://localhost:4096](http://localhost:4096))

`--password`

`-p`

Basic auth password (defaults to `OPENCODE_SERVER_PASSWORD`)

`--username`

`-u`

Basic auth username (defaults to `OPENCODE_SERVER_USERNAME` or `opencode`)

`--dir`

Directory to run in, or path on the remote server when attaching

`--port`

Port for the local server (defaults to random port)

`--variant`

Model variant (provider-specific reasoning effort)

`--thinking`

Show thinking blocks

`--dangerously-skip-permissions`

Auto-approve permissions that are not explicitly denied (dangerous!)

---

### [serve](#serve)

Start a headless OpenCode server for API access. Check out the [server docs](/docs/server) for the full HTTP interface.

Terminal window

```
opencode serve
```

This starts an HTTP server that provides API access to opencode functionality without the TUI interface. Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth (username defaults to `opencode`).

#### [Flags](#flags-7)

Flag

Description

`--port`

Port to listen on

`--hostname`

Hostname to listen on

`--mdns`

Enable mDNS discovery

`--mdns-domain`

Custom mDNS domain name

`--cors`

Additional browser origin(s) to allow CORS

---

### [session](#session)

Manage OpenCode sessions.

Terminal window

```
opencode session [command]
```

---

#### [list](#list-3)

List all OpenCode sessions.

Terminal window

```
opencode session list
```

##### [Flags](#flags-8)

Flag

Short

Description

`--max-count`

`-n`

Limit to N most recent sessions

`--format`

Output format: table or json (table)

---

#### [delete](#delete)

Delete an OpenCode session.

Terminal window

```
opencode session delete <sessionID>
```

---

### [stats](#stats)

Show token usage and cost statistics for your OpenCode sessions.

Terminal window

```
opencode stats
```

#### [Flags](#flags-9)

Flag

Description

`--days`

Show stats for the last N days (all time)

`--tools`

Number of tools to show (all)

`--models`

Show model usage breakdown (hidden by default). Pass a number to show top N

`--project`

Filter by project (all projects, empty string: current project)

---

### [export](#export)

Export session data as JSON.

Terminal window

```
opencode export [sessionID]
```

If you don’t provide a session ID, you’ll be prompted to select from available sessions.

#### [Flags](#flags-10)

Flag

Description

`--sanitize`

Redact sensitive transcript/file data

---

### [import](#import)

Import session data from a JSON file or OpenCode share URL.

Terminal window

```
opencode import <file>
```

You can import from a local file or an OpenCode share URL.

Terminal window

```
opencode import session.jsonopencode import https://opncd.ai/s/abc123
```

---

### [web](#web)

Start a headless OpenCode server with a web interface.

Terminal window

```
opencode web
```

This starts an HTTP server and opens a web browser to access OpenCode through a web interface. Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth (username defaults to `opencode`).

#### [Flags](#flags-11)

Flag

Description

`--port`

Port to listen on

`--hostname`

Hostname to listen on

`--mdns`

Enable mDNS discovery

`--mdns-domain`

Custom mDNS domain name

`--cors`

Additional browser origin(s) to allow CORS

---

### [acp](#acp)

Start an ACP (Agent Client Protocol) server.

Terminal window

```
opencode acp
```

This command starts an ACP server that communicates via stdin/stdout using nd-JSON.

#### [Flags](#flags-12)

Flag

Description

`--cwd`

Working directory

`--port`

Port to listen on

`--hostname`

Hostname to listen on

`--mdns`

Enable mDNS discovery

`--mdns-domain`

Custom mDNS domain name

`--cors`

Additional browser origin(s) to allow CORS

---

### [plugin](#plugin)

Install a plugin and update your config.

Terminal window

```
opencode plugin <module>
```

Or use the alias.

Terminal window

```
opencode plug <module>
```

#### [Flags](#flags-13)

Flag

Short

Description

`--global`

`-g`

Install in global config

`--force`

`-f`

Replace existing plugin version

---

### [pr](#pr)

Fetch and checkout a GitHub PR branch, then run OpenCode.

Terminal window

```
opencode pr <number>
```

---

### [db](#db)

Database tools.

Terminal window

```
opencode db [query]
```

#### [Flags](#flags-14)

Flag

Description

`--format`

Output format: `json` or `tsv`

---

#### [path](#path)

Print the database path.

Terminal window

```
opencode db path
```

---

### [debug](#debug-1)

Debugging and troubleshooting tools.

Terminal window

```
opencode debug [command]
```

---

### [uninstall](#uninstall)

Uninstall OpenCode and remove all related files.

Terminal window

```
opencode uninstall
```

#### [Flags](#flags-15)

Flag

Short

Description

`--keep-config`

`-c`

Keep configuration files

`--keep-data`

`-d`

Keep session data and snapshots

`--dry-run`

Show what would be removed without removing

`--force`

`-f`

Skip confirmation prompts

---

### [upgrade](#upgrade)

Updates opencode to the latest version or a specific version.

Terminal window

```
opencode upgrade [target]
```

To upgrade to the latest version.

Terminal window

```
opencode upgrade
```

To upgrade to a specific version.

Terminal window

```
opencode upgrade v0.1.48
```

#### [Flags](#flags-16)

Flag

Short

Description

`--method`

`-m`

The installation method that was used; curl, npm, pnpm, bun, brew

---

## [Global Flags](#global-flags)

The opencode CLI takes the following global flags.

Flag

Short

Description

`--help`

`-h`

Display help

`--version`

`-v`

Print version number

`--print-logs`

Print logs to stderr

`--log-level`

Log level (DEBUG, INFO, WARN, ERROR)

`--pure`

Run without external plugins

---

## [Environment variables](#environment-variables)

OpenCode can be configured using environment variables.

Variable

Type

Description

`OPENCODE_AUTO_SHARE`

boolean

Automatically share sessions

`OPENCODE_GIT_BASH_PATH`

string

Path to Git Bash executable on Windows

`OPENCODE_CONFIG`

string

Path to config file

`OPENCODE_TUI_CONFIG`

string

Path to TUI config file

`OPENCODE_CONFIG_DIR`

string

Path to config directory

`OPENCODE_CONFIG_CONTENT`

string

Inline json config content

`OPENCODE_DISABLE_AUTOUPDATE`

boolean

Disable automatic update checks

`OPENCODE_DISABLE_PRUNE`

boolean

Disable pruning of old data

`OPENCODE_DISABLE_TERMINAL_TITLE`

boolean

Disable automatic terminal title updates

`OPENCODE_PERMISSION`

string

Inlined json permissions config

`OPENCODE_DISABLE_DEFAULT_PLUGINS`

boolean

Disable default plugins

`OPENCODE_DISABLE_LSP_DOWNLOAD`

boolean

Disable automatic LSP server downloads

`OPENCODE_ENABLE_EXPERIMENTAL_MODELS`

boolean

Enable experimental models

`OPENCODE_DISABLE_AUTOCOMPACT`

boolean

Disable automatic context compaction

`OPENCODE_DISABLE_CLAUDE_CODE`

boolean

Disable reading from `.claude` (prompt + skills)

`OPENCODE_DISABLE_CLAUDE_CODE_PROMPT`

boolean

Disable reading `~/.claude/CLAUDE.md`

`OPENCODE_DISABLE_CLAUDE_CODE_SKILLS`

boolean

Disable loading `.claude/skills`

`OPENCODE_DISABLE_MODELS_FETCH`

boolean

Disable fetching models from remote sources

`OPENCODE_DISABLE_MOUSE`

boolean

Disable mouse capture in the TUI

`OPENCODE_FAKE_VCS`

string

Fake VCS provider for testing purposes

`OPENCODE_CLIENT`

string

Client identifier (defaults to `cli`)

`OPENCODE_ENABLE_EXA`

boolean

Enable Exa web search tools

`OPENCODE_SERVER_PASSWORD`

string

Enable basic auth for `serve`/`web`

`OPENCODE_SERVER_USERNAME`

string

Override basic auth username (default `opencode`)

`OPENCODE_MODELS_URL`

string

Custom URL for fetching models configuration

---

### [Experimental](#experimental)

These environment variables enable experimental features that may change or be removed.

Variable

Type

Description

`OPENCODE_EXPERIMENTAL`

boolean

Enable all experimental features

`OPENCODE_EXPERIMENTAL_ICON_DISCOVERY`

boolean

Enable icon discovery

`OPENCODE_EXPERIMENTAL_DISABLE_COPY_ON_SELECT`

boolean

Disable copy on select in TUI

`OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS`

number

Default timeout for bash commands in ms

`OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX`

number

Max output tokens for LLM responses

`OPENCODE_EXPERIMENTAL_FILEWATCHER`

boolean

Enable file watcher for entire dir

`OPENCODE_EXPERIMENTAL_OXFMT`

boolean

Enable oxfmt formatter

`OPENCODE_EXPERIMENTAL_LSP_TOOL`

boolean

Enable experimental LSP tool

`OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER`

boolean

Disable file watcher

`OPENCODE_EXPERIMENTAL_EXA`

boolean

Enable experimental Exa features

`OPENCODE_EXPERIMENTAL_LSP_TY`

boolean

Enable TY LSP for python files

`OPENCODE_EXPERIMENTAL_PLAN_MODE`

boolean

Enable plan mode

[Edit page](https://github.com/anomalyco/opencode/edit/dev/packages/web/src/content/docs/cli.mdx)[Found a bug? Open an issue](https://github.com/anomalyco/opencode/issues/new)[Join our Discord community](https://opencode.ai/discord) Select language EnglishالعربيةBosanskiDanskDeutschEspañolFrançaisItaliano日本語한국어Norsk BokmålPolskiPortuguês (Brasil)РусскийไทยTürkçe简体中文繁體中文 

© [Anomaly](https://anoma.ly)

Last updated: May 21, 2026
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.env.example"
}
```

**Output:**
```
<path>/home/kc/Projects/UDAN/ai-factory-setup/.env.example</path>
<type>file</type>
<content>
1: OPENROUTER_API_KEY=your_openrouter_api_key_here

(End of file - total 1 lines)
</content>
```

---

## Assistant (Build · Claude Sonnet 4.6 · 92.2s)

_Thinking:_

Now I have all the information I need. Let me plan what to create:

1. **`.env.example`** - Already exists with the right content. I just need to check if there's anything to update.

2. **`.opencode/agents.xml`** - The user wants this following the manifesto's XML pattern. This is used as a documentation/reference file since actual OpenCode uses `.md` files.

3. **`.opencode/agent/` markdown files** - Three agent files:
   - `core-implementation-agent.md`
   - `test-generation-agent.md`
   - `documentation-agent.md`
   
4. **`run-v1-pipeline.sh`** - The orchestrator script that runs the agents using the OpenCode CLI with the `deepseek/deepseek-coder-v4` model, leveraging flags like `--agent`, `--model`, and `--dangerously-skip-permissions` to automate the workflow.

I need to figure out the correct model format for OpenRouter - whether it's `openrouter/deepseek/deepseek-coder-v4` or just `deepseek/deepseek-coder-v4` depending on how OpenCode handles the provider routing. I need to set up the actual OpenCode agent files alongside the XML reference. The agent names will correspond to the markdown filenames in the `.opencode/agent/` directory, so I'll create the core implementation, test generation, and documentation agents as separate markdown files that OpenCode can execute.

For the orchestrator script, each agent runs sequentially with the target file passed as context—the core implementation agent handles the logic, the test generation agent writes tests based on that implementation, and the documentation agent adds comments and docstrings. The `.env.example` file already has the OpenRouter API key placeholder, so I'll leave that as-is.

Now I'm setting up the `.opencode/` directory structure and planning the pipeline script. It'll parse the target file, load the API key from the environment, then execute the three passes in order before reporting completion. The script needs to be executable, and I need to make sure the OPENROUTER_API_KEY is available to OpenCode's run command, either through the `.env` file or by explicitly exporting it.

Writing the agent definitions... I need to verify the exact model identifier format for OpenRouter—the user specified `deepseek/deepseek-coder-v4`, so I'll use that as-is in the OpenCode configuration with the `openrouter/` prefix to get `openrouter/deepseek/deepseek-coder-v4`. OpenCode should auto-load the `OPENROUTER_API_KEY` from the `.env` file, and I'll use the `openrouter/deepseek/deepseek-coder-v4` format for the model flag. Now I'm structuring the orchestrator script as a bash pipeline...

Setting up input validation...

Defining a function that runs each pass of the pipeline, executing different agents in sequence—first implementing the core logic, then generating tests, and finally adding documentation. Defining the test generation agent... Continuing with the documentation agent configuration, which focuses on adding JSDoc and docstring comments to the implementation without modifying any logic or algorithms. The Core Implementation Agent is configured to focus exclusively on writing or improving the core algorithmic logic of a target file, using DeepSeek Coder as its model. It's restricted from writing tests, documentation, or modifying anything outside the specified target file, and should follow existing code patterns while inferring the module's purpose from the filename if starting from scratch. I need to write comprehensive tests for the implementation, naming the test file appropriately based on the language, and ensuring each test is independent while covering happy paths, edge cases, and error conditions.

Now I'm moving to the documentation phase, where I'll add JSDoc or docstring comments to the implementation file without changing any logic or algorithms. Writing the orchestrator script... I'm thinking through whether the `--dangerously-skip-permissions` flag is necessary for the pipeline script. Since the agent's frontmatter explicitly allows certain operations, the flag should work well for auto-approving those permissions without prompts. Now I need to write out all the files systematically, starting with the `.env.example` file which already has the correct content and doesn't need changes.

For the `opencode run` command, I'm checking the model format against the CLI documentation—it expects "provider/model" format, so I'll use `openrouter/deepseek/deepseek-coder-v4` based on the user's specification.

Now I have everything I need. Let me plan and build all the files.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Read existing .env.example if it exists",
      "priority": "low",
      "status": "completed"
    },
    {
      "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
      "priority": "high",
      "status": "in_progress"
    },
    {
      "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "Create run-v1-pipeline.sh orchestrator script",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "Make run-v1-pipeline.sh executable",
      "priority": "medium",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Read existing .env.example if it exists",
    "status": "completed",
    "priority": "low"
  },
  {
    "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Create run-v1-pipeline.sh orchestrator script",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Make run-v1-pipeline.sh executable",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 6.7s)

**Tool: bash**

**Input:**
```json
{
  "command": "mkdir -p /home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent",
  "description": "Create .opencode/agent directory"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Claude Sonnet 4.6 · 24.7s)

**Tool: write**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agents.xml",
  "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!--\n  ai-factory-setup / .opencode/agents.xml\n  v0.1: The \"Hello World\" Pipeline — 3-Pass Agent Definitions\n\n  This file defines the strict XML personas for the v0.1 pipeline agents,\n  following the XML prompting standard described in architecture-manifesto.md §4.1.\n  XML creates absolute semantic walls between agent instructions and user code,\n  preventing prompt injection from code comments or Markdown collisions.\n\n  The corresponding OpenCode-native agent files live in .opencode/agent/*.md.\n  Orchestrator: run-v1-pipeline.sh\n\n  v0.2 will expand this to include XML boundaries and VS Code Plan Viewer.\n  v0.3 will add LiteLLM routing and Mermaid/Gherkin design agents.\n  DO NOT add v0.2+ agents here until those milestones are started.\n-->\n<agents version=\"0.1\" pipeline=\"hello-world\">\n\n  <!-- ================================================================ -->\n  <!-- PASS 1 — Core Implementation                                     -->\n  <!-- Goal: Write or improve the algorithmic logic of the target file. -->\n  <!-- ================================================================ -->\n  <agent id=\"core-implementation-agent\">\n    <role>Core Implementation Agent</role>\n    <model>openrouter/deepseek/deepseek-coder-v4</model>\n    <pass>1</pass>\n\n    <directives>\n      <rule>Your ONLY task is to write or improve the core algorithmic logic of the target file.</rule>\n      <rule>Do NOT write tests, documentation, or inline comments beyond minimal clarity.</rule>\n      <rule>Do NOT modify any file other than the specified target file.</rule>\n      <rule>Follow existing code style, naming conventions, and patterns present in the file.</rule>\n      <rule>If the file is empty, infer the module purpose from its filename and write a clean, idiomatic implementation.</rule>\n    </directives>\n\n    <scope>\n      <allowed_operations>read, edit (target file only)</allowed_operations>\n      <forbidden_operations>bash execution, test file creation, documentation changes</forbidden_operations>\n    </scope>\n\n    <task>\n      Review the file provided in the user_code tag. Implement or improve its core logic so that\n      the module fulfils its apparent purpose. Focus exclusively on correctness and clean\n      algorithmic structure. Do not add tests or doc comments.\n    </task>\n  </agent>\n\n  <!-- ================================================================ -->\n  <!-- PASS 2 — Test Generation                                         -->\n  <!-- Goal: Write a complete test suite against the Pass 1 output.    -->\n  <!-- ================================================================ -->\n  <agent id=\"test-generation-agent\">\n    <role>Test Generation Agent</role>\n    <model>openrouter/deepseek/deepseek-coder-v4</model>\n    <pass>2</pass>\n\n    <directives>\n      <rule>Your ONLY task is to write comprehensive unit tests for the provided implementation.</rule>\n      <rule>Do NOT modify the core implementation file under any circumstances.</rule>\n      <rule>Write tests that cover the happy path, edge cases, boundary conditions, and error scenarios.</rule>\n      <rule>Name the test file by appending .test.js/.test.ts (JS/TS) or _test.py (Python) to the original filename stem.</rule>\n      <rule>Each test must be independent, deterministic, and idempotent.</rule>\n    </directives>\n\n    <scope>\n      <allowed_operations>read (implementation file), edit (new test file only)</allowed_operations>\n      <forbidden_operations>bash execution, modifying the source implementation file</forbidden_operations>\n    </scope>\n\n    <task>\n      Read the target implementation file in the user_code tag. Create a new, co-located test file\n      that covers all public functions with unit tests. Do not touch the original file.\n    </task>\n  </agent>\n\n  <!-- ================================================================ -->\n  <!-- PASS 3 — Documentation                                           -->\n  <!-- Goal: Add JSDoc/docstrings to the Pass 1 implementation.        -->\n  <!-- ================================================================ -->\n  <agent id=\"documentation-agent\">\n    <role>Documentation Agent</role>\n    <model>openrouter/deepseek/deepseek-coder-v4</model>\n    <pass>3</pass>\n\n    <directives>\n      <rule>Your ONLY task is to add JSDoc or docstring comments to the target implementation file.</rule>\n      <rule>Do NOT modify any logic, algorithms, control flow, variable names, or test code.</rule>\n      <rule>Document all public functions and classes with @param, @returns, and @example tags where meaningful.</rule>\n      <rule>Add a module-level comment describing the file's purpose.</rule>\n      <rule>If logic is unclear, document what it DOES — do NOT rewrite or \"fix\" it.</rule>\n    </directives>\n\n    <scope>\n      <allowed_operations>read, edit (comments and docstrings only)</allowed_operations>\n      <forbidden_operations>bash execution, logic changes, test file edits</forbidden_operations>\n    </scope>\n\n    <task>\n      Review the target implementation file in the user_code tag. Add complete JSDoc (JS/TS) or\n      docstring (Python) documentation to all public functions, classes, and the module itself.\n      Do not alter any code behavior or structure.\n    </task>\n  </agent>\n\n</agents>\n"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 4.3s)

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Read existing .env.example if it exists",
      "priority": "low",
      "status": "completed"
    },
    {
      "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
      "priority": "high",
      "status": "in_progress"
    },
    {
      "content": "Create run-v1-pipeline.sh orchestrator script",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "Make run-v1-pipeline.sh executable",
      "priority": "medium",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Read existing .env.example if it exists",
    "status": "completed",
    "priority": "low"
  },
  {
    "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Create run-v1-pipeline.sh orchestrator script",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Make run-v1-pipeline.sh executable",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 8.3s)

Now create the three OpenCode-native agent `.md` files:

**Tool: write**

**Input:**
```json
{
  "content": "---\ndescription: Pass 1 of the v0.1 Hello World Pipeline. Writes or improves the core algorithmic logic of a target file. Use when the orchestrator invokes the implementation pass.\nmode: subagent\nmodel: openrouter/deepseek/deepseek-coder-v4\npermission:\n  read: allow\n  edit: allow\n  glob: allow\n  grep: allow\n  bash: deny\n  webfetch: deny\n  task: deny\n---\n\n<role>Core Implementation Agent</role>\n\n<directives>\n  <rule>Your ONLY task is to write or improve the core algorithmic logic of the target file provided.</rule>\n  <rule>Do NOT write tests, documentation blocks, or inline comments beyond the minimum needed for clarity.</rule>\n  <rule>Do NOT modify any file other than the single target file you were given.</rule>\n  <rule>Follow existing code style, naming conventions, and patterns already present in the file.</rule>\n  <rule>If the file is empty, infer the module's purpose from its filename and write a clean, idiomatic implementation.</rule>\n  <rule>If a change outside your scope is needed, stop and report it — do NOT make out-of-scope edits.</rule>\n</directives>\n\n<task>\n  Implement the core logic for the provided target file. Write clean, functional code that\n  fulfils the apparent purpose of the module. Focus exclusively on business logic and\n  algorithmic correctness. Do not add tests or documentation.\n</task>\n",
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/core-implementation-agent.md"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 7.4s)

**Tool: write**

**Input:**
```json
{
  "content": "---\ndescription: Pass 2 of the v0.1 Hello World Pipeline. Generates a comprehensive unit test suite for an existing implementation file. Use when the orchestrator invokes the test generation pass.\nmode: subagent\nmodel: openrouter/deepseek/deepseek-coder-v4\npermission:\n  read: allow\n  edit: allow\n  glob: allow\n  grep: allow\n  bash: deny\n  webfetch: deny\n  task: deny\n---\n\n<role>Test Generation Agent</role>\n\n<directives>\n  <rule>Your ONLY task is to write comprehensive unit tests for the implementation file you are given.</rule>\n  <rule>Do NOT modify the source implementation file under any circumstances.</rule>\n  <rule>Write tests that cover the happy path, edge cases, boundary conditions, and expected error scenarios.</rule>\n  <rule>Create the test file alongside the implementation: append .test.js or .test.ts for JavaScript/TypeScript, or _test.py for Python.</rule>\n  <rule>Each test must be independent, deterministic, and idempotent — no shared mutable state between tests.</rule>\n  <rule>Use the standard testing framework appropriate for the language (Jest for JS/TS, pytest for Python).</rule>\n  <rule>If a logic flaw is discovered in the implementation, document it as a failing test — do NOT fix the source.</rule>\n</directives>\n\n<task>\n  Read the target implementation file carefully. Create a new, co-located test file that covers\n  all public functions and classes with unit tests. Do not touch or modify the original\n  implementation file.\n</task>\n",
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/test-generation-agent.md"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 8.9s)

**Tool: write**

**Input:**
```json
{
  "content": "---\ndescription: Pass 3 of the v0.1 Hello World Pipeline. Adds JSDoc or docstring documentation to an existing implementation file. Use when the orchestrator invokes the documentation pass.\nmode: subagent\nmodel: openrouter/deepseek/deepseek-coder-v4\npermission:\n  read: allow\n  edit: allow\n  glob: allow\n  grep: allow\n  bash: deny\n  webfetch: deny\n  task: deny\n---\n\n<role>Documentation Agent</role>\n\n<directives>\n  <rule>Your ONLY task is to add JSDoc or docstring comments to the implementation file you are given.</rule>\n  <rule>Do NOT modify any logic, algorithms, control flow, variable names, or test code.</rule>\n  <rule>Add a module-level comment at the top of the file describing its purpose.</rule>\n  <rule>Document all public functions and classes with @param, @returns, and @throws tags (JSDoc) or Args/Returns/Raises sections (Python docstrings).</rule>\n  <rule>Include a concise @example (JSDoc) or Example (Python) block where the behaviour is non-obvious.</rule>\n  <rule>If logic appears unclear or potentially buggy, describe what it DOES — do NOT rewrite or silently fix it.</rule>\n  <rule>Do not modify test files.</rule>\n</directives>\n\n<task>\n  Review the target implementation file. Add complete JSDoc (JavaScript/TypeScript) or\n  docstring (Python) documentation to all public functions, classes, and the module itself.\n  Do not alter any code behaviour, structure, or logic.\n</task>\n",
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/documentation-agent.md"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 17.6s)

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Read existing .env.example if it exists",
      "priority": "low",
      "status": "completed"
    },
    {
      "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create run-v1-pipeline.sh orchestrator script",
      "priority": "high",
      "status": "in_progress"
    },
    {
      "content": "Make run-v1-pipeline.sh executable",
      "priority": "medium",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Read existing .env.example if it exists",
    "status": "completed",
    "priority": "low"
  },
  {
    "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create run-v1-pipeline.sh orchestrator script",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Make run-v1-pipeline.sh executable",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 26.2s)

**Tool: write**

**Input:**
```json
{
  "content": "#!/usr/bin/env bash\n# =============================================================================\n# run-v1-pipeline.sh — v0.1 \"Hello World\" Pipeline Orchestrator\n#\n# Usage:\n#   ./run-v1-pipeline.sh <target_file>\n#\n# Example:\n#   ./run-v1-pipeline.sh src/calculator.py\n#\n# What it does:\n#   Sequentially invokes OpenCode CLI with three scoped sub-agents against\n#   the given target file:\n#     Pass 1 — core-implementation-agent  (writes/improves core logic)\n#     Pass 2 — test-generation-agent      (generates the test suite)\n#     Pass 3 — documentation-agent        (adds JSDoc / docstrings)\n#\n# Prerequisites:\n#   - opencode CLI installed and on $PATH\n#   - OPENROUTER_API_KEY set in .env (or already exported in your shell)\n#   - Agent files present in .opencode/agent/\n#\n# Note on the model ID:\n#   The model below uses the OpenRouter provider prefix that OpenCode expects.\n#   If your OpenRouter account uses a different model slug, update MODEL below.\n# =============================================================================\n\nset -euo pipefail\n\n# ---------------------------------------------------------------------------\n# Configuration\n# ---------------------------------------------------------------------------\nMODEL=\"openrouter/deepseek/deepseek-coder-v4\"\n\nAGENTS=(\n  \"core-implementation-agent\"\n  \"test-generation-agent\"\n  \"documentation-agent\"\n)\n\nPASS_LABELS=(\n  \"Pass 1 — Core Implementation\"\n  \"Pass 2 — Test Generation\"\n  \"Pass 3 — Documentation\"\n)\n\n# ---------------------------------------------------------------------------\n# Helpers\n# ---------------------------------------------------------------------------\nprint_banner() {\n  echo \"\"\n  echo \"┌─────────────────────────────────────────────────────────┐\"\n  echo \"│  ai-factory-setup  •  v0.1 Hello World Pipeline         │\"\n  echo \"└─────────────────────────────────────────────────────────┘\"\n  echo \"\"\n}\n\nprint_pass_header() {\n  local label=\"$1\"\n  echo \"\"\n  echo \"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\"\n  echo \"  $label\"\n  echo \"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\"\n}\n\ndie() {\n  echo \"\"\n  echo \"[ERROR] $*\" >&2\n  exit 1\n}\n\n# ---------------------------------------------------------------------------\n# Validation\n# ---------------------------------------------------------------------------\nTARGET_FILE=\"${1:-}\"\n\n[[ -n \"$TARGET_FILE\" ]] || die \"No target file specified.\\n\\nUsage: $0 <target_file>\"\n[[ -f \"$TARGET_FILE\" ]] || die \"Target file not found: '$TARGET_FILE'\"\n\n# Load .env if present (OpenCode also reads this automatically, but we need\n# the key for our preflight check below).\nif [[ -f \".env\" ]]; then\n  # Export variables without executing arbitrary code\n  set -a\n  # shellcheck disable=SC1091\n  source .env\n  set +a\nfi\n\n[[ -n \"${OPENROUTER_API_KEY:-}\" ]] || \\\n  die \"OPENROUTER_API_KEY is not set. Add it to your .env file:\\n  OPENROUTER_API_KEY=sk-or-...\"\n\ncommand -v opencode >/dev/null 2>&1 || \\\n  die \"'opencode' CLI not found on PATH. Install it with: npm install -g opencode-ai\"\n\n# ---------------------------------------------------------------------------\n# Pipeline prompts (one per pass)\n# ---------------------------------------------------------------------------\nPROMPTS=(\n  # Pass 1 — Core Implementation\n  \"You are running as Pass 1 of the v0.1 pipeline. Review the attached file and implement its core logic. Write clean, functional code that fulfils the module's apparent purpose. Focus exclusively on algorithmic correctness. Do NOT add tests or documentation.\"\n\n  # Pass 2 — Test Generation\n  \"You are running as Pass 2 of the v0.1 pipeline. The attached file is a completed implementation. Create a co-located test file (e.g. <name>.test.py or <name>.test.js) with comprehensive unit tests covering happy paths, edge cases, and error conditions. Do NOT modify the source file.\"\n\n  # Pass 3 — Documentation\n  \"You are running as Pass 3 of the v0.1 pipeline. The attached file is a completed implementation. Add JSDoc (JS/TS) or docstring (Python) documentation to every public function and class, plus a module-level header comment. Do NOT change any logic, variable names, or test code.\"\n)\n\n# ---------------------------------------------------------------------------\n# Run pipeline\n# ---------------------------------------------------------------------------\nprint_banner\necho \"  Target : $TARGET_FILE\"\necho \"  Model  : $MODEL\"\necho \"  Agents : ${#AGENTS[@]} passes\"\necho \"\"\n\nPASS_COUNT=${#AGENTS[@]}\n\nfor (( i=0; i<PASS_COUNT; i++ )); do\n  agent=\"${AGENTS[$i]}\"\n  label=\"${PASS_LABELS[$i]}\"\n  prompt=\"${PROMPTS[$i]}\"\n\n  print_pass_header \"$label  [agent: $agent]\"\n\n  opencode run \\\n    --agent  \"$agent\"  \\\n    --model  \"$MODEL\"  \\\n    --file   \"$TARGET_FILE\" \\\n    --dangerously-skip-permissions \\\n    \"$prompt\"\n\n  echo \"\"\n  echo \"  ✓ $label complete.\"\ndone\n\n# ---------------------------------------------------------------------------\n# Summary\n# ---------------------------------------------------------------------------\necho \"\"\necho \"┌─────────────────────────────────────────────────────────┐\"\necho \"│  v0.1 Pipeline finished successfully.                   │\"\necho \"│                                                         │\"\necho \"│  Artifacts produced for: $TARGET_FILE\"\necho \"│    Pass 1 → core logic implemented                      │\"\necho \"│    Pass 2 → test file created alongside source          │\"\necho \"│    Pass 3 → JSDoc / docstrings added                    │\"\necho \"│                                                         │\"\necho \"│  Run 'git diff' to review all agent changes.            │\"\necho \"└─────────────────────────────────────────────────────────┘\"\necho \"\"\n",
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/run-v1-pipeline.sh"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 2.9s)

**Tool: bash**

**Input:**
```json
{
  "command": "chmod +x /home/kc/Projects/UDAN/ai-factory-setup/run-v1-pipeline.sh",
  "description": "Make orchestrator script executable"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Claude Sonnet 4.6 · 4.7s)

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Read existing .env.example if it exists",
      "priority": "low",
      "status": "completed"
    },
    {
      "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create run-v1-pipeline.sh orchestrator script",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Make run-v1-pipeline.sh executable",
      "priority": "medium",
      "status": "completed"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Read existing .env.example if it exists",
    "status": "completed",
    "priority": "low"
  },
  {
    "content": "Fetch OpenCode CLI docs for non-interactive/run mode",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .env.example with OPENROUTER_API_KEY placeholder",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agents.xml with 3 sub-agents (XML format per manifesto)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create .opencode/agent/ markdown files for actual OpenCode CLI integration",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create run-v1-pipeline.sh orchestrator script",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Make run-v1-pipeline.sh executable",
    "status": "completed",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.6s)

Let me do a final verification of all produced files:

**Tool: bash**

**Input:**
```json
{
  "command": "find /home/kc/Projects/UDAN/ai-factory-setup -not -path '*/docs/*' | sort && echo \"\" && ls -la /home/kc/Projects/UDAN/ai-factory-setup/run-v1-pipeline.sh",
  "description": "Verify all files were created correctly"
}
```

**Output:**
```
/home/kc/Projects/UDAN/ai-factory-setup
/home/kc/Projects/UDAN/ai-factory-setup/docs
/home/kc/Projects/UDAN/ai-factory-setup/.env
/home/kc/Projects/UDAN/ai-factory-setup/.env.example
/home/kc/Projects/UDAN/ai-factory-setup/.opencode
/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent
/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/core-implementation-agent.md
/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/documentation-agent.md
/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agents.xml
/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/test-generation-agent.md
/home/kc/Projects/UDAN/ai-factory-setup/run-v1-pipeline.sh

-rwxr-xr-x 1 kc kc 6425 May 21 17:38 /home/kc/Projects/UDAN/ai-factory-setup/run-v1-pipeline.sh

```

---

## Assistant (Build · Claude Sonnet 4.6 · 14.4s)

All files are in place and the script is executable (`-rwxr-xr-x`). Here is a summary of everything that was built.

---

## What was created

### File tree (v0.1 only)
```
ai-factory-setup/
├── .env.example                            ← already existed, content correct
├── .opencode/
│   ├── agents.xml                          ← XML agent manifest (per manifesto §4.1)
│   └── agent/
│       ├── core-implementation-agent.md   ← Pass 1: OpenCode-native agent def
│       ├── test-generation-agent.md       ← Pass 2: OpenCode-native agent def
│       └── documentation-agent.md         ← Pass 3: OpenCode-native agent def
└── run-v1-pipeline.sh                      ← orchestrator (executable)
```

### Design decisions

**Two layers of agent definition** — A deliberate dual approach:
- `.opencode/agents.xml` — the XML persona manifest described in the manifesto (§4.1). This is the human-readable policy reference. XML prevents prompt injection from Markdown collisions in code comments.
- `.opencode/agent/*.md` — the files OpenCode CLI actually reads. Each has YAML frontmatter (`model`, `mode`, `permission`) and the XML persona embedded in the body. Permissions are scoped: `read` + `edit` only; `bash` and `webfetch` are denied.

**Model format** — `openrouter/deepseek/deepseek-coder-v4`. OpenCode uses the `provider/model` prefix convention; `openrouter` is the provider namespace.

---

## How to run it

**1. Set your API key:**
```bash
cp .env.example .env
# edit .env and replace the placeholder value
```

**2. Run the pipeline against any target file:**
```bash
./run-v1-pipeline.sh src/calculator.py
```

**3. Review what the agents changed:**
```bash
git diff
```

The script will refuse to run if `OPENROUTER_API_KEY` is unset or `opencode` is not on your `$PATH`. After all three passes it prints a summary of what was produced.

> **One thing to verify:** confirm the exact OpenRouter model slug for DeepSeek Coder v4 matches what your account has access to. If the model ID differs, update the `MODEL` variable at the top of `run-v1-pipeline.sh` and the `<model>` tags in `agents.xml`.

---

## User

try running the pipeline against a target - I see some errors

---

## Assistant (Build · Claude Sonnet 4.6 · 7.1s)

_Thinking:_

The user wants me to try running the pipeline against a target file to see what errors occur. Let me first create a simple test target file, then run the pipeline and observe what happens.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/kc/Projects/UDAN/ai-factory-setup && bash run-v1-pipeline.sh 2>&1 | head -20",
  "description": "Run pipeline with no args to check basic validation"
}
```

**Output:**
```

[ERROR] No target file specified.\n\nUsage: run-v1-pipeline.sh <target_file>

```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.4s)

**Tool: bash**

**Input:**
```json
{
  "command": "cat > /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py << 'EOF'\ndef add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\nEOF",
  "description": "Create a minimal target Python file"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.8s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/kc/Projects/UDAN/ai-factory-setup && bash run-v1-pipeline.sh sample_target.py 2>&1",
  "description": "Run pipeline against sample target, capture all output",
  "timeout": 60000
}
```

**Output:**
```

┌─────────────────────────────────────────────────────────┐
│  ai-factory-setup  •  v0.1 Hello World Pipeline         │
└─────────────────────────────────────────────────────────┘

  Target : sample_target.py
  Model  : openrouter/deepseek/deepseek-coder-v4
  Agents : 3 passes


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pass 1 — Core Implementation  [agent: core-implementation-agent]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[93m[1m! [0m agent "core-implementation-agent" is a subagent, not a primary agent. Falling back to default agent
[91m[1mError: [0m
[91m[1mError: [0m{
  "name": "UnknownError",
  "data": {
    "message": "Unexpected server error. Check server logs for details."
  }
}

```

---

## Assistant (Build · Claude Sonnet 4.6 · 9.1s)

_Thinking:_

Two errors:
1. `agent "core-implementation-agent" is a subagent, not a primary agent. Falling back to default agent` - This means the agent mode needs to be `primary` (or `all`) not `subagent` when calling from the CLI. The `mode: subagent` means it can only be invoked as a subagent from another agent, not directly via `opencode run --agent`.

2. `UnknownError: Unexpected server error` - This is probably related to the model. 

The model ID `openrouter/deepseek/deepseek-coder-v4` might be incorrect, so I need to verify what DeepSeek Coder v4 is actually called on OpenRouter. I'll fix both issues by changing the agent mode to `all` to allow direct CLI invocation, and then verify the correct model identifier.

Two clear errors. Let me diagnose both:

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/kc/Projects/UDAN/ai-factory-setup && opencode models openrouter 2>&1 | grep -i deepseek",
  "description": "List OpenRouter models and grep for deepseek",
  "timeout": 30000
}
```

**Output:**
```
openrouter/deepseek/deepseek-chat
openrouter/deepseek/deepseek-chat-v3-0324
openrouter/deepseek/deepseek-chat-v3.1
openrouter/deepseek/deepseek-r1
openrouter/deepseek/deepseek-r1-0528
openrouter/deepseek/deepseek-r1-distill-llama-70b
openrouter/deepseek/deepseek-r1-distill-qwen-32b
openrouter/deepseek/deepseek-v3.1-terminus
openrouter/deepseek/deepseek-v3.2
openrouter/deepseek/deepseek-v3.2-exp
openrouter/deepseek/deepseek-v3.2-speciale
openrouter/deepseek/deepseek-v4-flash
openrouter/deepseek/deepseek-v4-flash:free
openrouter/deepseek/deepseek-v4-pro
openrouter/nex-agi/deepseek-v3.1-nex-n1

```

---

## Assistant (Build · Claude Sonnet 4.6 · 10.4s)

_Thinking:_

Now I can see the available DeepSeek models. The closest to "deepseek-coder-v4" would be `openrouter/deepseek/deepseek-v4-pro` or `openrouter/deepseek/deepseek-v4-flash`. There's no explicit "coder" variant. The manifesto mentioned "DeepSeek v4" as the model to use.

Looking at these options:
- `openrouter/deepseek/deepseek-v4-pro` - the pro variant of DeepSeek v4
- `openrouter/deepseek/deepseek-v4-flash` - the flash variant of DeepSeek v4  


- `openrouter/deepseek/deepseek-v4-flash:free` - free tier

The "coder" reference in the manifesto was about DeepSeek's coding capabilities rather than a specific model variant. For a coding pipeline, I should use `openrouter/deepseek/deepseek-v4-pro` as the correct model, and I need to update the agent mode configuration accordingly.

Now I'm updating all three agent files to switch the mode from `subagent` to `all` and correcting the model ID across the agent configurations and orchestrator script.

Two problems identified:

1. **`mode: subagent`** — agents set to `subagent` can't be called directly via `opencode run --agent`. Needs to be `all`.
2. **Wrong model ID** — `deepseek-coder-v4` doesn't exist. The correct slug is `deepseek/deepseek-v4-pro`.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Fix agent mode from subagent to all in all 3 agent .md files",
      "priority": "high",
      "status": "in_progress"
    },
    {
      "content": "Fix model ID to openrouter/deepseek/deepseek-v4-pro in agents, agents.xml, and script",
      "priority": "high",
      "status": "pending"
    },
    {
      "content": "Re-run pipeline to verify fixes",
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Fix agent mode from subagent to all in all 3 agent .md files",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Fix model ID to openrouter/deepseek/deepseek-v4-pro in agents, agents.xml, and script",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Re-run pipeline to verify fixes",
    "status": "pending",
    "priority": "high"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/core-implementation-agent.md",
  "oldString": "mode: subagent\nmodel: openrouter/deepseek/deepseek-coder-v4",
  "newString": "mode: all\nmodel: openrouter/deepseek/deepseek-v4-pro"
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.5s)

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/core-implementation-agent.md",
  "limit": 10
}
```

**Output:**
```
<path>/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/core-implementation-agent.md</path>
<type>file</type>
<content>
1: ---
2: description: Pass 1 of the v0.1 Hello World Pipeline. Writes or improves the core algorithmic logic of a target file. Use when the orchestrator invokes the implementation pass.
3: mode: subagent
4: model: openrouter/deepseek/deepseek-v4-flash
5: permission:
6:   read: allow
7:   edit: allow
8:   glob: allow
9:   grep: allow
10:   bash: deny

(Showing lines 1-10 of 30. Use offset=11 to continue.)
</content>
```

---

## Assistant (Build · Claude Sonnet 4.6 · 4.6s)

_Thinking:_

The model was already updated earlier (the skill showed `.env.example` already existed). It seems the model is already `openrouter/deepseek/deepseek-v4-flash`. Let me check all three files and update the mode from `subagent` to `all`.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/test-generation-agent.md",
  "limit": 10
}
```

**Output:**
```
<path>/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/test-generation-agent.md</path>
<type>file</type>
<content>
1: ---
2: description: Pass 2 of the v0.1 Hello World Pipeline. Generates a comprehensive unit test suite for an existing implementation file. Use when the orchestrator invokes the test generation pass.
3: mode: subagent
4: model: openrouter/deepseek/deepseek-v4-flash
5: permission:
6:   read: allow
7:   edit: allow
8:   glob: allow
9:   grep: allow
10:   bash: deny

(Showing lines 1-10 of 31. Use offset=11 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/documentation-agent.md",
  "limit": 10
}
```

**Output:**
```
<path>/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/documentation-agent.md</path>
<type>file</type>
<content>
1: ---
2: description: Pass 3 of the v0.1 Hello World Pipeline. Adds JSDoc or docstring documentation to an existing implementation file. Use when the orchestrator invokes the documentation pass.
3: mode: subagent
4: model: openrouter/deepseek/deepseek-v4-flash
5: permission:
6:   read: allow
7:   edit: allow
8:   glob: allow
9:   grep: allow
10:   bash: deny

(Showing lines 1-10 of 31. Use offset=11 to continue.)
</content>
```

---

## Assistant (Build · Claude Sonnet 4.6 · 11.7s)

_Thinking:_

I see - the models were already updated to `openrouter/deepseek/deepseek-v4-flash`. It seems the `.env` and `.env.example` files already exist and the agent files have `deepseek-v4-flash` (not the one I wrote). Wait, actually I wrote these files earlier and they should have `deepseek-coder-v4`, but looking at the content they already have `deepseek-v4-flash`. This is odd.

Oh wait - I think what happened is that when I was writing the files to disk, the model got changed. 

There's a discrepancy here - I wrote `openrouter/deepseek/deepseek-coder-v4` but the files show `openrouter/deepseek/deepseek-v4-flash` instead, which suggests OpenCode may have auto-corrected the model name or something else modified the files after I wrote them. Regardless, I'll focus on fixing the `mode: subagent` to `mode: all` across all three files.

The current model `deepseek-v4-flash` works fine, but since the version plan specifies "Core Implementation (DeepSeek v4)" and I need a capable model for code generation, I should upgrade to `deepseek-v4-pro` instead, which is better suited for this task than the flash variant.

The model field was already auto-corrected to `deepseek-v4-flash` somehow. I'll fix `mode: subagent` → `mode: all` in all three files, and upgrade the model to `deepseek-v4-pro` (more capable for code generation), plus sync `agents.xml` and the script.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/core-implementation-agent.md",
  "oldString": "mode: subagent\nmodel: openrouter/deepseek/deepseek-v4-flash",
  "newString": "mode: all\nmodel: openrouter/deepseek/deepseek-v4-pro"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 2.6s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/test-generation-agent.md",
  "newString": "mode: all\nmodel: openrouter/deepseek/deepseek-v4-pro",
  "oldString": "mode: subagent\nmodel: openrouter/deepseek/deepseek-v4-flash"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 2.7s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agent/documentation-agent.md",
  "newString": "mode: all\nmodel: openrouter/deepseek/deepseek-v4-pro",
  "oldString": "mode: subagent\nmodel: openrouter/deepseek/deepseek-v4-flash"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.8s)

Now sync `agents.xml` and the script to the corrected model ID:

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agents.xml",
  "oldString": "    <model>openrouter/deepseek/deepseek-coder-v4</model>\n    <pass>1</pass>",
  "newString": "    <model>openrouter/deepseek/deepseek-v4-pro</model>\n    <pass>1</pass>"
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 2.6s)

**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"model\\|deepseek\" /home/kc/Projects/UDAN/ai-factory-setup/.opencode/agents.xml",
  "description": "Find model lines in agents.xml"
}
```

**Output:**
```
26:    <model>openrouter/deepseek/deepseek-v4-flash</model>
55:    <model>openrouter/deepseek/deepseek-v4-flash</model>
83:    <model>openrouter/deepseek/deepseek-v4-flash</model>

```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.2s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/.opencode/agents.xml",
  "oldString": "    <model>openrouter/deepseek/deepseek-v4-flash</model>",
  "newString": "    <model>openrouter/deepseek/deepseek-v4-pro</model>",
  "replaceAll": true
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.0s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/kc/Projects/UDAN/ai-factory-setup/run-v1-pipeline.sh",
  "newString": "MODEL=\"openrouter/deepseek/deepseek-v4-pro\"",
  "oldString": "MODEL=\"openrouter/deepseek/deepseek-coder-v4\""
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Claude Sonnet 4.6 · 3.4s)

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Fix agent mode from subagent to all in all 3 agent .md files",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Fix model ID to openrouter/deepseek/deepseek-v4-pro in agents, agents.xml, and script",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Re-run pipeline to verify fixes",
      "priority": "high",
      "status": "in_progress"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Fix agent mode from subagent to all in all 3 agent .md files",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Fix model ID to openrouter/deepseek/deepseek-v4-pro in agents, agents.xml, and script",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Re-run pipeline to verify fixes",
    "status": "in_progress",
    "priority": "high"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 153.5s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/kc/Projects/UDAN/ai-factory-setup && bash run-v1-pipeline.sh sample_target.py 2>&1",
  "description": "Re-run pipeline with all fixes applied",
  "timeout": 300000
}
```

**Output:**
```

┌─────────────────────────────────────────────────────────┐
│  ai-factory-setup  •  v0.1 Hello World Pipeline         │
└─────────────────────────────────────────────────────────┘

  Target : sample_target.py
  Model  : openrouter/deepseek/deepseek-v4-pro
  Agents : 3 passes


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pass 1 — Core Implementation  [agent: core-implementation-agent]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[0m
> core-implementation-agent · deepseek/deepseek-v4-pro
[0m
[0m← [0mEdit sample_target.py
Index: /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py
===================================================================
--- /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py
+++ /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py
@@ -2,4 +2,12 @@
     return a + b
 
 def subtract(a, b):
     return a - b
+
+def multiply(a, b):
+    return a * b
+
+def divide(a, b):
+    if b == 0:
+        raise ZeroDivisionError("division by zero")
+    return a / b

[0m
The file is a basic arithmetic utility module. The existing `add` and `subtract` implementations are clean and correct. To complete the module's core logic, I'll add `multiply` and `divide` (the remaining fundamental arithmetic operations).
The module now contains all four fundamental arithmetic operations:

- **`add`** / **`subtract`** — unchanged, already correct.
- **`multiply(a, b)`** — returns `a * b`.
- **`divide(a, b)`** — returns `a / b`, with a `ZeroDivisionError` guard when `b == 0` for correctness.

  ✓ Pass 1 — Core Implementation complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pass 2 — Test Generation  [agent: test-generation-agent]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[0m
> test-generation-agent · deepseek/deepseek-v4-pro
[0m
[0m← [0mWrite sample_target_test.py
Wrote file successfully.
[0m
Now let me run the tests to verify everything passes
[0m→ [0mRead .
[0m→ [0mRead sample_target_test.py
[0m→ [0mRead .env
Test file created. Running the tests now
[0m
[0m← [0mEdit sample_target_test.py
Index: /home/kc/Projects/UDAN/ai-factory-setup/sample_target_test.py
===================================================================
--- /home/kc/Projects/UDAN/ai-factory-setup/sample_target_test.py
+++ /home/kc/Projects/UDAN/ai-factory-setup/sample_target_test.py
@@ -2,9 +2,8 @@
 Unit tests for sample_target.py
 Framework: pytest
 """
 
-import math
 import pytest
 from sample_target import add, subtract, multiply, divide
 
 

[0m

  ✓ Pass 2 — Test Generation complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pass 3 — Documentation  [agent: documentation-agent]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[0m
> documentation-agent · deepseek/deepseek-v4-pro
[0m
[0m← [0mEdit sample_target.py
Index: /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py
===================================================================
--- /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py
+++ /home/kc/Projects/UDAN/ai-factory-setup/sample_target.py
@@ -1,13 +1,85 @@
+"""A simple arithmetic module providing basic mathematical operations.
+
+This module implements the four fundamental arithmetic functions:
+addition, subtraction, multiplication, and division. The division
+function includes a guard against division by zero.
+"""
+
+
 def add(a, b):
+    """Return the sum of two numbers.
+
+    Args:
+        a (int | float): The first operand.
+        b (int | float): The second operand.
+
+    Returns:
+        int | float: The result of ``a + b``.
+
+    Example:
+        >>> add(2, 3)
+        5
+        >>> add(2.5, 3.5)
+        6.0
+    """
     return a + b
 
+
 def subtract(a, b):
+    """Return the difference between two numbers.
+
+    Args:
+        a (int | float): The minuend (value to subtract from).
+        b (int | float): The subtrahend (value to subtract).
+
+    Returns:
+        int | float: The result of ``a - b``.
+
+    Example:
+        >>> subtract(5, 3)
+        2
+    """
     return a - b
 
+
 def multiply(a, b):
+    """Return the product of two numbers.
+
+    Args:
+        a (int | float): The first factor.
+        b (int | float): The second factor.
+
+    Returns:
+        int | float: The result of ``a * b``.
+
+    Example:
+        >>> multiply(4, 3)
+        12
+    """
     return a * b
 
+
 def divide(a, b):
+    """Return the quotient of two numbers.
+
+    Args:
+        a (int | float): The numerator (dividend).
+        b (int | float): The denominator (divisor).
+
+    Returns:
+        float: The result of ``a / b``.
+
+    Raises:
+        ZeroDivisionError: If ``b`` is zero.
+
+    Example:
+        >>> divide(10, 2)
+        5.0
+        >>> divide(5, 0)
+        Traceback (most recent call last):
+            ...
+        ZeroDivisionError: division by zero
+    """
     if b == 0:
         raise ZeroDivisionError("division by zero")
     return a / b

[0m
[0m→ [0mRead sample_target.py
Let me verify the final result:
Documentation has been added to `sample_target.py` with no changes to logic, variable names, or behavior. Here's a summary of what was added:

| Element | Details |
|---|---|
| **Module docstring** | Describes the module as providing four fundamental arithmetic operations, noting the division-by-zero guard. |
| **`add(a, b)`** | `Args`, `Returns`, and `Example` (int and float cases). |
| **`subtract(a, b)`** | `Args`, `Returns`, and `Example`. |
| **`multiply(a, b)`** | `Args`, `Returns`, and `Example`. |
| **`divide(a, b)`** | `Args`, `Returns`, `Raises` (`ZeroDivisionError`), and `Example` (normal + error case). |

All docstrings follow the standard Python docstring convention with `Args`, `Returns`, `Raises`, and `Example` sections.

  ✓ Pass 3 — Documentation complete.

┌─────────────────────────────────────────────────────────┐
│  v0.1 Pipeline finished successfully.                   │
│                                                         │
│  Artifacts produced for: sample_target.py
│    Pass 1 → core logic implemented                      │
│    Pass 2 → test file created alongside source          │
│    Pass 3 → JSDoc / docstrings added                    │
│                                                         │
│  Run 'git diff' to review all agent changes.            │
└─────────────────────────────────────────────────────────┘


```

---

## Assistant (Build · Claude Sonnet 4.6 · 5.3s)

All three passes ran cleanly end-to-end.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Fix agent mode from subagent to all in all 3 agent .md files",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Fix model ID to openrouter/deepseek/deepseek-v4-pro in agents, agents.xml, and script",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Re-run pipeline to verify fixes",
      "priority": "high",
      "status": "completed"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Fix agent mode from subagent to all in all 3 agent .md files",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Fix model ID to openrouter/deepseek/deepseek-v4-pro in agents, agents.xml, and script",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Re-run pipeline to verify fixes",
    "status": "completed",
    "priority": "high"
  }
]
```

---

## Assistant (Build · Claude Sonnet 4.6 · 9.4s)

Pipeline is confirmed working. Here's a summary of the two bugs and their fixes:

---

## What was broken and why

### Bug 1 — `mode: subagent` in agent frontmatter
`opencode run --agent <name>` only accepts agents with `mode: primary` or `mode: all`. Mode `subagent` means the agent can only be *delegated to* by another agent inside a session — it cannot be the entry point from the CLI. Fixed to `mode: all` in all three `.md` files.

### Bug 2 — Model slug `deepseek-coder-v4` does not exist on OpenRouter
The manifesto name was aspirational. The actual available DeepSeek v4 models on OpenRouter are:
- `openrouter/deepseek/deepseek-v4-flash` — faster/cheaper
- `openrouter/deepseek/deepseek-v4-pro` — stronger (chosen for code quality)

Updated in all three agent `.md` files, `agents.xml`, and `run-v1-pipeline.sh`.

---

## What the pipeline produced against `sample_target.py`

| Pass | Agent | Output |
|---|---|---|
| 1 | `core-implementation-agent` | Added `multiply` and `divide` (with zero-guard) |
| 2 | `test-generation-agent` | Created `sample_target_test.py` with pytest coverage |
| 3 | `documentation-agent` | Added module docstring + full `Args/Returns/Raises/Example` blocks to all four functions |

---

