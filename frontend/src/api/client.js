import axios from "axios";

export const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      error.message = "Network error. Please check your connection.";
    } else if (error.response.status === 401) {
      localStorage.clear();
      window.location.href = "/login";
    } else if (error.response.status >= 500) {
      error.message = "Server error. Please try again later.";
    } else if (error.response.status === 404) {
      error.message = "Resource not found.";
    } else if (error.response.status === 400) {
      error.message = error.response.data?.detail || "Invalid request.";
    }
    return Promise.reject(error);
  }
);

export async function withRetry(fn, retries = 3, delay = 1000) {
  try {
    return await fn();
  } catch (error) {
    if (retries <= 0 || error.response?.status === 401) throw error;
    await new Promise((r) => setTimeout(r, delay));
    return withRetry(fn, retries - 1, delay * 2);
  }
}

export default client;