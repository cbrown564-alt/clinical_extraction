"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { emergencyPatients, fitEmergencyModel, reviewAtCapacity } from "@/lib/emergencyRisk";
import s from "./riskStratification.module.css";
import base from "./demo.module.css";
import shared from "./story.module.css";

export default function EmergencyRiskExplorer({ onBack }: { onBack: () => void }) {
  const models = useMemo(() => ({ structured: fitEmergencyModel(false), notes: fitEmergencyModel(true) }), []);
  const [includeNotes, setIncludeNotes] = useState(true);
  const [capacity, setCapacity] = useState(6);
  const [patientId, setPatientId] = useState(() => reviewAtCapacity(models.notes.rows, 6).ranked[0]?.patient.id ?? "");
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.scrollIntoView({ block: "start" }); }, []);
  const model = includeNotes ? models.notes : models.structured;
  const review = reviewAtCapacity(model.rows, capacity);
  const baseline = reviewAtCapacity(models.structured.rows, capacity);
  const enhanced = reviewAtCapacity(models.notes.rows, capacity);
  const patient = emergencyPatients.find(p => p.id === patientId) ?? emergencyPatients.find(p => p.id === review.ranked[0]?.patient.id);
  const rankOf = (rows: typeof review.ranked, id: string) => rows.findIndex(r => r.patient.id === id) + 1;
  const brier = (rows: typeof review.ranked) => rows.reduce((sum, r) => sum + (r.probability - r.target) ** 2, 0) / rows.length;
  return <div className={s.explorer}>
    <header className={`${shared.sectionHeading} ${s.heading}`}>
      <div><h1 ref={heading}>Prioritise clinical review</h1><p>Compare simulated emergency-care risk with and without clinical notes.</p></div>
      <button className={base.secondary} onClick={onBack}>Back to overview</button>
    </header>
    <div className={`${shared.filters} ${s.toolbar}`}>
      <label>Model inputs<select value={includeNotes ? "notes" : "structured"} onChange={e => setIncludeNotes(e.target.value === "notes")}><option value="structured">Structured records only</option><option value="notes">Structured records + clinical notes</option></select></label>
      <label className={s.capacity} htmlFor="review-capacity"><span>Review capacity <strong>{capacity} / {model.test.length} patients</strong></span><input id="review-capacity" type="range" min="0" max={model.test.length} value={capacity} onChange={e => setCapacity(Number(e.target.value))} /></label>
    </div>
    <section aria-label="Review outcomes" className={s.outcomes} aria-live="polite">
      <div><strong>{review.captured}<small> / {review.captured + review.missed}</small></strong><span>Emergency cases in review list</span></div>
      <div><strong>{review.missed}</strong><span>Emergency cases outside list</span></div>
      <div><strong>{review.withoutEvent}</strong><span>Reviews without an emergency</span></div>
    </section>
    <div className={s.workspace}>
      <section className={s.ranking} aria-label="Patient rankings">
        <div className={s.panelHeading}><h2>Priority review list</h2><span>{capacity} review places</span></div>
        <div className={s.columnLabels} aria-hidden="true"><span>Rank</span><span>Patient</span><span>Estimated risk</span><span>Rank change¹</span></div>
        <div className={s.list}>{review.ranked.map((row, i) => {
          const shift = rankOf(baseline.ranked, row.patient.id) - rankOf(enhanced.ranked, row.patient.id);
          return <div key={row.patient.id}>
            {i === capacity && capacity > 0 && <div className={s.cutoff}>Remaining patients · outside review capacity</div>}
            <button aria-pressed={patient?.id === row.patient.id} onClick={() => setPatientId(row.patient.id)} className={s.patient} data-review={i < capacity} aria-label={`${row.patient.id}, rank ${i + 1}, ${Math.round(row.probability * 100)} percent simulated risk, ${i < capacity ? "in review list" : "outside capacity"}, rank ${shift > 0 ? `up ${shift}` : shift < 0 ? `down ${-shift}` : "unchanged"} with notes`}>
              <span className={s.rank}>{i + 1}</span><strong>{row.patient.id}</strong>
              <span className={s.risk}><span className={s.track}><i style={{width: `${row.probability * 100}%`}} /></span><span>{Math.round(row.probability * 100)}%</span></span>
              <span className={s.shift} data-direction={shift > 0 ? "up" : "down"}>{shift > 0 ? `↑ ${shift}` : shift < 0 ? `↓ ${-shift}` : "—"}</span>
            </button>
          </div>;
        })}</div>
        <p className={s.listNote}>{capacity === 0 ? "No review places selected. Increase capacity to create a review list." : "Select a patient to inspect the evidence."}<br />¹ Change in rank when clinical notes are added.</p>
      </section>
      {patient && <aside className={`${shared.evidencePanel} ${s.evidence}`} aria-label="Risk feature evidence" key={patient.id}>
        <div className={s.panelHeading}><h2>{patient.id}</h2><span>Month 6 assessment</span></div>
        <p className={s.patientMeta}>{patient.age} years · {patient.medications} medication{patient.medications === 1 ? "" : "s"}</p>
        <div className={s.rankComparison}><div><span>Structured records</span><strong>#{rankOf(baseline.ranked, patient.id)}</strong></div><span aria-hidden="true">→</span><div><span>With clinical notes</span><strong>#{rankOf(enhanced.ranked, patient.id)}</strong></div></div>
        <h3>Clinical signals</h3>
        <dl className={s.features}>
          <div><dt>Previous emergency care<small>Preceding year · structured record</small></dt><dd>{patient.priorEmergency === 0 ? "None recorded" : "1 attendance"}</dd></div>
          <div><dt>Tonic-clonic seizures<small>Preceding 3 months · clinic note</small></dt><dd>{patient.tonicClonic === null ? "Not documented" : patient.tonicClonic}</dd></div>
          <div><dt>Missed medication doses<small>Patient report · clinic note</small></dt><dd>{patient.adherenceConcern === null ? "Not discussed" : patient.adherenceConcern ? "Most weeks" : "Reports none"}</dd></div>
        </dl>
        <details className={`${shared.more} ${s.source}`}><summary>Read supporting clinic note</summary><pre>{patient.riskNote}</pre></details>
        <h3>Frequency history</h3>
        <div className={s.visits}>{patient.visits.filter(v => v.month <= 6).map(v => <details key={v.id}><summary><span>Month {v.month}</span><strong>{v.rate === null ? "Unknown" : `${v.rate} / month`}</strong></summary><blockquote>{v.evidence}</blockquote><details className={s.source}><summary>Full visit note</summary><pre>{v.note}</pre></details></details>)}</div>
        <details className={s.source}><summary>Show follow-up outcome</summary><p>{patient.emergencyOutcome === 1 ? "A seizure-related emergency attendance or admission occurred" : "No seizure-related emergency attendance or admission occurred"} during months 6–18. This simulated outcome is not a model input.</p></details>
      </aside>}
    </div>
    <p className={s.footnote}>Simulated records and outcomes. Missing information remains unknown; review-list inclusion does not imply an emergency was prevented.</p>
    <details className={`${shared.more} ${s.methods}`}><summary>Model comparison, calibration and simulation assumptions</summary><p>Predictors use records available through month 6. Emergency attendance or admission is simulated over the following 12 months, through month 18.</p><p>{model.train.length} training patients · {model.test.length} evaluation patients · {model.excluded} patients excluded from both models because emergency follow-up is unknown. Exclusion is a demo simplification and may introduce bias in real data.</p><table><caption>Evaluation on the same simulated patients</caption><thead><tr><th>Measure</th><th>Structured only</th><th>With notes</th></tr></thead><tbody><tr><th>Emergency cases in {capacity} review places</th><td>{baseline.captured}</td><td>{enhanced.captured}</td></tr><tr><th>AUC</th><td>{models.structured.auc?.toFixed(2) ?? "Undefined"}</td><td>{models.notes.auc?.toFixed(2) ?? "Undefined"}</td></tr><tr><th>Brier score (lower is better)</th><td>{brier(models.structured.rows).toFixed(3)}</td><td>{brier(models.notes.rows).toFixed(3)}</td></tr><tr><th>Mean predicted risk</th><td>{Math.round(models.structured.rows.reduce((sum, r) => sum + r.probability, 0) / model.rows.length * 100)}%</td><td>{Math.round(models.notes.rows.reduce((sum, r) => sum + r.probability, 0) / model.rows.length * 100)}%</td></tr><tr><th>Observed event proportion</th><td colSpan={2}>{Math.round(model.rows.filter(r => r.target).length / model.rows.length * 100)}%</td></tr></tbody></table><p>Mean prediction versus observed proportion is a limited calibration check; this small simulation cannot establish calibrated clinical probabilities.</p><p>Emergency simulation v1, seed 91026, extends the existing 72 fictional profiles (seed 8056). Outcomes are Bernoulli draws from an arbitrary logistic formula using prior emergency care, tonic-clonic burden, adherence, frequency and trajectory. It intentionally makes note information relevant; any advantage is not research evidence.</p><p>Both logistic regressions use the same patient partitions (index modulo 3), training-only standardisation, 700 steps, learning rate 0.08 and L2 penalty 0.04 with an unpenalised intercept. No extraction model was run. Frequency features use the latest available value and first-to-last difference through month 6, plus missing-visit count. Unknown values use zero placeholders with missingness indicators. Ties are ordered by patient ID.</p></details>
    <details className={s.methods}><summary>Research basis and other risk-stratification uses</summary><p>A <a href="https://pubmed.ncbi.nlm.nih.gov/41212874/" target="_blank" rel="noreferrer">2025 cohort study protocol</a> proposes predicting emergency care and epilepsy-related death over one year. It motivates this workflow; it supplies neither fitted coefficients nor performance claims for this demo.</p><p>Other distinct applications include <a href="https://discovery.ucl.ac.uk/id/eprint/10127330" target="_blank" rel="noreferrer">SUDEP risk research</a> and <a href="https://repub.eur.nl/pub/99753/" target="_blank" rel="noreferrer">recurrence after medication withdrawal</a>. Each requires its own population, predictors, outcome and validation. The emergency score shown here cannot be used for those outcomes.</p></details>
  </div>;
}
