import asyncio
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_completely_different_topic(client: AsyncClient):
    # 1. Create a non-agricultural project: Autonomous Drone Navigation
    create_res = await client.post(
        "/api/v1/projects",
        json={
            "name": "Subterranean Autonomous Drone Navigation",
            "problem_statement": "Develop visual-inertial odometry and obstacle avoidance for micro-drones navigating GPS-denied underground tunnels.",
            "rules_text": "48 hours event. ROS2 and open-source release mandatory.",
            "judging_text": "Collision-free traversal, mapping fidelity, and real-time state estimation.",
            "team_size": 3,
            "team_skills": ["C++", "ROS2", "Python", "Robotics"],
            "time_hours": 48,
            "hardware": "NVIDIA Jetson Orin Nano",
        },
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Run Requirement Analysis
    analyze_res = await client.post(f"/api/v1/projects/{project_id}/analyze")
    assert analyze_res.status_code == 200
    detail = analyze_res.json()

    # Verify requirements and questions mention drone / navigation / odometry / jetson, NOT crop detection!
    req_texts = " ".join(r["text"] for r in detail["requirements"]).lower()
    assert "crop" not in req_texts
    assert "plant" not in req_texts
    assert "drone" in req_texts or "navigation" in req_texts or "odometry" in req_texts

    # Verify questions mention drone / navigation
    q_texts = " ".join(q["question"] for q in detail["research_questions"]).lower()
    assert "crop" not in q_texts
    assert "drone" in q_texts or "navigation" in q_texts or "subterranean" in q_texts

    # 3. Run Research
    run_res = await client.post(
        f"/api/v1/projects/{project_id}/research",
        json={"max_cycles": 1},
    )
    assert run_res.status_code == 202

    await asyncio.sleep(1.0)

    # 4. Verify Build Plan is tailored to Drone Navigation
    plan_res = await client.get(f"/api/v1/projects/{project_id}/build-plan")
    assert plan_res.status_code == 200
    plan = plan_res.json()
    assert "crop" not in plan["summary"].lower()
    assert "drone" in plan["title"].lower() or "subterranean" in plan["title"].lower()
    assert "crop" not in plan["architecture"]["mermaid"].lower()
