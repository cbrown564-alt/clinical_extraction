import DemoIllustration from "./DemoIllustration";
import s from "./introImagery.module.css";
const methods = [
  { name: "Rules", verb: "Write the rules.", kind: "rules", detail: "Explicit patterns and domain vocabularies make decisions inspectable, but varied phrasing and context require ongoing rule work. EpiDEA extends cTAKES with an epilepsy ontology and supports visual cohort queries.", cite: "Cui et al. · EpiDEA", href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC3540531/" },
  { name: "Trained models", verb: "Learn from labelled examples.", kind: "trained", detail: "Supervised models learn a task from labelled notes. Chang et al. compare fine-tuned BERT with DeepSeek-R1 for epilepsy and seizure-type phenotyping. Those are different targets from seizure frequency.", cite: "Chang et al. · 2026 preprint", href: "https://doi.org/10.64898/2026.02.11.26346003" },
  { name: "Prompted LLMs", verb: "Specify the task in a prompt.", kind: "prompted", detail: "Instructions and examples steer a pretrained model. CLINES uses a specification-driven workflow for extraction and structuring; SNOW uses multiple LLM agents to generate predictive features. These related systems address broader tasks and use different architectures.", cite: "Yang et al. · CLINES, 2025 preprint", href: "https://doi.org/10.64898/2025.12.01.25341355" },
];
const descriptions = [
  "Rules match the phrase, check whether it is current, and map it to 2 per month. Patterns and vocabulary supply the task knowledge.",
  "Labelled examples feed training. A new clinic letter passes through the trained model to produce 2 per month.",
  "A clinic letter and task instructions enter a pretrained LLM together at runtime to produce 2 per month."
];
export default function PastApproaches() {
  return <section className={s.section} aria-labelledby="past-approaches-title">
    <header><h2 id="past-approaches-title">Same task. Different machinery.</h2><p>Past approaches turn clinic letters into structured data. Where does the task knowledge come from?</p></header>
    <div className={s.methods}>{methods.map((method, i) => <article className={s.method} key={method.kind}>
      <header><h3>{method.name}</h3><p>{method.verb}</p></header>
      <DemoIllustration name={`past-${method.kind}-untitled-v1`} portrait alt={descriptions[i]} />
      <details><summary>How it works &amp; source</summary><p>{descriptions[i]}</p><p>{method.detail}</p><a href={method.href} target="_blank" rel="noreferrer">{method.cite} ↗</a></details>
    </article>)}</div>
    <p className={s.note}>Illustrative approaches, not measured predictions. The cited systems address different clinical tasks. Open any illustration to read it at full size.</p>
  </section>;
}
