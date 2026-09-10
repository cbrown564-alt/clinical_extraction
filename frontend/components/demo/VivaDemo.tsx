"use client";

import { useRef, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import Image from "next/image";
import { ArrowLeft, ArrowRight, Check, ChevronDown, Code2, FileText } from "lucide-react";
import { demoCases, storyFor, demoProvenance, evidenceParagraphs, quoteSegments } from "@/lib/viva";
import CasePicker from "./CasePicker";
import FullLetter from "./FullLetter";
import BatchExplorer from "./BatchExplorer";
import UnderTheHood, { type InspectorSection } from "./UnderTheHood";
import styles from "./demo.module.css";
import Introduction from "./Introduction";
import PaperResults from "./PaperResults";
import Applications from "./Applications";

type DemoView = "introduction" | "pipeline" | "batch" | "results" | "applications";
const views: DemoView[] = ["introduction", "pipeline", "batch", "results", "applications"];
function subscribeView(callback: () => void) {
  window.addEventListener("hashchange", callback);
  return () => window.removeEventListener("hashchange", callback);
}
function readView(): DemoView {
  const value = window.location.hash.slice(1) as DemoView;
  return views.includes(value) ? value : "introduction";
}
function setView(view: DemoView) { window.location.hash = view; }

const stepNames = ["Find the facts", "Calculate the rate"];

export default function VivaDemo() {
  const view = useSyncExternalStore(subscribeView, readView, () => "introduction" as DemoView);
  const [inspector, setInspector] = useState<InspectorSection | null>(null);
  const [caseId, setCaseId] = useState(demoCases[0].id);
  const [step, setStep] = useState(0);
  const [activeEvent, setActiveEvent] = useState<string | null>(null);
  const [fullLetter, setFullLetter] = useState(false);
  const [compare, setCompare] = useState(false);
  const current = demoCases.find(c => c.id === caseId)!;
  const story = storyFor(current);
  const events = current.record.events;
  const changed = current.hybrid.selection.final_label !== current.record.selection.final_label;
  const changes = current.hybrid.hops.filter(h => h.changed);

  function reset(id = caseId) {
    setCaseId(id); setStep(0); setActiveEvent(null); setFullLetter(false);
    setCompare(false);
  }

  function focusEvent(id: string) {
    setActiveEvent(id);
    requestAnimationFrame(() => document.getElementById(`quote-${id}`)?.scrollIntoView({ block: "nearest", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth" }));
  }

  return <div className={styles.demo}>
    <header className={styles.header}>
      <Link className={styles.identity} href="/demo"><Image className={styles.logo} src="/demo/imagery/header-mark-v1.png" alt="" width={40} height={40} sizes="40px" />Extract, then decide<span className={styles.subtitle}>A research demonstration</span></Link>
      <nav className={styles.viewNav} aria-label="Demo views">{([{ id: "introduction", label: "Introduction" }, { id: "pipeline", label: "The pipeline" }, { id: "results", label: "Results" }, { id: "applications", label: "Applications" }] as const).map(item => <button key={item.id} aria-pressed={view === item.id || (item.id === "pipeline" && view === "batch")} onClick={() => setView(item.id)}>{item.label}</button>)}</nav>
      <Link className={styles.workbenchLink} href="/workbench">Open workbench <ArrowRight size={15} /></Link>
    </header>
    {view === "introduction" && <div className={styles.chapterContainer}><Introduction onStart={() => setView("pipeline")} /></div>}
    {view === "results" && <div className={styles.chapterContainer}><PaperResults onApplications={() => setView("applications")} /></div>}
    <div className={styles.chapterContainer} hidden={view !== "applications"}><Applications onBatch={() => setView("batch")} /></div>
    <div className={styles.batchContainer} hidden={view !== "batch"}><BatchExplorer onInspect={id => { reset(id); setStep(1); setView("pipeline"); }} /></div>
    <div className={styles.pipeline} hidden={view !== "pipeline"}>
    <div className={styles.toolbar}>
      <CasePicker value={caseId} onChange={reset} />
      <button className={styles.batchShortcut} onClick={() => setView("batch")}>Browse all 25 letters</button>
      <nav className={styles.steps} aria-label="Demonstration progress">{stepNames.map((name, i) => <button key={name} aria-current={step === i ? "step" : undefined} onClick={() => { setStep(i); setActiveEvent(null); }}><span>{i < step ? <Check size={14} /> : i + 1}</span>{name}{i < 1 && <ArrowRight className={styles.stepArrow} size={15} />}</button>)}</nav>
    </div>
    <div className={styles.workspace}>
      <section className={styles.source} aria-label="Source letter">
        <div className={styles.sectionBar}><span><FileText size={16} />Clinic letter <span className={styles.letterId}>#{caseId}</span></span><button onClick={() => setFullLetter(true)}>Read full letter</button></div>
        <div className={styles.letterScroll}>
          <div className={styles.documentHeading}><span>Sample clinic note</span><h2>{current.note.match(/Clinic Date:\s*([^\n]+)/)?.[1] ?? "Epilepsy clinic"}</h2><p>Relevant passage · exact wording</p></div>
          <div className={styles.letterText}>{evidenceParagraphs(current.note, events).map((p, pi) => <p key={pi}>{quoteSegments(p, events).map((s, i) => s.ids.length ? <mark key={i} id={`quote-${s.ids[0]}`} role="button" tabIndex={0} data-active={activeEvent === null || s.ids.includes(activeEvent)} aria-pressed={activeEvent !== null && s.ids.includes(activeEvent)} onClick={() => setActiveEvent(s.ids[0])} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setActiveEvent(s.ids[0]); } }} aria-label={`Inspect evidence ${s.ids.join(", ")}`}>{s.text}<sup>{s.ids.join(", ").toUpperCase()}</sup></mark> : <span key={i}>{s.text}</span>)}</p>)}</div>
          <div className={styles.sourceFootnote}><span className={styles.sourceDot} />Synthetic letter for research evaluation · exact source text</div>
        </div>
      </section>
      <section className={styles.explanation} aria-label="Pipeline explanation">
        <div className={styles.sectionBar}><span>{step === 0 ? "AI extraction" : "Decision rules"}</span><button className={styles.underHoodButton} onClick={() => setInspector(step === 1 ? "rules" : "extract")}><Code2 size={15} />Under the hood</button></div>
        <div className={styles.explanationScroll} key={`${caseId}-${step}`}>
          <div key={step} className={styles.stageContent}>
            <div className={styles.stageHeading}><Image className={styles.stageIllustration} src={`/demo/imagery/pipeline-stage-${step === 0 ? "extract-v2" : "decide-v1"}.png`} width={1536} height={1024} sizes="(max-width: 760px) 110px, 150px" alt="" /><h1>{step === 0 ? "Pull out every seizure mention." : "Apply the calculation rules."}</h1><p>{step === 0 ? "The AI extracts each event and its exact quote from the letter. Click any fact to see where it appears." : "Clear rules review all the collected facts and work out the final frequency."}</p></div>
            <div className={step === 1 ? styles.compactEvents : styles.events} aria-label="Extracted events">{events.map((event, i) => <button key={event.event_id} className={styles.event} data-active={activeEvent === event.event_id} onClick={() => focusEvent(event.event_id)} aria-pressed={activeEvent === event.event_id}>
              <span className={styles.eventNumber}>{event.event_id.toUpperCase()}</span><span className={styles.eventBody}><span className={styles.eventMeta}>{event.time_window || event.temporality} · {event.kind.replaceAll("_", " ")}</span><strong>{event.raw_value || event.evidence}</strong>{step === 0 && <q>{event.evidence}</q>}</span><span className={styles.quoteLink} aria-hidden>{i + 1 < 10 ? "↗" : ""}</span>
            </button>)}</div>
            {step === 0 ? <section className={styles.extractionAnswer} aria-label="Proposed answer"><header><span>AI initial guess</span><div aria-label="Selected facts">{current.record.selection.selected_event_ids.map(id => <button key={id} onClick={() => focusEvent(id)} aria-label={`Find selected fact ${id.toUpperCase()}`}>{id.toUpperCase()} <ArrowRight size={12} /></button>)}</div></header><div className={styles.extractionAnswerBody}><h2>{current.record.selection.final_label}</h2><div className={styles.answerRationale}><h3>Rationale</h3><p>{current.record.selection.rationale}</p></div></div></section> : <>
              <div className={styles.decision}>
                <div className={styles.decisionHeading}><span>Rule outcome</span><span>{changed ? "Rule: Changed the answer" : "Rule: Kept the AI's guess"}</span></div>
                <div className={styles.answerChange}><div><span>AI initial guess</span><p>{current.record.selection.final_label}</p></div><ArrowRight size={24} /><div><span>Final verified answer</span><h2>{current.hybrid.selection.final_label}</h2></div></div>
                <div className={styles.rule}><h3>{story.rule}</h3><p>{story.explanation}</p>{story.calculation && <div className={styles.calculation}>{story.calculation}</div>}</div>
              </div>
              <button className={styles.compareToggle} aria-expanded={compare} onClick={() => setCompare(!compare)}>{compare ? "Hide" : "Compare with"} a direct LLM-only call <ChevronDown size={16} /></button>
              {compare && <div className={styles.comparison}><div><span>Hybrid · rules</span><strong>{current.hybrid.selection.final_label}</strong></div><div><span>Direct LLM call</span><strong>{current.llm.label}</strong></div><p>{current.llm.label === current.hybrid.selection.final_label ? "Both methods gave the same answer." : "The methods gave different answers."}</p></div>}
              <details className={styles.details}><summary><Code2 size={15} /> Trace & verification details</summary><div className={styles.detailBody}>{story.caveat && <p>{story.caveat}</p>}<p>Selected facts: {current.hybrid.selection.selected_event_ids.join(", ") || "None"}. Rules applied: {changes.map(h => h.stage_id).join(", ") || "None"}.</p><p>Verified benchmark category: {current.gold} ({current.hybrid_correct ? "matches" : "differs"}).</p><p>Dataset: {demoProvenance.dataset} / {demoProvenance.split} · Model: {demoProvenance.model}<br />Extraction prompt: {current.prompt_version}</p><pre>{JSON.stringify({ record: current.record, rule_trace: current.hybrid, llm_output: current.llm }, null, 2)}</pre></div></details>
            </>}
          </div>
        </div>
      </section>
    </div>
    <footer className={styles.footer}><span>Research demonstration <span className={styles.footerDot}>·</span> Synthetic examples</span><div><button className={styles.secondary} disabled={step === 0} onClick={() => setStep(step - 1)}><ArrowLeft size={16} />Back</button>{step < 1 ? <button className={styles.primary} onClick={() => setStep(step + 1)}>Calculate the rate<ArrowRight size={16} /></button> : <button className={styles.primary} onClick={() => setView("results")}>View results <ArrowRight size={16} /></button>}</div></footer>
    </div>
    {inspector && <UnderTheHood current={current} initial={inspector} onClose={() => setInspector(null)} />}
    {fullLetter && <FullLetter current={current} showEvidence onClose={() => setFullLetter(false)} />}
  </div>;
}
