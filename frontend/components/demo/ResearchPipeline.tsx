"use client";

import { useEffect, useState } from "react";
import { ArrowDown, ArrowRight, FileText, Pause, Play } from "lucide-react";
import s from "./researchPipeline.module.css";

const evidence = [
  { quote: "Three in February.", month: "February", count: 3 },
  { quote: "Five in April.", month: "April", count: 5 },
];
const stages = ["Read the letter", "Extract quotations", "Save the evidence", "Decide from the record"];

export default function ResearchPipeline() {
  const [stage, setStage] = useState(3);
  const [playing, setPlaying] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  useEffect(() => {
    if (!playing) return;
    const timers = [1, 2, 3].map(i => window.setTimeout(() => setStage(i), i * 1500));
    const end = window.setTimeout(() => setPlaying(false), 5200);
    return () => { timers.forEach(window.clearTimeout); window.clearTimeout(end); };
  }, [playing]);
  function play() {
    setSelected(null);
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { setStage(3); return; }
    setStage(0); setPlaying(true);
  }
  return <section className={s.section} aria-labelledby="research-pipeline-title" data-stage={stage} data-playing={playing}>
    <header className={s.heading}><div><span>This research</span><h2 id="research-pipeline-title">Extract the evidence. Then decide.</h2><p>One extraction. A shared record. Two ways to decide.</p></div><button className={s.play} onClick={playing ? () => setPlaying(false) : play}>{playing ? <Pause size={16} /> : <Play size={16} />}{playing ? "Pause" : "Follow the evidence"}</button></header>
    <div className={s.extraction}>
      <div className={s.letter} data-emphasis={stage === 0}>
        <span className={s.documentLabel}><FileText size={16} />Illustrative clinic letter</span>
        <div className={s.lines} aria-hidden="true"><i /><i /></div>
        <blockquote>{evidence.map((row, i) => <button key={row.month} aria-pressed={selected === i} onClick={() => setSelected(selected === i ? null : i)} className={s.quote} data-selected={selected === i} data-revealed={stage >= 1}>{row.quote}</button>)}</blockquote>
        <div className={s.lines} aria-hidden="true"><i /><i /></div>
        <small>Click a quotation to find it in the record.</small>
      </div>
      <div className={s.extractor} data-emphasis={stage === 1}><ArrowRight size={25} className={s.horizontalArrow} aria-hidden="true" /><div className={s.extractModel}>LLM<small>Extract</small></div><ArrowRight size={25} className={s.horizontalArrow} aria-hidden="true" /><p>One call keeps<br />events + exact words</p></div>
      <div className={s.record} data-emphasis={stage === 2}>
        <header><span>Saved evidence record</span><span aria-hidden="true">{ "{ }" }</span></header>
        {evidence.map((row, i) => <button key={row.month} className={s.evidenceRow} aria-pressed={selected === i} onClick={() => setSelected(selected === i ? null : i)} data-selected={selected === i} data-arrived={stage >= 2}><span><strong>{row.month}</strong><b>{row.count}</b></span><q>{row.quote}</q></button>)}
        <p>Extract also proposes an answer.</p><small>Shown here: the evidence used to decide.</small>
      </div>
    </div>
    <div className={s.recordConnector} aria-hidden="true"><span /></div>
    <div className={s.shared}><ArrowDown size={22} aria-hidden="true" /><strong>Same evidence. Same decision policy.</strong><span>Decide reads the saved record only.</span></div>
    <div className={s.fork} aria-hidden="true"><span /><span /></div>
    <div className={s.branches} data-emphasis={stage === 3}>
      <div className={s.branch}>
        <header><span>Hybrid</span><h3>Recorded rules decide</h3></header>
        <div className={s.ruleProcess} aria-label="Rules combine counts and determine the time span"><span>Combine counts</span><ArrowRight size={18} aria-hidden="true" /><span>Set time span</span></div>
        <div className={s.answer}><span>Illustrative answer</span><strong>8 <small>over</small> 3 <small>months</small></strong></div>
        <details className={s.calculation}><summary>How do the rules get there?</summary><div className={s.months}><div><span>February</span><b>3</b></div><div><span>March</span><b>—</b></div><div><span>April</span><b>5</b></div></div><div className={s.bracket}>3 months, including March</div><p><strong>3 + 5 = 8 seizures.</strong> The demonstrated policy uses the inclusive February–April span. March has no stated count; the dash does not mean zero.</p></details>
      </div>
      <div className={`${s.branch} ${s.modelBranch}`}>
        <header><span>LLM-only</span><h3>A second LLM decides</h3></header>
        <div className={s.llmProcess}><span className={s.policy}>Decision<br />policy</span><ArrowRight size={18} aria-hidden="true" /><div className={s.decideModel}>LLM<small>Decide</small></div></div>
        <div className={s.modelAnswer}><span>Model decision</span><strong>Can agree or differ</strong><p>Compare actual answers in a saved pipeline record.</p></div>
      </div>
    </div>
    <nav className={s.steps} aria-label="Evidence animation stages">{stages.map((name, i) => <button key={name} aria-pressed={stage === i} onClick={() => { setPlaying(false); setStage(i); }}><span aria-hidden="true" />{name}</button>)}</nav>
    <p className={s.note}>Authored teaching example. Quotations stay linked to their source; the decision steps cannot return to the letter for new evidence. The calculation illustrates a policy, not a universal clinical interpretation.</p>
  </section>;
}
