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



