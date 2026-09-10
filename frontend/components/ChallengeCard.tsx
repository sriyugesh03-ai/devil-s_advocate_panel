'use client';

import React, { useState } from 'react';
import { AgentChallenge, SeverityLevelType } from '../types';
import ReasoningSummary from './ReasoningSummary';
import { ShieldAlert, DollarSign, Target, AlertTriangle, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react';

interface ChallengeCardProps {
  challenge: AgentChallenge;
}

/**
 * Generates a simplified "What they're really asking" paraphrase
 * based on the persona and reasoning summary.
 */
function getSimplifiedHint(persona: string, question: string, reasoning: string): string {
  const q = question.toLowerCase();
  if (persona === 'Skeptical VC') {
    if (q.includes('competitor') || q.includes('copy') || q.includes('moat'))
      return 'They want to know: what makes your product so hard to copy that a bigger company with more money can\'t just build the same thing?';
    if (q.includes('scale') || q.includes('growth'))
      return 'They want to know: can your product handle 10x or 100x more users without breaking or becoming too expensive?';
    return 'They want to know: what\'s your unfair advantage — the one thing that makes investors confident competitors can\'t easily catch up?';
  }
  if (persona === 'Financial Analyst') {
    if (q.includes('cost') || q.includes('cac') || q.includes('acquisition'))
      return 'They want to know: how much money do you spend to get each new customer, and does that customer bring in enough revenue to cover that cost and more?';
    if (q.includes('margin') || q.includes('profit'))
      return 'They want to know: after paying for everything (servers, staff, tools), how much of each dollar of revenue do you actually keep?';
    if (q.includes('pricing') || q.includes('revenue'))
      return 'They want to know: is your pricing realistic? Will customers actually pay this much, and will that be enough to sustain the business?';
    return 'They want to know: do the numbers actually work? Show them the real math behind your business, not just projections.';
  }
  if (persona === 'Market Realist') {
    if (q.includes('switch') || q.includes('adoption') || q.includes('inertia'))
      return 'They want to know: why would customers bother switching from what they already use? What pain is bad enough to make them change?';
    if (q.includes('distribution') || q.includes('reach') || q.includes('customer'))
      return 'They want to know: how will you actually reach and sell to your first customers? What\'s your specific plan — not just "social media" or "marketing."';
    return 'They want to know: is there a real, reachable market for this, or are you assuming people need it more than they actually do?';
  }
  return 'They want to know: can you give a clear, specific answer backed by evidence or real data?';
}

export default function ChallengeCard({ challenge }: ChallengeCardProps) {
  const [hintOpen, setHintOpen] = useState(false);

  const getPersonaBadge = () => {
    switch (challenge.persona) {
      case 'Skeptical VC':
        return {
          icon: <ShieldAlert className="w-4 h-4 text-rose-400" />,
          color: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
          gradient: 'from-rose-500/20 to-transparent',
        };
      case 'Financial Analyst':
        return {
          icon: <DollarSign className="w-4 h-4 text-amber-400" />,
          color: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
          gradient: 'from-amber-500/20 to-transparent',
        };
      case 'Market Realist':
        return {
          icon: <Target className="w-4 h-4 text-blue-400" />,
          color: 'bg-blue-500/10 text-blue-300 border-blue-500/30',
          gradient: 'from-blue-500/20 to-transparent',
        };
    }
  };

  const getSeverityInfo = (severity: SeverityLevelType) => {
    switch (severity) {
      case 'Critical':
        return { color: 'bg-red-500/20 text-red-400 border-red-500/40', width: '100%', barColor: 'bg-red-500' };
      case 'High':
        return { color: 'bg-orange-500/20 text-orange-400 border-orange-500/40', width: '75%', barColor: 'bg-orange-500' };
      case 'Medium':
        return { color: 'bg-amber-500/20 text-amber-400 border-amber-500/40', width: '50%', barColor: 'bg-amber-500' };
      case 'Low':
        return { color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40', width: '25%', barColor: 'bg-emerald-500' };
    }
  };

  const badge = getPersonaBadge();
  const severityInfo = getSeverityInfo(challenge.severity);

  return (
    <div className="glass-panel p-6 rounded-2xl border border-white/10 hover:border-white/20 transition-all space-y-4 text-left shadow-xl relative overflow-hidden">
      {/* Top glow accent */}
      <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${badge?.gradient}`} />

      {/* Header Badges */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
        <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${badge?.color}`}>
          {badge?.icon}
          <span>{challenge.persona}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Severity Badge */}
          <div className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-xs font-bold uppercase tracking-wider ${severityInfo.color}`}>
            <AlertTriangle className="w-3 h-3" />
            <span>{challenge.severity}</span>
          </div>
        </div>
      </div>

      {/* Severity Progress Bar */}
      <div className="w-full h-1.5 bg-darkbg-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${severityInfo.barColor} transition-all duration-500`}
          style={{ width: severityInfo.width }}
        />
      </div>

      {/* Interrogation Question */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400 mb-2">
          Targeted Challenge
        </h4>
        <p className="text-lg font-bold text-white leading-snug">
          &ldquo;{challenge.question}&rdquo;
        </p>
      </div>

      {/* What They're Really Asking — Simplified Helper */}
      <button
        onClick={() => setHintOpen(!hintOpen)}
        className="flex items-center gap-2 w-full text-left px-4 py-2.5 rounded-xl bg-amber-950/30 border border-amber-500/20 hover:border-amber-500/40 transition-all group"
      >
        <Lightbulb className="w-4 h-4 text-amber-400 shrink-0" />
        <span className="text-xs font-semibold text-amber-300 flex-1">
          What they&apos;re really asking
        </span>
        {hintOpen ? (
          <ChevronUp className="w-4 h-4 text-amber-400 group-hover:translate-y-[-1px] transition-transform" />
        ) : (
          <ChevronDown className="w-4 h-4 text-amber-400 group-hover:translate-y-[1px] transition-transform" />
        )}
      </button>
      {hintOpen && (
        <div className="px-4 py-3 rounded-xl bg-amber-950/20 border border-amber-500/10 text-sm text-amber-200/80 leading-relaxed animate-fadeIn">
          {getSimplifiedHint(
            challenge.persona,
            challenge.question,
            challenge.reasoning_summary
          )}
        </div>
      )}

      {/* Reasoning Summary */}
      <ReasoningSummary
        summary={challenge.reasoning_summary}
        citation={challenge.evidence_citation}
      />
    </div>
  );
}
