'use client';

import React from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

interface RoundProgressProps {
  currentRound: number;
  totalRounds: number;
  status: string;
}

export default function RoundProgress({ currentRound, totalRounds, status }: RoundProgressProps) {
  const steps = [
    { num: 1, label: 'Core Moat & Unit Economics' },
    { num: 2, label: 'Adversarial Follow-Up' },
    { num: 3, label: 'Final Existential Defense' },
  ];

  return (
    <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/5 mb-8">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {steps.map((step) => {
          const isCompleted = step.num < currentRound || status === 'completed';
          const isCurrent = step.num === currentRound && status !== 'completed';

          return (
            <div
              key={step.num}
              className={`flex items-center gap-3 flex-1 w-full sm:w-auto ${
                isCurrent ? 'opacity-100' : isCompleted ? 'opacity-80' : 'opacity-40'
              }`}
            >
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm ${
                  isCompleted
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    : isCurrent
                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-950/60 animate-pulse'
                    : 'bg-white/5 text-slate-400 border border-white/10'
                }`}
              >
                {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : step.num}
              </div>

              <div className="text-left">
                <span className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Round {step.num}
                </span>
                <span className="text-xs sm:text-sm font-bold text-white">
                  {step.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
