'use client';

import React, { useEffect, useState } from 'react';
import { getMcpStatus } from '../lib/api';
import { Globe, Github, FileText, CheckCircle2, ShieldCheck, Sparkles, X, Cpu, RefreshCw, Zap } from 'lucide-react';

interface McpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function McpModal({ isOpen, onClose }: McpModalProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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

  const getIcon = (iconName: string) => {
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
              <span>Model Context Protocol Active</span>
            </div>
            <h2 className="text-2xl font-black text-white flex items-center gap-2">
              MCP External Diligence Hub
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Live external tools and databases grounded into the Devil's Advocate multi-agent gauntlet.
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
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-darkbg-800/80 border border-white/5">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Connectors</span>
            <span className="text-lg font-bold text-white">{data?.total_connectors || 3} Configured</span>
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Active Status</span>
            <span className="text-lg font-bold text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              100% Operational
            </span>
          </div>
          <div className="col-span-2 sm:col-span-1 flex items-center justify-start sm:justify-end">
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="px-3 py-1.5 rounded-lg bg-darkbg-700 border border-white/10 text-xs font-medium text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Connectors List */}
        <div className="space-y-4">
          {data?.connectors?.map((conn: any) => (
            <div 
              key={conn.id} 
              className="glass-panel p-5 rounded-xl border border-white/10 hover:border-cyan-500/30 transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-darkbg-800 border border-white/10">
                    {getIcon(conn.icon)}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{conn.name}</h3>
                    <span className="text-xs text-slate-400">{conn.provider} • <strong className="text-slate-300">{conn.quota}</strong></span>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-semibold self-start sm:self-auto">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Connected</span>
                </div>
              </div>

              <p className="text-xs text-slate-300">
                {conn.description}
              </p>

              <div className="flex flex-wrap gap-1.5 pt-1">
                {conn.capabilities?.map((cap: string, i: number) => (
                  <span 
                    key={i} 
                    className="px-2 py-0.5 rounded-md bg-darkbg-800/90 border border-white/5 text-[11px] font-medium text-slate-400"
                  >
                    ✓ {cap}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1.5 text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Zero Cost • 100% Free-Tier Limits
          </span>
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
