import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./vitest.setup.ts",
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        ".next/",
        "coverage/",
        "**/*.config.*",
        "**/*.test.*",
        "**/types/",
      ],
    },
  },
  resolve: {
    alias: [
      { find: "@/app", replacement: path.resolve(__dirname, "./src/app") },
      {
        find: "@/components",
        replacement: path.resolve(__dirname, "./components"),
      },
      {
        find: "@/contexts",
        replacement: path.resolve(__dirname, "./src/contexts"),
      },
      { find: "@/hooks", replacement: path.resolve(__dirname, "./src/hooks") },
      { find: "@/lib", replacement: path.resolve(__dirname, "./src/lib") },
      {
        find: "@/services",
        replacement: path.resolve(__dirname, "./src/services"),
      },
      { find: "@/types", replacement: path.resolve(__dirname, "./src/types") },
      { find: "@/utils", replacement: path.resolve(__dirname, "./src/utils") },
      { find: "@", replacement: path.resolve(__dirname, "./src") },
    ],
  },
});
