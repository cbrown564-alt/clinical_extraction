#!/usr/bin/env node

import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SOURCE = path.join(
  ROOT,
  "docs/research/gan2026_full_research_retrospective_2026-06-02.md",
);
const HTML_OUT = path.join(
  ROOT,
  "docs/research/gan2026_full_research_retrospective_2026-06-02.html",
);
const PDF_OUT = path.join(
  ROOT,
  "docs/research/gan2026_full_research_retrospective_2026-06-02.pdf",
);
const SHOT_OUT = path.join(
  ROOT,
  "docs/research/gan2026_full_research_retrospective_2026-06-02.preview.png",
);
const WANT_PREVIEW = process.argv.includes("--preview");

function loadPlaywright() {
  try {
    return require("playwright");
  } catch {
    return require(
      "/Users/cobro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright",
    );
  }
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/`([^`]+)`/g, "$1")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 90);
}

function inline(value) {
  const code = [];
  let text = value.replace(/`([^`]+)`/g, (_, body) => {
    code.push(`<code>${escapeHtml(body)}</code>`);
    return `@@CODE${code.length - 1}@@`;
  });
  text = escapeHtml(text);
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  code.forEach((replacement, index) => {
    text = text.replace(`@@CODE${index}@@`, replacement);
  });
  return text;
}

function splitTableRow(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function renderTable(lines) {
  const header = splitTableRow(lines[0]);
  const rows = lines.slice(2).map(splitTableRow);
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${header.map((cell) => `<th>${inline(cell)}</th>`).join("")}</tr></thead>
        <tbody>
          ${rows
            .map(
              (row) =>
                `<tr>${row.map((cell) => `<td>${inline(cell)}</td>`).join("")}</tr>`,
            )
            .join("\n")}
        </tbody>
      </table>
    </div>`;
}

function renderMarkdown(markdown) {
  const rawLines = markdown.replace(/\r\n/g, "\n").split("\n");
  const lines = [];
  let title = "Gan 2026 Full Research Retrospective";
  let date = "2026-06-02";

  for (let i = 0; i < rawLines.length; i += 1) {
    const line = rawLines[i];
    if (i === 0 && line.startsWith("# ")) {
      title = line.slice(2).trim();
      continue;
    }
    if (line.startsWith("Date: ")) {
      date = line.slice("Date: ".length).trim();
      continue;
    }
    lines.push(line);
  }

  const toc = [];
  const html = [];
  let paragraph = [];
  let list = null;

  function flushParagraph() {
    if (paragraph.length === 0) return;
    html.push(`<p>${inline(paragraph.join(" "))}</p>`);
    paragraph = [];
  }

  function flushList() {
    if (!list) return;
    html.push(`<${list.type}>${list.items.map((item) => `<li>${inline(item)}</li>`).join("")}</${list.type}>`);
    list = null;
  }

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];

    if (line.startsWith("```")) {
      flushParagraph();
      flushList();
      const language = line.slice(3).trim();
      const body = [];
      i += 1;
      while (i < lines.length && !lines[i].startsWith("```")) {
        body.push(lines[i]);
        i += 1;
      }
      if (language === "mermaid") {
        html.push(`<figure class="diagram"><div class="mermaid">${escapeHtml(body.join("\n"))}</div></figure>`);
      } else {
        html.push(`<pre><code>${escapeHtml(body.join("\n"))}</code></pre>`);
      }
      continue;
    }

    if (/^\|.+\|$/.test(line) && i + 1 < lines.length && /^\|\s*:?-+/.test(lines[i + 1])) {
      flushParagraph();
      flushList();
      const tableLines = [line, lines[i + 1]];
      i += 2;
      while (i < lines.length && /^\|.+\|$/.test(lines[i])) {
        tableLines.push(lines[i]);
        i += 1;
      }
      i -= 1;
      html.push(renderTable(tableLines));
      continue;
    }

    const heading = line.match(/^(#{2,4})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      const text = heading[2].trim();
      const id = slugify(text);
      if (level === 2) toc.push({ id, text: text.replace(/`/g, "") });
      html.push(`<h${level} id="${id}">${inline(text)}</h${level}>`);
      continue;
    }

    const unordered = line.match(/^\s*-\s+(.+)$/);
    const ordered = line.match(/^\s*\d+\.\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const type = unordered ? "ul" : "ol";
      if (!list || list.type !== type) {
        flushList();
        list = { type, items: [] };
      }
      list.items.push((unordered || ordered)[1].trim());
      continue;
    }

    if (list && /^\s{2,}\S/.test(line)) {
      list.items[list.items.length - 1] += ` ${line.trim()}`;
      continue;
    }

    if (line.trim() === "") {
      flushParagraph();
      flushList();
      continue;
    }

    paragraph.push(line.trim());
  }

  flushParagraph();
  flushList();

  return { title, date, toc, body: html.join("\n") };
}

function pageTemplate({ title, date, toc, body }) {
  const tocItems = toc
    .map((item) => `<a href="#${item.id}">${inline(item.text)}</a>`)
    .join("\n");

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(title)}</title>
  <style>
    :root {
      color-scheme: light;
      --paper: #f7f9fb;
      --page: #ffffff;
      --ink: #182026;
      --muted: #66727d;
      --quiet: #8c98a4;
      --line: #dfe5ea;
      --line-strong: #c6d0d9;
      --teal: #1f6f72;
      --blue: #315f9a;
      --green: #52733a;
      --red: #9a3f3f;
      --gold: #9b741e;
      --slate: #384653;
      --measure: 760px;
    }

    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 17px;
      line-height: 1.68;
      letter-spacing: 0;
    }

    a {
      color: var(--blue);
      text-decoration-color: rgba(49, 95, 154, 0.35);
      text-underline-offset: 0.18em;
    }

    .shell {
      display: grid;
      grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
      gap: 44px;
      max-width: 1280px;
      margin: 0 auto;
      padding: 42px 38px 80px;
    }

    .toc {
      position: sticky;
      top: 28px;
      align-self: start;
      padding-top: 22px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .toc .label {
      margin-bottom: 18px;
      color: var(--ink);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .toc a {
      display: block;
      padding: 8px 0;
      border-top: 1px solid rgba(198, 208, 217, 0.58);
      color: var(--muted);
      text-decoration: none;
    }

    .toc a:hover {
      color: var(--ink);
    }

    .page {
      min-width: 0;
      background: var(--page);
      border: 1px solid var(--line);
      box-shadow: 0 24px 80px rgba(56, 70, 83, 0.12);
    }

    .hero {
      padding: 72px 74px 46px;
      border-bottom: 1px solid var(--line);
    }

    .hero-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 16px 26px;
      margin-bottom: 26px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
      letter-spacing: 0.02em;
    }

    h1, h2, h3, h4 {
      margin: 0;
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      font-weight: 500;
      letter-spacing: 0;
    }

    h1 {
      max-width: 820px;
      font-size: clamp(44px, 6vw, 76px);
      line-height: 0.96;
    }

    .dek {
      max-width: 760px;
      margin-top: 30px;
      color: #34414c;
      font-size: 22px;
      line-height: 1.52;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1px;
      margin-top: 42px;
      border: 1px solid var(--line-strong);
      background: var(--line-strong);
    }

    .summary-card {
      min-height: 150px;
      padding: 20px;
      background: #fbfcfd;
    }

    .summary-card strong {
      display: block;
      margin-bottom: 10px;
      color: var(--ink);
      font-size: 12px;
      letter-spacing: 0.11em;
      text-transform: uppercase;
    }

    .summary-card span {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }

    article {
      padding: 18px 74px 80px;
    }

    article > h2 {
      margin-top: 72px;
      padding-top: 32px;
      border-top: 2px solid var(--ink);
      font-size: 38px;
      line-height: 1.12;
    }

    article > h3 {
      margin-top: 38px;
      font-size: 27px;
      line-height: 1.2;
    }

    article > h4 {
      margin-top: 28px;
      color: var(--slate);
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      font-size: 15px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    p, ul, ol, .table-wrap, pre, figure {
      max-width: var(--measure);
    }

    p {
      margin: 18px 0 0;
    }

    ul, ol {
      margin: 18px 0 0;
      padding-left: 1.25rem;
    }

    li + li {
      margin-top: 8px;
    }

    code {
      padding: 0.08em 0.28em;
      border: 1px solid #dce3e8;
      background: #f4f7f9;
      border-radius: 4px;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.86em;
    }

    pre {
      overflow: auto;
      margin: 24px 0 0;
      padding: 18px;
      border: 1px solid var(--line);
      background: #f5f8fa;
      border-radius: 6px;
      font-size: 13px;
      line-height: 1.5;
    }

    pre code {
      padding: 0;
      border: 0;
      background: transparent;
    }

    .table-wrap {
      overflow-x: auto;
      margin: 26px 0 0;
      border: 1px solid var(--line-strong);
      background: white;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      line-height: 1.42;
    }

    th, td {
      padding: 12px 13px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }

    th {
      background: #eef3f6;
      color: var(--slate);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    tr:last-child td {
      border-bottom: 0;
    }

    figure.diagram {
      margin: 30px 0 0;
      padding: 22px;
      border: 1px solid var(--line-strong);
      background: #fbfcfd;
      break-inside: avoid;
    }

    .mermaid {
      display: flex;
      justify-content: center;
      overflow-x: auto;
    }

    .mermaid svg {
      max-width: 100%;
      height: auto;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
    }

    article > h2:nth-of-type(2) { border-top-color: var(--teal); }
    article > h2:nth-of-type(3) { border-top-color: var(--blue); }
    article > h2:nth-of-type(4) { border-top-color: var(--green); }
    article > h2:nth-of-type(5) { border-top-color: var(--gold); }
    article > h2:nth-of-type(6) { border-top-color: var(--red); }

    @media (max-width: 980px) {
      .shell {
        display: block;
        padding: 18px;
      }

      .toc {
        position: static;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0 18px;
        margin-bottom: 18px;
        padding: 0;
      }

      .toc .label {
        grid-column: 1 / -1;
      }

      .hero, article {
        padding-left: 28px;
        padding-right: 28px;
      }

      .summary-grid {
        grid-template-columns: 1fr;
      }
    }

    @page {
      size: A4;
      margin: 16mm 16mm 18mm;
    }

    @media print {
      :root {
        --paper: #ffffff;
      }

      body {
        background: white;
        color: #111820;
        font-size: 11.3pt;
        line-height: 1.48;
      }

      .shell {
        display: block;
        max-width: none;
        padding: 0;
      }

      .toc {
        display: none;
      }

      .page {
        border: 0;
        box-shadow: none;
      }

      .hero {
        min-height: 0;
        padding: 0 0 12mm;
        border-bottom: 0;
        break-after: page;
      }

      .hero-meta {
        font-size: 9.5pt;
      }

      h1 {
        font-size: 34pt;
        line-height: 1.02;
      }

      .dek {
        font-size: 15pt;
        line-height: 1.42;
      }

      .summary-grid {
        margin-top: 12mm;
        break-inside: avoid;
      }

      .summary-card {
        min-height: 0;
        padding: 11pt;
      }

      article {
        padding: 0;
      }

      article > h2 {
        margin-top: 12mm;
        padding-top: 7mm;
        font-size: 22pt;
        break-after: avoid;
      }

      article > h3 {
        margin-top: 8mm;
        font-size: 16pt;
        break-after: avoid;
      }

      p, ul, ol, .table-wrap, pre, figure {
        max-width: none;
      }

      p {
        orphans: 3;
        widows: 3;
      }

      table {
        font-size: 8.8pt;
      }

      th, td {
        padding: 6pt 7pt;
      }

      .table-wrap {
        overflow: visible;
        break-inside: auto;
      }

      figure.diagram {
        padding: 10pt;
        break-inside: avoid;
      }

      a {
        color: inherit;
        text-decoration: none;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <nav class="toc" aria-label="Table of contents">
      <div class="label">Contents</div>
      ${tocItems}
    </nav>
    <div class="page">
      <header class="hero">
        <div class="hero-meta">
          <span>Clinical Extraction Research</span>
          <span>${escapeHtml(date)}</span>
          <span>Gan 2026 seizure-frequency retrospective</span>
        </div>
        <h1>${escapeHtml(title)}</h1>
        <p class="dek">A print-ready synthesis of six architecture families, what each one taught us, and how close the program is to its core research thesis.</p>
        <div class="summary-grid" aria-label="Retrospective summary">
          <div class="summary-card"><strong>Best transparent comparator</strong><span>Rules-only V1 reaches 0.9293 Purist on validation, but falls to about 0.7600 on locked test.</span></div>
          <div class="summary-card"><strong>Core attribution lesson</strong><span>The 0.9000 structured-events validation result is repair-heavy hybrid behavior, not clean LLM-first success.</span></div>
          <div class="summary-card"><strong>Current research path</strong><span>The state graph now separates coverage, projection, boundary nodes, invariance, and arbitration.</span></div>
        </div>
      </header>
      <article>
        ${body}
      </article>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    window.__mermaidDone = false;
    async function renderMermaid() {
      if (!window.mermaid) {
        window.__mermaidDone = true;
        return;
      }
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "loose",
        theme: "base",
        themeVariables: {
          fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
          primaryColor: "#f7fafc",
          primaryTextColor: "#182026",
          primaryBorderColor: "#9fb0bf",
          lineColor: "#66727d",
          secondaryColor: "#eef4f7",
          tertiaryColor: "#ffffff",
          clusterBkg: "#f6f9fb",
          clusterBorder: "#c6d0d9"
        }
      });
      try {
        await mermaid.run({ querySelector: ".mermaid" });
      } finally {
        window.__mermaidDone = true;
      }
    }
    renderMermaid();
  </script>
</body>
</html>`;
}

async function renderPdf() {
  const { chromium } = loadPlaywright();
  const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  const launchOptions = { headless: true };
  try {
    await fs.access(chromePath);
    launchOptions.executablePath = chromePath;
  } catch {
    // Fall back to Playwright's managed browser when it is installed.
  }
  const browser = await chromium.launch(launchOptions);
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
    await page.goto(pathToFileURL(HTML_OUT).href, { waitUntil: "networkidle" });
    try {
      await page.waitForFunction(() => window.__mermaidDone === true, { timeout: 20000 });
    } catch {
      console.warn("Mermaid render did not finish before timeout; continuing with available DOM.");
    }
    if (WANT_PREVIEW) {
      await page.screenshot({ path: SHOT_OUT, fullPage: false });
    }
    await page.emulateMedia({ media: "print" });
    await page.pdf({
      path: PDF_OUT,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: "16mm", right: "16mm", bottom: "18mm", left: "16mm" },
    });
  } finally {
    await browser.close();
  }
}

async function main() {
  const markdown = await fs.readFile(SOURCE, "utf8");
  const rendered = renderMarkdown(markdown);
  await fs.writeFile(HTML_OUT, pageTemplate(rendered), "utf8");
  await renderPdf();
  console.log(`HTML: ${HTML_OUT}`);
  console.log(`PDF: ${PDF_OUT}`);
  if (WANT_PREVIEW) {
    console.log(`Preview: ${SHOT_OUT}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
