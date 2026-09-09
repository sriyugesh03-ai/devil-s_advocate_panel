'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth, useUser, SignInButton } from '@clerk/nextjs';
import { getMySessions, getPdfDownloadUrl } from '../../lib/api';
import { SessionState } from '../../types';
import { 
  History, 
  Flame, 
  ArrowRight, 
  Clock, 
  FileText, 
  Download, 
  ShieldAlert, 
  PlusCircle, 
  Loader2, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';

import { useAppAuth } from '../../components/AuthProvider';

function AuthenticatedHistoryView() {
  const { getToken, isLoaded: isAuthLoaded, isSignedIn } = useAuth();
  const [sessions, setSessions] = useState<SessionState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSessions() {
      if (!isAuthLoaded) return;
      setLoading(true);
      setError(null);

      try {
        let token: string | null = null;
        if (isSignedIn) {
          token = await getToken();
        }
        const data = await getMySessions(token);
        setSessions(data.sessions || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load pitch history.');
      } finally {
        setLoading(false);
      }
    }

    fetchSessions();
  }, [isAuthLoaded, isSignedIn, getToken]);

  return (
    <>
      {isAuthLoaded && !isSignedIn && (
        <div className="mb-8 p-4 rounded-xl bg-amber-950/40 border border-amber-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <p className="text-sm text-amber-200">
              You are currently viewing public sessions. Sign in with Clerk to bind pitches to your founder account.
            </p>
          </div>
          <SignInButton mode="modal">
            <button className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors whitespace-nowrap">
              Sign In with Clerk
            </button>
          </SignInButton>
        </div>
      )}
      <HistoryList sessions={sessions} loading={loading} error={error} />
    </>
  );
}

function UnauthenticatedHistoryView() {
  const [sessions, setSessions] = useState<SessionState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSessions() {
      setLoading(true);
      setError(null);
      try {
        const data = await getMySessions(null);
        setSessions(data.sessions || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load pitch history.');
      } finally {
        setLoading(false);
      }
    }
    fetchSessions();
  }, []);

  return <HistoryList sessions={sessions} loading={loading} error={error} />;
}

export default function HistoryPage() {
  const { isClerkConfigured } = useAppAuth();

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full flex-1">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/10 pb-6 mb-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs font-semibold mb-2">
            <History className="w-3.5 h-3.5" />
            <span>MongoDB Atlas Stored Sessions</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Pitch History & Gauntlet Dossiers
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Review past investor interrogations, examine adversarial critiques, and access generated investment memos.
          </p>
        </div>

        <Link
          href="/pitch"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-semibold text-sm shadow-lg shadow-rose-900/30 transition-all transform hover:-translate-y-0.5"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Pitch New Startup</span>
        </Link>
      </div>

      {isClerkConfigured ? <AuthenticatedHistoryView /> : <UnauthenticatedHistoryView />}
    </main>
  );
}

function HistoryList({
  sessions,
  loading,
  error,
}: {
  sessions: SessionState[];
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-center">
        <Loader2 className="w-10 h-10 text-rose-500 animate-spin mb-4" />
        <p className="text-slate-400 font-medium">Fetching gauntlet archives from MongoDB Atlas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-rose-950/60 border border-rose-500/40 text-rose-200 text-center max-w-xl mx-auto">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
        <p className="font-semibold mb-2">Unable to load sessions</p>
        <p className="text-xs text-rose-300 mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="glass-panel py-16 px-6 rounded-2xl border border-white/5 text-center max-w-lg mx-auto">
        <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mx-auto mb-4">
          <Flame className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">No Pitch Gauntlets Found</h3>
        <p className="text-sm text-slate-400 mb-6 leading-relaxed">
          You haven't pitched a startup to the Devil's Advocate Panel yet. Step into the arena and face 3 adversarial AI investor personas.
        </p>
        <Link
          href="/pitch"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm shadow-lg shadow-rose-600/30 transition-all"
        >
          <span>Begin First Interrogation</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {sessions.map((session) => {
        const pitch = session.pitch || {};
        const isCompleted = session.status === 'completed' || !!session.verdict;
        const score = session.verdict?.overall_score;
        const decision = session.verdict?.investment_recommendation;

        return (
          <div
            key={session.session_id}
            className="glass-panel rounded-2xl border border-white/10 hover:border-rose-500/40 p-6 flex flex-col justify-between transition-all duration-300 group hover:shadow-xl hover:shadow-rose-950/20"
          >
            <div>
              {/* Top Status & Date */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium ${
                    isCompleted
                      ? 'bg-emerald-950/60 border border-emerald-500/40 text-emerald-300'
                      : 'bg-amber-950/60 border border-amber-500/40 text-amber-300 animate-pulse'
                  }`}
                >
                  {isCompleted ? (
                    <>
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      <span>VERDICT REACHED</span>
                    </>
                  ) : (
                    <>
                      <Clock className="w-3 h-3 text-amber-400" />
                      <span>ROUND {session.current_round} / {session.total_rounds || 3}</span>
                    </>
                  )}
                </span>

                <span className="text-xs text-slate-500 font-mono">
                  {session.created_at
                    ? new Date(session.created_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })
                    : 'Recent'}
                </span>
              </div>

              {/* Title and Tagline */}
              <h3 className="text-xl font-bold text-white group-hover:text-rose-400 transition-colors line-clamp-1 mb-1">
                {pitch.title || 'Untitled Venture'}
              </h3>
              <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed font-light">
                {pitch.tagline || pitch.problem || 'No description provided.'}
              </p>

              {/* Score & Decision Highlight if verdict exists */}
              {isCompleted && session.verdict && (
                <div className="p-3 rounded-xl bg-darkbg-800/80 border border-white/5 mb-4 flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="text-[10px] uppercase font-mono text-slate-400">Recommendation</span>
                    <span className={`text-xs font-bold ${decision?.toLowerCase().includes('invest') ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {decision || 'EVALUATED'}
                    </span>
                  </div>

                  {score !== undefined && (
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] uppercase font-mono text-slate-400">Panel Score</span>
                      <span className="text-sm font-extrabold text-white font-mono">
                        {score.toFixed(1)} <span className="text-slate-500 text-xs font-normal">/ 10</span>
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Card Action Buttons */}
            <div className="pt-4 border-t border-white/10 flex items-center justify-between gap-3">
              <Link
                href={`/session/${session.session_id}`}
                className="flex-1 inline-flex items-center justify-center gap-2 py-2 px-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-slate-200 hover:text-white text-xs font-semibold transition-all"
              >
                <span>{isCompleted ? 'View Full Dossier' : 'Resume Interrogation'}</span>
                <ArrowRight className="w-3.5 h-3.5 text-rose-400" />
              </Link>

              {isCompleted && (
                <a
                  href={getPdfDownloadUrl(session.session_id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 hover:text-rose-300 transition-colors"
                  title="Download PDF Investment Memo"
                >
                  <Download className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

