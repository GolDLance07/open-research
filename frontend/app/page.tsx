"use client";

import { useEffect, useState } from "react";
import {
  fetchHealth,
  sendDebugPrompt,
  createProject,
  fetchProjects,
  getProject,
  analyzeProject,
  updateRequirement,
  updateQuestion,
  HealthResponse,
  DebugLLMResponse,
  Project,
  ProjectDetail,
  Requirement,
  ResearchQuestion,
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
  PlusCircle,
  FileText,
  AlertTriangle,
  HelpCircle,
  CheckCheck,
  Edit2,
  Clock,
  Zap,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Projects & Navigation
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [activeProject, setActiveProject] = useState<ProjectDetail | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<"requirements" | "questions" | "debug">(
    "requirements"
  );

  // New Project Form
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newName, setNewName] = useState("AgriVision Crop Disease Detector");
  const [newProblem, setNewProblem] = useState(
    "Build an AI system for early detection of crop diseases in low-resource environments with high accuracy and explainability."
  );
  const [newRules, setNewRules] = useState(
    "Max 36 hours. All code must be open source under an OSI approved license."
  );
  const [newJudging, setNewJudging] = useState(
    "Evaluation based on practical accuracy, edge inference feasibility, and transparent evidence provenance."
  );
  const [newTeamSize, setNewTeamSize] = useState(4);
  const [newSkills, setNewSkills] = useState("Python, PyTorch, React, Edge ML");
  const [newTimeHours, setNewTimeHours] = useState(36);
  const [newHardware, setNewHardware] = useState("1x NVIDIA T4 (16GB VRAM)");
  const [createLoading, setCreateLoading] = useState(false);

  // Debug LLM
  const [debugPrompt, setDebugPrompt] = useState(
    "Analyze the problem statement: 'Build an AI system for early detection of crop diseases in low-resource environments.'"
  );
  const [debugResult, setDebugResult] = useState<DebugLLMResponse | null>(null);
  const [debugLoading, setDebugLoading] = useState(false);

  const loadHealth = async () => {
    setHealthLoading(true);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch {
      // Degraded
    } finally {
      setHealthLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const list = await fetchProjects();
      setProjects(list);
      if (list.length > 0 && !selectedProjectId) {
        setSelectedProjectId(list[0].id);
      }
    } catch {
      // Backend not ready
    }
  };

  const loadSelectedProject = async (id: string) => {
    try {
      const proj = await getProject(id);
      setActiveProject(proj);
    } catch (err: any) {
      alert(err.message || "Failed to load project details");
    }
  };

  useEffect(() => {
    loadHealth();
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadSelectedProject(selectedProjectId);
    }
  }, [selectedProjectId]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newProblem.trim()) return;

    setCreateLoading(true);
    try {
      const created = await createProject({
        name: newName,
        problem_statement: newProblem,
        rules_text: newRules,
        judging_text: newJudging,
        team_size: newTeamSize,
        team_skills: newSkills.split(",").map((s) => s.trim()),
        time_hours: newTimeHours,
        hardware: newHardware,
      });
      setShowCreateModal(false);
      await loadProjects();
      setSelectedProjectId(created.id);
    } catch (err: any) {
      alert(err.message || "Failed to create project");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedProjectId || analyzing) return;
    setAnalyzing(true);
    try {
      const updated = await analyzeProject(selectedProjectId);
      setActiveProject(updated);
      await loadProjects();
    } catch (err: any) {
      alert(err.message || "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleUpdateReqPriority = async (req: Requirement) => {
    if (!selectedProjectId) return;
    const nextPriority =
      req.priority === "high" ? "medium" : req.priority === "medium" ? "low" : "high";
    try {
      const updated = await updateRequirement(selectedProjectId, req.id, {
        priority: nextPriority,
      });
      if (activeProject) {
        setActiveProject({
          ...activeProject,
          requirements: activeProject.requirements.map((r) =>
            r.id === req.id ? updated : r
          ),
        });
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleUpdateQuestionPriority = async (q: ResearchQuestion) => {
    if (!selectedProjectId) return;
    const nextPriority =
      q.priority === "high" ? "medium" : q.priority === "medium" ? "low" : "high";
    try {
      const updated = await updateQuestion(selectedProjectId, q.id, {
        priority: nextPriority,
      });
      if (activeProject) {
        setActiveProject({
          ...activeProject,
          research_questions: activeProject.research_questions.map((item) =>
            item.id === q.id ? updated : item
          ),
        });
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRunDebug = async () => {
    if (!debugPrompt.trim() || debugLoading) return;
    setDebugLoading(true);
    try {
      const res = await sendDebugPrompt(debugPrompt);
      setDebugResult(res);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setDebugLoading(false);
    }
  };

  const requirementsList =
    activeProject?.requirements.filter((r) => r.kind === "requirement") || [];
  const constraintsList =
    activeProject?.requirements.filter((r) => r.kind === "constraint") || [];
  const deliverablesList =
    activeProject?.requirements.filter((r) => r.kind === "deliverable") || [];
  const judgingList =
    activeProject?.requirements.filter((r) => r.kind === "judging_criterion") || [];

  return (
    <div className="space-y-6">
      {/* System Status Strip */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl glass-card border border-slate-800/80">
        <div className="flex items-center space-x-6 text-xs text-slate-300">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-emerald-400" />
            <span>FastAPI:</span>
            <span className="font-semibold text-emerald-400">
              {health?.status === "healthy" ? "Online" : "Connecting"}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <Database className="h-4 w-4 text-blue-400" />
            <span>DB:</span>
            <span className="font-semibold text-blue-400">
              {health?.database ? "Connected" : "Standby"}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <Cpu className="h-4 w-4 text-purple-400" />
            <span>Reasoning Engine:</span>
            <span className="font-semibold text-purple-400">
              {health?.llm_model || "qwen3:8b"} ({health?.llm_provider || "mock"})
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs transition shadow-md shadow-emerald-500/10"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            <span>New Brief / Project</span>
          </button>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Project Selector (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <div className="flex items-center justify-between mb-3 text-xs font-semibold text-slate-300 uppercase tracking-wider">
              <span>Your Projects</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-normal">
                {projects.length}
              </span>
            </div>

            <div className="space-y-2">
              {projects.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500">
                  No projects yet. Click "New Brief / Project" to start.
                </div>
              ) : (
                projects.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedProjectId(p.id)}
                    className={`w-full text-left p-3 rounded-lg text-xs transition border ${
                      selectedProjectId === p.id
                        ? "bg-slate-800/90 border-emerald-500/50 text-white shadow-lg"
                        : "bg-slate-900/50 border-slate-800/60 text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                    }`}
                  >
                    <div className="font-semibold truncate">{p.name}</div>
                    <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
                      <span
                        className={`capitalize px-1.5 py-0.5 rounded font-mono ${
                          p.status === "analyzed"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {p.status}
                      </span>
                      <span>{p.time_hours}h · {p.team_size}p</span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Project Analysis & Detail View (9 cols) */}
        <div className="lg:col-span-9 space-y-6">
          {activeProject ? (
            <div className="space-y-6">
              {/* Project Header Banner */}
              <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-xl">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <h2 className="text-2xl font-bold text-white tracking-tight">
                        {activeProject.name}
                      </h2>
                      <span
                        className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                          activeProject.status === "analyzed"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                            : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                        }`}
                      >
                        {activeProject.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-slate-300 leading-relaxed max-w-3xl">
                      {activeProject.problem_statement}
                    </p>
                    <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                      <span>Team: {activeProject.team_size} members</span>
                      <span>•</span>
                      <span>Time: {activeProject.time_hours} hours</span>
                      <span>•</span>
                      <span>Compute: {activeProject.hardware || "Standard"}</span>
                      <span>•</span>
                      <span>Skills: {activeProject.team_skills.join(", ")}</span>
                    </div>
                  </div>

                  <button
                    onClick={handleRunAnalysis}
                    disabled={analyzing}
                    className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-400 hover:to-green-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-emerald-500/20 disabled:opacity-50 flex-shrink-0"
                  >
                    {analyzing ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span>Analyzing Brief with Qwen...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        <span>Run Requirement Analysis</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Tabs */}
                <div className="flex items-center space-x-4 border-b border-slate-800 mt-6 pt-2">
                  <button
                    onClick={() => setActiveTab("requirements")}
                    className={`pb-3 text-xs font-semibold tracking-wide transition border-b-2 flex items-center space-x-2 ${
                      activeTab === "requirements"
                        ? "border-emerald-400 text-white"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <CheckCheck className="h-4 w-4" />
                    <span>Requirements & Constraints ({activeProject.requirements.length})</span>
                  </button>

                  <button
                    onClick={() => setActiveTab("questions")}
                    className={`pb-3 text-xs font-semibold tracking-wide transition border-b-2 flex items-center space-x-2 ${
                      activeTab === "questions"
                        ? "border-emerald-400 text-white"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <HelpCircle className="h-4 w-4" />
                    <span>Research Questions ({activeProject.research_questions.length})</span>
                  </button>

                  <button
                    onClick={() => setActiveTab("debug")}
                    className={`pb-3 text-xs font-semibold tracking-wide transition border-b-2 flex items-center space-x-2 ${
                      activeTab === "debug"
                        ? "border-emerald-400 text-white"
                        : "border-transparent text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <Cpu className="h-4 w-4" />
                    <span>Model Reasoning Tester</span>
                  </button>
                </div>
              </div>

              {/* Tab 1: Requirements & Constraints */}
              {activeTab === "requirements" && (
                <div className="space-y-6">
                  {activeProject.requirements.length === 0 ? (
                    <div className="glass-card rounded-xl p-8 text-center border border-dashed border-slate-800">
                      <Sparkles className="h-8 w-8 text-emerald-400 mx-auto mb-2 opacity-80" />
                      <h3 className="text-sm font-semibold text-white">
                        Brief Not Analyzed Yet
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                        Click "Run Requirement Analysis" to run RequirementAnalyzer and
                        extract requirements, constraints, deliverables, and criteria.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Functional Requirements */}
                      <div className="glass-card rounded-xl p-5 border border-slate-800/80 space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                            <CheckCircle2 className="h-4 w-4" />
                            <span>Core Requirements ({requirementsList.length})</span>
                          </h3>
                        </div>
                        <div className="space-y-2.5">
                          {requirementsList.map((req) => (
                            <div
                              key={req.id}
                              className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <span className="text-slate-100 font-medium leading-relaxed">
                                  {req.text}
                                </span>
                                <button
                                  onClick={() => handleUpdateReqPriority(req)}
                                  className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition flex-shrink-0"
                                  title="Click to toggle priority"
                                >
                                  {req.priority || "medium"}
                                </button>
                              </div>
                              {req.source_span && (
                                <div className="text-[11px] text-slate-500 italic">
                                  "{req.source_span}"
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Constraints & Limits */}
                      <div className="glass-card rounded-xl p-5 border border-slate-800/80 space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                            <AlertTriangle className="h-4 w-4" />
                            <span>Constraints & Warnings ({constraintsList.length})</span>
                          </h3>
                        </div>
                        <div className="space-y-2.5">
                          {constraintsList.map((req) => (
                            <div
                              key={req.id}
                              className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1.5"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <span className="text-slate-100 font-medium leading-relaxed">
                                  {req.text}
                                </span>
                                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 flex-shrink-0">
                                  {req.severity || "warning"}
                                </span>
                              </div>
                              {req.source_span && (
                                <div className="text-[11px] text-slate-500 italic">
                                  "{req.source_span}"
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Deliverables */}
                      <div className="glass-card rounded-xl p-5 border border-slate-800/80 space-y-3">
                        <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
                          <FileText className="h-4 w-4" />
                          <span>Deliverables ({deliverablesList.length})</span>
                        </h3>
                        <div className="space-y-2.5">
                          {deliverablesList.map((req) => (
                            <div
                              key={req.id}
                              className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs"
                            >
                              <span className="text-slate-100 font-medium">
                                {req.text}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Judging Criteria */}
                      <div className="glass-card rounded-xl p-5 border border-slate-800/80 space-y-3">
                        <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
                          <ShieldAlert className="h-4 w-4" />
                          <span>Judging Criteria ({judgingList.length})</span>
                        </h3>
                        <div className="space-y-2.5">
                          {judgingList.map((req) => (
                            <div
                              key={req.id}
                              className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs"
                            >
                              <span className="text-slate-100 font-medium">
                                {req.text}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Research Questions */}
              {activeTab === "questions" && (
                <div className="space-y-4">
                  {activeProject.research_questions.length === 0 ? (
                    <div className="glass-card rounded-xl p-8 text-center border border-dashed border-slate-800">
                      <HelpCircle className="h-8 w-8 text-purple-400 mx-auto mb-2 opacity-80" />
                      <h3 className="text-sm font-semibold text-white">
                        No Research Questions Yet
                      </h3>
                      <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                        Run Requirement Analysis to have ResearchPlanner generate
                        targeted questions across existing approaches, datasets, and repos.
                      </p>
                    </div>
                  ) : (
                    <div className="glass-card rounded-xl p-5 border border-slate-800/80 space-y-3">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                          Prioritized Research Questions (RQ1–RQ{activeProject.research_questions.length})
                        </h3>
                        <span className="text-xs text-slate-500">
                          Click priority badge to reprioritize
                        </span>
                      </div>

                      <div className="space-y-2.5">
                        {activeProject.research_questions.map((q) => (
                          <div
                            key={q.id}
                            className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start justify-between gap-4 text-xs"
                          >
                            <div className="flex items-start space-x-3">
                              <span className="font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex-shrink-0">
                                {q.label}
                              </span>
                              <span className="text-slate-200 font-medium leading-relaxed">
                                {q.question}
                              </span>
                            </div>

                            <button
                              onClick={() => handleUpdateQuestionPriority(q)}
                              className={`text-[10px] uppercase font-mono px-2.5 py-1 rounded font-semibold transition flex-shrink-0 border ${
                                q.priority === "high"
                                  ? "bg-rose-500/10 text-rose-400 border-rose-500/20 hover:bg-rose-500/20"
                                  : q.priority === "medium"
                                  ? "bg-amber-500/10 text-amber-400 border-amber-500/20 hover:bg-amber-500/20"
                                  : "bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20"
                              }`}
                            >
                              {q.priority}
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Model Reasoning Playground */}
              {activeTab === "debug" && (
                <div className="glass-card rounded-xl p-6 border border-slate-800/80 space-y-4">
                  <h3 className="text-sm font-semibold text-white">
                    Direct Reasoning Probe (Qwen3-8B)
                  </h3>
                  <textarea
                    rows={3}
                    value={debugPrompt}
                    onChange={(e) => setDebugPrompt(e.target.value)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  />
                  <div className="flex justify-end">
                    <button
                      onClick={handleRunDebug}
                      disabled={debugLoading}
                      className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition"
                    >
                      {debugLoading ? "Running..." : "Test Model Response"}
                    </button>
                  </div>
                  {debugResult && (
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-200 whitespace-pre-wrap">
                      {debugResult.response}
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
              <FolderGit2 className="h-10 w-10 text-slate-600 mx-auto mb-3" />
              <h2 className="text-lg font-bold text-white">No Project Selected</h2>
              <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                Select an existing project on the left or create a new brief to begin requirement analysis.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl max-w-2xl w-full p-6 border border-slate-700 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">
                New Project / Competition Brief
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Project / Competition Name:
                </label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2.5 text-xs text-slate-100"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Problem Statement:
                </label>
                <textarea
                  rows={3}
                  value={newProblem}
                  onChange={(e) => setNewProblem(e.target.value)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2.5 text-xs text-slate-100"
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Rules & Constraints:
                  </label>
                  <textarea
                    rows={2}
                    value={newRules}
                    onChange={(e) => setNewRules(e.target.value)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Judging Criteria:
                  </label>
                  <textarea
                    rows={2}
                    value={newJudging}
                    onChange={(e) => setNewJudging(e.target.value)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2 text-xs text-slate-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Team Size:
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={newTeamSize}
                    onChange={(e) => setNewTeamSize(parseInt(e.target.value) || 1)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Time Budget (Hours):
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="720"
                    value={newTimeHours}
                    onChange={(e) => setNewTimeHours(parseInt(e.target.value) || 24)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Hardware / Compute:
                  </label>
                  <input
                    type="text"
                    value={newHardware}
                    onChange={(e) => setNewHardware(e.target.value)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2 text-xs text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Team Skills (comma separated):
                </label>
                <input
                  type="text"
                  value={newSkills}
                  onChange={(e) => setNewSkills(e.target.value)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700/80 p-2 text-xs text-slate-100"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLoading}
                  className="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold transition shadow-lg shadow-emerald-500/20"
                >
                  {createLoading ? "Creating..." : "Save Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
