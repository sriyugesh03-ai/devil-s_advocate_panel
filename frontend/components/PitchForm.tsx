'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { submitPitch, parsePitchDeck } from '../lib/api';
import { useAppAuth } from './AuthProvider';
import { 
  Flame, 
  ArrowRight, 
  Loader2, 
  Sparkles, 
  Building2, 
  Lightbulb, 
  Users, 
  DollarSign, 
  Github, 
  FileUp, 
  CheckCircle,
  Zap,
  Power
} from 'lucide-react';
import { getMcpEnabledState, MCP_STORAGE_KEY } from './McpModal';

interface PitchFormBaseProps {
  getToken?: () => Promise<string | null>;
}

function PitchFormBase({ getToken }: PitchFormBaseProps) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [deckParsing, setDeckParsing] = useState(false);
  const [deckParsedSuccess, setDeckParsedSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: 'PulseShield AI',
    tagline: 'Autonomous AI Reliability & Chaos Engineering for Enterprise Microservices',
    problem: 'Cloud microservices experience cascading outages that take engineers hours to diagnose, costing Fortune 500 companies millions per hour of downtime.',
    solution: 'We run continuous, non-disruptive eBPF chaos injections and predictive healing agents that isolate anomalies before SLA breaches occur.',
    target_market: 'Mid-to-large enterprises with 50+ microservices on Kubernetes, representing an estimated $12B DevSecOps addressable market.',
    business_model: '$3,500/month platform base + $50/node/month usage billing, targeting 85% SaaS gross margins.',
    traction: '3 enterprise pilots signed ($120k ARR pipeline), 400 waitlist signups.',
    competition: 'Datadog, Dynatrace, Gremlin (none have predictive eBPF auto-healing).',
    fundraising_goal: '$2.5M Seed at $15M pre-money valuation',
    github_url: 'https://github.com/tiangolo/fastapi',
  });

  const [mcpState, setMcpState] = useState<Record<string, boolean>>({
    'tavily-search': true,
    'github-diligence': true,
    'deck-parser': true,
  });

  const syncMcpState = () => {
    setMcpState(getMcpEnabledState());
  };

  React.useEffect(() => {
    syncMcpState();
    window.addEventListener('mcp-config-changed', syncMcpState);
    return () => window.removeEventListener('mcp-config-changed', syncMcpState);
  }, []);

  const toggleMcpTool = (id: string) => {
    const nextState = {
      ...mcpState,
      [id]: !mcpState[id]
    };
    setMcpState(nextState);
    if (typeof window !== 'undefined') {
      localStorage.setItem(MCP_STORAGE_KEY, JSON.stringify(nextState));
      window.dispatchEvent(new Event('mcp-config-changed'));
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleDeckUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a valid .pdf pitch deck file.');
      return;
    }

    setDeckParsing(true);
    setError(null);
    try {
      const parsed = await parsePitchDeck(file);
      setFormData(prev => ({
        ...prev,
        title: parsed.title || prev.title,
        tagline: parsed.tagline || prev.tagline,
        problem: parsed.problem || prev.problem,
        solution: parsed.solution || prev.solution,
        target_market: parsed.target_market || prev.target_market,
        business_model: parsed.business_model || prev.business_model,
        traction: parsed.traction || prev.traction,
        competition: parsed.competition || prev.competition,
        fundraising_goal: parsed.fundraising_goal || prev.fundraising_goal,
      }));
      setDeckParsedSuccess(`Auto-filled pitch from "${file.name}" via MCP Parser!`);
    } catch (err: any) {
      setError(err.message || 'Failed to parse pitch deck PDF.');
    } finally {
      setDeckParsing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // If GitHub Diligence MCP is toggled OFF, clear github_url so technical audit is skipped
    const submissionPayload = {
      ...formData,
      github_url: mcpState['github-diligence'] ? formData.github_url : undefined
    };

    try {
      let token: string | null = null;
      if (getToken) {
        try {
          token = await getToken();
        } catch (authErr) {
          // Continue unauthenticated if user is guest
        }
      }
      const session = await submitPitch(submissionPayload, token);
      router.push(`/session/${session.session_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to submit pitch.');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-10 rounded-2xl border border-white/10 shadow-2xl max-w-4xl mx-auto text-left space-y-6">
      <div className="border-b border-white/10 pb-4 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <Flame className="w-6 h-6 text-rose-500" />
            <span>Startup Pitch Dossier</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Fill your startup details or upload your pitch deck. The 3 panel agents will cross-examine your pitch in Round 1.
          </p>
        </div>

        {/* MCP PDF Deck Upload Trigger */}
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleDeckUpload}
            accept=".pdf"
            className="hidden"
          />
          <button
            type="button"
            disabled={deckParsing}
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-900/60 transition-all text-xs font-semibold shadow-sm"
          >
            {deckParsing ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <span>MCP Parsing Deck...</span>
              </>
            ) : (
              <>
                <FileUp className="w-3.5 h-3.5 text-cyan-400" />
                <span>Upload Pitch Deck (.PDF)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {deckParsedSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2 animate-in fade-in">
          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{deckParsedSuccess}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/80 border border-rose-500/50 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Row 1: Title & Tagline */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
            <Building2 className="w-4 h-4 text-rose-400" /> Startup Name
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-amber-400" /> Tagline / One-Liner
          </label>
          <input
            type="text"
            name="tagline"
            value={formData.tagline}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>
      </div>

      {/* Problem & Solution */}
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            The Problem & Customer Pain Point
          </label>
          <textarea
            name="problem"
            rows={3}
            value={formData.problem}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
            <Lightbulb className="w-4 h-4 text-amber-400" /> Unique Solution & Technical Edge
          </label>
          <textarea
            name="solution"
            rows={3}
            value={formData.solution}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>
      </div>

      {/* Market & Business Model */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
            <Users className="w-4 h-4 text-blue-400" /> Target Market (ICP & TAM)
          </label>
          <textarea
            name="target_market"
            rows={3}
            value={formData.target_market}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
            <DollarSign className="w-4 h-4 text-emerald-400" /> Business Model & Pricing
          </label>
          <textarea
            name="business_model"
            rows={3}
            value={formData.business_model}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>
      </div>

      {/* Traction & Competition */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            Traction / Metrics
          </label>
          <input
            type="text"
            name="traction"
            value={formData.traction}
            onChange={handleChange}
            className="w-full px-4 py-2.5 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors text-sm"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            Competition & Alternatives
          </label>
          <input
            type="text"
            name="competition"
            value={formData.competition}
            onChange={handleChange}
            className="w-full px-4 py-2.5 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors text-sm"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            Fundraising Goal
          </label>
          <input
            type="text"
            name="fundraising_goal"
            value={formData.fundraising_goal}
            onChange={handleChange}
            className="w-full px-4 py-2.5 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors text-sm"
          />
        </div>
      </div>

      {/* GitHub Repository (Technical Diligence MCP) with explicit ON/OFF Switch */}
      <div className={`p-5 rounded-xl border transition-all space-y-3 ${
        mcpState['github-diligence']
          ? 'bg-darkbg-800/80 border-cyan-500/30'
          : 'bg-darkbg-900/60 border-white/5 opacity-75'
      }`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-cyan-300 flex items-center gap-2">
            <Github className="w-4 h-4 text-violet-400" />
            <span>GitHub Repository (Technical Diligence MCP)</span>
          </label>

          {/* Quick ON / OFF Button */}
          <div className="flex items-center gap-2.5">
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
              mcpState['github-diligence']
                ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}>
              {mcpState['github-diligence'] ? 'ON' : 'OFF'}
            </span>

            <button
              type="button"
              onClick={() => toggleMcpTool('github-diligence')}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                mcpState['github-diligence'] ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              role="switch"
              aria-checked={mcpState['github-diligence']}
              title="Toggle GitHub Diligence ON/OFF"
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  mcpState['github-diligence'] ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>

        {mcpState['github-diligence'] ? (
          <>
            <input
              type="url"
              name="github_url"
              value={formData.github_url}
              onChange={handleChange}
              placeholder="https://github.com/your-org/your-repo"
              className="w-full px-4 py-2.5 rounded-lg bg-darkbg-900 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors text-sm font-mono"
            />
            <p className="text-[11px] text-slate-400">
              The <strong>Skeptical VC</strong> will audit commit velocity, language breakdown, and repo architecture via GitHub MCP.
            </p>
          </>
        ) : (
          <div className="p-3 rounded-lg bg-darkbg-950 border border-white/5 flex items-center justify-between text-xs text-slate-400">
            <span>GitHub technical diligence is currently <strong>toggled OFF</strong>. Code audits will be skipped.</span>
            <button
              type="button"
              onClick={() => toggleMcpTool('github-diligence')}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 underline ml-2"
            >
              Turn ON
            </button>
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-bold text-lg flex items-center justify-center gap-3 shadow-xl shadow-rose-950/50 transition-all disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              <span>Analyzing Pitch & Summoning Panel...</span>
            </>
          ) : (
            <>
              <span>Begin Interrogation (Round 1)</span>
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </form>
  );
}

function ClerkPitchForm() {
  const { getToken } = useAuth();
  return <PitchFormBase getToken={getToken} />;
}

export default function PitchForm() {
  const { isClerkConfigured } = useAppAuth();
  if (isClerkConfigured) {
    return <ClerkPitchForm />;
  }
  return <PitchFormBase />;
}
