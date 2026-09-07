"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowRight, Code2, X } from "lucide-react";
import method from "@/lib/viva-method.json";
import type { DemoCase } from "@/lib/viva";
import styles from "./demo.module.css";

export type InspectorSection = "extract" | "encode" | "rules" | "decide";
const sections: { id: InspectorSection; title: string }[] = [
  { id: "extract", title: "Extract prompt" }, { id: "encode", title: "Normalise / encode" },
  { id: "rules", title: "Decide rules" }, { id: "decide", title: "Decide prompt" },
];
const descriptions: Record<string, [string, string]> = {
  "gan.encode.format": ["Write a consistent label", "Standardise the written form of an already parsed label."],
  "gan.encode.codebook.monthly_diary": ["Encode diary counts", "Read month counts in the selected evidence and represent their combined rate."],
  "gan.encode.codebook.hourly_rate": ["Recognise an hourly rate", "Recover a rate from explicit hourly wording when the provisional label is unknown."],
  "gan.encode.codebook.single_last_period": ["One event in a stated period", "Recognise wording such as a single event last month."],
  "gan.encode.codebook.vague_periodic_cadence": ["Represent repeated occurrences", "Handle specific recurring expressions such as most weekdays."],
  "gan.encode.codebook.complete_cluster_cadence": ["Complete a cluster description", "Keep the frequency of clusters and the number of events within them distinct."],
  "gan.encode.codebook.explicit_cluster_interval": ["Represent the interval between clusters", "Use an explicit interval when the recorded cluster wording supplies one."],
  "gan.encode.codebook.drop_unknown_wrapper": ["Remove a redundant unknown prefix", "Keep a usable frequency when it is wrapped in an unknown label."],
  "gan.encode.codebook.year_to_date_window": ["Use the elapsed year window", "Represent a year-to-date count over its supported elapsed period."],
  "gan.select.usual_interval": ["Prefer the usual interval", "Use an extracted usual interval when the proposal is unknown or describes only a brief daily spell."],
  "gan.select.typical_over_ytd": ["Prefer a typical rate", "Use the typical frequency when another candidate is a year-to-date total."],
  "gan.select.breakthrough": ["Recent seizures after a quiet spell", "Combine a recent count and a recorded seizure-free interval when the proposed answer is unknown."],
  "gan.select.non_epileptic": ["Distinguish non-epileptic events", "Apply the study’s seizure-free policy when the retained evidence describes current non-epileptic events."],
  "gan.select.post_change_burst": ["Account for post-change seizures", "Use a burst count and its recorded time window when recent seizure freedom follows a treatment change."],
  "gan.select.last_event_well_since": ["Count the last event over its interval", "Combine a dated last event with a subsequent well or seizure-free interval."],
  "gan.select.dated_sequence": ["Combine separately dated events", "Count distinct events over their recorded date span, subject to the rule’s conditions."],
  "gan.select.monthly_diary": ["Combine the diary counts", "Sum the relevant diary counts over their calendar span, with guards for competing labels."],
};

export default function UnderTheHood({ current, initial, onClose }: { current: DemoCase; initial: InspectorSection; onClose: () => void }) {
  const [section, setSection] = useState(initial);
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    const element = dialog.current!;
    element.showModal();
    return () => { element.close(); opener?.focus(); };
  }, []);
  const prompt = section === "extract" ? method.prompts.extract : method.prompts.decide;
  const rules = section === "encode" ? method.rules.encode : method.rules.decide;
  const rawPrompt = section === "extract" ? { ...method.prompts.extract, note_text: current.note } : { ...method.prompts.decide, ...current.decide_input };

  return <dialog ref={dialog} className={styles.inspector} aria-labelledby="inspector-title" onCancel={e => { e.preventDefault(); onClose(); }}>
    <header className={styles.inspectorHeader}><div><span>Letter {current.id} · method details</span><h2 id="inspector-title">Under the hood</h2></div><button className={styles.iconButton} onClick={onClose} aria-label="Close method details"><X size={20} /></button></header>
    <nav className={styles.inspectorNav} aria-label="Method details">{sections.map(s => <button key={s.id} aria-pressed={s.id === section} onClick={() => setSection(s.id)}>{s.title}</button>)}</nav>
    <div className={styles.inspectorBody} key={section}>
      {section === "extract" || section === "decide" ? <>
        <div className={styles.inspectorLead}><span>{section === "extract" ? "One call · the full letter goes in" : "Second call · only the evidence record goes in"}</span><h3>{section === "extract" ? "The instructions behind extraction." : "The same policy, given to a model."}</h3><p>{prompt.task}</p><p className={styles.inspectorNote}>Exact saved prompt payload, presented by section. Framework message wrappers are not included. The text below has not been rewritten for the demo.</p></div>
        <section className={styles.promptSection}><h4>Instructions <span>{prompt.instructions.length}</span></h4><ol>{prompt.instructions.map((instruction, i) => <li key={i}>{instruction}</li>)}</ol></section>
        {section === "decide" && <section className={styles.promptSection}><h4>Policy cases and worked examples</h4>{method.prompts.decide.cases.map(c => <details key={c.title} className={styles.promptExample}><summary>{c.title}</summary><p>{c.instruction}</p><div className={styles.exampleEvents}>{c.example.events.map(e => <div key={e.event_id}><span>{e.event_id.toUpperCase()}</span><q>{e.evidence}</q><strong>{e.label}</strong></div>)}</div><div className={styles.exampleAnswer}><span>{c.example.first_choice.label}</span><ArrowRight size={16} /><strong>{"label" in c.example.answer ? c.example.answer.label : `Select ${c.example.answer.selected_event_ids.join(", ")}`}</strong></div><details className={styles.rawDisclosure}><summary>Exact example object</summary><pre>{JSON.stringify(c.example, null, 2)}</pre></details></details>)}</section>}
        {section === "extract" && <Schema title="Event fields" fields={method.prompts.extract.event_schema} />}
        <Schema title="Answer fields" fields={prompt.selection_schema} />
        <section className={styles.promptSection}><h4>Allowed labels and examples</h4><ul className={styles.labelRules}>{prompt.label_forms.rules.map(r => <li key={r}>{r}</li>)}</ul><div className={styles.labelForms}>{prompt.label_forms.forms.map(f => <div key={f.form}><code>{f.form}</code><p>{f.description}</p><span>{f.examples.join(" · ")}</span></div>)}</div></section>
        <details className={styles.rawDisclosure}><summary>Exact payload for letter {current.id}</summary><pre>{JSON.stringify(rawPrompt, null, 2)}</pre></details>
      </> : <>
        <div className={styles.inspectorLead}><span>Deterministic Python · {rules.length} entries</span><h3>{section === "encode" ? "Put the evidence into the required form." : "The rules that decide the final answer."}</h3><p>{section === "encode" ? "The model already proposes a label. These helpers standardise its form or derive a supported label from recorded evidence. Evidence-based encoding can change meaning; it is recorded separately from structural repairs." : "The rules inspect the saved record in a fixed order. Each can retain or revise the label. This view shows the rule entry points and the changes recorded for this letter."}</p><p className={styles.inspectorNote}>Descriptions are a reading guide. Expand an entry for the actual function, source location and file fingerprint from the exported program snapshot.</p></div>
        <div className={styles.ruleList}>{rules.map(rule => {
          const changes = current.hybrid.hops.filter(h => h.changed && h.stage_id === rule.id);
          const description = descriptions[rule.id] ?? [rule.name, "Inspect the source function for this rule’s conditions."];
          return <details key={rule.id} className={styles.ruleEntry} open={changes.length > 0 || undefined}><summary><span><strong>{description[0]}</strong><small>{rule.id}</small></span><span className={changes.length ? styles.changedBadge : styles.unchangedBadge}>{changes.length ? "Changed this answer" : "No rewrite recorded"}</span></summary><div className={styles.ruleEntryBody}><p>{description[1]}</p>{changes.map((h, i) => <div key={i} className={styles.exampleAnswer}><span>{h.before}</span><ArrowRight size={16} /><strong>{h.after}</strong></div>)}<details className={styles.rawDisclosure}><summary><Code2 size={14} /> View Python implementation</summary><p className={styles.sourceLocation}>{rule.path}:{rule.line}</p><pre>{rule.source}</pre><p className={styles.sourceLocation}>Source file SHA-256: {rule.sha256}</p></details></div></details>;
        })}</div>
        <p className={styles.inspectorNote}>Entry-point functions call additional helpers. “No rewrite recorded” does not mean the rule was never evaluated. Encoding records successful rewrites; the decision trace also records unchanged proposals.</p>
      </>}
    </div>
  </dialog>;
}

function Schema({ title, fields }: { title: string; fields: Record<string, unknown> }) {
  return <section className={styles.promptSection}><h4>{title}</h4><dl className={styles.schema}>{Object.entries(fields).map(([name, value]) => <div key={name}><dt>{name}</dt><dd>{Array.isArray(value) ? value.join(" / ") : String(value)}</dd></div>)}</dl></section>;
}
