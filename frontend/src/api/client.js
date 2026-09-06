import axios from "axios";

// Empty in dev: requests go to the Vite dev server's own origin and are proxied
// to the backend (see vite.config.js). Set VITE_API_URL for production builds,
// where the frontend is served as static files with no proxy in front of it.
const BASE_URL = import.meta.env.VITE_API_URL || "";

const client = axios.create({ baseURL: BASE_URL });

function getTokens() {
  return {
    access: localStorage.getItem("vx_access_token"),
    refresh: localStorage.getItem("vx_refresh_token"),
  };
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem("vx_access_token", access_token);
  if (refresh_token) localStorage.setItem("vx_refresh_token", refresh_token);
}

export function clearTokens() {
  localStorage.removeItem("vx_access_token");
  localStorage.removeItem("vx_refresh_token");
}

client.interceptors.request.use((config) => {
  const { access } = getTokens();
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

let refreshPromise = null;

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthRoute = originalRequest?.url?.includes("/api/auth/");

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRoute) {
      originalRequest._retry = true;
      const { refresh } = getTokens();
      if (!refresh) {
        clearTokens();
        return Promise.reject(error);
      }

      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${BASE_URL}/api/auth/refresh`, { refresh_token: refresh })
            .finally(() => {
              refreshPromise = null;
            });
        }
        const { data } = await refreshPromise;
        setTokens(data);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return client(originalRequest);
      } catch (refreshError) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default client;
