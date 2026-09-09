import Link from "next/link";
import { Flame, ShieldAlert, TrendingUp, DollarSign, Target, ChevronRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 text-center max-w-6xl mx-auto">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs sm:text-sm font-medium mb-8 backdrop-blur-md animate-pulse-slow">
        <Flame className="w-4 h-4 text-rose-500" />
        <span>Multi-Agent AI Startup Gauntlet</span>
      </div>

      {/* Hero Headline */}
      <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
        Pitch your idea. <br />
        <span className="bg-gradient-to-r from-rose-500 via-red-400 to-amber-400 bg-clip-text text-transparent">
          Get grilled by AI investors
        </span> <br />
        who won't go easy on you.
      </h1>

      <p className="text-base sm:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed font-light">
        Real venture capitalists won't tell you the brutal truth until it's too late. 
        Face 3 specialized AI agents grounded in domain RAG, battle through 3 adversarial rounds, and receive an investment-grade verdict.
      </p>

      {/* CTA Button */}
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-16">
        <Link
          href="/pitch"
          className="group relative inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-semibold text-lg shadow-lg shadow-rose-900/40 hover:shadow-rose-700/60 transition-all duration-300 transform hover:-translate-y-0.5"
        >
          <span>Enter the Panel</span>
          <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* Persona Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
        {/* Skeptical VC */}
        <div className="glass-panel p-6 rounded-2xl border border-white/5 hover:border-rose-500/40 transition-all duration-300 group">
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-4 group-hover:scale-110 transition-transform">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">The Skeptical VC</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Hunts for moat illusions, scalability bottlenecks, defensibility flaws, and 10x exit viability. Unpersuaded by buzzwords.
          </p>
        </div>

        {/* Financial Analyst */}
        <div className="glass-panel p-6 rounded-2xl border border-white/5 hover:border-amber-500/40 transition-all duration-300 group">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-4 group-hover:scale-110 transition-transform">
            <DollarSign className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">The Financial Analyst</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Dissects unit economics, CAC/LTV ratios, gross margins, cash burn rate, and runway. Zero tolerance for vague financials.
          </p>
        </div>

        {/* Market Realist */}
        <div className="glass-panel p-6 rounded-2xl border border-white/5 hover:border-blue-500/40 transition-all duration-300 group">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-110 transition-transform">
            <Target className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">The Market Realist</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Evaluates incumbent retaliation, distribution channels, customer adoption barriers, regulatory hurdles, and timing.
          </p>
        </div>
      </div>
    </main>
  );
}
