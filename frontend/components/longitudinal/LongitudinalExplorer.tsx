"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, BookOpen, ChevronRight, RefreshCw } from "lucide-react";
import { QUERIES, assertionTitle, displayDate, timeDescription, type Evidence, type Frame, type LongitudinalData, type Status } from "@/lib/longitudinal";
import styles from "./longitudinal.module.css";

const STATUS: Record<Status, string> = { eligible: "Eligible", ineligible: "Ineligible", indeterminate: "Indeterminate", failed: "Extraction unavailable" };
function Badge({ status }: { status: Status }) {
  return <span className={`${styles.badge} ${styles[status]}`}>{STATUS[status]}</span>;
}

export default function LongitudinalExplorer() {
  const [patient, setPatient] = useState("authored_patient_001");
  const [index, setIndex] = useState("T1");
  const [view, setView] = useState("visit");
  const [mode, setMode] = useState("reference");
  const [query, setQuery] = useState("Q2");
  const [cohortFilter, setCohortFilter] = useState("all");
  const [retry, setRetry] = useState(0);
  const key = new URLSearchParams({ patient, index, view, mode, query }).toString() + `&retry=${retry}`;
  const [response, setResponse] = useState<{ key: string; data?: LongitudinalData; error?: string }>();
  const [selection, setSelection] = useState<{ key: string; letter: string; evidence?: Evidence }>();
  const highlight = useRef<HTMLElement>(null);
  const data = response?.key === key ? response.data : undefined;
  const error = response?.key === key ? response.error : undefined;
  const loading = !data && !error;
  const frame = data?.selected;
  const request = frame?.requests[0];
  const answer = frame?.answers.find(a => a.query_id === query);
  const selected = selection?.key === key ? selection : undefined;
  const letter = frame?.documents.find(d => d.letter_id === selected?.letter) ?? frame?.documents[0];
  const evidence = selected?.evidence;
  const question = QUERIES.find(q => q.id === query)!;

  useEffect(() => {
    const controller = new AbortController();
    fetch(`/longitudinal/data?${key}`, { signal: controller.signal, cache: "no-store" })
      .then(async result => {
        const body = await result.json();
        if (!result.ok) throw new Error(body.error ?? "The demonstration could not be loaded.");
        return body as LongitudinalData;
      }).then(data => setResponse({ key, data }))
      .catch(reason => { if (!controller.signal.aborted) setResponse({ key, error: String(reason.message ?? reason) }); });
    return () => controller.abort();
  }, [key]);
  useEffect(() => {
    if (evidence) {
      highlight.current?.scrollIntoView({ block: "center", behavior: "instant" });
      highlight.current?.focus({ preventScroll: true });
    }
  }, [evidence]);
  const showEvidence = (e: Evidence) => setSelection({ key, letter: e.letter_id, evidence: e });
  const visibleCohort = data?.cohort.filter(p => cohortFilter === "all" || p.status === cohortFilter) ?? [];
  const counts = data?.cohort.reduce((totals, p) => ({ ...totals, [p.status]: (totals[p.status] ?? 0) + 1 }), {} as Record<string, number>);

  return <div className={styles.explorer}>
    <a className={styles.skip} href="#patient-history">Skip to patient history</a>
    <header className={styles.intro}>
      <div><p className={styles.eyebrow}>Synthetic development · 12 fictional patients</p>
        <h1>Longitudinal histories</h1>
        <p>Follow the evidence from clinic letters to a dated cohort answer.</p></div>
      <span className={styles.prototype}>Research prototype · provisional annotations</span>
    </header>
    <nav className={styles.mobileJump} aria-label="Jump to section"><a href="#cohort-results">Cohort</a><a href="#patient-history">Patient history</a><a href="#source-letters">Source letters</a></nav>
    <section className={styles.controls} aria-label="History and query settings">
      <label>Fact source<select value={mode} onChange={e => setMode(e.target.value)}>
        <option value="reference">Provisional reference facts</option><option value="predicted">Saved model predictions</option>
      </select></label>
      <label>Index schedule<select value={index} onChange={e => setIndex(e.target.value)}>
        <option value="T1">First visit</option><option value="T2">180 days after first visit</option>
      </select></label>
      <fieldset><legend>History view</legend><div className={styles.segment}>
        {[['visit', 'As known at visit'], ['retrospective', 'Retrospective']].map(([value, label]) =>
          <label key={value}><input type="radio" name="history-view" checked={view === value} onChange={() => setView(value)} /><span>{label}</span></label>)}
      </div></fieldset>
      <label className={styles.querySelect}>Cohort question<select value={query} onChange={e => setQuery(e.target.value)}>
        {QUERIES.map(q => <option key={q.id} value={q.id}>{q.id} · {q.title}</option>)}
      </select></label>
    </section>
    <div className={styles.context}>
      <span>{question.detail}</span>
      <span>{mode === "reference" ? "AI-authored reference facts + inferred links. No expert review." : "Saved Gemini extractions + inferred links. No new model call."}</span>
    </div>
    {loading && <div className={styles.state} role="status"><RefreshCw size={20} /><p>Loading permitted letters and the saved history…</p></div>}
    {error && <div className={styles.state} role="alert"><h2>Could not load the demonstration</h2><p>{error}</p><button onClick={() => setRetry(v => v + 1)}>Retry loading</button></div>}
    {data && frame && request && answer && <div className={styles.workspace}>
      <aside className={styles.cohort} id="cohort-results" aria-label="Cohort results">
        <div className={styles.panelHeading}><h2>Cohort</h2><span>12 patients</span></div>
        <p className={styles.cohortSummary} aria-live="polite"><strong>{counts?.eligible ?? 0}</strong> eligible · {counts?.ineligible ?? 0} ineligible<br />{counts?.indeterminate ?? 0} indeterminate · {counts?.failed ?? 0} unavailable</p>
        <label className={styles.filter}>Show<select value={cohortFilter} onChange={e => setCohortFilter(e.target.value)}>
          <option value="all">All patients</option>{Object.entries(STATUS).map(([v, label]) => <option value={v} key={v}>{label}</option>)}
        </select></label>
        <div className={styles.patientList}>{visibleCohort.length ? visibleCohort.map(p =>
          <button key={p.patient} aria-pressed={p.patient === patient} onClick={() => setPatient(p.patient)} className={p.patient === patient ? styles.activePatient : ""}>
            <span><strong>{p.label}</strong><ChevronRight size={14} aria-hidden /></span><Badge status={p.status} />
            <small>Index {displayDate(p.index_date)}</small>
          </button>) : <div className={styles.empty}><h3>No matching patients</h3><p>No patient has this status for the selected question and view.</p><button onClick={() => setCohortFilter("all")}>Show all patients</button></div>}</div>
        <p className={styles.cohortFoot}>Each patient uses their own index date. Indeterminate means the evidence cannot settle the question.</p>
      </aside>
      <section className={styles.history} id="patient-history" aria-label="Patient history" tabIndex={-1}>
        <div className={styles.panelHeading}><label>Patient<select aria-label="Patient" value={patient} onChange={e => setPatient(e.target.value)}>
          {data.patients.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
        </select></label></div>
        <div className={styles.dates}><div><span>Index date</span><strong>{displayDate(request.index_date)}</strong></div><div><span>Letters available through</span><strong>{displayDate(request.information_cutoff)}</strong></div></div>
        <p className={styles.viewNote}>{view === "visit" ? "This account uses only letters available by the index date." : "Later letters may revise the earlier interpretation. The original assertions are preserved."}</p>
        <article className={styles.answer} aria-live="polite">
          <div className={styles.answerHeading}><span>{query} · Cohort answer</span><Badge status={answer.status} /></div>
          <h2>{question.title}</h2><p>{answer.reason ?? answer.error}</p>
          <p className={styles.window}>Window: {displayDate(query === "Q1" || query === "Q2" ? request.lookback_90_start : request.lookback_180_start)} – {displayDate(request.index_date)}, inclusive</p>
          <div className={styles.evidenceLinks}>{answer.evidence.map((e, i) => <button key={`${e.letter_id}-${e.start}-${e.end}`} onClick={() => showEvidence(e)} aria-label={`Show answer evidence ${i + 1} in ${e.letter_id}`}><BookOpen size={13} aria-hidden />{e.letter_id} · Evidence {i + 1}<ArrowUpRight size={12} aria-hidden /></button>)}</div>
          {answer.status === "indeterminate" && <p className={styles.ambiguity}>Missing evidence is not a negative finding. Review the source accounts below.</p>}
          {!!answer.rule_ids.length && <details className={styles.ruleDetails}><summary>Why this answer</summary><ul>{answer.rule_ids.map(rule => <li key={rule}>{rule.replaceAll("-", " ")}</li>)}</ul></details>}
        </article>
        {frame.status === "failed" ? <div className={styles.empty}><h3>Saved extraction unavailable</h3><p>The original model attempt failed for this patient and view. The letters remain available.</p><div className={styles.actions}><button onClick={() => setRetry(v => v + 1)}>Retry loading saved output</button><button onClick={() => setMode("reference")}>Use provisional reference facts</button></div></div> : <History frame={frame} showEvidence={showEvidence} />}
        {mode === "predicted" && <p className={styles.provenance}>Saved {frame.provenance.attempt?.model_requested ?? "model"} output. The original extraction saw the query context. {frame.offset_repairs?.length ?? 0} exact quote offsets repaired; clinical fields unchanged. Model query answers are not used.</p>}
      </section>
      <section className={styles.letters} id="source-letters" aria-label="Source letters">
        <div className={styles.panelHeading}><h2>Source letters</h2><span>{frame.documents.length} available</span></div>
        <div className={styles.letterTabs} aria-label="Choose a source letter">{frame.documents.map(d => <button aria-pressed={d.letter_id === letter?.letter_id} key={d.letter_id} onClick={() => setSelection({ key, letter: d.letter_id })}><strong>{d.letter_id}</strong><span>{displayDate(d.visit_date)}</span></button>)}</div>
        {letter ? <><div className={styles.letterMeta}><span>Consultation {displayDate(letter.visit_date)}</span><span>Available {displayDate(letter.available_date)}</span></div>
          <div className={styles.document}><p className={styles.fictional}>Authored fictional letter · {letter.letter_id}</p>
            <div className={styles.letterText}>{evidence && evidence.letter_id === letter.letter_id ? <>{letter.text.slice(0, evidence.start)}<mark ref={highlight} tabIndex={-1} aria-label="Selected source evidence">{letter.text.slice(evidence.start, evidence.end)}</mark>{letter.text.slice(evidence.end)}</> : letter.text}</div>
          </div></> : <p className={styles.empty}>No letter is available by this cutoff.</p>}
      </section>
    </div>}
  </div>;
}

function History({ frame, showEvidence }: { frame: Frame; showEvidence: (e: Evidence) => void }) {
  return <section className={styles.accounts} aria-label="Evidence-supported accounts"><h2>Evidence-supported accounts</h2><p>Linked accounts retain their source, time and interpretation.</p>
    {frame.history?.length ? frame.history.map(group => {
      const correction = group.links.find(link => link.relation === "corrects_interpretation");
      const conflict = group.links.some(link => link.relation === "contradicts");
      return <details key={group.assertion_ids.join("+")} className={styles.account}>
        <summary><span className={styles.family}>{group.accounts[0].content.family}</span><strong>{assertionTitle(group.accounts[0])}</strong><span className={styles.accountMeta}>{group.accounts.length} {group.accounts.length === 1 ? "account" : "accounts"}{correction ? " · Interpretation revised" : conflict ? " · Conflicting reports" : ""}</span></summary>
        {correction && <p className={styles.correction}>Later evidence changes the interpretation. Decision: {timeDescription(correction.decision_time)}.</p>}
        {group.accounts.map(a => <div className={styles.assertion} key={a.assertion_id}>
          <p><strong>{a.letter_id}</strong> · {a.content.kind ?? a.content.status ?? "diagnosis"} · {a.content.interpretation?.replaceAll("_", " ") ?? a.polarity}</p>
          <p>{timeDescription(a.time)}</p>{a.content.burden?.text && <p>{a.content.burden.text}</p>}
          <small>{a.reporter} · {a.certainty} · {a.polarity} · coverage {a.coverage.replaceAll("_", " ")}</small>
          {a.evidence.map(e => <button key={`${e.letter_id}-${e.start}-${e.end}`} className={styles.quote} onClick={() => showEvidence(e)}>“{e.text}” <ArrowUpRight size={13} aria-label="Show in letter" /></button>)}
        </div>)}
        {!!group.links.length && <details className={styles.ruleDetails}><summary>Relationships ({group.links.length})</summary><ul>{group.links.map(link => <li key={link.link_id}>{link.relation.replaceAll("_", " ")}<button onClick={() => showEvidence(link.evidence[0])}>Show supporting text</button></li>)}</ul></details>}
      </details>;
    }) : <p>No grounded facts were extracted from the available letters.</p>}
  </section>;
}
