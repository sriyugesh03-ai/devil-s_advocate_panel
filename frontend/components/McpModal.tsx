'use client';

import React, { useEffect, useState } from 'react';
import { getMcpStatus } from '../lib/api';
import { 
  Globe, 
  Github, 
  FileText, 
  CheckCircle2, 
  ShieldCheck, 
  X, 
  Cpu, 
  RefreshCw, 
  Zap, 
  Power,
  ToggleLeft,
  ToggleRight,
  ShieldOff
} from 'lucide-react';

interface McpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MCP_STORAGE_KEY = 'mcp_connectors_enabled_state';

export function getMcpEnabledState(): Record<string, boolean> {
  if (typeof window === 'undefined') {
    return { 'tavily-search': true, 'github-diligence': true, 'deck-parser': true };
  }
  try {
    const saved = localStorage.getItem(MCP_STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch {}
  return { 'tavily-search': true, 'github-diligence': true, 'deck-parser': true };
}

export default function McpModal({ isOpen, onClose }: McpModalProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [enabledState, setEnabledState] = useState<Record<string, boolean>>({
    'tavily-search': true,
    'github-diligence': true,
    'deck-parser': true
  });

  useEffect(() => {
    setEnabledState(getMcpEnabledState());
  }, [isOpen]);

  const toggleConnector = (id: string) => {
    const nextState = {
      ...enabledState,
      [id]: !enabledState[id]
    };
    setEnabledState(nextState);
    if (typeof window !== 'undefined') {
      localStorage.setItem(MCP_STORAGE_KEY, JSON.stringify(nextState));
      window.dispatchEvent(new Event('mcp-config-changed'));
    }
  };

  const toggleAll = (enable: boolean) => {
    const nextState = {
      'tavily-search': enable,
      'github-diligence': enable,
      'deck-parser': enable,
    };
    setEnabledState(nextState);
    if (typeof window !== 'undefined') {
      localStorage.setItem(MCP_STORAGE_KEY, JSON.stringify(nextState));
      window.dispatchEvent(new Event('mcp-config-changed'));
    }
  };

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await getMcpStatus();
      setData(res);
    } catch {
      // Handled in api.ts fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const getIcon = (iconName: string, isEnabled: boolean) => {
    if (!isEnabled) {
      return <Cpu className="w-5 h-5 text-slate-500" />;
    }
    switch (iconName) {
      case 'globe':
        return <Globe className="w-5 h-5 text-cyan-400" />;
      case 'github':
        return <Github className="w-5 h-5 text-violet-400" />;
      case 'file-text':
        return <FileText className="w-5 h-5 text-amber-400" />;
      default:
        return <Cpu className="w-5 h-5 text-rose-400" />;
    }
  };

  const activeCount = Object.values(enabledState).filter(Boolean).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-darkbg-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-2xl rounded-2xl bg-darkbg-900 border border-white/10 p-6 sm:p-8 shadow-2xl space-y-6 text-left max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-white/10 pb-5">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
              <Zap className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              <span>Model Context Protocol (MCP) Control Center</span>
            </div>
            <h2 className="text-2xl font-black text-white flex items-center gap-2">
              MCP External Diligence Hub
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Toggle live external tools and databases on or off with a single click.
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-darkbg-800 border border-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Top Summary Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-darkbg-800/80 border border-white/5 items-center">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Configured</span>
            <span className="text-lg font-bold text-white">{data?.total_connectors || 3} Tools</span>
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Live Active</span>
            <span className="text-lg font-bold text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              {activeCount} of 3 Enabled
            </span>
          </div>
          <div className="col-span-2 sm:col-span-1 flex items-center justify-start sm:justify-end gap-2">
            <button
              onClick={() => toggleAll(true)}
              className="px-2.5 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/30 text-xs font-semibold text-emerald-300 hover:bg-emerald-900/60 transition-colors"
            >
              All ON
            </button>
            <button
              onClick={() => toggleAll(false)}
              className="px-2.5 py-1.5 rounded-lg bg-slate-800/80 border border-white/10 text-xs font-semibold text-slate-300 hover:bg-slate-700/80 transition-colors"
            >
              All OFF
            </button>
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="p-2 rounded-lg bg-darkbg-700 border border-white/10 text-slate-300 hover:text-white flex items-center justify-center transition-colors"
              title="Refresh MCP status"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Connectors List with Interactive ON / OFF Switches */}
        <div className="space-y-4">
          {data?.connectors?.map((conn: any) => {
            const isEnabled = enabledState[conn.id] !== false;

            return (
              <div 
                key={conn.id} 
                className={`p-5 rounded-xl border transition-all space-y-3 ${
                  isEnabled 
                    ? 'glass-panel border-white/10 hover:border-cyan-500/30' 
                    : 'bg-darkbg-800/40 border-white/5 opacity-70'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded-xl border ${isEnabled ? 'bg-darkbg-800 border-white/10' : 'bg-darkbg-900 border-white/5'}`}>
                      {getIcon(conn.icon, isEnabled)}
                    </div>
                    <div>
                      <h3 className={`text-sm font-bold ${isEnabled ? 'text-white' : 'text-slate-400 line-through decoration-slate-600'}`}>
                        {conn.name}
                      </h3>
                      <span className="text-xs text-slate-400">
                        {conn.provider} • <strong className="text-slate-300">{conn.quota}</strong>
                      </span>
                    </div>
                  </div>

                  {/* Interactive ON / OFF Switch */}
                  <div className="flex items-center gap-3 self-end sm:self-auto">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
                      isEnabled 
                        ? 'bg-emerald-950/60 border-emerald-500/30 text-emerald-300' 
                        : 'bg-slate-800 border-slate-700 text-slate-400'
                    }`}>
                      {isEnabled ? 'ON' : 'OFF'}
                    </span>

                    <button
                      type="button"
                      onClick={() => toggleConnector(conn.id)}
                      className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        isEnabled ? 'bg-emerald-600' : 'bg-slate-700'
                      }`}
                      role="switch"
                      aria-checked={isEnabled}
                    >
                      <span
                        className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          isEnabled ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-300">
                  {conn.description}
                </p>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {conn.capabilities?.map((cap: string, i: number) => (
                    <span 
                      key={i} 
                      className={`px-2 py-0.5 rounded-md border text-[11px] font-medium ${
                        isEnabled 
                          ? 'bg-darkbg-800/90 border-white/5 text-slate-400' 
                          : 'bg-darkbg-900 border-white/5 text-slate-600'
                      }`}
                    >
                      {isEnabled ? '✓' : '✗'} {cap}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1.5 text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Instant toggle takes effect on your next pitch submission.
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-colors"
          >
            Save & Close
          </button>
        </div>
      </div>
    </div>
  );
}

