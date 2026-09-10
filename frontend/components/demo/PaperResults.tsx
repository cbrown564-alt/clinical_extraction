"use client";
import Image from "next/image";
import chart from "./resultsCharts.module.css";
import { useState } from "react";
import { ArrowRight, Info } from "lucide-react";
import { ablationResults, externalResults, modelResults } from "@/lib/demoResults";
import s from "./story.module.css";
import base from "./demo.module.css";
import PromptComponents from "./PromptComponents";

type View = "models" | "ablations" | "external";
const views: { id: View; label: string; title: string; subtitle: string; source: string }[] = [
  { id: "models", label: "Model comparison", title: "Rules beat pure LLM reasoning.", subtitle: "Combining LLM extraction with deterministic logic outperforms asking models to decide everything themselves.", source: "Extract, then decide · Table VII · 450 synthetic test letters" },
  { id: "ablations", label: "Prompt breakdown", title: "Which instructions matter most?", subtitle: "Evaluating the impact of examples, quotation requirements, and strict label formats while keeping the rules unchanged.", source: "Extract, then decide · Table IX · Gemini 3.7 Flash · 450 synthetic test letters" },
  { id: "external", label: "Real-world notes", title: "Validating on real patient charts.", subtitle: "Testing how synthetic-benchmarked methods hold up on 300 real hospital letters from Gan et al.", source: "Extract, then decide · Table V · Gan Real(300) · aggregate results only" },
];
type Series = "provisional" | "hybrid" | "llm";
function VerticalChart({ rows, selected, onSelect }: { rows: { name: string; model?: string; values: { series: Series; value: number }[] }[]; selected?: number; onSelect?: (index: number) => void }) {
  return <div className={chart.scroll}><div className={chart.chart} style={{ minWidth: rows.length * 140 + 32 }}>
    <div className={chart.axis} aria-hidden="true">{[1, .75, .5, .25, 0].map(value => <span key={value} style={{ bottom: value * 100 + "%" }}>{value.toFixed(2)}</span>)}</div>
    <div className={chart.groups}>{rows.map((row, index) => {
      const content = <><span className={chart.bars}>{row.values.map(({ series, value }) => <span className={chart.track} key={series}><span className={chart.bar} data-series={series} style={{ height: value * 100 + "%" }} /><b style={{ bottom: value * 100 + "%" }}>{value.toFixed(2)}<span className={s.srOnly}> {series}</span></b></span>)}</span><span className={chart.label}><strong>{row.name}</strong>{row.model && <small>{row.model}</small>}</span></>;
      return onSelect ? <button key={row.name} className={chart.group} aria-pressed={selected === index} onClick={() => onSelect(index)}>{content}</button> : <div className={chart.group} key={row.name}>{content}</div>;
    })}</div>
  </div></div>;
}
export default function PaperResults({ onApplications }: { onApplications: () => void }) {
  const [view, setView] = useState<View>("models");
  const [selected, setSelected] = useState(0);
  const meta = views.find(v => v.id === view)!;
  return <div className={s.chapter}>
    <div className={chart.heading}><div className={s.resultHeading}><span className={s.kicker}>Evaluation</span><h1>{meta.title}</h1><p>{meta.subtitle}</p></div><Image src="/demo/imagery/results-hero-v2.png" alt="" width={300} height={200} sizes="(max-width: 760px) 180px, 260px" className={chart.illustration} /></div>
    <nav className={s.resultTabs} aria-label="Results comparisons">{views.map(v => <button key={v.id} aria-pressed={view === v.id} onClick={() => { setView(v.id); setSelected(0); }}>{v.label}</button>)}</nav>
    <section className={s.resultsPanel} aria-label={meta.label}>
      <div className={s.chartMeta}><span>Classification accuracy (Micro-F1) · 0–1 scale · higher is better</span><span>{view === "external" ? "Real patient letters" : "Held-out test set"}</span></div>
      {view === "models" && <>
        <div className={s.legend}><span><i data-series="provisional" />Initial AI proposal</span><span><i data-series="llm" />Two-pass LLM</span><span><i data-series="hybrid" />Hybrid pipeline</span></div>
        <VerticalChart rows={modelResults.map(m => ({ name: m.name, values: (["provisional", "llm", "hybrid"] as const).map(series => ({ series, value: m[series] })) }))} selected={selected} onSelect={setSelected} />
        <div className={s.chartInsight}><strong>{modelResults[selected].name}</strong><p>Deterministic rules improve accuracy by <b>+{(modelResults[selected].hybrid - modelResults[selected].provisional).toFixed(2)}</b> over the initial proposal. A second generative LLM pass {modelResults[selected].llm >= modelResults[selected].provisional ? "gains" : "loses"} <b>{Math.abs(modelResults[selected].llm - modelResults[selected].provisional).toFixed(2)}</b> from the same starting facts.</p></div>
      </>}
      {view === "ablations" && <><div className={s.legend}><span><i data-series="provisional" />Initial AI proposal</span><span><i data-series="hybrid" />Final score with rules</span></div><VerticalChart rows={ablationResults.map(a => ({ name: a.name, values: (["provisional", "hybrid"] as const).map(series => ({ series, value: a[series] })) }))} selected={selected} onSelect={setSelected} /><div className={s.chartInsight}><strong>{ablationResults[selected].name}</strong><p>{ablationResults[selected].detail} {selected > 0 && `Overall accuracy drops by ${(ablationResults[0].hybrid - ablationResults[selected].hybrid).toFixed(2)} when this instruction is omitted.`}</p></div></>}
      {view === "external" && <><VerticalChart rows={externalResults.map(r => ({ name: r.name, model: r.model, values: [{ series: r.name === "Hybrid" ? "hybrid" : r.name === "LLM-only" ? "llm" : "provisional", value: r.value }] }))} /><div className={s.chartInsight}><strong>Competitive performance on real hospital charts</strong><p>The hybrid system matched the accuracy of an extensively fine-tuned model on real patient letters, while preserving full auditability and exact source citations.</p></div></>}
      <details className={s.more}><summary><Info size={15} />Source and evaluation methodology</summary><div><p>{meta.source}. Values are transcribed at the paper’s two-decimal precision. Micro-F1 measures the proportion of letters classified with the exact clinical category.</p><p>{view === "external" ? "DeepSeek was run and scored outside the development environment. Real hospital letters are confidential and not displayed in this demo." : "Synthetic test data are held-out evaluation letters from Gan 2026. Results are aggregate-only. Hybrid runs deterministic rules over the shared extraction record; two-pass LLM sends the record back into the model for a second prompt."}</p><p>{view === "models" ? "Local and open-weight models demonstrate that transparent extraction is practical without reliance on closed APIs." : "These panels report benchmark scores from the submitted study."}</p></div></details>
      {view === "ablations" && <PromptComponents selected={selected} />}
    </section>
    <div className={s.chapterEnd}><p>What could structured, traceable records make possible in practice?</p><button className={base.primary} onClick={onApplications}>Next: Practical use cases <ArrowRight size={16} /></button></div>
  </div>;
}
