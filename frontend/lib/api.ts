import { StartupPitch, SessionState, FinalVerdict } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8999';

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

export async function checkBackendHealth(): Promise<{ status: string; port: number }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
    return await handleResponse(res, 'Backend health check failed');
  } catch (e: any) {
    throw new Error(`Cannot reach backend on ${API_BASE_URL}: ${e.message}`);
  }
}

export async function submitPitch(pitch: StartupPitch): Promise<SessionState> {
  const res = await fetch(`${API_BASE_URL}/api/pitches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(pitch),
  });
  return handleResponse<SessionState>(res, 'Failed to submit pitch');
}

export async function getSession(sessionId: string): Promise<SessionState> {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    cache: 'no-store',
  });
  return handleResponse<SessionState>(res, `Session ${sessionId} not found.`);
}

export async function submitFounderResponse(
  sessionId: string,
  roundNumber: number,
  responseText: string
): Promise<SessionState> {
  const res = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/response`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      round_number: roundNumber,
      response_text: responseText,
    }),
  });
  return handleResponse<SessionState>(res, 'Failed to submit founder response');
}

export async function getVerdict(sessionId: string): Promise<FinalVerdict> {
  const res = await fetch(`${API_BASE_URL}/api/verdict/${sessionId}`, {
    cache: 'no-store',
  });
  return handleResponse<FinalVerdict>(res, 'Failed to generate final verdict');
}

export function getPdfDownloadUrl(sessionId: string): string {
  return `${API_BASE_URL}/api/pdf/${sessionId}/download`;
}
