import { Braces } from "lucide-react";
import method from "@/lib/viva-method.json";
import s from "./story.module.css";
import p from "./promptComponents.module.css";

const prompt = method.prompts.extract;

export default function PromptComponents({ selected }: { selected: number }) {
  return <details className={s.more}>
    <summary><Braces size={15} />Prompt components</summary>
    <div className={p.content}>
      <p>Excerpts from the saved full extraction prompt, grouped by component. Original wording is preserved. Select an ablation row above to highlight the corresponding component; this is not the full ablated payload.</p>
      <section className={p.component} data-selected={selected === 1}>
        <h3>Examples {selected === 1 && <span>Selected ablation</span>}</h3>
        <p>Concrete answer strings show the model how to use the label forms. Three example groups from <code>label_forms.forms[].examples</code>:</p>
        <dl className={p.examples}>{prompt.label_forms.forms.slice(0, 3).map(form => <div key={form.form}><dt>{form.form}</dt><dd>{form.examples.map(example => <code key={example}>{example}</code>)}</dd></div>)}</dl>
      </section>
      <section className={p.component} data-selected={selected === 2}>
        <h3>Evidence obligation {selected === 2 && <span>Selected ablation</span>}</h3>
        <p>The instruction asks for source quotations; the event schema also defines the evidence field.</p>
        <blockquote>{prompt.instructions.find(instruction => instruction.startsWith("Every evidence value"))}</blockquote>
        <div className={p.field}><code>event_schema.evidence</code><q>{prompt.event_schema.evidence}</q></div>
      </section>
      <section className={p.component} data-selected={selected === 3}>
        <h3>Closed label forms {selected === 3 && <span>Selected ablation</span>}</h3>
        <p>The prompt restricts the answer to named forms. The instruction also refers to the examples above.</p>
        <blockquote>{prompt.instructions.find(instruction => instruction.startsWith("Write the seizure-frequency label"))}</blockquote>
        <div className={p.forms}>{prompt.label_forms.forms.map(form => <code key={form.form} title={form.description}>{form.form}</code>)}</div>
        <ul>{prompt.label_forms.rules.map(rule => <li key={rule}>{rule}</li>)}</ul>
      </section>
      <p className={p.source}>Source: saved Extract prompt used by the demo’s “Under the hood” view. These are label-format examples, not additional patient records.</p>
    </div>
  </details>;
}
