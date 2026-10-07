import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';

// Reuse the existing route handlers to preserve their exact public dev response.
// Enumerate only tracked dev750/dev140 scores; never read locked-test rows.
export async function packageScoredResponses(assets) {
  const files = spawnSync('git', ['ls-files', 'results/letter-benchmarks'], { cwd: '..', encoding: 'utf8' });
  if (files.status !== 0) throw new Error('Cannot enumerate published dev scores');
  const routes = new Set();
  const exectSlugs = new Set();
  for (const file of files.stdout.trim().split('\n')) {
    const match = /^results\/letter-benchmarks\/(gan|exect)\/([^/]+)\/([^/]+)\/(dev750|dev140)\/scored\.jsonl$/.exec(file);
    if (!match) continue;
    const [, task, method, slug, split] = match;
    if (task === 'gan' && split === 'dev750') routes.add(`gan/dev750/${method}/${slug}/scored`);
    if (task === 'exect' && split === 'dev140') exectSlugs.add(slug);
  }
  // Public ExECT route aliases are preserved by calling its existing handler.
  const methods = ['exect_llm_only','exect_llm_pre_post','exect_llm_with_rules','llm_extract','llm_encode','llm_select','llm_schema','llm_revise','llm_format','llm_post','llm_pre_post'];
  for (const slug of exectSlugs) for (const method of methods) routes.add(`exect/dev140/${method}/${slug}/scored`);
  const gan = await import('../app/api/paper/gan/dev750/[method]/[slug]/scored/route.ts');
  const exect = await import('../app/api/paper/exect/dev140/[method]/[slug]/scored/route.ts');
  let count = 0;
  for (const route of routes) {
    const [task,,method,slug] = route.split('/');
    const response = await (task === 'gan' ? gan : exect).GET(new Request('https://demo.example/api/paper/'+route), { params: Promise.resolve({ method, slug }) });
    if (response.status !== 200) continue;
    const output = path.join(assets, '_saved-api', 'api/paper', route);
    mkdirSync(path.dirname(output), { recursive: true });
    writeFileSync(output, await response.text());
    count++;
  }
  console.log(`Packaged ${count} existing public development-score responses; no locked rows`);
}
