# OpenResearch — Implementation Plan

| Field | Value |
|---|---|
| Product | OpenResearch |
| Version | 1.0 (V1 / Hackathon MVP) |
| Status | Draft for team review |
| Companion docs | `PRD.md`, `TRD.md` |

> **How to use this plan:** Work phase by phase. Never build the whole app in one pass. Do not redesign the architecture unless a documented technical blocker requires it. A phase is complete only when its tests pass, its docs are updated, and its Definition of Done (DoD) is verified.

---

## 1. Working Agreement

### 1.1 Phase loop

```
READ SPEC → IMPLEMENT → RUN TESTS → VERIFY DoD → FIX → COMMIT → NEXT PHASE
```

### 1.2 Git workflow

```
main (protected)
  ├── feat/backend
  ├── feat/research-tools
  ├── feat/agent
  └── feat/frontend
```

- Nobody experiments directly on `main`; all changes go through pull requests.
- Each PR: passing CI (lint, type-check, tests), at least one reviewer, docs updated.
- Use short-lived sub-branches (`feat/backend-projects-api`) off the lane branch when useful.
- Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

### 1.3 Suggested team lanes (4 people; adapt to actual skills)

| Lane | Owner focus | Primary phases |
|---|---|---|
| **Backend/Platform** | FastAPI, DB, migrations, API, SSE, security, CI | 0, 1, 3 (storage), 8 (API polish) |
| **Agents/LLM** | LLM providers, prompts, agents, orchestrator, critic | 0 (LLM), 1, 4, 5, 6, 7 |
| **Research tools** | Web/Semantic Scholar/GitHub/HF tools, source + evidence pipeline | 2, 3 |
| **Frontend** | Next.js UI, SSE hook, evidence/gap/build views, demo polish | 0, 1 (UI), 3 (UI), 8 |

Everyone participates in Phase 9 (evaluation) and the final demo rehearsal. Interfaces (schemas in TRD §6, §7, §9) are frozen early so lanes can work in parallel against `MockProvider` and mocked tools.

### 1.4 Definition of "done" for any task
1. Code merged via PR.
2. Unit/integration tests added and passing.
3. Relevant doc section updated.
4. No new lint/type errors.
5. Works with `LLM_PROVIDER=mock` (no GPU needed).

### 1.5 Time model
The handoff does not state a project calendar. Estimates below are in **relative effort units** (S ≈ ½ day, M ≈ 1 day, L ≈ 2 days of one person). Map them to the real deadline at kickoff and cut P1/P2 items first if time is short (see §4).

---

## 2. Phase Overview

| # | Phase | Goal | Effort | Depends on |
|---|---|---|---|---|
| 0 | Foundation | Next.js → FastAPI → Qwen → response | M–L | — |
| 1 | Requirement analysis | Brief → structured requirements & questions | M | 0 |
| 2 | Research tools | Brief → normalized source collection | L | 0 (1 for real queries) |
| 3 | Evidence | Claims traceable to verified evidence | L | 2 |
| 4 | Analysis | Landscape, comparisons, gaps | M | 3 |
| 5 | Build planner | Feasibility, architecture, MVP, risks | M | 4 |
| 6 | Critic loop | Detect problems, retry research | M | 3–5 |
| 7 | Challenge My Idea | Idea → related work, issues, differentiation | M | 3, 5 |
| 8 | UI polish | Dashboard, cards, graph, streaming, report | L | 1–7 |
| 9 | Evaluation | Benchmark + metrics + docs | M | 1–7 |

```
0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9
        ╰ frontend and tools lanes run in parallel against mocks ╯
```

---

## 3. Phase Details

### Phase 0 — Foundation

**Goal:** A request travels `Next.js → FastAPI → Qwen → Response`, with the repo, DB, CI, and environment in place.

| # | Task | Lane | Effort |
|---|---|---|---|
| 0.1 | Create public repo with README stub, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, `.env.example`, `docs/` (copy PRD, TRD, this plan) | Backend | S |
| 0.2 | Scaffold FastAPI app (config via env, structured logging, `/health`, error format, CORS) | Backend | S |
| 0.3 | PostgreSQL + SQLAlchemy async session + Alembic; initial migration (users, projects) | Backend | S |
| 0.4 | `docker-compose.yml` (postgres, backend, frontend; optional ollama profile) | Backend | S |
| 0.5 | `LLMProvider` interface + `OllamaProvider` + `MockProvider`; stub `VLLMProvider` | Agents | M |
| 0.6 | Pull `qwen3:8b` via Ollama; smoke-test `chat` and `structured` (JSON schema) | Agents | S |
| 0.7 | Scaffold Next.js (App Router, TS, Tailwind, shadcn/ui); API client base; env | Frontend | S |
| 0.8 | Throwaway "ask the model" page/endpoint proving the full path (`POST /api/v1/debug/llm`, disabled outside dev) | All | S |
| 0.9 | GitHub Actions: ruff, mypy, pytest, eslint, tsc, build | Backend | S |
| 0.10 | Seed single local user when `AUTH_MODE=none` | Backend | S |

**Tests:** `/health` reports DB + LLM status; `MockProvider` returns deterministic output; structured output validation + repair path unit-tested; CI green.

**Definition of Done**
- [ ] `docker compose up` (or documented local run) starts DB, backend, frontend.
- [ ] Submitting text in the UI returns a Qwen3-8B response through the backend.
- [ ] Switching `LLM_PROVIDER=mock` works with no GPU.
- [ ] CI passes on `main`.

**Commits:** `feat: initialize project architecture`, `feat: add qwen llm provider`

---

### Phase 1 — Requirement Analysis

**Goal:** A pasted competition brief produces structured requirements, constraints, deliverables, judging criteria, and research questions.

| # | Task | Lane | Effort |
|---|---|---|---|
| 1.1 | Migrations: projects (full fields), requirements, research_questions | Backend | S |
| 1.2 | Project CRUD endpoints with validation limits (TRD §9) | Backend | M |
| 1.3 | `RequirementAnalyzer` agent: prompt, schema, `source_span` extraction | Agents | M |
| 1.4 | `ResearchPlanner` (questions part): RQ1–RQn with priority, default coverage areas | Agents | M |
| 1.5 | `POST /projects/{id}/analyze` + PATCH endpoints for requirements/questions | Backend | S |
| 1.6 | UI: dashboard, new-project form, project overview, Requirements tab (✓ requirements / ⚠ constraints), research questions list with edit | Frontend | L |
| 1.7 | Mock fixtures for both agents | Agents | S |
| 1.8 | Prompt files versioned under `app/llm/prompts/` | Agents | S |

**Tests:** schema validation of agent outputs; API validation errors (422); fixture-based agent tests with mock; 3 real briefs run against Qwen (`llm` marker) to eyeball quality; UI E2E: create project → analyze → see requirements.

**Definition of Done**
- [ ] A pasted real brief produces structured requirements/constraints/deliverables/judging criteria.
- [ ] 5–10 prioritized research questions are generated and editable.
- [ ] Invalid inputs show clear errors; project CRUD works.

**Commits:** `feat: implement requirement extraction`, `feat: add research planner and project crud`

---

### Phase 2 — Research Tools

**Goal:** A problem statement produces a normalized, deduplicated, safely-fetched source collection.

| # | Task | Lane | Effort |
|---|---|---|---|
| 2.1 | `Source` schema + migration (sources, papers, repositories, models, datasets, run_events, research_runs) | Backend | M |
| 2.2 | URL validator + SSRF guard + safe fetcher (timeouts, size caps, redirect re-validation) | Tools | M |
| 2.3 | Content extraction (`trafilatura`) + sanitizer + injection-pattern flagging | Tools | M |
| 2.4 | `SearchProvider` interface + Tavily adapter (+ fallback adapter if time) | Tools | M |
| 2.5 | `PaperTool`: Semantic Scholar search → `Source` + `Paper` (handle rate limits/keys) | Tools | M |
| 2.6 | `GitHubTool`: repo search; fields name, description, language, stars, activity, license, topics, URL; README fetch + summary (LLM `no-think`) | Tools | M |
| 2.7 | `HFTool`: Hugging Face models/datasets search (P1) | Tools | M |
| 2.8 | Source normalization, canonical URL + hash dedupe, relevance note | Tools | S |
| 2.9 | Query generation: planner turns RQs into per-tool queries (validated) | Agents | M |
| 2.10 | Run lifecycle: `POST /research` → queued run, async worker, budget accounting (tool calls, timeouts, retries), run state in DB | Backend | M |
| 2.11 | Tool response caching (24 h TTL) | Tools | S |
| 2.12 | `GET` list endpoints for sources/papers/repos/models/datasets | Backend | S |

**Tests:** respx-mocked tool tests; SSRF cases (localhost, 169.254.169.254, private ranges, redirect to private IP); sanitizer fixtures including malicious page; dedupe; budget enforcement (stops at cap); tool failure degrades gracefully; rate-limit/backoff behavior.

**Definition of Done**
- [ ] A project run produces ≥ 15 deduplicated sources across web, papers, and GitHub for a typical brief.
- [ ] Each source carries id, title, url, type, author, date, publisher, snippet, retrieved_at, license (when available).
- [ ] All SSRF and sanitization tests pass; budgets enforced.

**Commits:** `feat: add web research tool`, `feat: add semantic scholar integration`, `feat: add github research`, `feat: add source pipeline and safe fetcher`

---

### Phase 3 — Evidence

**Goal:** Every important claim traces to verified source evidence.

| # | Task | Lane | Effort |
|---|---|---|---|
| 3.1 | Migrations: evidence, claims, claim_evidence | Backend | S |
| 3.2 | Chunker + BM25 passage ranker (per RQ) | Tools | M |
| 3.3 | `EvidenceExtractor` agent: schema-constrained evidence + claims with status labels | Agents | L |
| 3.4 | Deterministic snippet verifier (normalized substring + high-threshold fuzzy) | Tools | M |
| 3.5 | Integrity enforcement: auto-downgrade unverified `FACT`/`DIRECTLY_SUPPORTED`; require reasoning for `INFERENCE`/`HYPOTHESIS`; `SYNTHESIS` needs ≥ 2 sources | Backend | M |
| 3.6 | SSE: `GET /research/{run_id}/stream` with persisted events + `Last-Event-ID` replay | Backend | M |
| 3.7 | Endpoints: claims list/detail with evidence + source | Backend | S |
| 3.8 | UI: Sources tab with `SourceCard`; `useResearchStream` hook; Claims list; `EvidencePanel` (Claim → Evidence → Source, status badge, Open Source) | Frontend | L |
| 3.9 | Injection-defense wrapper (`<untrusted_source>` delimiters, system rule, delimiter escaping) | Agents | S |

**Tests:** snippet-not-in-source ⇒ `verified=false` and claim downgraded; injection fixture does not alter behavior and is flagged; SYNTHESIS integrity; SSE replay after disconnect; claim detail API contract; E2E: run (mock) → open claim → open source.

**Definition of Done**
- [ ] Every generated important claim can be traced Claim → Evidence → Source in the UI.
- [ ] `FACT`/`DIRECTLY_SUPPORTED` claims always have programmatically verified evidence.
- [ ] Live progress visible in the UI during a run.

**Commits:** `feat: implement evidence pipeline`, `feat: add claim status classification`, `feat: add sse research stream`

---

### Phase 4 — Analysis

**Goal:** Existing approaches mapped; limitations and potential opportunities identified with correct labeling.

| # | Task | Lane | Effort |
|---|---|---|---|
| 4.1 | `LandscapeAnalyzer`: approaches, architectures, models, datasets, tools, each citing claim IDs | Agents | M |
| 4.2 | Model and dataset comparison tables (license, size, task, access notes) | Agents | M |
| 4.3 | `GapAnalyzer`: limitations, contradictions, underexplored, opportunities; classification + qualitative confidence | Agents | L |
| 4.4 | Forbidden-phrase / numeric-novelty guard + "among the sources reviewed" language rule | Agents | S |
| 4.5 | Migrations: gaps, gap_claims; `GET /landscape`, `GET /gaps` | Backend | S |
| 4.6 | UI: Landscape view; Models and Datasets tabs; `GapCard` with evidence count, type, confidence, ⚠ verification | Frontend | M |

**Tests:** every gap links ≥ 1 claim; gaps default to `requires_human_verification=true`; guard rejects "no one has done this" and "87% novel"; landscape items reference existing claim IDs only.

**Definition of Done**
- [ ] Existing approaches grouped (e.g., CNN/Transformer/YOLO/segmentation/multimodal for the crop example).
- [ ] At least one evidence-backed potential opportunity shown with classification and verification warning.
- [ ] No numeric novelty displayed anywhere.

**Commits:** `feat: add landscape analyzer`, `feat: add gap analyzer with classification guards`

---

### Phase 5 — Build Planner

**Goal:** Feasibility analysis, architecture, MVP, stretch goals, and risks tailored to the team.

| # | Task | Lane | Effort |
|---|---|---|---|
| 5.1 | `FeasibilityAnalyzer`: difficulty, compute, dependencies, risks, MVP feasibility using team/time/hardware/skills | Agents | M |
| 5.2 | `BuildPlanner`: architecture (components, data flow, Mermaid), tech stack, MVP tasks with hour estimates, stretch, sequence, risks | Agents | L |
| 5.3 | Time-budget check: MVP hours ≤ `time_hours × team_size × 0.6`; overflow moves to stretch or flags | Backend | S |
| 5.4 | Migrations: proposals, architectures, mvp_tasks, risks; `POST/GET /build-plan` | Backend | M |
| 5.5 | UI: Architecture tab (Mermaid), MVP tab (MVP vs STRETCH numbered list), risks, "Generate Build Plan" button | Frontend | M |

**Tests:** budget overflow rule; plans reference only skills/hardware the team stated or flag a gap; mermaid validity (parse check); API contract.

**Definition of Done**
- [ ] "Generate Build Plan" produces architecture, MVP, stretch, risks for the example project.
- [ ] MVP fits the stated time budget (or explicitly warns).
- [ ] Plan reflects hardware constraints (e.g., recommends quantized/edge-friendly options when GPU is limited).

**Commits:** `feat: add feasibility analyzer`, `feat: add build planner`

---

### Phase 6 — Critic

**Goal:** Automatically detect weak output and trigger targeted re-research.

| # | Task | Lane | Effort |
|---|---|---|---|
| 6.1 | `ResearchCritic` agent with issue types (unsupported claim, missing source, contradiction, unrealistic recommendation, duplicate existing project, requirement misread, overstated novelty) | Agents | L |
| 6.2 | Deterministic pre-checks (claims without verified evidence, forbidden phrases, budget overflow) feeding the critic | Agents | S |
| 6.3 | Orchestrator loop: issue → targeted query → search → extract → update claim; max cycles; delta-only re-run | Agents | L |
| 6.4 | Cycle events in SSE (`cycle_started`, `critic_issue`); caveats persisted for unresolved issues | Backend | S |
| 6.5 | UI: critic issues, resolved/unresolved indicators in report and claim view | Frontend | S |

**Tests:** seeded unsupported claim triggers a targeted query and gets updated or downgraded; loop terminates at `MAX_CRITIC_CYCLES`; no infinite loops under tool failure; unresolved issues surface as caveats.

**Definition of Done**
- [ ] A claim lacking support triggers a second research cycle and ends supported, downgraded, or explicitly caveated.
- [ ] Loop always terminates within budgets.

**Commits:** `feat: add research critic`, `feat: add iterative research loop`

---

### Phase 7 — Challenge My Idea

**Goal:** Test a user's idea against existing work, with evidence and no verdict.

| # | Task | Lane | Effort |
|---|---|---|---|
| 7.1 | `IdeaParser` + query generation for related work | Agents | M |
| 7.2 | Reuse tool + evidence pipelines in a `challenge` run | Agents | S |
| 7.3 | `DifferentiationAnalyzer` (same vs. different dimensions) | Agents | M |
| 7.4 | Issue detection: duplication, dataset accessibility, compute | Agents | M |
| 7.5 | Migration: idea_challenges; `POST /challenge-idea`, `GET /challenge-idea/{id}` | Backend | S |
| 7.6 | UI: Ideas tab (form + result: existing work counts/links, ⚠ issues, differentiation, suggested investigation) | Frontend | M |

**Tests:** weak-idea fixture ("AI doctor") returns related work + issues; output contains no accept/reject verdict; counts match stored sources.

**Definition of Done**
- [ ] An intentionally weak idea yields related projects/papers, concrete issues, and a differentiation summary, all linked to sources.

**Commits:** `feat: add challenge my idea`

---

### Phase 8 — UI Polish

**Goal:** A demo-quality experience.

| # | Task | Lane | Effort |
|---|---|---|---|
| 8.1 | Dashboard: projects, recent research, saved opportunities | Frontend | M |
| 8.2 | Research progress checklist bound to SSE stages | Frontend | S |
| 8.3 | Evidence graph (React Flow): Source → Evidence → Claim → Gap (P2) | Frontend | M |
| 8.4 | Compiled Report page with all 15 sections; Markdown export (`/report.md`) | Both | M |
| 8.5 | Show model badge ("Qwen3-8B via Ollama") in run header | Frontend | S |
| 8.6 | Empty/error/loading states; accessibility pass; responsive layout | Frontend | M |
| 8.7 | Demo mode: cached demo project + cached tool results | Both | M |
| 8.8 | Rate limiting, final security pass against TRD §11 | Backend | S |

**Definition of Done**
- [ ] The full 3–5 minute demo script runs without intervention.
- [ ] No unhandled UI errors in the happy path; keyboard navigation works for main flows.

**Commits:** `feat: research dashboard and report`, `feat: evidence graph`, `chore: demo mode`

---

### Phase 9 — Evaluation

**Goal:** Measured, honest quality numbers and a complete public repo.

| # | Task | Lane | Effort |
|---|---|---|---|
| 9.1 | Assemble 10–20 benchmark briefs with ground-truth requirements (diverse domains) | All | M |
| 9.2 | `eval/run_eval.py` to run briefs headless and save outputs | Agents | M |
| 9.3 | Automated metrics: snippet-verification rate, claim status distribution, source counts, run reliability/time | Agents | S |
| 9.4 | Manual rating sheet: source relevance, citation correctness sample, gap usefulness, feasibility quality (2 raters) | All | M |
| 9.5 | `EVALUATION.md` with methodology, results, limitations | All | S |
| 9.6 | Final README (what/why, architecture, open-weight model, install, run, env vars, evaluation, limitations, roadmap) | Backend | M |
| 9.7 | Split `TRD.md` into `ARCHITECTURE.md`, `API_SPEC.md`, `DATABASE_SCHEMA.md`, `AGENT_DESIGN.md`, etc. if desired | Backend | S |
| 9.8 | Final license check; confirm repository is public | Backend | S |

**Definition of Done**
- [ ] Metrics reported for the full benchmark in `EVALUATION.md`.
- [ ] Targets from PRD §11.2 either met or limitations explained honestly.
- [ ] README complete; repo public with an OSI license.

**Commits:** `docs: add evaluation results`, `docs: finalize readme`

---

## 4. Scope-Cut Order (if time runs short)

Cut from the bottom up; never cut the P0 items needed for the demo.

1. PDF export, auth, file upload (already P2)
2. Evidence graph visualization
3. Hugging Face model/dataset tool (fall back to web search for models/datasets)
4. vLLM provider (stay on Ollama)
5. Editing of requirements/questions in UI
6. Second critic cycle (keep one)
7. Manual evaluation scale (reduce to 10 briefs; rate a smaller claim sample)

**Must keep for the demo:** requirements → research → evidence trace → gap → build plan → challenge idea → open-weight model visibility.

---

## 5. Risk Register (Execution)

| Risk | Phase | Mitigation |
|---|---|---|
| Qwen3-8B produces invalid JSON | 0–3 | Schema-constrained decoding, repair retry, small focused prompts, `MockProvider` fallback for UI work |
| Slow generation on limited GPU | All | Quantized model, thinking mode only where valuable, caching, demo mode with cached run |
| Semantic Scholar / GitHub / search rate limits | 2 | API keys, cache, backoff, per-run caps, graceful degradation |
| Hallucinated evidence | 3 | Deterministic verification; downgrade rules; critic |
| Lanes diverge on contracts | All | Freeze schemas (TRD §6, §7, §9) in Phase 0; generate FE types from OpenAPI; weekly doc-agreement check |
| Scope creep toward non-goals | All | Non-goal list in PRD §2.2; PR reviewers enforce |
| Demo-day network failure | 8 | Demo mode with cached sources + pre-recorded fallback |

---

## 6. Document Consistency Checklist (Stage B Review)

Before starting Phase 0, confirm agreement across documents:

```
PRD → Architecture → Database → API → Agents → UI
```

- [ ] Every PRD functional requirement maps to a TRD section (TRD §17).
- [ ] Every API response field exists in the DB schema or is derived from it.
- [ ] Every agent output schema matches its persisted tables and API schemas.
- [ ] SSE stage identifiers match the UI progress checklist.
- [ ] Claim status enum is identical in DB, API, agents, UI (`FACT`, `DIRECTLY_SUPPORTED`, `SYNTHESIS`, `INFERENCE`, `HYPOTHESIS`).
- [ ] Budgets and limits are identical in `.env.example`, TRD §8.3, and tests.
- [ ] Open decisions in PRD §14 are resolved or explicitly deferred.

---

## 7. Hand-off Prompts

### 7.1 For Claude (documentation lead)
> Do not write application code yet. Act as the project's technical lead. Convert the specification into implementation-ready documentation, resolve ambiguities with sensible defaults, and ensure all APIs, database entities, agent interfaces, and frontend/backend contracts are consistent.

### 7.2 For Antigravity (implementation)
Provide: `PRD.md`, `TRD.md` (or its split documents), `IMPLEMENTATION_PLAN.md`.

> Implement this project according to the specification. Do not redesign the architecture unless a documented technical blocker requires it. Work phase by phase starting at Phase 0. After each phase, run the relevant tests and verify the Definition of Done before continuing. Commit after each completed phase using the commit messages in the plan. Do not build the whole application in one pass.

### 7.3 Per-phase prompt template
> Implement **Phase N: <name>** from `IMPLEMENTATION_PLAN.md`, following `TRD.md` for schemas and contracts. List the tasks you will complete, implement them, run the tests listed for this phase, and report each Definition of Done item as pass/fail with evidence. Do not start Phase N+1.

---

## 8. Demo Checklist (3–5 minutes)

| Scene | Show | Phase needed |
|---|---|---|
| 1. Problem | A real competition brief | — |
| 2. Research | Paste brief; ✓ requirements, ✓ questions, ✓ papers, ✓ GitHub, ✓ evidence (live SSE) | 1–3 |
| 3. Landscape | Existing approaches | 4 |
| 4. Evidence | Click a claim → Claim → Evidence → Source | 3 |
| 5. Gap | Potential opportunity + evidence + verification warning | 4 |
| 6. Build | Generate Build Plan → architecture, MVP, risks | 5 |
| 7. Challenge | Intentionally weak idea → existing work + issues | 7 |
| 8. Open-weight | OpenResearch → Qwen3-8B → reasoning → synthesis | 0, 8 |

Rehearse twice with demo mode on and once live. Keep a pre-recorded fallback.

---

## 9. Final V1 Acceptance (maps to PRD §11.1)

- [ ] 1. Paste a real competition problem
- [ ] 2. Requirements understood
- [ ] 3. Research questions generated
- [ ] 4. Papers, GitHub, and web sources researched
- [ ] 5. Evidence stored
- [ ] 6. Existing approaches identified
- [ ] 7. Facts distinguished from inferences
- [ ] 8. Potential opportunities identified
- [ ] 9. Feasible architecture generated
- [ ] 10. MVP generated
- [ ] 11. Risks identified
- [ ] 12. Claims traceable to evidence
- [ ] 13. Reasoning demonstrably powered by an open-weight model
- [ ] 14. Published under an open-source license

All 14 checked ⇒ coherent, demonstrable hackathon MVP.
