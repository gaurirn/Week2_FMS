import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite configuration: dev server on :5173, proxy `/api` to FastAPI.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
