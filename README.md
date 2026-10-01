# OpenResearch

OpenResearch is an AI research workspace that turns a **problem statement or competition brief** into an **evidence-backed build strategy**.

It researches the landscape across web, academic papers, GitHub repositories, and open models/datasets, extracts structured evidence, separates fact from inference, identifies opportunities, and proposes a feasible architecture and MVP tailored to the user's team and time budget.

The reasoning layer is designed to run on open-weight models (**Qwen3-8B**).

---

## Key Features

- **Source → Evidence → Claim → Gap → Build Plan**: Complete provenance chain.
- **Evidence ≠ Inference**: Explicit classification labels (`FACT`, `DIRECTLY_SUPPORTED`, `SYNTHESIS`, `INFERENCE`, `HYPOTHESIS`).
- **Open-Weight Reasoning**: Powered by Qwen3-8B (via Ollama or vLLM), with a mock provider for zero-GPU development and testing.
- **Honest Feasibility & MVP**: Calculates realistic build capacity based on team size, available hours, and compute.
- **Challenge My Idea**: Tests any project idea against existing work, highlighting differentiation and potential pitfalls.

---

## Architecture Overview

```
Next.js Frontend (TypeScript, Tailwind, shadcn/ui)
       │ (REST / SSE)
FastAPI Backend (Python 3.11+)
       │
PostgreSQL / SQLAlchemy (Async)
       │
ResearchOrchestrator
 ├── RequirementAnalyzer
 ├── ResearchPlanner
 ├── Tools (Web, Paper, GitHub, HF)
 ├── Evidence Pipeline (Chunk, Rank, LLM Extract, Deterministic Verify)
 ├── LandscapeAnalyzer
 ├── GapAnalyzer
 ├── FeasibilityAnalyzer
 ├── BuildPlanner
 └── ResearchCritic
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional, for containerized run)
- Ollama (optional, with `ollama pull qwen3:8b`)

### Option 1: Docker Compose
```bash
cp .env.example .env
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API & Docs: `http://localhost:8000/docs`

### Option 2: Local Development
1. **Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## Documentation
- [PRD.md](docs/PRD.md): Product Requirements Document
- [TRD.md](docs/TRD.md): Technical Requirements Document
- [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md): Step-by-step phased execution plan

---

## License
OpenResearch is released under the [Apache 2.0 License](LICENSE).
