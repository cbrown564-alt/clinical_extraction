"use client";

import { ArrowRight } from "lucide-react";
import s from "./story.module.css";
import imagery from "./introImagery.module.css";
import base from "./demo.module.css";
import DemoIllustration from "./DemoIllustration";
import PastApproaches from "./PastApproaches";
import ResearchPipeline from "./ResearchPipeline";

const challenges = [
  { name: "Time", image: "time", explanation: "Distinguish the current account from the past.", alt: "Previously: daily seizures. Now: two each month. Both accounts remain visible; the current statement is highlighted." },
  { name: "Arithmetic", image: "arithmetic", explanation: "Combine counts over the stated span. Missing does not mean zero.", alt: "Three events in February, March not stated, five events in April. The inclusive span is three months; 3 plus 5 equals 8." },
  { name: "Context", image: "context", explanation: "One event type can stop while another continues.", alt: "Two separate accounts: convulsions have stopped, while brief auras continue weekly." },
];

export default function Introduction({ onStart }: { onStart: () => void }) {
  return <div className={s.chapter}>
    <section className={imagery.hero}>
      <div><span className={s.kicker}>The problem</span><h1>Useful clinical data.<br />Written as a story.</h1><p>Seizure frequency is recorded in clinic letters. Research needs an answer that can be compared, counted, and traced back.</p><button className={base.primary} onClick={onStart}>Follow a saved pipeline record <ArrowRight size={16} /></button></div>
      <DemoIllustration name="hero-clinic-v1" hero alt="Paper sculpture of a clinician and patient in conversation, with highlighted passages on a clinic letter." />
    </section>
    <section className={imagery.challenges} aria-labelledby="challenges-title"><h2 id="challenges-title">Reading the words is only the start.</h2>
      <div className={imagery.challengeGrid}>{challenges.map(c => <article className={imagery.challenge} key={c.name}><h3>{c.name}</h3><DemoIllustration name={`challenge-${c.image}-v1`} alt={c.alt} /><p>{c.explanation}</p></article>)}</div>
      <p className={imagery.note}>Authored teaching examples. The arithmetic illustrates a decision policy, not a universal clinical interpretation.</p>
    </section>
    <PastApproaches />
    <ResearchPipeline />
    <div className={s.chapterEnd}><p>Now follow a saved letter through each step.</p><button className={base.primary} onClick={onStart}>Explore the pipeline <ArrowRight size={15} /></button></div>
  </div>;
}
