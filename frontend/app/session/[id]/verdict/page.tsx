'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getVerdict, getSession } from '../../../../lib/api';
import { FinalVerdict, SessionState } from '../../../../types';
import VerdictCard from '../../../../components/VerdictCard';
import AgentScore from '../../../../components/AgentScore';
import WeaknessRanking from '../../../../components/WeaknessRanking';
import DownloadReport from '../../../../components/DownloadReport';
import Link from 'next/link';
import { Flame, Loader2, ArrowLeft, RefreshCw } from 'lucide-react';

export default function VerdictPage() {
  const params = useParams();
  const sessionId = params.id as string;

  const [verdict, setVerdict] = useState<FinalVerdict | null>(null);
  const [session, setSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVerdict = async () => {
    try {
      const [verdictData, sessionData] = await Promise.all([
        getVerdict(sessionId),
        getSession(sessionId),
      ]);
      setVerdict(verdictData);
      setSession(sessionData);
    } catch (err: any) {
      setError(err.message || 'Failed to synthesize verdict.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVerdict();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[70vh] text-center px-4">
        <Loader2 className="w-12 h-12 text-rose-500 animate-spin mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">
          Investment Committee in Final Deliberation
        </h2>
        <p className="text-slate-400 max-w-md text-sm">
          Aggregating all 3 adversarial rounds, ranking existential vulnerabilities, and compiling your diagnostic report...
        </p>
      </div>
    );
  }

  if (error || !verdict) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-md mx-auto">
        <h2 className="text-xl font-bold text-white mb-2">Verdict Generation Issue</h2>
        <p className="text-sm text-slate-400 mb-6">{error || 'Could not load verdict.'}</p>
        <button
          onClick={fetchVerdict}
          className="px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="py-10 px-4 sm:px-6 max-w-6xl mx-auto w-full space-y-10">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/10 pb-6 text-left">
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Home
          </Link>
          <h1 className="text-3xl sm:text-4xl font-black text-white">
            Final Investment Verdict
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Diagnostic report synthesized for <strong className="text-white">{session?.pitch.title}</strong>
          </p>
        </div>

        <div>
          <DownloadReport sessionId={sessionId} startupName={session?.pitch.title} />
        </div>
      </div>

      {/* Main Consensus Score Card */}
      <VerdictCard verdict={verdict} />

      {/* 3 Specialist Persona Scorecards */}
      <div className="space-y-3 text-left">
        <h3 className="text-xl font-bold text-white">Panel Persona Scorecards</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {verdict.persona_scores.map((score, idx) => (
            <AgentScore key={idx} score={score} />
          ))}
        </div>
      </div>

      {/* Ranked Weaknesses & Recommended Fixes */}
      <WeaknessRanking weaknesses={verdict.ranked_weaknesses} />

      {/* Footer Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-10 border-t border-white/10">
        <Link
          href="/pitch"
          className="px-8 py-4 rounded-xl bg-darkbg-800 border border-white/10 hover:border-rose-500 text-white font-semibold text-sm transition-all"
        >
          Stress Test Another Startup
        </Link>
        <DownloadReport sessionId={sessionId} startupName={session?.pitch.title} />
      </div>
    </div>
  );
}
