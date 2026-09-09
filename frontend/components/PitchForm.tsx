'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { submitPitch } from '../lib/api';
import { Flame, ArrowRight, Loader2, Sparkles, Building2, Lightbulb, Users, DollarSign } from 'lucide-react';

export default function PitchForm() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(false);
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
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let token: string | null = null;
      try {
        token = await getToken();
      } catch (authErr) {
        // Continue unauthenticated if user is guest
      }
      const session = await submitPitch(formData, token);
      router.push(`/session/${session.session_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to submit pitch.');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-10 rounded-2xl border border-white/10 shadow-2xl max-w-4xl mx-auto text-left space-y-6">
      <div className="border-b border-white/10 pb-4 mb-6">
        <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
          <Flame className="w-6 h-6 text-rose-500" />
          <span>Startup Pitch Dossier</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Provide your startup details. The 3 panel agents will read your pitch and commence Round 1 interrogation.
        </p>
      </div>

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
