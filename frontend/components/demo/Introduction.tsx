"use client";

import { useState } from "react";
import { ArrowRight, FileText, Play } from "lucide-react";
import s from "./story.module.css";
import base from "./demo.module.css";
import PastApproaches from "./PastApproaches";
import ResearchPipeline from "./ResearchPipeline";

const challenges = [
  { name: "Time", before: "Previously, seizures were daily.", quote: "Now, two each month.", answer: "2 per month", explanation: "A past frequency and a current frequency can appear in the same sentence. The question is which period the answer should describe." },
  { name: "Arithmetic", before: "Three seizures in February.", quote: "Five in April.", answer: "8 over 3 months", explanation: "Counts need a denominator. Under the demonstrated policy, February through April is a three-month span, including March. This is a teaching example of a policy, not a universal clinical interpretation." },
  { name: "Context", before: "No more convulsions.", quote: "Brief auras still occur weekly.", answer: "Continuing events", explanation: "Freedom from one seizure type is not necessarily freedom from all events. Keeping each statement allows the decision policy to resolve the apparent conflict." },
];

export default function Introduction({ onStart }: { onStart: () => void }) {
  const [challenge, setChallenge] = useState(0);
  const example = challenges[challenge];
  return <div className={s.chapter}>
    <section className={s.hero}>
      <div><span className={s.kicker}>The problem</span><h1>Useful clinical data.<br />Written as a story.</h1><p>Seizure frequency is recorded in clinic letters.<br />Research needs an answer that can be compared, counted, and traced back.</p><button className={base.primary} onClick={onStart}>Follow a saved pipeline record <ArrowRight size={16} /></button></div>
      <div className={s.problemIllustration} aria-label="Illustrative clinic text becomes a structured research record">
        <div className={s.sampleLetter}><span><FileText size={16} />Illustrative clinic letter</span><p>“{example.before}<br /><mark>{example.quote}</mark>”</p><small>Two statements. One current answer.</small></div>
        <div className={s.sampleOutput}><ArrowRight size={22} /><div><small>What should we record?</small><strong key={challenge}>{example.answer}</strong></div></div>
      </div>
    </section>
    <section className={s.challengeStrip} aria-label="Why extraction is difficult"><div><h2>Reading the words is only the start.</h2><div className={s.segmented}>{challenges.map((c, i) => <button key={c.name} aria-pressed={challenge === i} onClick={() => setChallenge(i)}>{c.name}</button>)}</div></div><p>{example.explanation}</p></section>
    <PastApproaches />
    <ResearchPipeline />
    <div className={s.chapterEnd}><p>Now follow a saved letter through each step.</p><button className={base.primary} onClick={onStart}>Explore the pipeline <Play size={15} /></button></div>
  </div>;
}
