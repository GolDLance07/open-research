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
  text: string;
  source_span?: string | null;
  priority?: string | null;
  severity?: string | null;
  user_edited: boolean;
  position: number;
}

export interface ResearchQuestion {
  id: string;
  project_id: string;
  label: string;
  question: string;
  priority: "high" | "medium" | "low";
  status: string;
  position: number;
}

export interface Source {
  id: string;
  project_id: string;
  run_id?: string;
  title: string;
  url: string;
  canonical_url: string;
  source_type: "web" | "paper" | "repository" | "model" | "dataset";
  author?: string;
  publisher?: string;
  snippet: string;
  license?: string;
  relevance_note?: string;
  retrieved_at: string;
}

export interface Claim {
  id: string;
  text: string;
  status: "FACT" | "DIRECTLY_SUPPORTED" | "SYNTHESIS" | "INFERENCE" | "HYPOTHESIS";
  confidence: "low" | "medium" | "high";
  category?: string;
  critic_flags: string[];
  reasoning?: string;
  evidence: Array<{
    id: string;
    snippet: string;
    location?: string;
    verified: boolean;
    source?: {
      id: string;
      title: string;
      url: string;
      source_type: string;
    };
  }>;
}

export interface Gap {
  id: string;
  title: string;
  description: string;
  gap_type: "limitation" | "contradiction" | "underexplored" | "opportunity";
  classification: string;
  confidence: string;
  requires_human_verification: boolean;
  claims_count: number;
  claim_ids: string[];
}

export interface BuildPlan {
  id: string;
  title: string;
  summary: string;
  feasibility: Record<string, any>;
  architecture?: {
    components: Array<{ name: string; tech: string; role: string }>;
    data_flow: Array<{ from: string; to: string; desc: string }>;
    tech_stack: Record<string, string>;
    mermaid: string;
  };
  tasks: Array<{
    id: string;
    tier: "mvp" | "stretch";
    sequence: number;
    title: string;
    description: string;
    est_hours: number;
    skill_tags: string[];
  }>;
  risks: Array<{
    id: string;
    text: string;
    severity: string;
    mitigation: string;
  }>;
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
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function sendDebugPrompt(prompt: string): Promise<DebugLLMResponse> {
  const res = await fetch(`${API_BASE_URL}/debug/llm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("LLM request failed");
  return res.json();
}

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE_URL}/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function getProject(id: string): Promise<ProjectDetail> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to get project");
  return res.json();
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const res = await fetch(`${API_BASE_URL}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function analyzeProject(id: string): Promise<ProjectDetail> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/analyze`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to analyze project");
  return res.json();
}

export async function startResearch(id: string): Promise<{ run_id: string }> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ max_cycles: 1 }),
  });
  if (!res.ok) throw new Error("Failed to start research");
  return res.json();
}

export async function fetchSources(id: string): Promise<Source[]> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/sources`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch sources");
  return res.json();
}

export async function fetchClaims(id: string): Promise<Claim[]> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/claims`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch claims");
  return res.json();
}

export async function fetchGaps(id: string): Promise<Gap[]> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/gaps`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch gaps");
  return res.json();
}

export async function fetchBuildPlan(id: string): Promise<BuildPlan> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/build-plan`, { cache: "no-store" });
  if (!res.ok) throw new Error("Build plan not ready yet");
  return res.json();
}

export async function challengeIdea(id: string, ideaText: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/projects/${id}/challenge-idea`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idea_text: ideaText }),
  });
  if (!res.ok) throw new Error("Challenge idea request failed");
  return res.json();
}

export async function updateRequirement(projectId: string, reqId: string, data: Partial<Requirement>) {
  const res = await fetch(`${API_BASE_URL}/projects/${projectId}/requirements/${reqId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateQuestion(projectId: string, qId: string, data: Partial<ResearchQuestion>) {
  const res = await fetch(`${API_BASE_URL}/projects/${projectId}/questions/${qId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}
