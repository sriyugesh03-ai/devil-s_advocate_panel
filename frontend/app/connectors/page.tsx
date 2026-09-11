'use client';

import React, { useEffect, useState } from 'react';
import {
  getMcpStatus,
  getGithubAuthUrl,
  exchangeGithubOAuthCode,
  disconnectMcpProvider,
} from '../../lib/api';
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
  KeyRound,
  LogOut,
  AlertCircle,
  Check,
} from 'lucide-react';

export default function ConnectorsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
  const [notification, setNotification] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);

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

  // Check URL for GitHub OAuth code return
  useEffect(() => {
    const handleOAuthCallback = async () => {
      if (typeof window === 'undefined') return;
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');

      if (code) {
        setOauthLoading(true);
        setNotification({
          type: 'info',
          message: 'Exchanging GitHub OAuth code for access token...',
        });

        try {
          const redirectUri = `${window.location.origin}/connectors`;
          const res = await exchangeGithubOAuthCode(code, redirectUri);

          if (res.status === 'success') {
            setNotification({
              type: 'success',
              message: 'GitHub OAuth connected successfully! Live repo diligence is active.',
            });
          } else {
            setNotification({
              type: 'error',
              message: res.message || 'Failed to exchange GitHub authorization code.',
            });
          }
        } catch (err: any) {
          setNotification({
            type: 'error',
            message: err.message || 'Error completing GitHub authorization.',
          });
        } finally {
          // Clean URL params
          window.history.replaceState({}, document.title, window.location.pathname);
          setOauthLoading(false);
          fetchStatus();
        }
      }
    };

    handleOAuthCallback();
    fetchStatus();
    setEnabledState(getMcpEnabledState());

    const handler = () => setEnabledState(getMcpEnabledState());
    window.addEventListener('mcp-config-changed', handler);
    return () => window.removeEventListener('mcp-config-changed', handler);
  }, []);

  const handleStartGithubOAuth = async () => {
    setOauthLoading(true);
    try {
      const redirectUri = `${window.location.origin}/connectors`;
      const res = await getGithubAuthUrl(redirectUri);
      if (res?.auth_url && !res.auth_url.includes('client_id=&')) {
        window.location.href = res.auth_url;
      } else {
        throw new Error('GITHUB_CLIENT_ID is not configured in the backend environment variables. Please add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET to your environment.');
      }
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: err.message || 'Failed to initiate GitHub OAuth.',
      });
      setOauthLoading(false);
    }
  };

  const handleDisconnectGithub = async () => {
    setOauthLoading(true);
    try {
      await disconnectMcpProvider('github');
      setNotification({
        type: 'info',
        message: 'GitHub OAuth credentials disconnected. Falling back to default diligence token.',
      });
      fetchStatus();
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: err.message || 'Failed to disconnect GitHub account.',
      });
    } finally {
      setOauthLoading(false);
    }
  };

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

  const getStatusBadge = (conn: any, isEnabled: boolean) => {
    if (!isEnabled) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
          <XCircle className="w-3 h-3" /> Disabled
        </span>
      );
    }
    if (conn.status === 'connected') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3" /> Connected
        </span>
      );
    }
    if (conn.status === 'ready_to_connect') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-violet-950/60 text-violet-300 border border-violet-500/30">
          <KeyRound className="w-3 h-3" /> OAuth Ready
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
          <span>Model Context Protocol (MCP) & OAuth Center</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          External Diligence Connectors
        </h1>
        <p className="text-sm text-slate-400 max-w-2xl">
          Connect live external tools that enrich the AI panel's cross-examination with real-time competitor data, technical codebase audits, and pitch deck parsing.
        </p>
      </div>

      {/* Notification Banner */}
      {notification && (
        <div
          className={`flex items-center justify-between p-4 rounded-xl border text-sm animate-in fade-in duration-200 ${
            notification.type === 'success'
              ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-200'
              : notification.type === 'error'
              ? 'bg-rose-950/70 border-rose-500/40 text-rose-200'
              : 'bg-cyan-950/70 border-cyan-500/40 text-cyan-200'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {notification.type === 'success' ? (
              <Check className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : notification.type === 'error' ? (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            ) : (
              <RefreshCw className="w-4 h-4 text-cyan-400 shrink-0 animate-spin" />
            )}
            <span>{notification.message}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-xs opacity-70 hover:opacity-100 underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

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
          const isGithub = conn.id === 'github-diligence';

          return (
            <div
              key={conn.id}
              className={`relative p-6 rounded-2xl border transition-all flex flex-col justify-between space-y-5 ${
                isEnabled
                  ? 'glass-panel border-white/10 hover:border-cyan-500/30 hover:shadow-lg hover:shadow-cyan-950/20'
                  : 'bg-darkbg-900/60 border-white/5 opacity-70'
              }`}
            >
              <div className="space-y-4">
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
                      <span className="text-xs text-slate-400">
                        {conn.provider}
                      </span>
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
                  {getStatusBadge(conn, isEnabled)}
                  <span className="text-[11px] text-slate-500 font-mono">
                    {conn.auth_type || conn.quota}
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

              {/* GitHub OAuth Action Section */}
              {isGithub && (
                <div className="pt-3 border-t border-white/10 space-y-2">
                  {conn.is_oauth_connected ? (
                    <div className="flex items-center justify-between bg-violet-950/40 p-2.5 rounded-xl border border-violet-500/20">
                      <div className="flex items-center gap-2 text-xs text-violet-300 font-medium">
                        <CheckCircle2 className="w-3.5 h-3.5 text-violet-400" />
                        <span>OAuth Authorized</span>
                      </div>
                      <button
                        onClick={handleDisconnectGithub}
                        disabled={oauthLoading}
                        className="inline-flex items-center gap-1 text-[11px] text-rose-400 hover:text-rose-300 transition-colors"
                      >
                        <LogOut className="w-3 h-3" />
                        Disconnect
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={handleStartGithubOAuth}
                      disabled={oauthLoading || !isEnabled}
                      className="w-full py-2 px-3 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-sm"
                    >
                      <Github className="w-3.5 h-3.5" />
                      {oauthLoading ? 'Redirecting...' : 'Authorize with GitHub (OAuth 2.0)'}
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer Note */}
      <div className="flex items-center gap-2 text-xs text-slate-400 pt-2">
        <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
        <span>
          Dynamic OAuth flow auto-adapts to your current environment URL (localhost or deployed production).
        </span>
      </div>
    </div>
  );
}
