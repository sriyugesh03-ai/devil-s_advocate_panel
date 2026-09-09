'use client';

import React from 'react';
import { AgentChallenge, SeverityLevelType } from '../types';
import ReasoningSummary from './ReasoningSummary';
import { ShieldAlert, DollarSign, Target, AlertTriangle } from 'lucide-react';

interface ChallengeCardProps {
  challenge: AgentChallenge;
}

export default function ChallengeCard({ challenge }: ChallengeCardProps) {
  const getPersonaBadge = () => {
    switch (challenge.persona) {
      case 'Skeptical VC':
        return {
          icon: <ShieldAlert className="w-4 h-4 text-rose-400" />,
          color: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
        };
      case 'Financial Analyst':
        return {
          icon: <DollarSign className="w-4 h-4 text-amber-400" />,
          color: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
        };
      case 'Market Realist':
        return {
          icon: <Target className="w-4 h-4 text-blue-400" />,
          color: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
        };
    }
  };

  const getSeverityBadge = (severity: SeverityLevelType) => {
    switch (severity) {
      case 'Critical':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'High':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'Medium':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'Low':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  const badge = getPersonaBadge();

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 hover:border-white/20 transition-all space-y-4 text-left shadow-xl">
      {/* Header Badges */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${badge.color}`}>
          {badge.icon}
          <span>{challenge.persona}</span>
        </div>

        <div className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-xs font-bold uppercase tracking-wider ${getSeverityBadge(challenge.severity)}`}>
          <AlertTriangle className="w-3 h-3" />
          <span>{challenge.severity} Severity</span>
        </div>
      </div>

      {/* Interrogation Question */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400 mb-1">
          Targeted Challenge
        </h4>
        <p className="text-lg font-bold text-white leading-snug">
          "{challenge.question}"
        </p>
      </div>

      {/* Reasoning Summary */}
      <ReasoningSummary
        summary={challenge.reasoning_summary}
        citation={challenge.evidence_citation}
      />
    </div>
  );
}
