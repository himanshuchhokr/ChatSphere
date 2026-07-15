const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

function getTokens() {
  return {
    access: localStorage.getItem('access'),
    refresh: localStorage.getItem('refresh'),
  };
}

function setTokens({ access, refresh }) {
  if (access) localStorage.setItem('access', access);
  if (refresh) localStorage.setItem('refresh', refresh);
}

function clearTokens() {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
}

async function refreshAccessToken() {
  const { refresh } = getTokens();
  if (!refresh) throw new Error('No refresh token');
  const res = await fetch(`${BASE_URL}/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) {
    clearTokens();
    throw new Error('Session expired, please log in again');
  }
  const data = await res.json();
  setTokens({ access: data.access });
  return data.access;
}

async function apiFetch(path, options = {}, retry = true) {
  const { access } = getTokens();
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (access) headers['Authorization'] = `Bearer ${access}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401 && retry) {
    await refreshAccessToken();
    return apiFetch(path, options, false);
  }

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    const message = errBody.detail || JSON.stringify(errBody) || `Request failed (${res.status})`;
    throw new Error(message);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  async register(username, email, password) {
    return apiFetch('/register/', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    }, false);
  },

  async login(username, password) {
    const res = await fetch(`${BASE_URL}/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error('Invalid username or password');
    const data = await res.json();
    setTokens(data);
    return data;
  },

  logout() {
    clearTokens();
  },

  isLoggedIn() {
    return !!getTokens().access;
  },

  getRooms: () => apiFetch('/rooms/'),
  createRoom: (name) => apiFetch('/rooms/', { method: 'POST', body: JSON.stringify({ name }) }),
  joinRoom: (id) => apiFetch(`/rooms/${id}/join/`, { method: 'POST' }),
  getMessages: (id) => apiFetch(`/rooms/${id}/messages/`),

  /**
   * Opens a WebSocket connection for a room, authenticated via the current
   * access token passed as a query param (browsers can't set custom headers
   * on WebSocket handshakes).
   */
  connectToRoom(slug) {
    const { access } = getTokens();
    return new WebSocket(`${WS_URL}/ws/chat/${slug}/?token=${access}`);
  },
};
