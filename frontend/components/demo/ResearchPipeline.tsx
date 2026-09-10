import DemoIllustration from "./DemoIllustration";
import s from "./introImagery.module.css";

export default function ResearchPipeline() {
  return <section className={s.section} aria-labelledby="research-pipeline-title">
    <header><h2 id="research-pipeline-title">Extract the evidence. Then decide.</h2><p>Keep the facts, their exact evidence and normalised labels, together with the extraction’s proposed answer and rationale. Rules or a second LLM can then decide from that saved record.</p></header>
    <DemoIllustration name="research-overview-v2" alt="Extract turns a clinic letter into one organised record, preserving evidence, structured facts and a proposed selection. Decide reads that shared record using either rules or a second LLM." />
    <p className={s.note}>These are authored illustrations, not saved model outputs. Both decision methods read the record; neither returns to the letter for new evidence.</p>
    <article className={s.stage}>
      <header><h3>Extract: preserve the facts and their evidence.</h3><p>The record keeps both February and April, even when extraction proposes April alone. Each fact retains its quotation, normalised label and timeframe. Selection and rationale are recorded separately.</p></header>
      <DemoIllustration name="research-extract-v2" alt="A clinic letter links to two evidence entries: Three in February, normalised to 3 per month; Five in April, normalised to 5 per month. Extraction proposes Fact 2 because April is the latest reported month." />
      <details className={s.recordText}><summary>Read the illustrative extraction record</summary><ul><li><strong>Fact 1:</strong> “Three in February.” Normalised label: 3 per month. Time: February.</li><li><strong>Fact 2:</strong> “Five in April.” Normalised label: 5 per month. Time: April.</li><li><strong>Extraction proposal:</strong> select Fact 2; answer 5 per month. Rationale: April is the latest reported month.</li></ul><p>This illustration shows the richer record structure. Older saved demo records may have no per-fact normalised label.</p></details>
    </article>
    <article className={s.stage}>
      <header><h3>Decide: apply the policy and explain the selection.</h3><p>The demonstrated policy selects both facts, combines their stated counts and uses the inclusive February–April span. Preserving Fact 1 makes this decision possible even though extraction proposed Fact 2.</p></header>
      <DemoIllustration name="research-decide-v1" alt="Both retained facts contribute to the decision. The policy combines 3 and 5 across February to April, a three-month span. Selected facts: Fact 1 and Fact 2. Answer: 8 over 3 months." />
      <details className={s.recordText}><summary>Read the illustrative decision record</summary><ul><li><strong>Selected facts:</strong> Fact 1 and Fact 2.</li><li><strong>Calculation:</strong> 3 + 5 = 8 stated events. February through April spans three months.</li><li><strong>Answer:</strong> 8 over 3 months.</li><li><strong>Rationale:</strong> both counts contribute; February–April spans three months.</li></ul><p>March has no stated count. The dash does not mean zero. This calculation illustrates the demonstrated policy, not a universal clinical interpretation.</p></details>
    </article>
  </section>;
}
