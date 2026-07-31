import { NextResponse } from "next/server";

export function proxy() {
  return new NextResponse(null, {
    status: 404,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

export const config = {
  matcher: "/mock-data/:path*",
};
