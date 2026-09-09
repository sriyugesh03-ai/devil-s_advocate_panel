'use client';

import React from 'react';
import { WeaknessItem, SeverityLevelType } from '../types';
import { AlertOctagon, Wrench, ChevronRight } from 'lucide-react';

interface WeaknessRankingProps {
  weaknesses: WeaknessItem[];
}

export default function WeaknessRanking({ weaknesses }: WeaknessRankingProps) {
  const getSeverityStyle = (sev: SeverityLevelType) => {
    switch (sev) {
      case 'Critical':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'High':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
      case 'Medium':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/50';
      case 'Low':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50';
    }
  };

  return (
    <div className="space-y-4 text-left">
      <h3 className="text-xl font-bold text-white flex items-center gap-2">
        <AlertOctagon className="w-5 h-5 text-rose-500" />
        <span>Vulnerabilities Ranked by Severity</span>
      </h3>

      <div className="space-y-4">
        {weaknesses.map((item, idx) => (
          <div
            key={idx}
            className="glass-panel p-5 rounded-2xl border border-white/10 hover:border-white/20 transition-all space-y-3"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className={`px-2.5 py-0.5 rounded-full border text-xs font-bold uppercase tracking-wider ${getSeverityStyle(item.severity)}`}>
                {item.severity} Severity
              </span>
              <span className="text-xs text-slate-400 font-medium">
                Category: {item.category}
              </span>
            </div>

            <h4 className="text-base font-bold text-white">{item.title}</h4>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              {item.description}
            </p>

            <div className="p-3.5 rounded-xl bg-darkbg-800/80 border border-emerald-500/20 text-emerald-300 text-xs sm:text-sm flex items-start gap-2.5">
              <Wrench className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-emerald-400 block mb-0.5">Recommended Founder Fix:</strong>
                <span>{item.recommended_fix}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
