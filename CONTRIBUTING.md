# Contributing to OpenResearch

Thank you for your interest in contributing to OpenResearch!

## Development Philosophy
- **Tools collect evidence; the model reasons over it.** Tools never reason; the LLM never fetches.
- **Controlled orchestrator, not an agent swarm.** A deterministic Python orchestrator calls single-purpose agents in a fixed graph with one bounded loop.
- **Structured I/O everywhere.** Every agent has a Pydantic input and output schema; model output is schema-constrained and validated.
- **Verifiable provenance.** Evidence snippets must be programmatically verifiable against stored source text.
- **Untrusted content stays untrusted.** Retrieved text is data, never instructions.

## Development Workflow
1. Work phase by phase according to `IMPLEMENTATION_PLAN.md`.
2. Follow conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
3. Ensure CI passes:
   - Backend: `ruff check .`, `mypy app`, `pytest`
   - Frontend: `npm run lint`, `npm run build`
4. Code should always run out of the box with `LLM_PROVIDER=mock`.

## Local Setup
See `README.md` for step-by-step setup instructions.
