'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getSession, submitFounderResponse } from '../../../lib/api';
import { SessionState } from '../../../types';
import PanelMember from '../../../components/PanelMember';
import RoundProgress from '../../../components/RoundProgress';
import ChallengeCard from '../../../components/ChallengeCard';
import UserResponse from '../../../components/UserResponse';
import Link from 'next/link';
import { Flame, Loader2, RefreshCw, ArrowRight, ShieldAlert, Award } from 'lucide-react';

export default function SessionRoomPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [session, setSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchState = async () => {
    try {
      const data = await getSession(sessionId);
      setSession(data);
      if (data.status === 'completed' || data.verdict) {
        router.push(`/session/${sessionId}/verdict`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load session');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchState();
  }, [sessionId]);

  const handleFounderSubmit = async (response: string) => {
    if (!session) return;
    try {
      const updated = await submitFounderResponse(sessionId, session.current_round, response);
      setSession(updated);
      if (updated.status === 'completed' || updated.current_round > updated.total_rounds || updated.verdict) {
        router.push(`/session/${sessionId}/verdict`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to submit response');
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="w-10 h-10 text-rose-500 animate-spin mb-4" />
        <p className="text-slate-400 font-medium">Entering the Panel Chambers...</p>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-lg mx-auto">
        <ShieldAlert className="w-12 h-12 text-rose-500 mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">Panel Session Error</h2>
        <p className="text-sm text-slate-400 mb-6">{error || 'Unable to retrieve session.'}</p>
        <button
          onClick={fetchState}
          className="px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="py-8 px-4 sm:px-6 max-w-6xl mx-auto w-full space-y-8">
      {/* Session Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/10 pb-6 text-left">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs font-semibold mb-2">
            <Flame className="w-3.5 h-3.5 text-rose-500" />
            <span>Session #{session.session_id.slice(-6)}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            {session.pitch.title}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
            {session.pitch.tagline}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchState}
            className="p-2.5 rounded-xl bg-darkbg-800 border border-white/10 text-slate-400 hover:text-white transition-colors"
            title="Refresh State"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Round Progression Timeline */}
      <RoundProgress
        currentRound={session.current_round}
        totalRounds={session.total_rounds}
        status={session.status}
      />

      {/* 3 Panel Members Status */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <PanelMember persona="Skeptical VC" isActive={true} />
        <PanelMember persona="Financial Analyst" isActive={true} />
        <PanelMember persona="Market Realist" isActive={true} />
      </div>

      {/* Current Round Challenges Grid */}
      <div className="space-y-4 text-left">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white">
            Round {session.current_round} Interrogation Challenges
          </h3>
          <span className="text-xs text-rose-400 font-semibold uppercase tracking-wider">
            All 3 Agents Ready
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {session.current_challenges && session.current_challenges.length > 0 ? (
            session.current_challenges.map((challenge, idx) => (
              <ChallengeCard key={idx} challenge={challenge} />
            ))
          ) : (
            <div className="col-span-3 p-8 rounded-2xl glass-panel text-center text-slate-400">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-rose-500" />
              Deliberating challenges...
            </div>
          )}
        </div>
      </div>

      {/* Founder Response Box */}
      <UserResponse
        currentRound={session.current_round}
        totalRounds={session.total_rounds}
        onSubmit={handleFounderSubmit}
        disabled={session.status === 'completed'}
      />

      {/* Previous Round Transcripts (if any) */}
      {session.rounds_history && session.rounds_history.length > 0 && (
        <div className="space-y-4 text-left pt-6 border-t border-white/10">
          <h3 className="text-base font-bold text-slate-300">Previous Round Logs & Critiques</h3>
          <div className="space-y-4">
            {session.rounds_history.map((r, i) => (
              <div key={i} className="glass-panel p-5 rounded-xl border border-white/5 space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  Round {r.round_number} Rebuttal
                </span>
                <p className="text-sm text-slate-300 italic">"{r.founder_response}"</p>
                {r.reactions && (
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-white/5">
                    {r.reactions.map((react, j) => (
                      <div key={j} className="text-xs text-slate-400 bg-darkbg-800/60 p-2.5 rounded-lg">
                        <strong className="text-white block">{react.persona} (Score: {react.satisfaction_score}/100)</strong>
                        <span>{react.reaction_summary}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
