import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import wasm from "vite-plugin-wasm";
import path from "path";
const LIB = path.resolve(process.env.ARTCRAFT_EDITOR_SRC!);
export default defineConfig({
  plugins: [react(), wasm()],
  resolve: { alias: { "@ve": path.join(LIB, "src") } },
  build: { target: "esnext", outDir: process.env.OUT_DIR || "dist", emptyOutDir: true },
  worker: { format: "es", plugins: () => [wasm()] },
  define: { "process.env.NODE_ENV": JSON.stringify("production") },
});
