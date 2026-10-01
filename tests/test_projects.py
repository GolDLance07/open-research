import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_debug_llm_endpoint(client: AsyncClient):
    payload = {
        "prompt": "Hello Qwen, please identify open research gaps.",
        "temperature": 0.2,
        "thinking": False,
    }
    response = await client.post("/api/v1/debug/llm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "mock"
    assert "response" in data
    assert data["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_project_crud_lifecycle(client: AsyncClient):
    # 1. Create project
    create_payload = {
        "name": "Crop Disease Detection",
        "competition_name": "AgriAI Hackathon",
        "problem_statement": "Build an AI system for early detection of crop diseases in low-resource environments.",
        "rules_text": "Must be open source, max 36 hours.",
        "judging_text": "Accuracy, latency, and feasibility.",
        "team_size": 4,
        "team_skills": ["Python", "PyTorch", "React"],
        "time_hours": 36,
        "hardware": "1x NVIDIA T4 GPU",
    }
    create_res = await client.post("/api/v1/projects", json=create_payload)
    assert create_res.status_code == 201
    project = create_res.json()
    project_id = project["id"]
    assert project["name"] == "Crop Disease Detection"
    assert project["team_size"] == 4
    assert project["status"] == "draft"

    # 2. Get project by ID
    get_res = await client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project_id

    # 3. List projects
    list_res = await client.get("/api/v1/projects")
    assert list_res.status_code == 200
    projects_list = list_res.json()
    assert any(p["id"] == project_id for p in projects_list)

    # 4. Patch project
    patch_res = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"name": "Crop Disease Detection V2", "time_hours": 48},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Crop Disease Detection V2"
    assert patch_res.json()["time_hours"] == 48

    # 5. Delete project
    del_res = await client.delete(f"/api/v1/projects/{project_id}")
    assert del_res.status_code == 204

    # 6. Verify deleted
    get_again = await client.get(f"/api/v1/projects/{project_id}")
    assert get_again.status_code == 404
