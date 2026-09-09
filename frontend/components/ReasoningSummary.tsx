'use client';

import React, { useState } from 'react';
import { BrainCircuit, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

interface ReasoningSummaryProps {
  summary: string;
  citation?: string;
}

export default function ReasoningSummary({ summary, citation }: ReasoningSummaryProps) {
  const [open, setOpen] = useState(true);

  return (
    <div className="rounded-xl bg-darkbg-800/80 border border-white/5 p-4 text-left transition-all">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400 hover:text-slate-200 transition-colors"
      >
        <span className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-rose-400" />
          <span>Agent Reasoning & Thesis Skepticism</span>
        </span>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {open && (
        <div className="mt-3 pt-3 border-t border-white/5 space-y-2">
          <p className="text-sm text-slate-300 leading-relaxed font-light">{summary}</p>
          {citation && (
            <div className="flex items-center gap-1.5 text-xs text-amber-300/80 bg-amber-950/30 px-2.5 py-1 rounded-md border border-amber-500/20">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Grounding: {citation}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
