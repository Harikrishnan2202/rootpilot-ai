import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Log endpoints
export const logAPI = {
  getLogs: (limit: number = 100, service?: string, level?: string) =>
    api.get("/logs/", { params: { limit, service, level } }),
  generateLogs: (count: number = 5) => api.post("/logs/generate", null, { params: { count } }),
  triggerIncident: (incidentType: string, duration: number = 10) =>
    api.post("/logs/trigger-incident", null, { params: { incident_type: incidentType, duration } }),
  getIncidentStatus: () => api.get("/logs/incident-status"),
  clearLogs: () => api.post("/logs/clear"),
};

// Analysis endpoints
export const analysisAPI = {
  analyze: (logs: any[], incidentId?: string) =>
    api.post("/analyze/", { logs, incident_id: incidentId }),
  health: () => api.get("/analyze/health"),
};

// Chat endpoints
export const chatAPI = {
  sendMessage: (question: string, incidentId?: string, logsContext?: any[]) =>
    api.post("/chat/", { question, incident_id: incidentId, logs_context: logsContext }),
  getSuggestions: (sessionId?: string) =>
    api.get("/chat/suggestions", { params: { session_id: sessionId } }),
  setContext: (sessionId: string, logs: any[], analysis?: any) =>
    api.post("/chat/context", { session_id: sessionId, logs, analysis }),
  clearContext: (sessionId: string) => api.delete(`/chat/${sessionId}`),
};