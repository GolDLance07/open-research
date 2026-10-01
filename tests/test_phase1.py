import pytest
from httpx import AsyncClient
from app.agents.requirement_analyzer import RequirementAnalyzer
from app.agents.research_planner import ResearchPlanner
from app.db.models.project import Project
from app.llm.mock import MockProvider


@pytest.mark.asyncio
async def test_requirement_analyzer_agent():
    llm = MockProvider()
    agent = RequirementAnalyzer(llm)
    dummy_project = Project(
        id="test-proj-1",
        name="Crop Health Scanner",
        problem_statement="Build an AI system for early detection of crop diseases in low-resource environments.",
        rules_text="Max 36 hours. Open source.",
        team_size=4,
        team_skills=["Python", "ML"],
        time_hours=36,
    )
    result = await agent.run(dummy_project)
    assert len(result.requirements) > 0
    assert len(result.constraints) > 0
    assert len(result.deliverables) > 0
    assert len(result.judging_criteria) > 0
    assert result.requirements[0].text is not None


@pytest.mark.asyncio
async def test_research_planner_agent():
    llm = MockProvider()
    planner = ResearchPlanner(llm)
    dummy_project = Project(
        id="test-proj-2",
        name="Crop Health Scanner",
        problem_statement="Build an AI system for early detection of crop diseases in low-resource environments.",
        team_size=4,
        team_skills=["Python", "ML"],
        time_hours=36,
    )
    result = await planner.run(dummy_project)
    assert len(result.questions) >= 5
    assert result.questions[0].id == "RQ1"
    assert result.questions[0].priority in ("high", "medium", "low")


@pytest.mark.asyncio
async def test_analyze_endpoint_and_patching(client: AsyncClient):
    # 1. Create project
    create_res = await client.post(
        "/api/v1/projects",
        json={
            "name": "Phase 1 Hackathon Project",
            "problem_statement": "Detect agricultural leaf disease using computer vision and edge models.",
            "rules_text": "36 hours time limit. Open source only.",
            "judging_text": "Accuracy, edge performance, and feasibility.",
            "team_size": 3,
            "team_skills": ["Python", "FastAPI", "PyTorch"],
            "time_hours": 36,
        },
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Run Analyze endpoint
    analyze_res = await client.post(f"/api/v1/projects/{project_id}/analyze")
    assert analyze_res.status_code == 200
    detail = analyze_res.json()
    assert detail["status"] == "analyzed"
    assert len(detail["requirements"]) >= 4
    assert len(detail["research_questions"]) >= 5

    # 3. Patch requirement
    req_to_edit = detail["requirements"][0]
    patch_req_res = await client.patch(
        f"/api/v1/projects/{project_id}/requirements/{req_to_edit['id']}",
        json={"text": "Updated requirement text", "priority": "high"},
    )
    assert patch_req_res.status_code == 200
    updated_req = patch_req_res.json()
    assert updated_req["text"] == "Updated requirement text"
    assert updated_req["user_edited"] is True

    # 4. Patch question
    q_to_edit = detail["research_questions"][0]
    patch_q_res = await client.patch(
        f"/api/v1/projects/{project_id}/questions/{q_to_edit['id']}",
        json={"priority": "low"},
    )
    assert patch_q_res.status_code == 200
    assert patch_q_res.json()["priority"] == "low"


@pytest.mark.asyncio
async def test_validation_error_on_short_problem_statement(client: AsyncClient):
    bad_res = await client.post(
        "/api/v1/projects",
        json={
            "name": "Too short",
            "problem_statement": "Too short",  # min is 20 chars
        },
    )
    assert bad_res.status_code == 422
    data = bad_res.json()
    assert data["error"]["code"] == "validation_error"
