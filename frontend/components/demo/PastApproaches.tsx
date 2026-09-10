import DemoIllustration from "./DemoIllustration";
import s from "./introImagery.module.css";
const methods = [
  { name: "Handwritten rules", verb: "Write explicit logic.", kind: "rules", detail: "Fast and inspectable, but varied phrasing and context require ongoing maintenance as notes change. EpiDEA extends cTAKES with an epilepsy ontology and supports visual cohort queries.", cite: "Cui et al. · EpiDEA", href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC3540531/" },
  { name: "Trained models", verb: "Learn from labelled examples.", kind: "trained", detail: "Supervised models learn from annotated notes, but require large training datasets to cover edge cases. Chang et al. compare fine-tuned BERT with DeepSeek-R1 for epilepsy and seizure-type phenotyping.", cite: "Chang et al. · 2026 preprint", href: "https://doi.org/10.64898/2026.02.11.26346003" },
  { name: "Prompted LLMs", verb: "Ask an LLM directly in a prompt.", kind: "prompted", detail: "Instructions steer a pretrained model at runtime. Flexible, but prone to silent calculation errors and hard to audit directly. CLINES and SNOW explore broader multi-agent clinical extraction.", cite: "Yang et al. · CLINES, 2025 preprint", href: "https://doi.org/10.64898/2025.12.01.25341355" },
];
const descriptions = [
  "Rules match phrases and map them to numbers using predetermined patterns and vocabularies.",
  "Annotated examples train a model to predict structured categories directly from new notes.",
  "A clinical note and instructions are sent directly to an LLM to generate an answer in one go."
];
export default function PastApproaches() {
  return <section className={s.section} aria-labelledby="past-approaches-title">
    <header><h2 id="past-approaches-title">Three traditional ways to extract clinical data</h2><p>How existing tools turn unstructured clinic notes into structured figures:</p></header>
    <div className={s.methods}>{methods.map((method, i) => <article className={s.method} key={method.kind}>
      <header><h3>{method.name}</h3><p>{method.verb}</p></header>
      <DemoIllustration name={`past-${method.kind}-untitled-v2`} portrait alt={descriptions[i]} />
      <details><summary>How it works &amp; source</summary><p>{descriptions[i]}</p><p>{method.detail}</p><a href={method.href} target="_blank" rel="noreferrer">{method.cite} ↗</a></details>
    </article>)}</div>
    <p className={s.note}>Illustrative approaches, not measured predictions. The cited systems address different clinical tasks. Open any illustration to read it at full size.</p>
  </section>;
}
