const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('technopie_token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Network response was not ok' }));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    return res.json() as Promise<T>;
  } catch (err: any) {
    // If it's already a handled error with specific detail, re-throw
    if (err.message && !err.message.includes('Failed to fetch') && !err.message.includes('NetworkError')) {
      throw err;
    }

    const isBrowser = typeof window !== 'undefined';
    const isProdHost = isBrowser && !window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1');
    const isLocalBackend = API_BASE.includes('localhost') || API_BASE.includes('127.0.0.1');

    if (isProdHost && isLocalBackend) {
      throw new Error(
        `Cloud Configuration Error: The frontend is attempting to call '${API_BASE}', which is a local address. ` +
        `Please set 'NEXT_PUBLIC_API_URL' in your Render Frontend Environment to your backend URL (e.g. https://<your-backend>.onrender.com/api) and trigger 'Clear build cache & deploy'.`
      );
    }

    const origin = isBrowser ? window.location.origin : 'your frontend origin';
    throw new Error(
      `Connection failed to backend at ${API_BASE}. ` +
      `Check that: 1) The backend Web Service is active on Render (free tier cold starts take 30-50s), and 2) '${origin}' is added to the backend's 'CORS_ORIGINS' environment variable.`
    );
  }
}
