'use client';

import React from 'react';
import { PersonaScore } from '../types';
import { ShieldAlert, DollarSign, Target } from 'lucide-react';

interface AgentScoreProps {
  score: PersonaScore;
}

export default function AgentScore({ score }: AgentScoreProps) {
  const getIcon = () => {
    switch (score.persona) {
      case 'Skeptical VC':
        return <ShieldAlert className="w-5 h-5 text-rose-400" />;
      case 'Financial Analyst':
        return <DollarSign className="w-5 h-5 text-amber-400" />;
      case 'Market Realist':
        return <Target className="w-5 h-5 text-blue-400" />;
    }
  };

  const getScoreColor = (val: number) => {
    if (val >= 75) return 'text-emerald-400';
    if (val >= 50) return 'text-amber-400';
    return 'text-rose-400';
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-white/10 text-left space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-white/5">{getIcon()}</div>
          <div>
            <h4 className="font-bold text-white text-sm">{score.persona}</h4>
            <span className="text-xs text-slate-400">Verdict: {score.verdict}</span>
          </div>
        </div>
        <div className={`text-2xl font-black ${getScoreColor(score.score)}`}>
          {score.score}<span className="text-xs text-slate-400 font-normal">/100</span>
        </div>
      </div>

      <p className="text-xs text-slate-300 leading-relaxed font-light border-t border-white/5 pt-2.5">
        {score.key_takeaway}
      </p>
    </div>
  );
}
