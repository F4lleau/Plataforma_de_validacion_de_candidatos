import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  server: {
    headers: { "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" },
  },
  preview: {
    headers: { "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
