'use client';

import React, { useEffect, useState } from 'react';
import { getMcpStatus } from '../../lib/api';
import {
  getMcpEnabledState,
  toggleMcpConnector,
  setAllMcpConnectors,
  McpEnabledState,
} from '../../lib/mcp-state';
import {
  Globe,
  Github,
  FileText,
  Zap,
  RefreshCw,
  ShieldCheck,
  Cpu,
  ExternalLink,
  CheckCircle2,
  XCircle,
} from 'lucide-react';

export default function ConnectorsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [enabledState, setEnabledState] = useState<McpEnabledState>(
    getMcpEnabledState()
  );

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await getMcpStatus();
      setData(res);
    } catch {}
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
    setEnabledState(getMcpEnabledState());
    const handler = () => setEnabledState(getMcpEnabledState());
    window.addEventListener('mcp-config-changed', handler);
    return () => window.removeEventListener('mcp-config-changed', handler);
  }, []);

  const handleToggle = (id: keyof McpEnabledState) => {
    const next = toggleMcpConnector(id);
    setEnabledState(next);
  };

  const handleToggleAll = (enabled: boolean) => {
    const next = setAllMcpConnectors(enabled);
    setEnabledState(next);
  };

  const activeCount = Object.values(enabledState).filter(Boolean).length;

  const getIcon = (iconName: string, isEnabled: boolean) => {
    const cls = isEnabled ? '' : 'opacity-40';
    switch (iconName) {
      case 'globe':
        return <Globe className={`w-7 h-7 text-cyan-400 ${cls}`} />;
      case 'github':
        return <Github className={`w-7 h-7 text-violet-400 ${cls}`} />;
      case 'file-text':
        return <FileText className={`w-7 h-7 text-amber-400 ${cls}`} />;
      default:
        return <Cpu className={`w-7 h-7 text-rose-400 ${cls}`} />;
    }
  };

  const getStatusBadge = (status: string, isEnabled: boolean) => {
    if (!isEnabled) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
          <XCircle className="w-3 h-3" /> Disabled
        </span>
      );
    }
    if (status === 'connected') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3" /> Connected
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-950/60 text-amber-300 border border-amber-500/30">
          <Cpu className="w-3 h-3" /> Fallback
      </span>
    );
  };

  return (
    <div className="flex-1 p-6 sm:p-8 lg:p-10 max-w-6xl mx-auto w-full space-y-8">
      {/* Page Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-semibold">
          <Zap className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>Model Context Protocol (MCP)</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          External Diligence Connectors
        </h1>
        <p className="text-sm text-slate-400 max-w-2xl">
          Connect and manage live external tools that enrich the AI panel's cross-examination with real-time competitor data, technical codebase audits, and pitch deck parsing.
        </p>
      </div>

      {/* Summary Bar */}
      <div className="flex flex-wrap items-center gap-4 p-5 rounded-2xl bg-darkbg-800/60 border border-white/5">
        <div className="flex-1 min-w-[140px]">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            Configured
          </span>
          <span className="text-xl font-bold text-white">
            {data?.total_connectors || 3} Tools
          </span>
        </div>
        <div className="flex-1 min-w-[140px]">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
            Currently Active
          </span>
          <span className="text-xl font-bold text-emerald-400 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            {activeCount} of 3 Enabled
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleToggleAll(true)}
            className="px-3 py-2 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-xs font-semibold text-emerald-300 hover:bg-emerald-900/60 transition-colors"
          >
            All ON
          </button>
          <button
            onClick={() => handleToggleAll(false)}
            className="px-3 py-2 rounded-xl bg-slate-800/80 border border-white/10 text-xs font-semibold text-slate-300 hover:bg-slate-700/80 transition-colors"
          >
            All OFF
          </button>
          <button
            onClick={fetchStatus}
            disabled={loading}
            className="p-2 rounded-xl bg-darkbg-700 border border-white/10 text-slate-300 hover:text-white transition-colors"
            title="Refresh status"
          >
            <RefreshCw
              className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`}
            />
          </button>
        </div>
      </div>

      {/* Connector Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {data?.connectors?.map((conn: any) => {
          const isEnabled =
            enabledState[conn.id as keyof McpEnabledState] !== false;

          return (
            <div
              key={conn.id}
              className={`relative p-6 rounded-2xl border transition-all space-y-5 ${
                isEnabled
                  ? 'glass-panel border-white/10 hover:border-cyan-500/30 hover:shadow-lg hover:shadow-cyan-950/20'
                  : 'bg-darkbg-900/60 border-white/5 opacity-70'
              }`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`p-3 rounded-xl border ${
                      isEnabled
                        ? 'bg-darkbg-800 border-white/10'
                        : 'bg-darkbg-900 border-white/5'
                    }`}
                  >
                    {getIcon(conn.icon, isEnabled)}
                  </div>
                  <div>
                    <h3
                      className={`text-base font-bold ${
                        isEnabled
                          ? 'text-white'
                          : 'text-slate-400 line-through decoration-slate-600'
                      }`}
                    >
                      {conn.name}
                    </h3>
                    <span className="text-xs text-slate-400">{conn.provider}</span>
                  </div>
                </div>

                {/* Toggle Switch */}
                <button
                  type="button"
                  onClick={() =>
                    handleToggle(conn.id as keyof McpEnabledState)
                  }
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

              {/* Status & Quota */}
              <div className="flex items-center justify-between">
                {getStatusBadge(conn.status, isEnabled)}
                <span className="text-[11px] text-slate-500 font-mono">
                  {conn.quota}
                </span>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-300 leading-relaxed">
                {conn.description}
              </p>

              {/* Capabilities */}
              <div className="flex flex-wrap gap-1.5">
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

      {/* Footer Note */}
      <div className="flex items-center gap-2 text-xs text-slate-400 pt-2">
        <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
        <span>
          Toggle changes take effect on your next pitch submission. All MCP tools operate within 100% free-tier quotas.
        </span>
      </div>
    </div>
  );
}
