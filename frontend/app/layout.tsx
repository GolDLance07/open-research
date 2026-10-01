import type { Metadata } from "next";
import "./globals.css";
import { Sparkles, Terminal, BookOpen, Layers } from "lucide-react";

export const metadata: Metadata = {
  title: "OpenResearch — Evidence-Backed Build Strategy",
  description:
    "AI research workspace turning problem statements into evidence-backed build strategies powered by open-weight models.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 flex flex-col min-h-screen">
        <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-emerald-500 to-green-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Sparkles className="h-5 w-5 text-slate-950 stroke-[2.5]" />
              </div>
              <div>
                <span className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-slate-200 to-slate-400">
                  OpenResearch
                </span>
                <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  v1.0 MVP
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2 text-xs px-3 py-1.5 rounded-md bg-slate-900/80 border border-slate-800 text-slate-300">
                <Terminal className="h-3.5 w-3.5 text-emerald-400" />
                <span>Reasoning:</span>
                <span className="font-semibold text-white">Qwen3-8B</span>
              </div>

              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-xs px-3 py-1.5 rounded-md bg-slate-800/60 hover:bg-slate-700/80 transition-colors text-slate-200 flex items-center space-x-1.5"
              >
                <BookOpen className="h-3.5 w-3.5 text-slate-400" />
                <span>API Docs</span>
              </a>
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
          <p>
            OpenResearch — Powered by open-weight reasoning. Licensed under Apache 2.0.
          </p>
        </footer>
      </body>
    </html>
  );
}
