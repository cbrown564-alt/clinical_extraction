import ApplicationIcon from "./ApplicationIcon";
import Image from "next/image";
import { ArrowRight } from "lucide-react";
import { syntheticPatients, stateFor, visitMonths } from "@/lib/syntheticPatients";
import s from "./applicationStories.module.css";
const states = ["Seizure free", "1–3 / month", "4+ / month", "Unknown"];
export default function LongitudinalIntroduction({ onExplore }: { onExplore: () => void }) {
  return <div className={s.story}>
    <section className={s.hero}><div><span className={s.badge}><ApplicationIcon kind="longitudinal" />Patient timelines · simulated data</span><h1>Track patient progress<br />across multiple visits.</h1><p>See how seizure frequency evolves over a 12-month period, with every change linked to a clinic letter.</p><button className={s.action} onClick={onExplore}>Inspect patient timelines <ArrowRight size={17} /></button></div><Image className={s.heroIllustration} src="/demo/imagery/longitudinal-hero-v2.png" alt="Paper sculpture of a researcher reviewing one patient’s history across an unfolding sequence of visit records." width={1536} height={1024} sizes="(max-width: 760px) 100vw, 55vw" /></section>
    <section className={s.timelineScope} aria-label="Timeline cohort overview">
      <div className={s.timelineCohort}>
        <Image src="/demo/imagery/application-cohort-icon-v2.png" alt="" width={100} height={100} sizes="100px" />
        <div><strong>72 patients</strong><span>One year of follow-up</span></div>
      </div>
      <div className={s.timelineVisits}>
        <div className={s.timelineScopeHeading}><strong>5 clinic visits</strong><span>Seizure frequency recorded at each visit</span></div>
        <ol aria-label="Clinic visit months">{visitMonths.map(month => <li key={month}><i aria-hidden="true" /><span>Month {month}</span></li>)}</ol>
      </div>
    </section>
    <section className={`${s.section} ${s.split} ${s.splitReverse}`}><div><h2>Separate when it happened<br />from when it was written.</h2><p>Letters often describe events that occurred months earlier. The pipeline keeps event dates distinct from documentation dates.</p><ul className={s.cohortCriteria}><li>February: Seizure occurred</li><li>December: Clinic letter written</li></ul></div><Image className={s.heroIllustration} src="/demo/imagery/longitudinal-two-dates-v2.png" alt="A December letter says: She had a seizure in February. Its quotation connects back to a single event on the February calendar." width={1536} height={1024} sizes="(max-width: 760px) 100vw, 55vw" /></section>
    <section className={s.section}><h2>Building a connected patient history.</h2><div className={s.historyIllustrations}><article><Image className={s.heroIllustration} src="/demo/imagery/history-mentions-v2.png" alt="Two source quotations connect to the same event." width={1536} height={1024} sizes="(max-width: 760px) 100vw, 33vw" /><h3>Repeated mentions</h3><p>Connect multiple references back to the same event.</p></article><article><Image className={s.heroIllustration} src="/demo/imagery/history-new-evidence-v2.png" alt="A new source quotation joins the existing patient record." width={1536} height={1024} sizes="(max-width: 760px) 100vw, 33vw" /><h3>New updates</h3><p>Log updates and medication adjustments as letters arrive.</p></article><article><Image className={s.heroIllustration} src="/demo/imagery/history-gap-v2.png" alt="One patient’s unfolding history retains an empty evidence slot between documented visits." width={1536} height={1024} sizes="(max-width: 760px) 100vw, 33vw" /><h3>Gaps in care</h3><p>Keep unmentioned periods transparent instead of assuming zero.</p></article></div></section>
    <section className={`${s.section} ${s.split}`}><div><h2>From one patient<br />to cohort-wide trends.</h2><p>Compare seizure control across all 72 patients at every clinic visit.</p><button className={s.action} onClick={onExplore}>Inspect the timeline <ArrowRight size={17} /></button></div><div><div className={s.chart}>{visitMonths.map(m => <div key={m}><div className={s.stack}>{states.map((state, i) => { const count = syntheticPatients.filter(p => stateFor(p.visits.find(v => v.month === m)!.rate) === state).length; return count > 0 && <span key={state} data-state={i} style={{height: `${count / 72 * 100}%`}} title={`${state}: ${count}`} aria-label={`Month ${m}, ${state}: ${count}`}>{count}</span>; })}</div><small>Month {m}</small></div>)}</div><div className={s.legend}>{states.map((state, i) => <span key={state}><i data-state={i} />{state}</span>)}</div></div></section>
    <div className={s.footer}><small>Simulated visit histories · select any point to view its source note</small><button onClick={onExplore}>Open timeline explorer <ArrowRight size={16} /></button></div>
    <details className={s.note}><summary>Methodology notes &amp; sources</summary><p>Displays documented frequency across 5 clinic visits. Unknown visits remain flagged. Demonstrates longitudinal assembly and timeline navigation.</p><p>Background: literature on longitudinal epilepsy outcome registries and health records extraction (Xie et al., Long-term epilepsy outcome dynamics; Chang et al.).</p></details>
  </div>;
}
