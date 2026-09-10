import DemoIllustration from "./DemoIllustration";
import s from "./introImagery.module.css";

export default function ResearchPipeline() {
  return <section className={s.section} aria-labelledby="research-pipeline-title">
    <header><h2 id="research-pipeline-title">Step 1: Pull out the facts. Step 2: Make the decision.</h2><p>Instead of asking an LLM to do everything in one shot, we split the job in two: first capture every quoted fact, then apply clear decision rules to pick the answer.</p></header>
    <DemoIllustration name="research-overview-v3" alt="Extract turns a clinic letter into one organised record, preserving evidence, structured facts and a proposed selection. Decide reads that shared record using either rules or a second LLM." />
    <p className={s.note}>These are authored illustrations, not saved model outputs. Both decision methods read the record; neither returns to the letter for new evidence.</p>
    <article className={s.stage}>
      <header><h3>Step 1 (Extract): Capture the facts with exact quotes</h3><p>An AI reads the letter and identifies every mention of seizures, along with its exact quote and normalized rate. If the extraction suggests an initial answer, that proposal is saved alongside the evidence.</p></header>
      <DemoIllustration name="research-extract-v3" alt="A clinic letter links to two evidence entries: Three in February, normalised to 3 per month; Five in April, normalised to 5 per month. Extraction proposes Fact 2 because April is the latest reported month." />
      <details className={s.recordText}><summary>Read the illustrative extraction record</summary><ul><li><strong>Fact 1:</strong> “Three in February.” Normalised label: 3 per month.</li><li><strong>Fact 2:</strong> “Five in April.” Normalised label: 5 per month.</li><li><strong>Extraction proposal:</strong> select Fact 2; answer 5 per month. Rationale: April is the latest reported month.</li></ul><p>This illustration shows the richer record structure. Older saved demo records may have no per-fact normalised label.</p></details>
    </article>
    <article className={s.stage}>
      <header><h3>Step 2 (Decide): Run transparent rules over the record</h3><p>Explicit decision rules review the collected facts, calculate the totals across the relevant months, and produce the final category. If an answer looks unexpected, you can inspect both the arithmetic and the source quotes.</p></header>
      <DemoIllustration name="research-decide-v2" alt="Both retained facts contribute to the decision. The policy combines 3 and 5 across February to April, a three-month span. Selected facts: Fact 1 and Fact 2. Answer: 8 over 3 months." />
      <details className={s.recordText}><summary>Read the illustrative decision record</summary><ul><li><strong>Selected facts:</strong> Fact 1 and Fact 2.</li><li><strong>Calculation:</strong> 3 + 5 = 8 stated events. February through April spans three months.</li><li><strong>Answer:</strong> 8 over 3 months.</li><li><strong>Rationale:</strong> both counts contribute; February–April spans three months.</li></ul><p>March has no stated count. The dash does not mean zero. This calculation illustrates the demonstrated policy, not a universal clinical interpretation.</p></details>
    </article>
  </section>;
}
