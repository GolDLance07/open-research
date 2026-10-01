from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.agents.requirement_analyzer import RequirementAnalyzer
from app.agents.research_planner import ResearchPlanner
from app.api.deps import get_current_user, get_db
from app.db.models.project import Project
from app.db.models.requirement import Requirement
from app.db.models.research_question import ResearchQuestion
from app.db.models.user import User
from app.llm.base import LLMProvider
from app.llm.factory import get_llm_provider
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.schemas.requirement import RequirementResponse, RequirementUpdate
from app.schemas.research_question import (
    ResearchQuestionResponse,
    ResearchQuestionUpdate,
)

router = APIRouter()


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
) -> List[ProjectResponse]:
    stmt = select(Project).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return list(projects)


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
) -> ProjectResponse:
    project = Project(
        user_id=user.id if user else None,
        name=data.name,
        competition_name=data.competition_name,
        problem_statement=data.problem_statement,
        rules_text=data.rules_text,
        judging_text=data.judging_text,
        team_size=data.team_size,
        team_skills=data.team_skills,
        time_hours=data.time_hours,
        hardware=data.hardware,
        status="draft",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/projects/{id}", response_model=ProjectDetailResponse)
async def get_project(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectDetailResponse:
    stmt = (
        select(Project)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.research_questions),
        )
        .where(Project.id == id)
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{id}' not found",
        )
    return project


@router.patch("/projects/{id}", response_model=ProjectResponse)
async def update_project(
    id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    stmt = select(Project).where(Project.id == id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{id}' not found",
        )

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(project, field, val)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/projects/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    stmt = select(Project).where(Project.id == id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{id}' not found",
        )
    await db.delete(project)
    await db.commit()


@router.post("/projects/{id}/analyze", response_model=ProjectDetailResponse)
async def analyze_project(
    id: str,
    db: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
) -> ProjectDetailResponse:
    stmt = (
        select(Project)
        .options(
            selectinload(Project.requirements),
            selectinload(Project.research_questions),
        )
        .where(Project.id == id)
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{id}' not found",
        )

    # 1. Run RequirementAnalyzer
    req_analyzer = RequirementAnalyzer(llm)
    req_output = await req_analyzer.run(project)

    # Clear previous generated requirements if re-running analysis
    project.requirements.clear()
    project.research_questions.clear()
    await db.flush()

    position = 0
    # Add requirements
    for item in req_output.requirements:
        project.requirements.append(
            Requirement(
                kind="requirement",
                text=item.text,
                source_span=item.source_span,
                priority=item.priority,
                severity=None,
                position=position,
            )
        )
        position += 1

    # Add constraints
    for item in req_output.constraints:
        project.requirements.append(
            Requirement(
                kind="constraint",
                text=item.text,
                source_span=item.source_span,
                priority=item.priority,
                severity=item.severity or "warning",
                position=position,
            )
        )
        position += 1

    # Add deliverables
    for item in req_output.deliverables:
        project.requirements.append(
            Requirement(
                kind="deliverable",
                text=item.text,
                source_span=item.source_span,
                priority=None,
                severity=None,
                position=position,
            )
        )
        position += 1

    # Add judging criteria
    for item in req_output.judging_criteria:
        project.requirements.append(
            Requirement(
                kind="judging_criterion",
                text=item.text,
                source_span=item.source_span,
                priority=None,
                severity=None,
                position=position,
            )
        )
        position += 1

    # 2. Run ResearchPlanner
    planner = ResearchPlanner(llm)
    planner_output = await planner.run(project, req_output)

    for idx, q in enumerate(planner_output.questions, start=1):
        project.research_questions.append(
            ResearchQuestion(
                label=q.id or f"RQ{idx}",
                question=q.question,
                priority=q.priority,
                status="open",
                position=idx,
            )
        )

    project.status = "analyzed"
    await db.commit()
    return project


@router.patch("/projects/{id}/requirements/{rid}", response_model=RequirementResponse)
async def update_requirement(
    id: str,
    rid: str,
    data: RequirementUpdate,
    db: AsyncSession = Depends(get_db),
) -> RequirementResponse:
    stmt = select(Requirement).where(
        Requirement.id == rid, Requirement.project_id == id
    )
    result = await db.execute(stmt)
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement '{rid}' not found for project '{id}'",
        )

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(req, field, val)
    req.user_edited = True

    await db.commit()
    await db.refresh(req)
    return req


@router.patch("/projects/{id}/questions/{qid}", response_model=ResearchQuestionResponse)
async def update_question(
    id: str,
    qid: str,
    data: ResearchQuestionUpdate,
    db: AsyncSession = Depends(get_db),
) -> ResearchQuestionResponse:
    stmt = select(ResearchQuestion).where(
        ResearchQuestion.id == qid, ResearchQuestion.project_id == id
    )
    result = await db.execute(stmt)
    rq = result.scalar_one_or_none()
    if not rq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research question '{qid}' not found for project '{id}'",
        )

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(rq, field, val)

    await db.commit()
    await db.refresh(rq)
    return rq
