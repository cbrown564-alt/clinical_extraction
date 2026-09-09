"use client";
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
export default function PaperResults({ onApplications }: { onApplications: () => void }) {
  const [view, setView] = useState<View>("models");
  const [selected, setSelected] = useState(0);
  const meta = views.find(v => v.id === view)!;
  return <div className={s.chapter}>
    <div className={s.resultHeading}><span className={s.kicker}>The paper in perspective</span><h1>{meta.title}</h1><p>{meta.subtitle}</p></div>
    <nav className={s.resultTabs} aria-label="Results comparisons">{views.map(v => <button key={v.id} aria-pressed={view === v.id} onClick={() => { setView(v.id); setSelected(0); }}>{v.label}</button>)}</nav>
    <section className={s.resultsPanel} aria-label={meta.label}>
      <div className={s.chartMeta}><span>Purist micro-F1 · 0–1 scale · higher is better</span><span>{view === "external" ? "Real patient letters" : "Synthetic held-out test"}</span></div>
      {view === "models" && <>
        <div className={s.legend}><span><i data-series="provisional" />Provisional</span><span><i data-series="hybrid" />Hybrid</span><span><i data-series="llm" />LLM-only</span></div>
        <div className={s.modelChart}>{modelResults.map((m, i) => <button key={m.name} className={s.modelRow} aria-pressed={selected === i} onClick={() => setSelected(i)}><strong>{m.name}</strong><span className={s.barGroup}>{(["provisional", "hybrid", "llm"] as const).map(series => <span className={s.barTrack} key={series}><span className={s.bar} data-series={series} style={{ width: `${m[series] * 100}%` }} /><b style={{ left: `${m[series] * 100}%` }}>{m[series].toFixed(2)}<span className={s.srOnly}> {series}</span></b></span>)}</span></button>)}</div>
        <div className={s.chartInsight}><strong>{modelResults[selected].name}</strong><p>Rules add <b>+{(modelResults[selected].hybrid - modelResults[selected].provisional).toFixed(2)}</b> F1 after extraction. The second LLM call {modelResults[selected].llm >= modelResults[selected].provisional ? "adds" : "loses"} <b>{Math.abs(modelResults[selected].llm - modelResults[selected].provisional).toFixed(2)}</b> from the same provisional answer.</p></div>
      </>}
      {view === "ablations" && <><div className={s.legend}><span><i data-series="provisional" />Provisional</span><span><i data-series="hybrid" />After rules decide</span></div><div className={s.modelChart}>{ablationResults.map((a, i) => <button key={a.name} className={s.modelRow} aria-pressed={selected === i} onClick={() => setSelected(i)}><strong>{a.name}</strong><span className={s.barGroup}>{(["provisional", "hybrid"] as const).map(series => <span className={s.barTrack} key={series}><span className={s.bar} data-series={series} style={{ width: `${a[series] * 100}%` }} /><b style={{ left: `${a[series] * 100}%` }}>{a[series].toFixed(2)}<span className={s.srOnly}> {series}</span></b></span>)}</span></button>)}</div><div className={s.chartInsight}><strong>{ablationResults[selected].name}</strong><p>{ablationResults[selected].detail} {selected > 0 && `Final F1 falls by ${(ablationResults[0].hybrid - ablationResults[selected].hybrid).toFixed(2)}.`} These effects are not additive.</p></div></>}
      {view === "external" && <><div className={s.externalChart}>{externalResults.map(r => <div className={s.modelRow} key={r.name}><span><strong>{r.name}</strong><small>{r.model}</small></span><span className={s.barTrack}><span className={s.bar} data-series={r.name === "Hybrid" ? "hybrid" : r.name === "LLM-only" ? "llm" : "provisional"} style={{ width: `${r.value * 100}%` }} /><b style={{ left: `${r.value * 100}%` }}>{r.value.toFixed(2)}</b></span></div>)}</div><div className={s.chartInsight}><strong>Comparable scores on this sample</strong><p>The methods use different models and training procedures. This comparison does not isolate architecture alone, establish statistical superiority, or demonstrate clinical deployment readiness.</p></div></>}
      <details className={s.more}><summary><Info size={15} />Source and interpretation</summary><div><p>{meta.source}. Values are transcribed at the paper’s two-decimal precision. Purist micro-F1 is the share of letters with the correct fine-grained category for this single-label task.</p><p>{view === "external" ? "DeepSeek was run and scored outside the development environment. Real letters are not included in this demonstration." : "The synthetic data come from Gan 2026. Test results are aggregate-only; no held-out letter or error can be opened here. Hybrid replays recorded rules; LLM-only uses a second same-model decision call on the shared extraction record. The provisional answer is the extraction call’s own selection. Format repair and semantic decisions remain separate."}</p><p>{view === "models" ? "A numerical lead is not evidence of statistical superiority. Local-model results on this synthetic corpus demonstrate technical feasibility." : "These panels report the submitted study; they are not new experiments."}</p></div></details>
      {view === "ablations" && <PromptComponents selected={selected} />}
    </section>
    <div className={s.chapterEnd}><p>What could structured, traceable records make possible?</p><button className={base.primary} onClick={onApplications}>Explore applications <ArrowRight size={16} /></button></div>
  </div>;
}
