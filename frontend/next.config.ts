import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    root: process.cwd(),
  },
  async headers() {
    return process.env.CF_MIGRATION_MODE === "migration-preview" ? [{
      source: "/:path*",
      headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }],
    }] : [];
  },
  async redirects() {
    return [
      {
        source: "/architect",
        destination: "/workbench",
        permanent: true,
      },
    ];
  },
  async rewrites() {
    // Vercel has no loopback Python service. Its bundled route handlers serve
    // the public mock fixtures instead; local development can still opt into
    // the full API when the research service is running.
    if (process.env.VERCEL === "1" || process.env.NEXT_PUBLIC_DEMO_SURFACE === "1") return [];
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
