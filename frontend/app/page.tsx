"use client";

import { useEffect, useState } from "react";
import {
  fetchHealth,
  sendDebugPrompt,
  createProject,
  fetchProjects,
  HealthResponse,
  DebugLLMResponse,
  Project,
} from "@/lib/api";
import {
  Activity,
  Cpu,
  Database,
  Send,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  FolderGit2,
  RefreshCw,
  Clock,
  Zap,
} from "lucide-react";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState<string | null>(null);

  // Debug LLM state
  const [prompt, setPrompt] = useState(
    "Analyze the problem statement: 'Build an AI system for early detection of crop diseases in low-resource environments.'"
  );
  const [temperature, setTemperature] = useState(0.2);
  const [thinking, setThinking] = useState(false);
  const [llmLoading, setLlmLoading] = useState(false);
  const [llmResult, setLlmResult] = useState<DebugLLMResponse | null>(null);
  const [llmError, setLlmError] = useState<string | null>(null);

  // Projects state
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectLoading, setProjectLoading] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [problemStatement, setProblemStatement] = useState("");

  const loadHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err: any) {
      setHealthError(err.message || "Failed to connect to backend");
    } finally {
      setHealthLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const list = await fetchProjects();
      setProjects(list);
    } catch {
      // Ignored if backend not ready
    }
  };

  useEffect(() => {
    loadHealth();
    loadProjects();
  }, []);

  const handleAskModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || llmLoading) return;

    setLlmLoading(true);
    setLlmError(null);
    try {
      const res = await sendDebugPrompt(prompt, temperature, thinking);
      setLlmResult(res);
    } catch (err: any) {
      setLlmError(err.message || "LLM request failed");
    } finally {
      setLlmLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim() || !problemStatement.trim() || projectLoading) return;

    setProjectLoading(true);
    try {
      await createProject({
        name: projectName,
        problem_statement: problemStatement,
        team_size: 4,
        time_hours: 36,
        team_skills: ["Python", "PyTorch", "React"],
      });
      setProjectName("");
      setProblemStatement("");
      await loadProjects();
    } catch (err: any) {
      alert(err.message || "Failed to create project");
    } finally {
      setProjectLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
            <span>Phase 0: Foundation Verification</span>
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Verifying the full stack flow: Next.js → FastAPI → Qwen3-8B Reasoning → Response.
          </p>
        </div>

        <button
          onClick={loadHealth}
          className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${healthLoading ? "animate-spin" : ""}`}
          />
          <span>Refresh System Health</span>
        </button>
      </div>

      {/* Health & Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Backend API status */}
        <div className="glass-card rounded-xl p-5 border border-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Backend API
            </span>
            <Activity className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-center gap-2">
            {health?.status === "healthy" ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            ) : healthLoading ? (
              <RefreshCw className="h-5 w-5 text-amber-400 animate-spin" />
            ) : (
              <AlertCircle className="h-5 w-5 text-rose-400" />
            )}
            <span className="text-xl font-bold text-white">
              {healthLoading
                ? "Connecting..."
                : health?.status === "healthy"
                ? "Online & Healthy"
                : health?.status || "Offline"}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            {healthError || "FastAPI on port 8000"}
          </p>
        </div>

        {/* Database status */}
        <div className="glass-card rounded-xl p-5 border border-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Database
            </span>
            <Database className="h-4 w-4 text-blue-400" />
          </div>
          <div className="mt-3 flex items-center gap-2">
            {health?.database ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            ) : healthLoading ? (
              <RefreshCw className="h-5 w-5 text-amber-400 animate-spin" />
            ) : (
              <AlertCircle className="h-5 w-5 text-rose-400" />
            )}
            <span className="text-xl font-bold text-white">
              {healthLoading
                ? "Connecting..."
                : health?.database
                ? "Connected"
                : "Disconnected"}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            SQLAlchemy async session active
          </p>
        </div>

        {/* LLM Provider status */}
        <div className="glass-card rounded-xl p-5 border border-slate-800/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              LLM Engine
            </span>
            <Cpu className="h-4 w-4 text-purple-400" />
          </div>
          <div className="mt-3 flex items-center gap-2">
            {health?.llm_healthy ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            ) : healthLoading ? (
              <RefreshCw className="h-5 w-5 text-amber-400 animate-spin" />
            ) : (
              <AlertCircle className="h-5 w-5 text-amber-400" />
            )}
            <span className="text-xl font-bold text-white">
              {healthLoading
                ? "Detecting..."
                : `${health?.llm_model || "qwen3:8b"}`}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Provider: {health?.llm_provider || "mock"}
          </p>
        </div>
      </div>

      {/* Main Interactive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Ask the Model Playground (7 cols) */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-emerald-400" />
              <h2 className="text-lg font-semibold text-white">
                Ask the Model Playground
              </h2>
            </div>
            <span className="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400">
              POST /api/v1/debug/llm
            </span>
          </div>

          <form onSubmit={handleAskModel} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Research Prompt / Problem Statement:
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                className="w-full rounded-xl bg-slate-900/90 border border-slate-700/80 p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                placeholder="Enter a prompt to test model reasoning..."
                required
              />
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
              <div className="flex items-center space-x-4 text-xs">
                <div>
                  <label className="text-slate-400 mr-2">Temperature:</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-16 rounded bg-slate-900 border border-slate-700 px-2 py-1 text-white text-xs"
                  />
                </div>

                <label className="flex items-center space-x-2 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={thinking}
                    onChange={(e) => setThinking(e.target.checked)}
                    className="rounded border-slate-700 bg-slate-900 text-emerald-500 focus:ring-0"
                  />
                  <span>Thinking Mode</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={llmLoading || !prompt.trim()}
                className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
              >
                {llmLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span>Reasoning...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    <span>Run Verification</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Model Response Box */}
          {llmError && (
            <div className="mt-5 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
              <strong>Error:</strong> {llmError}
            </div>
          )}

          {llmResult && (
            <div className="mt-6 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold text-emerald-400">
                  Model Output ({llmResult.provider} / {llmResult.model})
                </span>
                <div className="flex items-center space-x-3">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {llmResult.latency_ms} ms
                  </span>
                  <span className="flex items-center gap-1">
                    <Zap className="h-3.5 w-3.5" />
                    {llmResult.prompt_tokens + llmResult.completion_tokens} tokens
                  </span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                {llmResult.response}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Database Project Seed / Persistence Test (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel rounded-2xl p-6 border border-slate-800/80">
            <div className="flex items-center space-x-2 mb-4">
              <FolderGit2 className="h-5 w-5 text-blue-400" />
              <h2 className="text-lg font-semibold text-white">
                Project Database Test
              </h2>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Create a sample research project to verify SQLAlchemy async write and read operations.
            </p>

            <form onSubmit={handleCreateProject} className="space-y-3">
              <div>
                <input
                  type="text"
                  placeholder="Project Name (e.g. AgriAI Crop Disease)"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <textarea
                  placeholder="Problem Statement (min 20 characters)..."
                  value={problemStatement}
                  onChange={(e) => setProblemStatement(e.target.value)}
                  rows={2}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={projectLoading || !projectName.trim()}
                className="w-full py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition disabled:opacity-50"
              >
                {projectLoading ? "Saving..." : "Create Project in Database"}
              </button>
            </form>

            <div className="mt-5 border-t border-slate-800 pt-4">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>Existing Projects in DB</span>
                <span>{projects.length} recorded</span>
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {projects.length === 0 ? (
                  <p className="text-xs text-slate-600 italic">No projects yet.</p>
                ) : (
                  projects.map((p) => (
                    <div
                      key={p.id}
                      className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs"
                    >
                      <div className="font-semibold text-slate-200">{p.name}</div>
                      <div className="text-slate-500 truncate mt-0.5">
                        {p.problem_statement}
                      </div>
                      <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-emerald-400">
                          {p.status}
                        </span>
                        <span>{p.time_hours}h · {p.team_size} members</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
