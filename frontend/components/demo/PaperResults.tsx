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
  { id: "models", label: "Across models", title: "One record. Two ways to decide.", subtitle: "Recorded rules improve the provisional answer for all six models. A second LLM call is less consistent.", source: "Extract, then decide · Table VII · 450 synthetic test letters" },
  { id: "ablations", label: "Prompt ablations", title: "The extraction prompt matters.", subtitle: "Remove one ingredient at a time. Keep the decision rules fixed.", source: "Extract, then decide · Table IX · Gemini 3.7 Flash · 450 synthetic test letters" },
  { id: "external", label: "Real letters", title: "Beyond the synthetic corpus.", subtitle: "An independently scored comparison on the same 300 real patient letters used by Gan et al.", source: "Extract, then decide · Table V · Gan Real(300) · aggregate results only" },
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
    <div className={chart.heading}><div className={s.resultHeading}><span className={s.kicker}>The paper in perspective</span><h1>{meta.title}</h1><p>{meta.subtitle}</p></div><Image src="/demo/imagery/results-hero-v2.png" alt="" width={300} height={200} sizes="(max-width: 760px) 180px, 260px" className={chart.illustration} /></div>
    <nav className={s.resultTabs} aria-label="Results comparisons">{views.map(v => <button key={v.id} aria-pressed={view === v.id} onClick={() => { setView(v.id); setSelected(0); }}>{v.label}</button>)}</nav>
    <section className={s.resultsPanel} aria-label={meta.label}>
      <div className={s.chartMeta}><span>Purist micro-F1 · 0–1 scale · higher is better</span><span>{view === "external" ? "Real patient letters" : "Synthetic held-out test"}</span></div>
      {view === "models" && <>
        <div className={s.legend}><span><i data-series="provisional" />Provisional</span><span><i data-series="llm" />LLM-only</span><span><i data-series="hybrid" />Hybrid</span></div>
        <VerticalChart rows={modelResults.map(m => ({ name: m.name, values: (["provisional", "llm", "hybrid"] as const).map(series => ({ series, value: m[series] })) }))} selected={selected} onSelect={setSelected} />
        <div className={s.chartInsight}><strong>{modelResults[selected].name}</strong><p>Rules add <b>+{(modelResults[selected].hybrid - modelResults[selected].provisional).toFixed(2)}</b> F1 after extraction. The second LLM call {modelResults[selected].llm >= modelResults[selected].provisional ? "adds" : "loses"} <b>{Math.abs(modelResults[selected].llm - modelResults[selected].provisional).toFixed(2)}</b> from the same provisional answer.</p></div>
      </>}
      {view === "ablations" && <><div className={s.legend}><span><i data-series="provisional" />Provisional</span><span><i data-series="hybrid" />After rules decide</span></div><VerticalChart rows={ablationResults.map(a => ({ name: a.name, values: (["provisional", "hybrid"] as const).map(series => ({ series, value: a[series] })) }))} selected={selected} onSelect={setSelected} /><div className={s.chartInsight}><strong>{ablationResults[selected].name}</strong><p>{ablationResults[selected].detail} {selected > 0 && `Final F1 falls by ${(ablationResults[0].hybrid - ablationResults[selected].hybrid).toFixed(2)}.`} These effects are not additive.</p></div></>}
      {view === "external" && <><VerticalChart rows={externalResults.map(r => ({ name: r.name, model: r.model, values: [{ series: r.name === "Hybrid" ? "hybrid" : r.name === "LLM-only" ? "llm" : "provisional", value: r.value }] }))} /><div className={s.chartInsight}><strong>Comparable scores on this sample</strong><p>The methods use different models and training procedures. This comparison does not isolate architecture alone, establish statistical superiority, or demonstrate clinical deployment readiness.</p></div></>}
      <details className={s.more}><summary><Info size={15} />Source and interpretation</summary><div><p>{meta.source}. Values are transcribed at the paper’s two-decimal precision. Purist micro-F1 is the share of letters with the correct fine-grained category for this single-label task.</p><p>{view === "external" ? "DeepSeek was run and scored outside the development environment. Real letters are not included in this demonstration." : "The synthetic data come from Gan 2026. Test results are aggregate-only; no held-out letter or error can be opened here. Hybrid replays recorded rules; LLM-only uses a second same-model decision call on the shared extraction record. The provisional answer is the extraction call’s own selection. Format repair and semantic decisions remain separate."}</p><p>{view === "models" ? "A numerical lead is not evidence of statistical superiority. Local-model results on this synthetic corpus demonstrate technical feasibility." : "These panels report the submitted study; they are not new experiments."}</p></div></details>
      {view === "ablations" && <PromptComponents selected={selected} />}
    </section>
    <div className={s.chapterEnd}><p>What could structured, traceable records make possible?</p><button className={base.primary} onClick={onApplications}>Explore applications <ArrowRight size={16} /></button></div>
  </div>;
}
