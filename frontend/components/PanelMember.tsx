'use client';

import React from 'react';
import { ShieldAlert, DollarSign, Target } from 'lucide-react';
import { AgentPersonaType } from '../types';

interface PanelMemberProps {
  persona: AgentPersonaType;
  isActive?: boolean;
}

export default function PanelMember({ persona, isActive = false }: PanelMemberProps) {
  const getIcon = () => {
    switch (persona) {
      case 'Skeptical VC':
        return <ShieldAlert className="w-5 h-5 text-rose-400" />;
      case 'Financial Analyst':
        return <DollarSign className="w-5 h-5 text-amber-400" />;
      case 'Market Realist':
        return <Target className="w-5 h-5 text-blue-400" />;
    }
  };

  const getBorderColor = () => {
    if (!isActive) return 'border-white/10 opacity-70';
    switch (persona) {
      case 'Skeptical VC':
        return 'border-rose-500 shadow-lg shadow-rose-950/50 bg-rose-950/20';
      case 'Financial Analyst':
        return 'border-amber-500 shadow-lg shadow-amber-950/50 bg-amber-950/20';
      case 'Market Realist':
        return 'border-blue-500 shadow-lg shadow-blue-950/50 bg-blue-950/20';
    }
  };

  return (
    <div className={`p-4 rounded-xl border transition-all duration-300 flex items-center gap-3 ${getBorderColor()}`}>
      <div className="p-2 rounded-lg bg-white/5">{getIcon()}</div>
      <div>
        <h4 className="font-bold text-white text-sm">{persona}</h4>
        <span className="text-xs text-slate-400">
          {persona === 'Skeptical VC' && 'Defensibility & Moats'}
          {persona === 'Financial Analyst' && 'Unit Economics & Margins'}
          {persona === 'Market Realist' && 'Incumbents & GTM Timing'}
        </span>
      </div>
    </div>
  );
}
