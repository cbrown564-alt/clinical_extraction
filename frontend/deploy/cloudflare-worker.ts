import app from 'vinext/server/fetch-handler';

const worker = {
  async fetch(request: Request, env: Cloudflare.Env, ctx: ExecutionContext) {
    const url = new URL(request.url);
    // Data resources are reachable only through their existing public API routes.
    if (url.pathname.startsWith('/_saved-api/')) return new Response('Not found', { status: 404 });
    if (['GET', 'HEAD'].includes(request.method) && /^\/api\/paper\/(gan\/dev750|exect\/dev140)\/[^/]+\/[^/]+\/scored\/?$/.test(url.pathname)) {
      const saved = new URL(request.url);
      saved.pathname = '/_saved-api'+url.pathname.replace(/\/$/, '');
      saved.search = '';
      const response = await env.ASSETS.fetch(new Request(saved, request));
      if (response.ok) {
        const headers = new Headers(response.headers);
        headers.set('Content-Type', 'application/json');
        return new Response(response.body, { status: response.status, headers });
      }
    }
    return app.fetch(request, env, ctx);
  },
};

export default worker;
