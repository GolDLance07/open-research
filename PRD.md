# OpenResearch — Product Requirements Document (PRD)

| Field | Value |
|---|---|
| Product | OpenResearch |
| Category | AI Research Agent / Research-to-Build Platform |
| Version | 1.0 (V1 / Hackathon MVP) |
| Status | Draft for team review |
| Source | `OpenResearch_Project_Handoff.md` |
| Companion docs | `TRD.md`, `IMPLEMENTATION_PLAN.md` |

---

## 1. Overview

### 1.1 Summary
OpenResearch is an AI research workspace that turns a **problem statement or competition brief** into an **evidence-backed build strategy**. It researches the landscape (web, academic papers, GitHub, model and dataset repositories), extracts structured evidence, separates fact from inference, identifies potential gaps, and proposes a feasible architecture and MVP for the user's team and time budget.

### 1.2 Problem
Students and developers in hackathons, competitions, college projects, and research challenges lose hours (often the first third of the event) working out:

- What is actually being asked, and what the rules and judging criteria imply
- What already exists (papers, repos, models, datasets)
- What the limitations of existing approaches are
- Whether their idea is differentiated and feasible within their time and compute
- What they should build

Existing tools either give unsourced chat answers or raw search results. Neither gives a traceable path from source to recommendation.

### 1.3 Vision
> "Here's what exists, here's the evidence, here's what's missing or worth investigating, and here's what your team can realistically build."

The system maintains a traceable chain for every important statement:

```
Source → Evidence → Claim → Analysis → Recommendation
```

### 1.4 Hackathon deliverable
A working application whose reasoning layer is powered by an **open-weight model (Qwen3-8B)**, published in a public GitHub repository under an OSI-approved open-source license.

---

## 2. Goals and Non-Goals

### 2.1 Goals (V1)
| ID | Goal |
|---|---|
| G1 | Convert a pasted competition brief into structured requirements, constraints, deliverables, and judging criteria |
| G2 | Generate prioritized research questions |
| G3 | Retrieve relevant web sources, papers, and GitHub repositories (plus models and datasets) |
| G4 | Extract structured evidence and generate claims linked to sources |
| G5 | Label every insight as `FACT`, `DIRECTLY_SUPPORTED`, `SYNTHESIS`, `INFERENCE`, or `HYPOTHESIS` |
| G6 | Map existing approaches and identify limitations, contradictions, and potential opportunities |
| G7 | Produce a feasibility assessment tailored to team size, skills, time, and hardware |
| G8 | Produce an architecture, MVP, stretch goals, and risks |
| G9 | Run an iterative critic loop that finds unsupported claims and triggers targeted re-research |
| G10 | Provide a "Challenge My Idea" feature that tests a user's idea against existing work |
| G11 | Demonstrably use an open-weight model for all core reasoning |

### 2.2 Non-Goals (V1)
Custom model training, fine-tuning, mobile app, browser extension, autonomous coding, automatic deployment, fully autonomous research, model harness, multi-model routing, multi-agent swarms, large vector database, arbitrary web scraping, Agent Skill extraction.

> The goal is research intelligence, not technological maximalism.

---

## 3. Target Users

### 3.1 Primary persona — "Hackathon Team Lead"
A student or developer on a small team (2–5 people) in a hackathon, technical competition, college project, research project, or innovation challenge.

| Attribute | Detail |
|---|---|
| Context | Time-boxed (e.g., 24–72 hours), limited GPU, mixed skills |
| Pain | Doesn't know the landscape; fears building something that already exists |
| Need | Fast, trustworthy orientation and a realistic plan |
| Success | Leaves with a defensible idea, an MVP scope, and sources to cite |

### 3.2 Example scenario
A 4-person BTech team gets "Build an AI system for early detection of crop diseases." They paste the brief, team skills (Python, React, ML), 36 hours, and limited GPU. OpenResearch returns existing approaches (CNN, Transformer, YOLO, segmentation, multimodal), datasets, models, limitations, a flagged opportunity ("lightweight, explainable inference for low-resource devices"), and a 36-hour MVP plan.

### 3.3 Secondary users (informal)
Mentors, judges, and solo researchers doing quick landscape scans.

---

## 4. Product Principles

| # | Principle | Product implication |
|---|---|---|
| P1 | **Evidence first** | Important claims must have sources. Never state "no one has done this"; say "among the sources reviewed, we found…" |
| P2 | **Evidence ≠ inference** | Every insight carries a classification label, visible in the UI |
| P3 | **Meaningful open-weight model** | The model performs requirement extraction, planning, synthesis, claim generation, comparison, gap analysis, feasibility, architecture, MVP planning, and critique |
| P4 | **Sources are first-class** | Every source stores id, title, url, type, author, date, publisher, snippet, retrieved_at, license |
| P5 | **Human in control** | The system presents evidence and analysis; the user decides |
| P6 | **No fake precision** | No "87% novel" scores. Use qualitative confidence (Low/Medium/High) and "Requires human verification" |
| P7 | **Retrieved content is untrusted** | Web content is data, never instructions |

---

## 5. Scope

### 5.1 Inputs
| Input | Required | Notes |
|---|---|---|
| Problem statement | Yes | Paste text; file upload (`.txt`, `.md`) as stretch |
| Competition description / rules | No | Pasted text |
| Judging criteria | No | Pasted or extracted from brief |
| Team size | Yes | Integer |
| Team skills | Yes | Free-text tags |
| Available development time | Yes | Hours |
| Hardware constraints | No | e.g., "no GPU", "1× 8 GB GPU" |

### 5.2 Outputs (the Research Report)
1. Requirement analysis
2. Research questions
3. Relevant web sources
4. Relevant papers
5. Relevant GitHub projects
6. Existing approaches
7. Models
8. Datasets
9. Evidence-backed observations (claims)
10. Potential gaps / opportunities
11. Feasibility analysis
12. Proposed architecture
13. MVP (and stretch goals)
14. Risks
15. Sources

---

## 6. User Flow

```
Create project → Provide inputs → Competition analysis → Research questions
→ Research run (streamed) → Evidence & landscape → Gaps → Build plan
→ (optional) Challenge My Idea → Export / share report
```

| Step | User action | System response |
|---|---|---|
| 1 | Create project (name, competition, time, team, skills, hardware) | Project saved |
| 2 | Paste problem statement, rules, judging criteria | Inputs stored |
| 3 | Click **Analyze** | Requirements, constraints, deliverables, judging criteria shown with ✓ / ⚠ markers |
| 4 | Review research questions (RQ1…RQn); optionally edit/remove | Questions confirmed |
| 5 | Click **Run Research** | Live progress stream; sources, claims populate as they arrive |
| 6 | Browse Sources / Papers / GitHub / Models / Datasets | Source cards with "relevant because…" |
| 7 | Open a claim | Claim → Evidence → Source trace with status label |
| 8 | Review Gaps | Opportunities with evidence count, type, confidence, verification warning |
| 9 | Click **Generate Build Plan** | Architecture, MVP, stretch, stack, sequence, risks |
| 10 | Use **Challenge My Idea** | Related work, issues, differentiation, suggested investigation |

---

## 7. Functional Requirements

Priority: **P0** = required for V1 demo, **P1** = should have, **P2** = nice to have.

### 7.1 Project and Input Management
| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | User can create, view, list, and delete projects | P0 |
| FR-1.2 | Project stores problem statement, rules, judging criteria, team size, skills, time, hardware | P0 |
| FR-1.3 | Input validation with clear error messages (length limits, required fields) | P0 |
| FR-1.4 | File upload of brief (`.txt`/`.md`) | P2 |

### 7.2 Requirement Analysis
| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | Extract `requirements`, `constraints`, `deliverables`, `judging_criteria` as structured JSON | P0 |
| FR-2.2 | Each extracted item references the span of input text it came from | P1 |
| FR-2.3 | User can edit extracted requirements before research | P1 |

### 7.3 Research Planning
| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | Generate 5–10 research questions with id (RQn), text, priority (high/medium/low) | P0 |
| FR-3.2 | Default question coverage: existing solutions, datasets, models, limitations, open-source models, deployment, underexplored areas | P0 |
| FR-3.3 | User can add/remove/reprioritize questions | P1 |

### 7.4 Research Tools
| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | Web search via a pluggable search provider | P0 |
| FR-4.2 | Academic search via Semantic Scholar | P0 |
| FR-4.3 | GitHub repository search extracting name, description, language, stars, activity, license, topics, URL, README summary | P0 |
| FR-4.4 | Model discovery (Hugging Face model hub) | P1 |
| FR-4.5 | Dataset discovery (Hugging Face datasets; Kaggle/others via web) | P1 |
| FR-4.6 | All results normalized into the unified `Source` object, deduplicated by canonical URL | P0 |
| FR-4.7 | Every source is validated (URL scheme, domain rules) and sanitized before reaching the model | P0 |

### 7.5 Evidence and Claims
| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | Extract structured evidence (quote/snippet, location such as section or URL fragment, source id) from sources | P0 |
| FR-5.2 | Generate claims; each claim links to ≥1 evidence item or is labeled `INFERENCE` / `HYPOTHESIS` | P0 |
| FR-5.3 | Every claim has one status: `FACT`, `DIRECTLY_SUPPORTED`, `SYNTHESIS`, `INFERENCE`, `HYPOTHESIS` | P0 |
| FR-5.4 | `FACT` and `DIRECTLY_SUPPORTED` claims must have evidence whose snippet is verifiably present in the source text | P0 |
| FR-5.5 | Claim detail view shows Claim → Evidence → Source with "Open Source" action | P0 |
| FR-5.6 | Evidence graph visualization | P2 |

### 7.6 Analysis
| ID | Requirement | Priority |
|---|---|---|
| FR-6.1 | Landscape: group approaches, architectures, models, datasets, tools | P0 |
| FR-6.2 | Model and dataset comparison tables | P1 |
| FR-6.3 | Gap analysis: limitations, contradictions, underexplored areas, potential opportunities | P0 |
| FR-6.4 | Each gap carries a classification, qualitative confidence, linked evidence, and verification flag | P0 |
| FR-6.5 | Language rule: gaps use "among the sources reviewed…", never absolute novelty claims | P0 |

### 7.7 Feasibility and Build Planning
| ID | Requirement | Priority |
|---|---|---|
| FR-7.1 | Feasibility output: difficulty, compute, dependencies, risks, MVP feasibility, tailored to team/time/hardware/skills | P0 |
| FR-7.2 | Architecture proposal (components, data flow, stack) | P0 |
| FR-7.3 | MVP task list in implementation sequence, plus stretch goals | P0 |
| FR-7.4 | Risk list with mitigations | P0 |
| FR-7.5 | MVP tasks are scoped to the stated time budget | P1 |

### 7.8 Critic and Research Loop
| ID | Requirement | Priority |
|---|---|---|
| FR-8.1 | Critic reviews output for unsupported claims, missing sources, contradictory evidence, unrealistic recommendations, duplicate existing projects, misread requirements | P0 |
| FR-8.2 | On issues, orchestrator generates targeted search queries and runs another cycle | P0 |
| FR-8.3 | Hard caps on cycles, tool calls, and wall-clock time | P0 |
| FR-8.4 | Unresolved issues appear in the report as visible caveats | P0 |

### 7.9 Challenge My Idea
| ID | Requirement | Priority |
|---|---|---|
| FR-9.1 | User submits a free-text idea in a project | P0 |
| FR-9.2 | System researches related projects and papers | P0 |
| FR-9.3 | Output: existing work found (counts + links), potential issues (duplication, dataset access, compute), differentiation summary, suggested investigation | P0 |
| FR-9.4 | Output is evidence and analysis only, never a go/no-go verdict | P0 |

### 7.10 Progress Streaming
| ID | Requirement | Priority |
|---|---|---|
| FR-10.1 | Research runs stream stage-level progress via SSE | P0 |
| FR-10.2 | Stages: reading requirements, creating research questions, searching web/academic/GitHub, extracting evidence, comparing approaches, analyzing opportunities, building plan | P0 |
| FR-10.3 | Reconnecting clients receive missed events | P1 |

### 7.11 Report
| ID | Requirement | Priority |
|---|---|---|
| FR-11.1 | Compiled report page with all 15 output sections | P0 |
| FR-11.2 | Export report as Markdown | P1 |
| FR-11.3 | Export as PDF | P2 |

### 7.12 Model Abstraction
| ID | Requirement | Priority |
|---|---|---|
| FR-12.1 | `LLMProvider` interface with `OllamaProvider`, `VLLMProvider`, `MockProvider` | P0 |
| FR-12.2 | Provider and model selected via environment variables only | P0 |
| FR-12.3 | UI shows which model is powering a run (supports the open-weight demo scene) | P0 |

---

## 8. User Interface Requirements

### 8.1 Screens
| Screen | Contents |
|---|---|
| **Dashboard** | Projects, recent research, saved opportunities |
| **Project page (tabbed)** | Overview, Requirements, Research, Sources, Papers, GitHub, Models, Datasets, Gaps, Ideas, Architecture, MVP |
| **Research view** | Live progress checklist; incremental results |
| **Claim detail** | Claim, status, source, evidence, "Open Source" |
| **Report** | Full compiled report |

### 8.2 Component requirements
| Component | Requirement |
|---|---|
| **Source card** | Title, type badge, year, "Relevant because…", **View Source** and **Use Evidence** actions |
| **Evidence panel** | Claim text, status badge (✓ Directly supported, etc.), source name, evidence location, **Open Source** |
| **Gap card** | Title, evidence count, type, confidence, ⚠ "Human verification required" |
| **Build plan** | Numbered MVP tasks (01…) and STRETCH tasks, architecture diagram, risks |
| **Progress list** | ✓ complete, ○ pending, spinner active; live via SSE |

### 8.3 UX rules
- Never show numeric novelty scores.
- Status labels use consistent colors and text (do not rely on color alone).
- Every empty and error state is explicit and actionable.
- Long-running operations always show progress.

---

## 9. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | Requirement analysis completes in ≤ 30 s on the demo hardware; full research run in ≤ 8 min on a typical brief (target; measured in evaluation) |
| NFR-2 | Responsiveness | First progress event within 2 s of starting a run |
| NFR-3 | Reliability | Tool failures degrade gracefully: the run continues with remaining tools and reports what failed |
| NFR-4 | Security | Env-based secrets, rate limiting, request validation, URL validation, prompt-injection defenses (see TRD §11) |
| NFR-5 | Portability | Runs locally with Docker Compose; model served via Ollama; vLLM supported |
| NFR-6 | Observability | Structured logs per run, tool call counts, token usage, errors |
| NFR-7 | Testability | `MockProvider` makes the pipeline testable without a GPU |
| NFR-8 | Accessibility | Keyboard navigable; labels not color-only; contrast AA |
| NFR-9 | Licensing | Public repo with OSI-approved license; third-party license compatibility checked |
| NFR-10 | Maintainability | Documentation updated in the same PR as the feature |

---

## 10. Assumptions and Defaults (Resolved Ambiguities)

The handoff leaves several decisions open. These are the defaults adopted; each can be revisited at team review.

| # | Ambiguity | Default |
|---|---|---|
| A1 | Web search provider | Pluggable `SearchProvider`; default **Tavily** (API key via `SEARCH_API_KEY`); fallback adapter for Brave / SerpAPI |
| A2 | Authentication | **Single-user mode by default** (`AUTH_MODE=none`) with a seeded local user; `User` table retained; JWT auth is P2 |
| A3 | Background execution | In-process async worker with run state persisted in PostgreSQL; no Celery/Redis in V1 |
| A4 | Retrieval/ranking | PostgreSQL full-text search plus lightweight BM25 passage ranking; **no vector database** |
| A5 | Model discovery sources | Hugging Face Hub API for models and datasets |
| A6 | Report export | Markdown (P1); PDF deferred |
| A7 | Max critic cycles | 2 additional research cycles |
| A8 | Max tool calls per run | 60 (configurable) |
| A9 | Context window | Configured at 16k–32k tokens for Qwen3-8B; long documents are chunked and passage-ranked |
| A10 | Qwen3 reasoning mode | Thinking mode on for planning/gap/critic; off for extraction and formatting tasks |
| A11 | API versioning | All endpoints under `/api/v1` |
| A12 | Language | English only in V1 |
| A13 | Team collaboration | Not in V1; one owner per project |

---

## 11. Success Metrics

### 11.1 Definition of Done for V1 (from handoff)
The team can:
1. Paste a real competition problem.
2. Have OpenResearch understand the requirements.
3. Generate research questions.
4. Research papers, GitHub, and web sources.
5. Store evidence.
6. Identify existing approaches.
7. Distinguish facts from inferences.
8. Identify potential opportunities.
9. Generate a feasible architecture.
10. Generate an MVP.
11. Identify risks.
12. Trace important claims to evidence.
13. Demonstrate that the reasoning layer is powered by an open-weight model.
14. Publish the project under an appropriate open-source license.

### 11.2 Quality metrics (benchmark of 10–20 problem statements)
| Metric | Definition | Initial target |
|---|---|---|
| Requirement extraction accuracy | Fraction of ground-truth requirements recovered; precision of extracted items | ≥ 80% recall |
| Source relevance | Human-rated relevant sources / total sources shown | ≥ 70% |
| Citation correctness | Cited evidence snippet actually present in the source and supports the claim | ≥ 90% for `FACT`/`DIRECTLY_SUPPORTED` |
| Claim support rate | Claims with valid evidence or correctly labeled inference | ≥ 95% correctly labeled |
| Gap usefulness | Human rating (1–5) of opportunity usefulness | Mean ≥ 3.5 |
| Feasibility quality | Human rating (1–5) of plan realism for stated team/time | Mean ≥ 3.5 |
| Run reliability | Runs completing without fatal error | ≥ 95% |

Targets are initial hypotheses to be calibrated after the first benchmark pass.

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Qwen3-8B hallucinates citations | Breaks the core promise | Programmatic verification that evidence snippets exist in stored source text; critic loop; downgrade unverifiable claims to `INFERENCE` |
| 8B model struggles with long contexts | Poor synthesis | Chunk + rank passages; small, focused prompts per agent; JSON-schema constrained output |
| Prompt injection via web pages | Security / corrupted output | Treat content as untrusted data, delimiters, sanitization, no tool access from content (TRD §11) |
| External API rate limits (Semantic Scholar, GitHub, search) | Incomplete research | Caching, backoff, API keys, per-run call caps, graceful degradation |
| Limited GPU at event | Slow runs | Quantized model via Ollama; `MockProvider` for UI work; cached demo runs |
| Overreach in scope | Unfinished demo | Strict non-goals; phase gates; P0/P1/P2 prioritization |
| Overstated novelty | Misleads users | Language rules, "Requires human verification," no numeric novelty |
| Demo failure due to network | Failed demo | Pre-recorded fallback run; cached sources for the demo brief |

---

## 13. Release Plan

| Milestone | Content |
|---|---|
| **M1 — Foundation** | Phases 0–1: stack runs end-to-end; requirement analysis |
| **M2 — Research core** | Phases 2–3: tools, sources, evidence, claims |
| **M3 — Intelligence** | Phases 4–6: analysis, build planner, critic loop |
| **M4 — Differentiators** | Phase 7: Challenge My Idea |
| **M5 — Demo-ready** | Phases 8–9: UI polish, benchmark, README, license |

See `IMPLEMENTATION_PLAN.md` for tasks and gates.

---

## 14. Open Questions for Team Review

1. Confirm Tavily vs. an alternative search provider and available API budget.
2. Confirm target hardware for the live demo (affects Ollama vs. vLLM).
3. Is authentication needed for the demo, or is single-user mode acceptable?
4. Which open-source license (recommended: Apache-2.0 for patent grant, or MIT for simplicity)?
5. Which 10–20 problem statements form the evaluation benchmark?
6. Should Markdown export be promoted to P0 for the demo?

---

## Appendix A — Glossary

| Term | Meaning |
|---|---|
| Source | A retrieved web page, paper, repo, model card, or dataset card with metadata |
| Evidence | A specific snippet/location within a source |
| Claim | A statement derived from evidence, with a classification |
| Gap | A limitation, contradiction, or potentially underexplored area derived from claims |
| Proposal | A recommended direction produced from gaps and feasibility |
| Research run | One execution of the research pipeline, including critic cycles |

## Appendix B — Claim Classification Reference

| Status | Meaning | Evidence requirement | Example |
|---|---|---|---|
| `FACT` | Specific, verifiable data point stated in a source | Exact snippet in source | "Paper X reports 94.2% accuracy." |
| `DIRECTLY_SUPPORTED` | Source states the claim in substance | Snippet in source | "Model X supports edge inference." |
| `SYNTHESIS` | Aggregation across multiple sources | ≥ 2 linked evidence items | "Three reviewed papers use transformer-based architectures." |
| `INFERENCE` | Reasoned conclusion not stated in sources | Supporting evidence plus reasoning | "Lightweight transformers may suit edge deployment." |
| `HYPOTHESIS` | Speculative direction for investigation | Optional | "Combining X and Y may yield a useful direction." |
