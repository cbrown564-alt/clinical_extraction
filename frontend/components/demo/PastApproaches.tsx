"use client";

import { useEffect, useState } from "react";
import { ArrowDown, FileText, Play, RotateCcw } from "lucide-react";
import s from "./pastApproaches.module.css";

const methods = [
  { name: "Rules", verb: "Write the rules.", kind: "rules", detail: "Explicit patterns and domain vocabularies make decisions inspectable, but varied phrasing and context require ongoing rule work. EpiDEA extends cTAKES with an epilepsy ontology and supports visual cohort queries.", cite: "Cui et al. · EpiDEA", href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC3540531/" },
  { name: "Trained models", verb: "Learn from labelled examples.", kind: "trained", detail: "Supervised models learn a task from labelled notes. Chang et al. compare fine-tuned BERT with DeepSeek-R1 for epilepsy and seizure-type phenotyping. Those are different targets from seizure frequency.", cite: "Chang et al. · 2026 preprint", href: "https://doi.org/10.64898/2026.02.11.26346003" },
  { name: "Prompted LLMs", verb: "Specify the task in a prompt.", kind: "prompted", detail: "Instructions and examples steer a pretrained model. CLINES uses a specification-driven workflow for extraction and structuring; SNOW uses multiple LLM agents to generate predictive features. These related systems address broader tasks and use different architectures.", cite: "Yang et al. · CLINES, 2025 preprint", href: "https://doi.org/10.64898/2025.12.01.25341355" },
];

function Rules() {
  return <div className={s.machine} aria-label="Handwritten rules match a frequency phrase, check its context, and map it to a field">
    <svg viewBox="0 0 300 244" role="img" aria-label="Match a phrase, then check: current? Yes: map frequency. No: skip this mention.">
      <path className={s.activePath} d="M150 0v22m0 44v18m0 66v26m0 36v32m-4-72 4 4 4-4" />
      <path className={s.skipPath} d="M228 117h40v33m-4-5 4 5 4-5" />
      <rect className={s.ruleShape} x="88" y="22" width="124" height="44" rx="4" />
      <text x="150" y="49">Match phrase</text>
      <path className={s.ruleShape} d="m150 84 78 33-78 33-78-33z" />
      <text x="150" y="122">Current?</text>
      <text className={s.smallText} x="177" y="163">Yes</text>
      <text className={s.smallText} x="263" y="109">No</text>
      <rect className={s.ruleShape} x="77" y="176" width="146" height="36" rx="4" />
      <text x="150" y="199">Map frequency</text>
      <rect className={s.skipShape} x="240" y="151" width="56" height="30" rx="15" />
      <text x="268" y="171">Skip</text>
    </svg>
    <span className={s.machineCaption}>Patterns + vocabulary</span>
  </div>;
}
function Trained() {
  return <div className={s.machine} aria-label="Labelled examples train a model. A new letter passes through the trained model.">
    <svg viewBox="0 0 300 244" role="img" aria-label="Annotated examples feed training from the side; the new letter flows vertically through a learned network">
      <path className={s.activePath} d="M184 0v93m0 112v39" />
      <g className={s.examples}>
        <rect x="11" y="23" width="98" height="43" rx="3" /><rect x="17" y="29" width="98" height="43" rx="3" /><rect x="23" y="35" width="98" height="43" rx="3" />
        <text x="72" y="52">“every day”</text><text className={s.exampleLabel} x="72" y="68">→ daily</text>
      </g>
      <path className={s.trainingPath} d="M72 82v67h42m-7-5 7 5-7 5" />
      <text className={s.smallText} x="72" y="105">Train</text>
      <rect className={s.networkBody} x="114" y="92" width="140" height="114" rx="22" />
      {[128, 156, 184, 212, 240].slice(0, 4).map((x, i) => [120, 149, 178].flatMap(y => [120, 149, 178].map(nextY => <line key={`${x}-${y}-${nextY}`} className={s.networkLink} x1={x} y1={y} x2={128 + (i + 1) * 28} y2={nextY} />)))}
      {[128, 156, 184, 212, 240].map(x => [120, 149, 178].map(y => <circle key={`${x}-${y}`} className={s.networkDot} cx={x} cy={y} r="4" />))}
    </svg>
    <span className={s.machineCaption}>Learned model weights</span>
  </div>;
}
function Prompted() {
  return <div className={s.machine} aria-label="A new letter and task instructions enter a pretrained language model together">
    <svg viewBox="0 0 300 244" role="img" aria-label="Instructions join the letter at runtime and enter a pretrained language model">
      <path className={s.activePath} d="M184 0v123m0 77v44" />
      <path className={s.promptSheet} d="M15 21h94l14 14v68H15z" /><path className={s.otherPath} d="M109 21v14h14" />
      <text className={s.promptTitle} x="69" y="47">Instructions</text>
      <text className={s.smallText} x="69" y="67">Find the current</text><text className={s.smallText} x="69" y="83">seizure frequency.</text>
      <path className={s.activePath} d="M69 106v56h44m-7-5 7 5-7 5" />
      <rect className={s.llmBody} x="113" y="125" width="142" height="75" rx="12" />
      <text className={s.llmTitle} x="184" y="158">LLM</text><text className={s.llmSubtitle} x="184" y="181">Pretrained model</text>
    </svg>
    <span className={s.machineCaption}>Instructions at runtime</span>
  </div>;
}

export default function PastApproaches() {
  const [tracing, setTracing] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);
  useEffect(() => {
    if (!tracing) return;
    const timer = window.setTimeout(() => setTracing(false), 3600);
    return () => window.clearTimeout(timer);
  }, [tracing]);
  return <section className={s.section} aria-labelledby="past-approaches-title">
    <div className={s.heading}><div><span className={s.eyebrow}>Past approaches</span><h2 id="past-approaches-title">Same task. Different machinery.</h2><p>Turn a clinic letter into structured data. Where does the task knowledge come from?</p></div>
      <button className={s.traceButton} disabled={tracing} onClick={() => { setHasPlayed(true); if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) setTracing(true); }}>{hasPlayed ? <RotateCcw size={15} /> : <Play size={15} />}{tracing ? "Tracing…" : "Trace a letter"}</button>
    </div>
    <div className={s.scrollHint}>Three approaches · scroll sideways to compare</div>
    <div className={s.comparisonScroll} role="region" aria-label="Three pipeline comparison" tabIndex={0}>
      <div className={s.comparison} data-tracing={tracing}>
        {methods.map((method, i) => <article className={s.lane} data-kind={method.kind} key={method.kind}>
          <header><h3>{method.name}</h3><p>{method.verb}</p></header>
          <div className={s.letter}><span><FileText size={14} />Clinic letter</span><p>“Now, <mark>two each month.</mark>”</p><div className={s.textLines} aria-hidden="true"><i /><i /></div></div>
          <ArrowDown className={s.arrow} size={20} aria-hidden="true" />
          <div className={s.processor}>{i === 0 ? <Rules /> : i === 1 ? <Trained /> : <Prompted />}</div>
          <ArrowDown className={s.arrow} size={20} aria-hidden="true" />
          <div className={s.output}><span>Structured data</span><div><span>Frequency</span><strong>2 / month</strong></div></div>
          <details className={s.details}><summary>Context & source</summary><p>{method.detail}</p><a href={method.href} target="_blank" rel="noreferrer">{method.cite} ↗</a></details>
        </article>)}
      </div>
    </div>
    <p className={s.note}>Illustrative flows, not measured predictions. The cited systems address different clinical tasks; the shared example shows the idea of extraction.</p>
  </section>;
}
