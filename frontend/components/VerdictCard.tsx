'use client';

import React from 'react';
import { FinalVerdict } from '../types';
import { Trophy, TrendingUp, Sparkles, CheckCircle } from 'lucide-react';

interface VerdictCardProps {
  verdict: FinalVerdict;
}

export default function VerdictCard({ verdict }: VerdictCardProps) {
  const getVerdictGradient = (score: number) => {
    if (score >= 75) return 'from-emerald-500 to-teal-700';
    if (score >= 50) return 'from-amber-500 to-orange-700';
    return 'from-rose-600 to-red-800';
  };

  return (
    <div className="glass-panel-glow p-8 rounded-3xl border border-rose-500/40 text-left space-y-6">
      {/* Hero Stats */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border-b border-white/10 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Investment Committee Consensus</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white">
            {verdict.investment_recommendation}
          </h2>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-center">
            <span className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Consolidated Score
            </span>
            <div className="text-4xl sm:text-5xl font-black bg-gradient-to-r from-rose-400 to-amber-400 bg-clip-text text-transparent">
              {verdict.overall_score}<span className="text-lg text-slate-400 font-normal">/100</span>
            </div>
          </div>

          <div className="text-center border-l border-white/10 pl-6">
            <span className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              24-Mo Survival Odds
            </span>
            <div className="text-4xl sm:text-5xl font-black text-emerald-400">
              {verdict.survival_odds_percentage}%
            </div>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400">
          Executive Diagnostic Synthesis
        </h4>
        <p className="text-slate-300 leading-relaxed text-base font-light">
          {verdict.executive_summary}
        </p>
      </div>

      {/* Priority Action Plan */}
      {verdict.priority_action_plan && verdict.priority_action_plan.length > 0 && (
        <div className="p-5 rounded-2xl bg-darkbg-800/80 border border-white/10 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
            <Trophy className="w-4 h-4" />
            <span>Priority Action Plan Before Pitching Real Angels/VCs</span>
          </h4>
          <ul className="space-y-2">
            {verdict.priority_action_plan.map((action, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-slate-200">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
