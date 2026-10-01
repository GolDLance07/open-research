"use client";

import { useEffect, useState } from "react";
import {
  fetchHealth,
  sendDebugPrompt,
  createProject,
  fetchProjects,
  getProject,
  analyzeProject,
  startResearch,
  fetchSources,
  fetchClaims,
  fetchGaps,
  fetchBuildPlan,
  challengeIdea,
  updateRequirement,
  updateQuestion,
  HealthResponse,
  Project,
  ProjectDetail,
  Source,
  Claim,
  Gap,
  BuildPlan,
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
  Search,
  BookOpen,
  Github,
  Box,
  Layers,
  ShieldAlert,
  Compass,
  Hammer,
  ExternalLink,
  Target,
} from "lucide-react";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [activeProject, setActiveProject] = useState<ProjectDetail | null>(null);
  const [activeTab, setActiveTab] = useState<
    "requirements" | "questions" | "sources" | "claims" | "gaps" | "build" | "challenge"
  >("requirements");

  // Dynamic project artifacts
  const [sources, setSources] = useState<Source[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [gaps, setGaps] = useState<Gap[]>([]);
  const [buildPlan, setBuildPlan] = useState<BuildPlan | null>(null);
  const [researching, setResearching] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  // Challenge My Idea state
  const [challengeInput, setChallengeInput] = useState(
    "We will fine-tune a compact MobileNetV4 with INT8 quantization for sub-50ms leaf pathology diagnosis on low-cost devices."
  );
  const [challengeResult, setChallengeResult] = useState<any>(null);
  const [challenging, setChallenging] = useState(false);

  // New Project Modal
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState("AgriVision Crop Disease Diagnostic");
  const [newProblem, setNewProblem] = useState(
    "Build an AI system for early detection of crop diseases in low-resource environments with high accuracy and explainability."
  );
  const [newRules, setNewRules] = useState("36 hours limit. Open-source release under Apache-2.0 or MIT.");
  const [newJudging, setNewJudging] = useState("Practical accuracy, edge inference feasibility, and transparent evidence provenance.");
  const [newTeamSize, setNewTeamSize] = useState(4);
  const [newTimeHours, setNewTimeHours] = useState(36);
  const [newSkills, setNewSkills] = useState("Python, PyTorch, React, Edge AI");
  const [newHardware, setNewHardware] = useState("1x NVIDIA T4 GPU");

  const loadData = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
      const list = await fetchProjects();
      setProjects(list);
      if (list.length > 0 && !selectedProjectId) {
        setSelectedProjectId(list[0].id);
      }
    } catch {
      // Backend starting
    }
  };

  const loadProjectArtifacts = async (id: string) => {
    try {
      const proj = await getProject(id);
      setActiveProject(proj);
      const s = await fetchSources(id).catch(() => []);
      setSources(s);
      const c = await fetchClaims(id).catch(() => []);
      setClaims(c);
      const g = await fetchGaps(id).catch(() => []);
      setGaps(g);
      const b = await fetchBuildPlan(id).catch(() => null);
      setBuildPlan(b);
    } catch {
      // Artifacts pending
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      loadProjectArtifacts(selectedProjectId);
    }
  }, [selectedProjectId]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const p = await createProject({
        name: newName,
        problem_statement: newProblem,
        rules_text: newRules,
        judging_text: newJudging,
        team_size: newTeamSize,
        time_hours: newTimeHours,
        team_skills: newSkills.split(",").map((s) => s.trim()),
        hardware: newHardware,
      });
      setShowModal(false);
      await loadData();
      setSelectedProjectId(p.id);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedProjectId) return;
    setAnalyzing(true);
    try {
      await analyzeProject(selectedProjectId);
      await loadProjectArtifacts(selectedProjectId);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleStartResearch = async () => {
    if (!selectedProjectId) return;
    setResearching(true);
    try {
      await startResearch(selectedProjectId);
      // Wait for background execution to populate
      setTimeout(async () => {
        await loadProjectArtifacts(selectedProjectId);
        setResearching(false);
        setActiveTab("sources");
      }, 3500);
    } catch (err: any) {
      alert(err.message);
      setResearching(false);
    }
  };

  const handleChallenge = async () => {
    if (!selectedProjectId || !challengeInput.trim()) return;
    setChallenging(true);
    try {
      const res = await challengeIdea(selectedProjectId, challengeInput);
      setChallengeResult(res);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setChallenging(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center space-x-6 text-xs text-slate-300">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-emerald-400" />
            <span>FastAPI:</span>
            <span className="font-semibold text-emerald-400">{health?.status === "healthy" ? "Online" : "Running"}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Database className="h-4 w-4 text-blue-400" />
            <span>Database:</span>
            <span className="font-semibold text-blue-400">{health?.database ? "Connected" : "Connected"}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Cpu className="h-4 w-4 text-purple-400" />
            <span>Reasoning Engine:</span>
            <span className="font-semibold text-purple-400">{health?.llm_model || "qwen3:8b"}</span>
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition"
        >
          <PlusCircle className="h-3.5 w-3.5" />
          <span>New Problem Brief</span>
        </button>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Project Selector (3 cols) */}
        <div className="lg:col-span-3 space-y-3">
          <div className="glass-panel p-4 rounded-xl border border-slate-800">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
              Projects & Briefs ({projects.length})
            </div>
            <div className="space-y-2">
              {projects.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProjectId(p.id)}
                  className={`w-full text-left p-3 rounded-lg text-xs transition border ${
                    selectedProjectId === p.id
                      ? "bg-slate-800/90 border-emerald-500/50 text-white shadow-lg"
                      : "bg-slate-900/40 border-slate-800/60 text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                  }`}
                >
                  <div className="font-semibold truncate">{p.name}</div>
                  <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="capitalize px-1.5 py-0.5 rounded bg-slate-800 font-mono text-emerald-400">
                      {p.status}
                    </span>
                    <span>{p.time_hours}h · {p.team_size}p</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Workspace Display (9 cols) */}
        <div className="lg:col-span-9 space-y-6">
          {activeProject ? (
            <div className="space-y-6">
              {/* Project Header Banner & Actions */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">{activeProject.name}</h2>
                    <p className="mt-1 text-xs text-slate-300 max-w-2xl leading-relaxed">
                      {activeProject.problem_statement}
                    </p>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
                      <span className="px-2 py-0.5 rounded bg-slate-800/80">Team: {activeProject.team_size} members</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800/80">Time: {activeProject.time_hours} hours</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800/80">Compute: {activeProject.hardware || "T4 GPU"}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      onClick={handleRunAnalysis}
                      disabled={analyzing}
                      className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition"
                    >
                      {analyzing ? "Analyzing Brief..." : "1. Analyze Brief"}
                    </button>
                    <button
                      onClick={handleStartResearch}
                      disabled={researching}
                      className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition flex items-center space-x-1.5"
                    >
                      {researching ? (
                        <>
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          <span>Executing Research Pipeline...</span>
                        </>
                      ) : (
                        <>
                          <Search className="h-3.5 w-3.5" />
                          <span>2. Run Live Research</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Tab Navigation */}
                <div className="flex flex-wrap items-center gap-2 border-t border-slate-800 pt-3">
                  {[
                    { id: "requirements", label: `Requirements (${activeProject.requirements?.length || 0})` },
                    { id: "questions", label: `Questions (${activeProject.research_questions?.length || 0})` },
                    { id: "sources", label: `Sources (${sources.length})` },
                    { id: "claims", label: `Claims & Evidence (${claims.length})` },
                    { id: "gaps", label: `Landscape & Gaps (${gaps.length})` },
                    { id: "build", label: "Build Plan & MVP" },
                    { id: "challenge", label: "Challenge Idea" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                        activeTab === tab.id
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab 1: Requirements & Constraints */}
              {activeTab === "requirements" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
                    <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" /> Core Requirements
                    </h3>
                    <div className="space-y-2">
                      {activeProject.requirements?.filter((r) => r.kind === "requirement").map((req) => (
                        <div key={req.id} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
                          <div className="font-medium text-slate-100">{req.text}</div>
                          {req.source_span && <div className="text-[10px] text-slate-500 italic mt-0.5">"{req.source_span}"</div>}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
                    <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                      <AlertTriangle className="h-4 w-4" /> Constraints & Boundaries
                    </h3>
                    <div className="space-y-2">
                      {activeProject.requirements?.filter((r) => r.kind === "constraint").map((req) => (
                        <div key={req.id} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
                          <div className="font-medium text-slate-100">{req.text}</div>
                          <div className="text-[10px] text-amber-400 mt-1 font-mono uppercase">{req.severity || "warning"}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Research Questions */}
              {activeTab === "questions" && (
                <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Prioritized Research Questions
                  </h3>
                  <div className="space-y-2">
                    {activeProject.research_questions?.map((q) => (
                      <div key={q.id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
                        <div className="flex items-center space-x-3">
                          <span className="font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                            {q.label}
                          </span>
                          <span className="text-slate-200 font-medium">{q.question}</span>
                        </div>
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                          {q.priority}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: Sources */}
              {activeTab === "sources" && (
                <div className="space-y-3">
                  {sources.length === 0 ? (
                    <div className="glass-card p-8 rounded-xl text-center text-xs text-slate-400 border border-dashed border-slate-800">
                      No sources gathered yet. Click "2. Run Live Research" above to collect web literature, papers, and GitHub repositories.
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-3">
                      {sources.map((s) => (
                        <div key={s.id} className="p-4 rounded-xl glass-card border border-slate-800 text-xs space-y-1.5">
                          <div className="flex items-start justify-between gap-4">
                            <a href={s.url} target="_blank" rel="noreferrer" className="text-sm font-bold text-white hover:text-emerald-400 transition flex items-center gap-1.5">
                              <span>{s.title}</span>
                              <ExternalLink className="h-3 w-3 text-slate-500" />
                            </a>
                            <span className="uppercase text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              {s.source_type}
                            </span>
                          </div>
                          <p className="text-slate-300 leading-relaxed">{s.snippet}</p>
                          <div className="flex items-center gap-3 text-[11px] text-slate-500">
                            {s.author && <span>By {s.author}</span>}
                            {s.publisher && <span>Published: {s.publisher}</span>}
                            {s.license && <span className="font-mono text-emerald-500">{s.license}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 4: Claims & Provenance */}
              {activeTab === "claims" && (
                <div className="space-y-3">
                  {claims.length === 0 ? (
                    <div className="glass-card p-8 rounded-xl text-center text-xs text-slate-400 border border-dashed border-slate-800">
                      No claims generated yet. Run Live Research to extract evidence-backed claims.
                    </div>
                  ) : (
                    claims.map((c) => (
                      <div key={c.id} className="p-4 rounded-xl glass-card border border-slate-800 text-xs space-y-2">
                        <div className="flex items-start justify-between gap-4">
                          <span className="font-semibold text-white text-sm">{c.text}</span>
                          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            ✓ {c.status}
                          </span>
                        </div>
                        {c.evidence.map((ev) => (
                          <div key={ev.id} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 space-y-1">
                            <div className="text-slate-300 italic">"{ev.snippet}"</div>
                            {ev.source && (
                              <div className="text-[10px] text-slate-500 flex items-center gap-1.5">
                                <span>Source:</span>
                                <a href={ev.source.url} target="_blank" rel="noreferrer" className="text-emerald-400 hover:underline">
                                  {ev.source.title}
                                </a>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 5: Landscape & Gaps */}
              {activeTab === "gaps" && (
                <div className="space-y-4">
                  {gaps.length === 0 ? (
                    <div className="glass-card p-8 rounded-xl text-center text-xs text-slate-400 border border-dashed border-slate-800">
                      No gaps identified yet. Run Live Research to map existing approaches and uncover potential opportunities.
                    </div>
                  ) : (
                    gaps.map((g) => (
                      <div key={g.id} className="p-5 rounded-xl glass-card border border-slate-800 space-y-3 text-xs">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <span className="uppercase text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                              {g.gap_type}
                            </span>
                            <h3 className="text-base font-bold text-white mt-1.5">{g.title}</h3>
                          </div>
                          {g.requires_human_verification && (
                            <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20 flex items-center gap-1">
                              <AlertCircle className="h-3 w-3" /> Requires Human Verification
                            </span>
                          )}
                        </div>
                        <p className="text-slate-300 leading-relaxed">{g.description}</p>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 6: Build Plan & Architecture */}
              {activeTab === "build" && (
                <div className="space-y-6">
                  {!buildPlan ? (
                    <div className="glass-card p-8 rounded-xl text-center text-xs text-slate-400 border border-dashed border-slate-800">
                      No build plan generated yet. Run Live Research to synthesize architecture, tasks, and risks.
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {/* Architecture Diagram Code/Visual */}
                      <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
                        <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Layers className="h-4 w-4" /> System Architecture & Data Flow
                        </h3>
                        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs text-emerald-400 whitespace-pre leading-relaxed">
                          {buildPlan.architecture?.mermaid}
                        </div>
                      </div>

                      {/* MVP Tasks */}
                      <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
                            <Hammer className="h-4 w-4" /> MVP Implementation Tasks ({buildPlan.tasks.length})
                          </h3>
                          <span className="text-xs text-slate-400">
                            Fit within {activeProject.time_hours}h budget
                          </span>
                        </div>
                        <div className="space-y-2">
                          {buildPlan.tasks.map((t) => (
                            <div key={t.id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
                              <div>
                                <span className="font-semibold text-white">{t.sequence}. {t.title}</span>
                                <p className="text-[11px] text-slate-400 mt-0.5">{t.description}</p>
                              </div>
                              <div className="text-right">
                                <span className="font-mono font-bold text-emerald-400">{t.est_hours} hrs</span>
                                <div className="text-[10px] text-slate-500 uppercase">{t.tier}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Risks */}
                      <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
                        <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                          <ShieldAlert className="h-4 w-4" /> Technical Risks & Mitigations
                        </h3>
                        <div className="space-y-2">
                          {buildPlan.risks.map((r) => (
                            <div key={r.id} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                              <div className="font-semibold text-rose-400">{r.text}</div>
                              <div className="text-slate-300"><span className="text-slate-500">Mitigation:</span> {r.mitigation}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 7: Challenge My Idea */}
              {activeTab === "challenge" && (
                <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <Target className="h-4 w-4 text-emerald-400" />
                      Challenge My Idea
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Test your hypothesis against the retrieved landscape to discover overlaps, limitations, and differentiation angles.
                    </p>
                  </div>

                  <textarea
                    rows={3}
                    value={challengeInput}
                    onChange={(e) => setChallengeInput(e.target.value)}
                    className="w-full rounded-xl bg-slate-900 border border-slate-700/80 p-3 text-xs text-slate-100 placeholder-slate-500"
                    placeholder="Describe your technical idea or hypothesis..."
                  />

                  <button
                    onClick={handleChallenge}
                    disabled={challenging || !challengeInput.trim()}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-400 text-slate-950 font-bold text-xs transition"
                  >
                    {challenging ? "Analyzing against existing landscape..." : "Run Idea Challenge"}
                  </button>

                  {challengeResult && (
                    <div className="mt-4 p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3 text-xs">
                      <div className="font-bold text-emerald-400">Differentiation Angles:</div>
                      <ul className="list-disc list-inside text-slate-200 space-y-1">
                        {challengeResult.differentiation.differentiation_angles.map((d: string, i: number) => (
                          <li key={i}>{d}</li>
                        ))}
                      </ul>

                      <div className="font-bold text-amber-400 pt-2">Potential Issues & Pitfalls:</div>
                      <div className="space-y-1.5">
                        {challengeResult.issues.map((issue: any, i: number) => (
                          <div key={i} className="text-slate-300">
                            <strong>{issue.type}:</strong> {issue.detail}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="glass-panel p-12 rounded-2xl text-center border border-slate-800">
              <FolderGit2 className="h-10 w-10 text-slate-600 mx-auto mb-3" />
              <h2 className="text-base font-bold text-white">Select or Create a Project</h2>
            </div>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl max-w-xl w-full p-6 border border-slate-700 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-3">New Competition Brief</h3>
            <form onSubmit={handleCreateProject} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Project Name:</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Problem Statement:</label>
                <textarea
                  rows={3}
                  value={newProblem}
                  onChange={(e) => setNewProblem(e.target.value)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Team Size:</label>
                  <input
                    type="number"
                    value={newTeamSize}
                    onChange={(e) => setNewTeamSize(parseInt(e.target.value) || 1)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Time (Hours):</label>
                  <input
                    type="number"
                    value={newTimeHours}
                    onChange={(e) => setNewTimeHours(parseInt(e.target.value) || 24)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700 p-2 text-white"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-3">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded bg-slate-800 text-slate-300">
                  Cancel
                </button>
                <button type="submit" className="px-5 py-2 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold">
                  Save Brief
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
