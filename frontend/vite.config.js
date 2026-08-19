import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/health": "http://127.0.0.1:8000",
      "/catalog": "http://127.0.0.1:8000",
      "/domains": "http://127.0.0.1:8000",
      "/intents": "http://127.0.0.1:8000",
      "/capabilities": "http://127.0.0.1:8000",
      "/enterprises": "http://127.0.0.1:8000",
      "/use-cases": "http://127.0.0.1:8000",
      "/demo": "http://127.0.0.1:8000",
      "/explore": "http://127.0.0.1:8000",
      "/executions": "http://127.0.0.1:8000",
      "/coverage": "http://127.0.0.1:8000",
      "/demand": "http://127.0.0.1:8000",
      "/meet": "http://127.0.0.1:8000",
      "/map": "http://127.0.0.1:8000",
      "/preflight": "http://127.0.0.1:8000",
      "/start": "http://127.0.0.1:8000",
    },
  },
});
