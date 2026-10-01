import asyncio
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_research_lifecycle(client: AsyncClient):
    # 1. Create project
    create_res = await client.post(
        "/api/v1/projects",
        json={
            "name": "AgriVision Plant Disease Classifier",
            "problem_statement": "Real-time crop disease diagnosis using computer vision on low-resource hardware.",
            "rules_text": "36 hours hackathon limit. Open-source release.",
            "judging_text": "Accuracy, latency, and proof of research provenance.",
            "team_size": 4,
            "team_skills": ["Python", "PyTorch", "React", "Edge AI"],
            "time_hours": 36,
            "hardware": "1x NVIDIA T4 GPU",
        },
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Analyze project
    analyze_res = await client.post(f"/api/v1/projects/{project_id}/analyze")
    assert analyze_res.status_code == 200

    # 3. Start research run
    run_res = await client.post(
        f"/api/v1/projects/{project_id}/research",
        json={"max_cycles": 1},
    )
    assert run_res.status_code == 202
    run_id = run_res.json()["run_id"]

    # Allow background execution
    await asyncio.sleep(1.0)

    # 4. Check sources
    sources_res = await client.get(f"/api/v1/projects/{project_id}/sources")
    assert sources_res.status_code == 200
    sources = sources_res.json()
    assert len(sources) > 0
    assert any(s["source_type"] in ("web", "paper", "repository", "model") for s in sources)

    # 5. Check claims with evidence
    claims_res = await client.get(f"/api/v1/projects/{project_id}/claims")
    assert claims_res.status_code == 200
    claims = claims_res.json()
    assert len(claims) > 0
    assert claims[0]["status"] in ("FACT", "DIRECTLY_SUPPORTED", "SYNTHESIS")
    assert len(claims[0]["evidence"]) > 0

    # 6. Check gaps
    gaps_res = await client.get(f"/api/v1/projects/{project_id}/gaps")
    assert gaps_res.status_code == 200
    gaps = gaps_res.json()
    assert len(gaps) > 0
    assert gaps[0]["requires_human_verification"] is True

    # 7. Check build plan
    plan_res = await client.get(f"/api/v1/projects/{project_id}/build-plan")
    assert plan_res.status_code == 200
    plan = plan_res.json()
    assert "architecture" in plan
    assert len(plan["tasks"]) > 0
    assert "mermaid" in plan["architecture"]

    # 8. Challenge an idea
    challenge_res = await client.post(
        f"/api/v1/projects/{project_id}/challenge-idea",
        json={"idea_text": "We will fine-tune a compact MobileNet with INT8 quantization for sub-50ms leaf inference."},
    )
    assert challenge_res.status_code == 200
    challenge = challenge_res.json()
    assert len(challenge["issues"]) > 0
    assert len(challenge["differentiation"]["differentiation_angles"]) > 0
