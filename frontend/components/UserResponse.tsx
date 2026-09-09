'use client';

import React, { useState } from 'react';
import { Send, Loader2, MessageSquare } from 'lucide-react';

interface UserResponseProps {
  currentRound: number;
  totalRounds: number;
  onSubmit: (response: string) => Promise<void>;
  disabled?: boolean;
}

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

  return (
    <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-2xl border border-rose-500/30 shadow-2xl space-y-4 text-left">
      <div className="flex items-center justify-between">
        <label className="text-sm font-bold text-white flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-rose-400" />
          <span>Your Founder Defense (Round {currentRound} of {totalRounds})</span>
        </label>
        <span className="text-xs text-slate-400">
          Address all 3 challenges directly. Avoid hand-waving.
        </span>
      </div>

      <textarea
        rows={4}
        value={response}
        onChange={(e) => setResponse(e.target.value)}
        placeholder="Respond to the panel's skepticism with specific technical moats, unit economics metrics, and distribution channels..."
        disabled={disabled || loading}
        required
        className="w-full p-4 rounded-xl bg-darkbg-800 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 transition-colors text-sm"
      />

      <div className="flex justify-end">
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
