"use client";

import { useState } from "react";
import { ArrowRight, Download, Search } from "lucide-react";
import { batchCases, batchPolicy, categoryNames, decisionEvidence, exportBatch } from "@/lib/viva";
import CategoryPill, { CategoryMark } from "./CategoryPill";
import styles from "./demo.module.css";

export default function BatchExplorer({ onInspect }: { onInspect: (id: number) => void }) {
  const [category, setCategory] = useState("all");
  const [query, setQuery] = useState("");
  const [downloaded, setDownloaded] = useState(false);
  const categories = ["currently_no_seizure", "seizure_infrequent", "seizure_frequent", "seizure_freq_unknown"];
  const filtered = batchCases.filter(c => (category === "all" || c.category === category) && `${c.id} ${c.hybrid.selection.final_label} ${c.record.events.map(e => e.evidence).join(" ")}`.toLowerCase().includes(query.toLowerCase()));
  function download() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(exportBatch(filtered), null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = "extracted-evidence-dev750.json"; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000); setDownloaded(true);
  }
  return <div className={styles.batch}>
    <div className={styles.batchHeading}><div><span className={styles.overline}>Batch inspection</span><h1>Review and export extracted records</h1><p>Filter by extracted frequency, open any letter to inspect its evidence quotes, and export records for review.</p></div><button className={styles.secondary} onClick={download} disabled={!filtered.length}><Download size={16} /><span>{`Export ${filtered.length} ${filtered.length === 1 ? "record" : "records"}`}</span></button></div>
    <div className={styles.batchScope}><strong>25 sample clinic letters</strong><span>Inspect individual evidence quotes or export full records for audit.</span></div>
    <div className={styles.batchFilters}>
      <div className={styles.categoryFilters} aria-label="Filter by extracted category"><button aria-pressed={category === "all"} onClick={() => setCategory("all")}>All <span>{batchCases.length}</span></button>{categories.map(key => <button key={key} aria-pressed={category === key} onClick={() => setCategory(key)}><CategoryMark category={key} />{categoryNames[key]} <span>{batchCases.filter(c => c.category === key).length}</span></button>)}</div>
      <label className={styles.search}><Search size={16} /><input aria-label="Search batch evidence" placeholder="Search the evidence…" value={query} onChange={e => setQuery(e.target.value)} /></label>
    </div>
    <div className={styles.tableScroll}>
      <table className={styles.batchTable}>
        <thead><tr><th>Source</th><th>Extracted frequency</th><th>Category</th><th>Selected evidence</th><th><span className={styles.srOnly}>Inspect source</span></th></tr></thead>
        <tbody>{filtered.map(c => {
          const evidence = decisionEvidence(c);
          const selected = evidence.ids.map(id => id.toUpperCase()).join(", ");
          const quotes = evidence.quotes.map((quote, i) => <q key={i}>{quote}</q>);
          return <tr key={c.id}>
            <td><span className={styles.tableId}>Letter {c.id}</span><small>{c.note.match(/Clinic Date:\s*([^\n]+)/)?.[1] ?? "Synthetic letter"}</small></td>
            <td><strong>{c.hybrid.selection.final_label}</strong>{c.record.selection.final_label !== c.hybrid.selection.final_label && <small>Revised by rules</small>}</td>
            <td><CategoryPill category={c.category} /></td>
            <td>{evidence.attributionUnchanged ? <div className={styles.attributionReview}>
              <span>Evidence attribution needs review</span>
              <small>The rule revised the label but kept the original selection.</small>
              <details><summary>View saved selection · {selected}</summary>{quotes}</details>
            </div> : <>{quotes.length ? quotes : <span className={styles.missingEvidence}>No source quote recorded for this selection.</span>}<small>{selected || "No event IDs recorded"} · {c.record.events.length} extracted {c.record.events.length === 1 ? "event" : "events"}</small></>}</td>
            <td><button aria-label={`Inspect letter ${c.id}`} onClick={() => onInspect(c.id)}><ArrowRight size={18} /></button></td>
          </tr>;
        })}</tbody>
      </table>
    {!filtered.length && <div className={styles.empty}><h2>No records match these filters.</h2><p>Try a different phrase or return to all letters.</p><button className={styles.secondary} onClick={() => { setCategory("all"); setQuery(""); }}>Clear filters</button></div>}</div>
    <div className={styles.batchNotes}><p>Each quote comes from the final recorded selection. When a rule revises the label without updating its evidence attribution, the row flags it for review. Open a letter to inspect all candidates and the decision trace.</p><details><summary>Selection and intended use</summary><p>{batchPolicy} All outputs use the saved Gemini 3.7 Flash extraction and the recorded Hybrid rules.</p><p>This illustrates screening records for research review. These letters are not linked patient visits. Exports are marked “not_reviewed”; using them as training labels or predictive outcomes would require a separate review and evaluation.</p></details><span role="status">{downloaded ? "Export prepared with source text, evidence, provenance and review status." : `${filtered.length} of ${batchCases.length} records shown`}</span></div>
  </div>;
}
