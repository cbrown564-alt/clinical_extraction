import { bindings, defineConfig, defineWorker } from "cf/config";

export default defineConfig(({ mode }) => ({
  accountId: "e1909c4d4aec0a75a0a34fc15ee35482",
  worker: defineWorker({
    name: (process.env.CF_MIGRATION_MODE ?? mode) === "production"
      ? "clinical-extraction" : "clinical-extraction-migration-preview",
    entrypoint: "./deploy/cloudflare-worker.ts",
    compatibilityDate: "2026-10-07",
    compatibilityFlags: ["nodejs_compat"],
    workersDev: true,
    observability: { enabled: true, traces: { enabled: true, headSamplingRate: 0.01 } },
    assets: { notFoundHandling: "none", runWorkerFirst: ["/mock-data/*", "/api/*", "/_saved-api/*"] },
    env: {
      ASSETS: bindings.assets(),
      NEXT_PUBLIC_DEMO_SURFACE: bindings.text("1"),
    },
  }),
}));
