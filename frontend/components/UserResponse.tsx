'use client';

import React, { useState } from 'react';
import { Send, Loader2, MessageSquare, Lightbulb, Sparkles } from 'lucide-react';

interface UserResponseProps {
  currentRound: number;
  totalRounds: number;
  onSubmit: (response: string) => Promise<void>;
  disabled?: boolean;
}

const ANSWER_TIPS = [
  { label: '📊 Numbers & Unit Economics', text: 'Our CAC is $X, LTV is $Y (X:Y ratio), and gross margin stands at Z% because...' },
  { label: '🛡️ Defense Against Copycats', text: 'Competitors cannot easily copy this because our proprietary moat relies on...' },
  { label: '🚀 Distribution & First 100 Users', text: 'We acquire early customers specifically through...' },
];

export default function UserResponse({
  currentRound,
  totalRounds,
  onSubmit,
  disabled = false,
}: UserResponseProps) {
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!response.trim() || loading) return;

    setLoading(true);
    try {
      await onSubmit(response);
      setResponse('');
    } finally {
      setLoading(false);
    }
  };

  const appendTemplate = (text: string) => {
    setResponse((prev) => {
      if (!prev.trim()) return text;
      return `${prev}\n\n${text}`;
    });
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-2xl border border-rose-500/30 shadow-2xl space-y-4 text-left">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <label className="text-sm font-bold text-white flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-rose-400" />
          <span>Your Founder Defense (Round {currentRound} of {totalRounds})</span>
        </label>
        <span className="text-xs text-slate-400">
          Be specific and use real numbers or concrete details.
        </span>
      </div>

      {/* Quick Answer Starters */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-amber-400" /> Need inspiration?
        </span>
        {ANSWER_TIPS.map((tip, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => appendTemplate(tip.text)}
            className="text-[11px] px-2.5 py-1 rounded-lg bg-darkbg-800 hover:bg-darkbg-700 border border-white/10 text-slate-300 hover:text-white transition-all"
          >
            {tip.label}
          </button>
        ))}
      </div>

      <textarea
        rows={4}
        value={response}
        onChange={(e) => setResponse(e.target.value)}
        placeholder="Address the panel's skepticism: explain your technical defensibility, unit economics math, and early customer adoption plan..."
        disabled={disabled || loading}
        required
        className="w-full p-4 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors text-sm"
      />

      <div className="flex items-center justify-between pt-1">
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <Lightbulb className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>Clear and direct answers score higher in the final investment memo.</span>
        </div>

        <button
          type="submit"
          disabled={disabled || loading || !response.trim()}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-semibold text-sm flex items-center gap-2 shadow-lg shadow-rose-950/40 transition-all disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Panel Deliberating...</span>
            </>
          ) : (
            <>
              <span>Submit Rebuttal to Panel</span>
              <Send className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </form>
  );
}

