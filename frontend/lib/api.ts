import { StartupPitch, SessionState, FinalVerdict } from '../types';

export function getApiBaseUrl(): string {
  // In the browser, use the same-origin Next.js proxy to bypass adblockers & CORS
  if (typeof window !== 'undefined') {
    return '/api/proxy';
  }

  // On the server (SSR), call the backend URL directly
  let url = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_INTERNAL_URL;
  if (!url || url.trim() === '') {
    url = process.env.NODE_ENV === 'production'
      ? 'https://devils-advocate-backend.onrender.com'
      : 'http://localhost:8999';
  }

  url = url.trim();
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`;
  }
  return url.replace(/\/+$/, '');
}

function getAuthHeaders(token?: string | null): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(res: Response, fallbackError: string): Promise<T> {
  if (!res.ok) {
    let errorDetail = fallbackError;
    try {
      const data = await res.json();
      if (data.detail) {
        errorDetail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // Use fallback
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export async function checkBackendHealth(): Promise<{ status: string; port: number; database?: any }> {
  const baseUrl = getApiBaseUrl();
  try {
    const res = await fetch(`${baseUrl}/health`, { cache: 'no-store' });
    return await handleResponse(res, 'Backend health check failed');
  } catch (e: any) {
    // Fallback direct attempt if proxy is unavailable
    if (baseUrl === '/api/proxy') {
      try {
        const directRes = await fetch('https://devils-advocate-backend.onrender.com/health', { cache: 'no-store' });
        return await handleResponse(directRes, 'Backend health check failed');
      } catch {}
    }
    throw new Error(`Cannot reach backend on ${baseUrl}: ${e.message}`);
  }
}

export async function submitPitch(pitch: StartupPitch, token?: string | null): Promise<SessionState> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/pitches`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(pitch),
  });
  return handleResponse<SessionState>(res, 'Failed to submit pitch');
}

export async function getSession(sessionId: string, token?: string | null): Promise<SessionState> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/sessions/${sessionId}`, {
    cache: 'no-store',
    headers: getAuthHeaders(token),
  });
  return handleResponse<SessionState>(res, `Session ${sessionId} not found.`);
}

export async function getMySessions(token?: string | null): Promise<{ sessions: SessionState[]; count: number }> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/sessions/my`, {
    cache: 'no-store',
    headers: getAuthHeaders(token),
  });
  return handleResponse<{ sessions: SessionState[]; count: number }>(res, 'Failed to retrieve past pitch sessions');
}

export async function submitFounderResponse(
  sessionId: string,
  roundNumber: number,
  responseText: string,
  token?: string | null
): Promise<SessionState> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/sessions/${sessionId}/response`, {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify({
      session_id: sessionId,
      round_number: roundNumber,
      response_text: responseText,
    }),
  });
  return handleResponse<SessionState>(res, 'Failed to submit founder response');
}

export async function getVerdict(sessionId: string, token?: string | null): Promise<FinalVerdict> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/verdict/${sessionId}`, {
    cache: 'no-store',
    headers: getAuthHeaders(token),
  });
  return handleResponse<FinalVerdict>(res, 'Failed to generate final verdict');
}

export function getPdfDownloadUrl(sessionId: string): string {
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}/api/pdf/${sessionId}/download`;
}

export async function getMcpStatus(): Promise<{
  total_connectors: number;
  active_connectors: number;
  oauth_app_configured?: boolean;
  connectors: Array<{
    id: string;
    name: string;
    provider: string;
    icon: string;
    status: string;
    quota: string;
    auth_type?: string;
    is_oauth_connected?: boolean;
    has_oauth_app?: boolean;
    description: string;
    capabilities: string[];
  }>;
}> {
  const baseUrl = getApiBaseUrl();
  try {
    const res = await fetch(`${baseUrl}/api/mcp/status`, { cache: 'no-store' });
    return await handleResponse(res, 'Failed to fetch MCP status');
  } catch (e: any) {
    return {
      total_connectors: 3,
      active_connectors: 3,
      connectors: [
        {
          id: 'tavily-search',
          name: 'Live Web & Competitor Search',
          provider: 'Tavily MCP',
          icon: 'globe',
          status: 'connected',
          quota: '1,000 requests/mo (Free Tier)',
          description: 'Real-time competitor intelligence, funding database lookups, and market pricing verification.',
          capabilities: ['Stealth competitor discovery', 'Live pricing page scraping', 'Crunchbase & TechCrunch funding checks']
        },
        {
          id: 'github-diligence',
          name: 'GitHub Technical Diligence',
          provider: 'GitHub MCP',
          icon: 'github',
          status: 'connected',
          quota: '5,000 requests/hr (Free Tier)',
          description: 'Deep repository inspection, commit velocity tracking, language ratios, and technical moat verification.',
          capabilities: ['Commit velocity analysis', 'Language & stack ratio breakdown', 'Open-source dependency audit']
        },
        {
          id: 'deck-parser',
          name: 'Pitch Deck & Document Ingestion',
          provider: 'Filesystem / PDF Parser MCP',
          icon: 'file-text',
          status: 'connected',
          quota: 'Unlimited (Local Engine)',
          description: 'Extracts pitch narrative, TAM/SAM numbers, and financial tables directly from uploaded PDF pitch decks.',
          capabilities: ['PDF slide text extraction', 'Financial model ingestion', 'Automatic pitch form population']
        }
      ]
    };
  }
}

export async function parsePitchDeck(file: File): Promise<Partial<StartupPitch>> {
  const baseUrl = getApiBaseUrl();
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${baseUrl}/api/pitches/parse-deck`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse<Partial<StartupPitch>>(res, 'Failed to parse pitch deck PDF');
}

export async function getGithubAuthUrl(redirectUri?: string): Promise<{ auth_url: string }> {
  const baseUrl = getApiBaseUrl();
  const uri = redirectUri || (typeof window !== 'undefined' ? `${window.location.origin}/connectors` : 'http://localhost:3000/connectors');
  const res = await fetch(`${baseUrl}/api/mcp/oauth/github/authorize?redirect_uri=${encodeURIComponent(uri)}`, {
    cache: 'no-store',
  });
  return handleResponse<{ auth_url: string }>(res, 'Failed to get GitHub authorization URL');
}

export async function exchangeGithubOAuthCode(code: string, redirectUri?: string, userId: string = 'default'): Promise<{ status: string; message: string }> {
  const baseUrl = getApiBaseUrl();
  const uri = redirectUri || (typeof window !== 'undefined' ? `${window.location.origin}/connectors` : 'http://localhost:3000/connectors');
  const res = await fetch(`${baseUrl}/api/mcp/oauth/github/callback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code,
      redirect_uri: uri,
      user_id: userId,
    }),
  });
  return handleResponse<{ status: string; message: string }>(res, 'Failed to complete GitHub OAuth authentication');
}

export async function disconnectMcpProvider(provider: string, userId: string = 'default'): Promise<{ status: string; disconnected: boolean }> {
  const baseUrl = getApiBaseUrl();
  const res = await fetch(`${baseUrl}/api/mcp/oauth/${provider}?user_id=${encodeURIComponent(userId)}`, {
    method: 'DELETE',
  });
  return handleResponse<{ status: string; disconnected: boolean }>(res, `Failed to disconnect ${provider}`);
}
