import { defineConfig } from "vite";
import vinext from "vinext";
import { cloudflare } from "@cloudflare/vite-plugin";
import { createHash } from "node:crypto";
import { patchCssModules } from "vite-css-modules";
import path from "node:path";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  define: {
    "process.env.NEXT_PUBLIC_DEMO_SURFACE": JSON.stringify("1"),
  },
  resolve: {
    alias: {
      "@/lib/server/fixture-store": path.resolve(import.meta.dirname, "lib/server/fixture-store.cloudflare.ts"),
    },
  },
  plugins: [
    tailwindcss(),
    patchCssModules({ exportMode: "default" }),
    vinext(),
    cloudflare({
      viteEnvironment: {
        name: "rsc",
        childEnvironments: ["ssr"],
      },
    }),
  ],
  css: {
    postcss: { plugins: [] },
    modules: {
      generateScopedName(name: string, filename: string) {
        const relativePath = path.relative(import.meta.dirname, filename.replace(/\?.*$/, "")).replaceAll("\\", "/");
        return `_${name}_${createHash("sha256").update(relativePath).digest("hex").slice(0, 7)}`;
      },
    },
  },
});
