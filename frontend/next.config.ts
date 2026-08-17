import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    root: process.cwd(),
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
    if (process.env.VERCEL === "1") return [];
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
