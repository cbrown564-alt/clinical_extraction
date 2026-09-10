"use client";

import { ArrowRight } from "lucide-react";
import s from "./story.module.css";
import imagery from "./introImagery.module.css";
import base from "./demo.module.css";
import DemoIllustration from "./DemoIllustration";
import PastApproaches from "./PastApproaches";
import ResearchPipeline from "./ResearchPipeline";

const challenges = [
  { name: "Time", image: "time", explanation: "Distinguish past seizure rates from what is happening right now.", alt: "Previously: daily seizures. Now: two each month. Both accounts remain visible; the current statement is highlighted." },
  { name: "Math", image: "arithmetic", explanation: "Combine counts across months to calculate the total over the whole window.", alt: "Three events in February, March not stated, five events in April. The inclusive span is three months; 3 plus 5 equals 8." },
  { name: "Context", image: "context", explanation: "Recognise when one seizure type stops while another continues.", alt: "Two separate accounts: convulsions have stopped, while brief auras continue weekly." },
];

export default function Introduction({ onStart }: { onStart: () => void }) {
  return <div className={s.chapter}>
    <section className={imagery.hero}>
      <div><span className={s.kicker}>The problem</span><h1>Clinical notes are messy.<br />Research needs clean data.</h1><p>Doctors describe seizures using varied phrasing, dates, and estimates across multiple visits. Turning that narrative into dependable numbers requires extracting the right facts, doing the math, and keeping an exact quote for every count.</p><button className={base.primary} onClick={onStart}>See how the pipeline works <ArrowRight size={16} /></button></div>
      <DemoIllustration name="hero-clinic-v2" hero alt="Paper sculpture of a clinician and patient in conversation, with highlighted passages on a clinic letter." />
    </section>
    <section className={imagery.valueBeat} aria-labelledby="value-title">
      <header>
        <h2 id="value-title">From individual letters to life-changing research</h2>
        <p>Reliable, verifiable extraction turns routine clinical letters into actionable data across healthcare and research:</p>
      </header>
      <div className={imagery.valueGrid}>
        <article className={imagery.valueCard}>
          <DemoIllustration name="research-value-trials-v2" alt="A researcher selects a patient record from a collection of clinical histories." />
          <strong>Screening clinical trials</strong>
          <p>Find eligible trial participants in minutes instead of manually reading hundreds of hospital records.</p>
        </article>
        <article className={imagery.valueCard}>
          <DemoIllustration name="research-value-registry-v2" alt="An unfolding patient history connects records across successive visits." />
          <strong>Long-term patient registries</strong>
          <p>Track multi-year treatment response and seizure freedom across thousands of routine patient visits.</p>
        </article>
        <article className={imagery.valueCard}>
          <DemoIllustration name="research-value-risk-v2" alt="An evidence record connects to three groups of patient histories for risk stratification." />
          <strong>Predicting patient risk</strong>
          <p>Spot subtle trajectory changes in notes that help identify who is at risk of treatment failure.</p>
        </article>
      </div>
    </section>
    <section className={imagery.challenges} aria-labelledby="challenges-title"><h2 id="challenges-title">Three common challenges in clinic notes</h2>
      <div className={imagery.challengeGrid}>{challenges.map(c => <article className={imagery.challenge} key={c.name}><DemoIllustration name={`challenge-${c.image}-v2`} alt={c.alt} /><div className={imagery.challengeCopy}><h3>{c.name}</h3><p>{c.explanation}</p></div></article>)}</div>
      <p className={imagery.note}>Sample cases created to demonstrate the logic. Clinic policies and calculations can be customized.</p>
    </section>
    <PastApproaches />
    <ResearchPipeline />
    <div className={s.chapterEnd}><p>Now follow a saved letter through each step.</p><button className={base.primary} onClick={onStart}>Explore the pipeline <ArrowRight size={15} /></button></div>
  </div>;
}
