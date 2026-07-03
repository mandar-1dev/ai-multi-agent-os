const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("agentos_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export const api = {
  base: BASE_URL,

  register: (email: string, password: string, full_name?: string) =>
    request<{ access_token: string; user_id: string; api_key: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string; user_id: string; api_key: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request("/api/auth/me"),

  agents: () => request<any[]>("/api/agents"),
  agentDefinitions: () => request<any[]>("/api/agents/definitions"),

  tasks: (status?: string) => request<any[]>(`/api/tasks${status ? `?status=${status}` : ""}`),

  chat: (message: string, user_id?: string) =>
    request<any>("/api/chat", { method: "POST", body: JSON.stringify({ message, user_id }) }),

  workflowTemplates: () => request<any[]>("/api/workflows/templates"),
  listWorkflows: () => request<any[]>("/api/workflows"),
  runWorkflow: (workflow_name: string, goal: string, user_id?: string) =>
    request<any>("/api/workflows/run", { method: "POST", body: JSON.stringify({ workflow_name, goal, user_id }) }),

  recentMemory: (memory_type?: string) =>
    request<any[]>(`/api/memory/recent${memory_type ? `?memory_type=${memory_type}` : ""}`),
  recallMemory: (query: string, memory_type?: string) =>
    request<any[]>("/api/memory/recall", { method: "POST", body: JSON.stringify({ query, memory_type }) }),

  documents: () => request<any[]>("/api/documents"),
  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/api/documents/upload`, {
      method: "POST",
      headers: { ...authHeaders() },
      body: form,
    });
    return res.json();
  },

  knowledgeGraph: () => request<{ nodes: any[]; edges: any[] }>("/api/knowledge-graph"),
  extractGraph: (text: string) =>
    request<any>("/api/knowledge-graph/extract", { method: "POST", body: JSON.stringify({ text }) }),

  dashboardStats: () => request<any>("/api/dashboard/stats"),
};

export function wsUrl(): string {
  const url = new URL(BASE_URL);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = "/ws/agent-status";
  return url.toString();
}

export function setToken(token: string) {
  localStorage.setItem("agentos_token", token);
}
export function getToken(): string | null {
  return localStorage.getItem("agentos_token");
}
export function clearToken() {
  localStorage.removeItem("agentos_token");
}
