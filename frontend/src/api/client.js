import axios from "axios";

// Base URL for the FastAPI backend.
// Override at build time with VITE_API_BASE_URL in a .env file, e.g.:
// VITE_API_BASE_URL=https://your-fastapi-host.com
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // resume parsing / NLP scoring can take a few seconds
});

// Attach an auth token automatically if one is stored (no-op if absent).
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("ra_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize FastAPI error shapes ({"detail": "..."} or validation arrays)
// into a single readable message so every screen can show one thing.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = "Something went wrong. Please try again.";
    const requestUrl = error.config?.url || "";

    if (error.code === "ECONNABORTED") {
      message = "The request timed out. The server may be busy — try again.";
    } else if (error.response) {
      const { data, status } = error.response;
      if (typeof data?.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data?.detail)) {
        // FastAPI / Pydantic validation error array
        message = data.detail
          .map((d) => d.msg || JSON.stringify(d))
          .join(" ");
      } else if (status === 404) {
        message = "We couldn't find that on the server.";
      } else if (status >= 500) {
        message = "The server hit an error processing this. Please retry.";
      } else if (status === 401 && !requestUrl.startsWith("/auth/")) {
        localStorage.removeItem("ra_token");
        localStorage.removeItem("ra_user");
        if (typeof window !== "undefined" && !["/login", "/signup"].includes(window.location.pathname)) {
          window.location.assign("/login");
        }
      }
    } else if (error.request) {
      message = "Can't reach the server. Check your connection and that the API is running.";
    }

    return Promise.reject({ ...error, friendlyMessage: message });
  }
);

export default apiClient;
