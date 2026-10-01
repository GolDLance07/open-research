const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export interface HealthResponse {
  status: string;
  database: boolean;
  llm_provider: string;
  llm_model: string;
  llm_healthy: boolean;
}

export interface DebugLLMResponse {
  provider: string;
  model: string;
  response: string;
  prompt_tokens: number;
  completion_tokens: number;
  latency_ms: number;
}

export interface Requirement {
  id: string;
  project_id: string;
  kind: "requirement" | "constraint" | "deliverable" | "judging_criterion";
  text: str;
  source_span?: string | null;
  priority?: string | null;
  severity?: string | null;
  user_edited: boolean;
  position: number;
}

type str = string;

export interface ResearchQuestion {
  id: string;
  project_id: string;
  label: string;
  question: string;
  priority: "high" | "medium" | "low";
  status: string;
  position: number;
}

export interface Project {
  id: string;
  name: string;
  competition_name?: string;
  problem_statement: string;
  rules_text?: string;
  judging_text?: string;
  team_size: number;
  team_skills: string[];
  time_hours: number;
  hardware?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  requirements: Requirement[];
  research_questions: ResearchQuestion[];
}

export interface ProjectCreate {
  name: string;
  competition_name?: string;
  problem_statement: string;
  rules_text?: string;
  judging_text?: string;
  team_size?: number;
  team_skills?: string[];
  time_hours?: number;
  hardware?: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function sendDebugPrompt(
  prompt: string,
  temperature = 0.2,
  thinking = false
): Promise<DebugLLMResponse> {
  const res = await fetch(`${API_BASE_URL}/debug/llm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, temperature, thinking }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      errorData?.error?.message || `LLM request failed: ${res.statusText}`
    );
  }
  return res.json();
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE_URL}/projects`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch projects: ${res.statusText}`);
  }
  return res.json();
}

export async function getProject(id: string): Promise<ProjectDetail> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to get project: ${res.statusText}`);
  }
  return res.json();
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const res = await fetch(`${API_BASE_URL}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      errorData?.error?.message || `Failed to create project: ${res.statusText}`
    );
  }
  return res.json();
}

export async function analyzeProject(id: string): Promise<ProjectDetail> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/analyze`, {
    method: "POST",
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(
      errorData?.error?.message || `Failed to analyze project: ${res.statusText}`
    );
  }
  return res.json();
}

export async function updateRequirement(
  projectId: string,
  reqId: string,
  data: Partial<Requirement>
): Promise<Requirement> {
  const res = await fetch(
    `${API_BASE_URL}/projects/${projectId}/requirements/${reqId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) {
    throw new Error("Failed to update requirement");
  }
  return res.json();
}

export async function updateQuestion(
  projectId: string,
  qId: string,
  data: Partial<ResearchQuestion>
): Promise<ResearchQuestion> {
  const res = await fetch(
    `${API_BASE_URL}/projects/${projectId}/questions/${qId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) {
    throw new Error("Failed to update research question");
  }
  return res.json();
}
