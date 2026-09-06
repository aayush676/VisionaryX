import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Proxy API calls through the dev server instead of having the browser talk
    // to the backend directly. This keeps requests same-origin (no CORS in dev)
    // and pins the backend to 127.0.0.1 explicitly -- on Windows `localhost`
    // resolves to IPv6 ::1 first, which uvicorn does not listen on by default,
    // so a direct browser call to localhost:8000 gets connection-refused.
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
})
