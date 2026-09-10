import Link from "next/link";
import { Flame, ShieldAlert, DollarSign, Target, ChevronRight, Zap, Plug, FileText, CheckCircle2, Award } from "lucide-react";

export default function Home() {
  return (
    <main className="flex-1 flex flex-col items-center justify-center px-4 sm:px-8 py-12 lg:py-16 text-center max-w-6xl mx-auto space-y-12">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-center gap-3">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs sm:text-sm font-medium backdrop-blur-md">
          <Flame className="w-4 h-4 text-rose-500 animate-pulse" />
          <span>Multi-Agent AI Startup Stress-Testing Gauntlet</span>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold backdrop-blur-md">
          <Plug className="w-3.5 h-3.5 text-cyan-400" />
          <span>MCP Diligence Live</span>
        </div>
      </div>

      {/* Hero Headline */}
      <div className="space-y-6 max-w-4xl">
        <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight leading-[1.1] text-white">
          Pitch your idea. <br />
          <span className="bg-gradient-to-r from-rose-500 via-amber-400 to-rose-400 bg-clip-text text-transparent">
            Get grilled by AI investors
          </span> <br />
          before real VCs do.
        </h1>

        <p className="text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed font-light">
          Real venture capitalists won't tell you the brutal truth until it's too late. 
          Face 3 specialized AI agents grounded in domain RAG, battle through 3 adversarial rounds with live MCP competitor and repo audits, and receive an investment-grade verdict.
        </p>
      </div>

      {/* CTA Button Group */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
        <Link
          href="/pitch"
          className="group relative inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-bold text-lg shadow-xl shadow-rose-900/40 hover:shadow-rose-700/60 transition-all duration-300 transform hover:-translate-y-0.5"
        >
          <span>Enter the Panel</span>
          <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </Link>
        <Link
          href="/connectors"
          className="inline-flex items-center gap-2 px-6 py-4 rounded-2xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/10 text-slate-200 font-semibold text-base transition-all"
        >
          <Plug className="w-4 h-4 text-cyan-400" />
          <span>Explore MCP Connectors</span>
        </Link>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-4xl text-left pt-4">
        <div className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/5">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span className="text-xs text-slate-300 font-medium">3-Round Stateful Multi-Agent Debate</span>
        </div>
        <div className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/5">
          <Plug className="w-5 h-5 text-cyan-400 shrink-0" />
          <span className="text-xs text-slate-300 font-medium">Tavily & GitHub MCP Live Diligence</span>
        </div>
        <div className="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/5">
          <Award className="w-5 h-5 text-amber-400 shrink-0" />
          <span className="text-xs text-slate-300 font-medium">Investment Verdict & PDF Memo</span>
        </div>
      </div>

      {/* Persona Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left pt-6">
        {/* Skeptical VC */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 hover:border-rose-500/40 transition-all duration-300 group hover:shadow-xl hover:shadow-rose-950/20">
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-4 group-hover:scale-110 transition-transform">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">The Skeptical VC</h3>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Hunts for moat illusions, scalability bottlenecks, defensibility flaws, and 10x exit viability. Unpersuaded by buzzwords.
          </p>
        </div>

        {/* Financial Analyst */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 hover:border-amber-500/40 transition-all duration-300 group hover:shadow-xl hover:shadow-amber-950/20">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4 group-hover:scale-110 transition-transform">
            <DollarSign className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">The Financial Analyst</h3>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Dissects unit economics, CAC/LTV ratios, gross margins, cash burn rate, and runway. Zero tolerance for hand-waving.
          </p>
        </div>

        {/* Market Realist */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 hover:border-blue-500/40 transition-all duration-300 group hover:shadow-xl hover:shadow-blue-950/20">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-110 transition-transform">
            <Target className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">The Market Realist</h3>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Evaluates incumbent retaliation, distribution channels, customer adoption barriers, regulatory hurdles, and timing.
          </p>
        </div>
      </div>
    </main>
  );
}

