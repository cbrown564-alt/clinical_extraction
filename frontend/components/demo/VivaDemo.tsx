"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Check, ChevronDown, Code2, FileText, Play, RotateCcw } from "lucide-react";
import { demoCases, storyFor, demoProvenance, evidenceParagraphs, quoteSegments } from "@/lib/viva";
import CasePicker from "./CasePicker";
import MethodMark from "./MethodMark";
import FullLetter from "./FullLetter";
import BatchExplorer from "./BatchExplorer";
import UnderTheHood, { type InspectorSection } from "./UnderTheHood";
import styles from "./demo.module.css";

type Execution = "saved" | "running" | "live" | "error";
const stepNames = ["The letter", "Extract", "Decide"];

export default function VivaDemo() {
  const [view, setView] = useState<"pipeline" | "batch">("pipeline");
  const [inspector, setInspector] = useState<InspectorSection | null>(null);
  const [caseId, setCaseId] = useState(demoCases[0].id);
  const [step, setStep] = useState(0);
  const [activeEvent, setActiveEvent] = useState<string | null>(null);
  const [fullLetter, setFullLetter] = useState(false);
  const [compare, setCompare] = useState(false);
  const [execution, setExecution] = useState<Execution>("saved");
  const [error, setError] = useState("");
  const abort = useRef<AbortController | null>(null);
  const current = demoCases.find(c => c.id === caseId)!;
  const story = storyFor(current);
  const events = current.record.events;
  const changed = current.hybrid.selection.final_label !== current.record.selection.final_label;
  const changes = current.hybrid.hops.filter(h => h.changed);

  useEffect(() => () => abort.current?.abort(), []);

  function reset(id = caseId) {
    abort.current?.abort();
    setCaseId(id); setStep(0); setActiveEvent(null); setFullLetter(false);
    setCompare(false); setExecution("saved"); setError("");
  }

  function focusEvent(id: string) {
    setActiveEvent(id);
    requestAnimationFrame(() => document.getElementById(`quote-${id}`)?.scrollIntoView({ block: "nearest", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" }));
  }

  async function runRules() {
    abort.current?.abort();
    const controller = new AbortController();
    abort.current = controller;
    setExecution("running"); setError("");
    try {
      const response = await fetch("/demo/replay", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: caseId }), signal: controller.signal });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error);
      if (result.id !== caseId || result.sha256 !== current.sha256 || JSON.stringify(result.selection) !== JSON.stringify(current.hybrid.selection) || JSON.stringify(result.hops) !== JSON.stringify(current.hybrid.hops)) {
        throw new Error("The current rules differ from this saved demonstration. The saved result remains visible; inspect the program version before using the new result.");
      }
      setExecution("live");
    } catch (e) {
      if (controller.signal.aborted) return;
      setExecution("error"); setError(e instanceof Error ? e.message : "The local rules could not run.");
    }
  }

  return <div className={styles.demo}>
    <header className={styles.header}>
      <Link className={styles.identity} href="/demo"><span className={styles.logo}><FileText size={19} /></span>Extract, then decide<span className={styles.subtitle}>A research demonstration</span></Link>
      <nav className={styles.viewNav} aria-label="Demo views"><button aria-pressed={view === "pipeline"} onClick={() => setView("pipeline")}>The pipeline</button><button aria-pressed={view === "batch"} onClick={() => setView("batch")}>A batch of letters</button></nav>
      <Link className={styles.workbenchLink} href="/workbench">Open workbench <ArrowRight size={15} /></Link>
    </header>
    <div className={styles.batchContainer} hidden={view !== "batch"}><BatchExplorer onInspect={id => { reset(id); setStep(2); setView("pipeline"); }} /></div>
    <div className={styles.pipeline} hidden={view !== "pipeline"}>
    <div className={styles.toolbar}>
      <CasePicker value={caseId} onChange={reset} />
      <nav className={styles.steps} aria-label="Demonstration progress">{stepNames.map((name, i) => <button key={name} aria-current={step === i ? "step" : undefined} onClick={() => { setStep(i); setActiveEvent(null); }}><span>{i < step ? <Check size={14} /> : i + 1}</span>{name}{i < 2 && <ArrowRight className={styles.stepArrow} size={15} />}</button>)}</nav>
      <button className={styles.iconButton} onClick={() => reset()} aria-label="Restart case"><RotateCcw size={17} /></button>
    </div>
    <div className={styles.workspace}>
      <section className={styles.source} aria-label="Source letter">
        <div className={styles.sectionBar}><span><FileText size={16} />Source letter <span className={styles.letterId}>#{caseId}</span></span><button onClick={() => setFullLetter(true)}>Read full letter</button></div>
        <div className={styles.letterScroll}>
          <div className={styles.documentHeading}><span>Synthetic clinic letter</span><h2>{current.note.match(/Clinic Date:\s*([^\n]+)/)?.[1] ?? "Epilepsy clinic"}</h2><p>Relevant passage · original wording</p></div>
          <div className={styles.letterText}>{evidenceParagraphs(current.note, events).map((p, pi) => <p key={pi}>{quoteSegments(p, step > 0 ? events : []).map((s, i) => s.ids.length ? <mark key={i} id={`quote-${s.ids[0]}`} data-active={activeEvent === null || s.ids.includes(activeEvent)}><button onClick={() => setActiveEvent(s.ids[0])} aria-label={`Inspect evidence ${s.ids.join(", ")}`}>{s.text}<sup>{s.ids.join(", ").toUpperCase()}</sup></button></mark> : <span key={i}>{s.text}</span>)}</p>)}</div>
          <div className={styles.sourceFootnote}><span className={styles.sourceDot} />Gan 2026 · synthetic development data · exact source text</div>
        </div>
      </section>
      <section className={styles.explanation} aria-label="Pipeline explanation">
        <div className={styles.sectionBar}><span>{step === 0 ? "The research question" : step === 1 ? "One LLM call" : "A fixed decision policy"}</span><button className={styles.underHoodButton} onClick={() => setInspector(step === 2 ? "rules" : "extract")}><Code2 size={15} />Under the hood</button></div>
        <div className={styles.explanationScroll} key={`${caseId}-${step}`}>
          {step === 0 ? <div key="intro" className={styles.intro}>
            <span className={styles.overline}>From narrative to structured evidence</span>
            <h1>{story.question}</h1>
            <p>{story.lesson}</p>
            <div className={styles.miniFlow}><span><MethodMark stage="extract" /><strong>Extract</strong><small>Keep the evidence</small></span><ArrowRight size={21} /><span><MethodMark stage="decide" /><strong>Decide</strong><small>Apply the policy</small></span></div>
            <p className={styles.quiet}>Follow one letter through the method. Every quoted passage stays available for inspection.</p>
          </div> : <div key={step} className={styles.stageContent}>
            <div className={styles.stageHeading}><h1>{step === 1 ? "Keep every candidate." : "Make the decision explicit."}</h1><p>{step === 1 ? "Saved Gemini 3.7 Flash output. The model records the evidence and proposes an answer. Select an event to find its exact words in the letter." : "Decide receives this extraction record. It has no access to the full letter and cannot collect new evidence."}</p></div>
            <div className={step === 2 ? styles.compactEvents : styles.events} aria-label="Extracted events">{events.map((event, i) => <button key={event.event_id} className={styles.event} data-active={activeEvent === event.event_id} onClick={() => focusEvent(event.event_id)} aria-pressed={activeEvent === event.event_id}>
              <span className={styles.eventNumber}>{event.event_id.toUpperCase()}</span><span className={styles.eventBody}><span className={styles.eventMeta}>{event.time_window || event.temporality} · {event.kind.replaceAll("_", " ")}</span><strong>{event.raw_value || event.evidence}</strong>{step === 1 && <q>{event.evidence}</q>}</span><span className={styles.quoteLink} aria-hidden>{i + 1 < 10 ? "↗" : ""}</span>
            </button>)}</div>
            {step === 1 ? <div className={styles.provisional}><span>Provisional answer · extraction call</span><h2>{current.record.selection.final_label}</h2><p>{current.record.selection.rationale}</p></div> : <>
              <div className={styles.decision}>
                <div className={styles.decisionHeading}><span>Hybrid · recorded rules</span><span>{changed ? "Answer revised" : "Answer retained"}</span></div>
                <div className={styles.answerChange}><div><span>Provisional</span><p>{current.record.selection.final_label}</p></div><ArrowRight size={24} /><div><span>Final answer</span><h2>{current.hybrid.selection.final_label}</h2></div></div>
                <div className={styles.rule}><h3>{story.rule}</h3><p>{story.explanation}</p>{story.calculation && <div className={styles.calculation}>{story.calculation}</div>}</div>
              </div>
              {story.caveat && <p className={styles.caveat}>{story.caveat}</p>}
              <div className={styles.executionRow}><button className={styles.secondary} disabled={execution === "running"} onClick={runRules}><Play size={14} />{execution === "running" ? "Running local rules…" : "Run rules locally"}</button><span role="status">{execution === "live" ? "Same record. Same answer. Verified just now." : execution === "running" ? "Executing Python on the saved record" : "Saved decision · no model connection needed"}</span>{execution === "running" && <button onClick={() => { abort.current?.abort(); setExecution("saved"); }}>Cancel</button>}</div>
              {execution === "error" && <div className={styles.error} role="alert"><p>{error}</p><button onClick={() => { setExecution("saved"); setError(""); }}>Continue with saved decision</button></div>}
              <button className={styles.compareToggle} aria-expanded={compare} onClick={() => setCompare(!compare)}>{compare ? "Hide" : "Compare with"} the second LLM decision <ChevronDown size={16} /></button>
              {compare && <div className={styles.comparison}><div><span>Hybrid · rules</span><strong>{current.hybrid.selection.final_label}</strong></div><div><span>LLM-only · second call</span><strong>{current.llm.label}</strong></div><p>Same extracted candidates · saved Gemini 3.7 Flash decisions. {current.llm.label === current.hybrid.selection.final_label ? "Both executors return the same label here." : "The two executors return different labels here."}</p></div>}
              <details className={styles.details}><summary><Code2 size={15} /> Inspect the recorded trace and provenance</summary><div className={styles.detailBody}><p>The trace preserves the original selection fields. A label rewrite does not necessarily update its event IDs, evidence quote or model rationale.</p><p>Recorded selection: {current.hybrid.selection.selected_event_ids.join(", ")}. Changed rules: {changes.map(h => h.stage_id).join(", ") || "none"}.</p><p>Gold label: {current.gold}. Hybrid {current.hybrid_correct ? "matches" : "does not match"} the Purist category. Exact quotation is not proof of clinical correctness.</p><p>{demoProvenance.dataset} / {demoProvenance.split} / {demoProvenance.model}<br />Prompt: {current.prompt_version}<br />Replay: {demoProvenance.repair}</p><p>Extraction source: {current.extract_source}<br />Decision source: {current.decision_source}<br />Extraction SHA-256: {current.sha256}</p><pre>{JSON.stringify({ record: current.record, rule_trace: current.hybrid, llm_output: current.llm }, null, 2)}</pre></div></details>
            </>}
          </div>}
        </div>
      </section>
    </div>
    <footer className={styles.footer}><span>Research demonstration <span className={styles.footerDot}>·</span> Synthetic examples, not clinical advice</span><div><button className={styles.secondary} disabled={step === 0} onClick={() => setStep(step - 1)}><ArrowLeft size={16} />Back</button>{step < 2 ? <button className={styles.primary} onClick={() => setStep(step + 1)}>{step === 0 ? "Extract evidence" : "Apply decision policy"}<ArrowRight size={16} /></button> : <button className={styles.secondary} onClick={() => reset()}>Restart case <RotateCcw size={15} /></button>}</div></footer>
    </div>
    {inspector && <UnderTheHood current={current} initial={inspector} onClose={() => setInspector(null)} />}
    {fullLetter && <FullLetter current={current} showEvidence={step > 0} onClose={() => setFullLetter(false)} />}
  </div>;
}
