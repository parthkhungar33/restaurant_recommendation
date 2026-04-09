import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const api = env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";

  return {
    server: {
      port: 5173,
      proxy: {
        "/recommendations": { target: api, changeOrigin: true },
        "/metadata": { target: api, changeOrigin: true },
        "/health": { target: api, changeOrigin: true },
      },
    },
  };
});
