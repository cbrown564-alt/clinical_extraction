/**
 * Local Next route handlers exist so Vercel can serve fixtures. When the
 * Python trace-explorer is running, prefer it so paper cells hydrate from
 * paper_experiments instead of the static mock.
 */
export async function proxyPython(
  path: string,
  init?: RequestInit
): Promise<Response | null> {
  if (process.env.VERCEL === "1") return null;
  try {
    const upstream = await fetch(`http://127.0.0.1:8000${path}`, init);
    if (!upstream.ok) return null;
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type":
          upstream.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch {
    return null;
  }
}
