'use client';

/**
 * Shared MCP connector state management.
 * Persists enabled/disabled state in localStorage and broadcasts changes
 * via a custom window event so all components stay in sync.
 */

export const MCP_STORAGE_KEY = 'mcp_connectors_enabled_state';

export interface McpEnabledState {
  'tavily-search': boolean;
  'github-diligence': boolean;
  'deck-parser': boolean;
}

const DEFAULT_STATE: McpEnabledState = {
  'tavily-search': true,
  'github-diligence': true,
  'deck-parser': true,
};

export function getMcpEnabledState(): McpEnabledState {
  if (typeof window === 'undefined') return { ...DEFAULT_STATE };
  try {
    const saved = localStorage.getItem(MCP_STORAGE_KEY);
    if (saved) return { ...DEFAULT_STATE, ...JSON.parse(saved) };
  } catch {}
  return { ...DEFAULT_STATE };
}

export function setMcpEnabledState(state: McpEnabledState): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(MCP_STORAGE_KEY, JSON.stringify(state));
  window.dispatchEvent(new Event('mcp-config-changed'));
}

export function toggleMcpConnector(id: keyof McpEnabledState): McpEnabledState {
  const current = getMcpEnabledState();
  const next: McpEnabledState = { ...current, [id]: !current[id] };
  setMcpEnabledState(next);
  return next;
}

export function setAllMcpConnectors(enabled: boolean): McpEnabledState {
  const next: McpEnabledState = {
    'tavily-search': enabled,
    'github-diligence': enabled,
    'deck-parser': enabled,
  };
  setMcpEnabledState(next);
  return next;
}

export function getMcpActiveCount(): number {
  const state = getMcpEnabledState();
  return Object.values(state).filter(Boolean).length;
}
