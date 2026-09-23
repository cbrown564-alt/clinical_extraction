"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { FileText, Layers3 } from "lucide-react";
import LetterRenderer from "@/components/surface/LetterRenderer";
import {
  ControlBar, ControlField, ControlFixedValue, ControlSelect, ExplorerBody,
  LensStrip, LetterPicker, MetricChips, SurfaceError, SurfaceLayout, SurfaceLoading,
  type LensItem,
} from "@/components/surface";

type Finding = {
  id: string;
  event: { type: string; scope?: string; seizure_status?: string };
  measurement: Record<string, unknown>;
  timing?: string;
  period?: { time?: string };
  condition?: string;
  evidence: string;
};
type ComponentPair = { gold_id: string; prediction_id: string; measurement_correct: boolean; subtype_correct: boolean; event_correct: boolean };
type Letter = {
  source_row_index: number;
  note: string;
  gold_answer: string;
  predicted_answer: string | null;
  answer_correct: boolean;
  usable: boolean;
  purist_tp: number;
  purist_fp: number;
  purist_fn: number;
  pairs: [string, string][];
  reference: Finding[];
  predicted: Finding[];
  component_score?: { pairs: ComponentPair[]; unpaired_gold: string[]; unpaired_predictions: string[] };
};
type ReviewBundle = {
  scope: string;
  matcher: string;
  aggregate: { tp: number; fp: number; fn: number };
  rows: Letter[];
};
type Outcome = "all" | "answer" | "missed" | "extra" | "invalid";
type Lens = "all" | "matched" | "missed" | "extra";

const OUTCOMES: { id: Outcome; label: string }[] = [
  { id: "all", label: "All letters" },
  { id: "answer", label: "Purist answer mismatch" },
  { id: "missed", label: "Missed findings" },
  { id: "extra", label: "Extra findings" },
  { id: "invalid", label: "Invalid inventory" },
];

function quantity(value: unknown): string {
  if (typeof value === "number" || typeof value === "string") return String(value);
  if (!value || typeof value !== "object") return "?";
  const q = value as Record<string, unknown>;
  if (q.type === "bound") return `${q.relation === "at_most" ? "≤" : q.relation === "at_least" ? "≥" : q.relation === "less_than" ? "<" : ">"}${quantity(q.value)}`;
  if (q.type === "range") return `${quantity(q.lower)}–${quantity(q.upper)}`;
  if (q.type === "number") return String(q.value);
  if (q.type === "qualitative") return String(q.quantity);
  return JSON.stringify(q);
}
function durationText(value: Record<string, unknown>): string {
  if (value.type === "qualitative") return String(value.quantity ?? "unspecified period");
  const unit = String(value.unit ?? "");
  const singular = (value.type === "number" || value.type === "bound") && value.value === 1;
  const unitText = `${unit}${singular ? "" : "s"}`.trim();
  if (value.type === "range") return `${quantity(value.lower)}–${quantity(value.upper)} ${unitText}`;
  if (value.type === "bound") {
    const relation = { at_least: "at least", more_than: "more than", at_most: "at most", less_than: "less than" }[String(value.relation)] ?? "about";
    return `${relation} ${quantity(value.value)} ${unitText}`;
  }
  return `${quantity(value.value)} ${unitText}`.trim();
}
function measurement(finding: Finding): string {
  const m = finding.measurement;
  if (m.type === "seizure_free") {
    const duration = m.duration as Record<string, unknown> | undefined;
    if (duration) {
      const phrase = durationText(duration);
      return `seizure-free ${duration.type === "qualitative" && /^(this|last|in|over|since)\b/i.test(phrase) ? "" : "for "}${phrase}`;
    }
    const since = m.since as { time?: string } | undefined;
    return since?.time && since.time.toLowerCase() !== "since" ? `seizure-free since ${since.time}` : "seizure-free";
  }
  if (m.type === "rate") {
    const per = m.per as Record<string, unknown> | undefined;
    return `${quantity(m.count)} per ${per ? `${quantity(per.value)} ${per.unit}` : "?"}`;
  }
  if (m.type === "cluster") {
    const rate = m.rate as { count?: unknown; per?: Record<string, unknown> } | undefined;
    const count = m.count;
    const size = m.seizures_per_cluster;
    const cadence = rate?.count && rate.per ? `${quantity(rate.count)} clusters per ${durationText(rate.per)}` : count ? `${quantity(count)} ${quantity(count) === "1" ? "cluster" : "clusters"}` : "";
    const clusterSize = size ? `${quantity(size)} seizures per cluster` : "";
    return [cadence, clusterSize].filter(Boolean).join(" · ") || "cluster";
  }
  if (m.type === "qualitative") return String(m.frequency);
  return `${String(m.type)} · ${JSON.stringify(Object.fromEntries(Object.entries(m).filter(([key]) => key !== "type")))}`;
}
function findingFields(finding: Finding): Array<[string, string]> {
  return [
    ["event", finding.event.type],
    ["measurement", measurement(finding)],
    ["timing", finding.timing ?? "current"],
    ...(finding.period?.time ? [["period", finding.period.time] as [string,string]] : []),
    ...(finding.condition ? [["condition", finding.condition] as [string,string]] : []),
  ];
}
function FindingSummary({finding, onEvidence}: {finding: Finding; onEvidence: (quote: string) => void}) {
  return <button type="button" onClick={() => onEvidence(finding.evidence)} className="w-full px-3 py-2.5 text-left hover:bg-surface-raised/50">
    <div className="text-xs font-semibold text-foreground">{finding.event.type}</div>
    <div className="mt-1 text-[11px] leading-snug text-muted">{finding.evidence}</div>
    <div className="mt-2 flex flex-wrap gap-1">{findingFields(finding).filter(([key]) => key !== "event").map(([key,value]) => <span key={key} className="rounded border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[10px] text-muted">{key}: {value}</span>)}</div>
  </button>;
}
function MatchedCard({gold, predicted, onEvidence}: {gold: Finding; predicted: Finding; onEvidence: (quote: string) => void}) {
  const goldFields = new Map(findingFields(gold));
  const predFields = new Map(findingFields(predicted));
  const keys = [...new Set([...goldFields.keys(), ...predFields.keys()])];
  return <div className="rounded-md border border-border bg-surface p-3">
    <div className="flex items-center gap-2 border-b border-border/50 pb-2"><span className="rounded bg-success/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-success">Matched finding</span><span className="text-xs font-semibold">{gold.event.type}</span></div>
    <div className="mt-2 grid grid-cols-2 gap-2">
      <button onClick={() => onEvidence(gold.evidence)} className="rounded bg-surface-raised/50 p-2 text-left text-xs hover:bg-surface-raised"><span className="font-mono text-[10px] uppercase text-muted">Gold {gold.id}</span><p className="mt-1 font-medium">{gold.evidence}</p></button>
      <button onClick={() => onEvidence(predicted.evidence)} className="rounded bg-surface-raised/50 p-2 text-left text-xs hover:bg-surface-raised"><span className="font-mono text-[10px] uppercase text-muted">Predicted {predicted.id}</span><p className="mt-1 font-medium">{predicted.evidence}</p></button>
    </div>
    <table className="mt-2 w-full text-left text-[11px]"><thead><tr className="border-b border-border text-muted"><th className="py-1 font-medium">Field</th><th className="py-1 font-medium">Gold</th><th className="py-1 font-medium">Predicted</th></tr></thead><tbody>{keys.map(key => {const g=goldFields.get(key);const p=predFields.get(key);return <tr key={key} className={`border-b border-border/50 last:border-0 ${g===p?"":"bg-error/5"}`}><td className="py-1 pr-2 text-muted">{key}</td><td className="py-1 pr-2">{g??"—"}</td><td className="py-1">{p??"—"}{g===p&&<span className="ml-1 text-success">✓</span>}</td></tr>;})}</tbody></table>
  </div>;
}
function UnmatchedPanel({title, findings, onEvidence}: {title: string; findings: Finding[]; onEvidence: (quote: string) => void}) {
  return <section className="overflow-hidden rounded-md border border-border bg-surface"><div className="border-b border-border bg-surface-raised/50 px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-muted">{title} · {findings.length}</div>{findings.length ? findings.map(finding => <div key={finding.id} className="border-b border-border/60 last:border-0"><FindingSummary finding={finding} onEvidence={onEvidence}/></div>) : <p className="px-3 py-4 text-xs text-muted">None</p>}</section>;
}
function ComponentCard({gold, predicted, pair, onEvidence}: {gold: Finding; predicted: Finding; pair: ComponentPair; onEvidence: (quote: string) => void}) {
  return <section className="rounded-md border border-border bg-surface p-3 text-xs">
    <div className="flex flex-wrap items-center gap-2 border-b border-border/50 pb-2"><span className="font-semibold">Same source evidence</span><span className={pair.measurement_correct?"text-success":"text-error"}>Measurement {pair.measurement_correct?"✓":"✕"}</span><span className={pair.subtype_correct?"text-success":"text-error"}>Subtype {pair.subtype_correct?"✓":"✕"}</span><span className={pair.event_correct?"text-success":"text-error"}>Event label {pair.event_correct?"✓":"✕"}</span></div>
    <div className="mt-2 grid grid-cols-2 gap-2"><button onClick={()=>onEvidence(gold.evidence)} className="rounded bg-surface-raised/50 p-2 text-left hover:bg-surface-raised"><span className="font-mono text-[10px] uppercase text-muted">Gold</span><p className="mt-1 font-semibold">{gold.event.type}</p><p className="mt-1 text-muted">{measurement(gold)}</p></button><button onClick={()=>onEvidence(predicted.evidence)} className="rounded bg-surface-raised/50 p-2 text-left hover:bg-surface-raised"><span className="font-mono text-[10px] uppercase text-muted">R8</span><p className="mt-1 font-semibold">{predicted.event.type}</p><p className="mt-1 text-muted">{measurement(predicted)}</p></button></div>
  </section>;
}
function Inspector({row, lens, onEvidence, version}: {row: Letter; lens: Lens; onEvidence: (quote:string)=>void; version: "v07" | "v08" | "v081" | "v082" | "v083" | "v084" | "v085"}) {
  const gold = new Map(row.reference.map(f => [f.id, f]));
  const pred = new Map(row.predicted.map(f => [f.id, f]));
  const matchedGold = new Set(row.pairs.map(([,id])=>id));
  const matchedPred = new Set(row.pairs.map(([id])=>id));
  const missed = row.reference.filter(f => !matchedGold.has(f.id));
  const extra = row.predicted.filter(f => !matchedPred.has(f.id));
  const componentPairs = row.component_score?.pairs ?? [];
  const componentResidual = componentPairs.filter(pair => !matchedGold.has(pair.gold_id));
  const [mode, setMode] = useState<"matched"|"raw">("matched");
  return <div className="flex h-full min-h-0 flex-col">
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2"><div className="flex items-center justify-between gap-2"><Layers3 className="h-3.5 w-3.5 text-muted"/><h3 className="text-xs font-semibold">Seizure Frequency</h3><span className="hidden text-[11px] text-muted sm:inline">{version === "v085" ? "v0.8.5 unscored cluster spans versus saved R8" : version === "v084" ? "v0.8.4 cluster and seizure-link decisions versus saved R8" : version === "v083" ? "v0.8.3 owner decisions versus saved R8" : version === "v082" ? "v0.8.2 claim units versus saved R8" : version === "v081" ? "v0.8.1 one-year timing versus saved R8" : version === "v08" ? "v0.8 gold versus projected saved R8" : "Gold versus saved R8 predictions"}</span></div><div className="flex rounded-md border border-border bg-surface-raised p-0.5 text-[11px]"><button onClick={()=>setMode("matched")} className={`rounded px-2 py-0.5 ${mode==="matched"?"bg-surface font-semibold shadow-xs":"text-muted"}`}>Matched Diff</button><button onClick={()=>setMode("raw")} className={`rounded px-2 py-0.5 ${mode==="raw"?"bg-surface font-semibold shadow-xs":"text-muted"}`}>Raw Lists</button></div></div>
    <div className="flex-1 space-y-3 overflow-y-auto p-4">
      <div className="rounded-md border border-border bg-surface p-3"><div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted">Selected answer <span className={row.answer_correct?"text-success":"text-error"}>· Purist {row.answer_correct?"agrees":"differs"}</span></div><div className="grid grid-cols-2 gap-2 text-xs"><div className="rounded bg-surface-raised/50 p-2"><div className="font-mono text-[10px] uppercase text-muted">Gold label</div><p className="mt-1 font-semibold">{row.gold_answer}</p></div><div className="rounded bg-surface-raised/50 p-2"><div className="font-mono text-[10px] uppercase text-muted">R8 answer</div><p className="mt-1 font-semibold">{row.predicted_answer??"No answer"}</p></div></div></div>
      {!row.usable && <div className="rounded-md border border-error/25 bg-error/5 p-3 text-xs text-error">R8 inventory failed schema validation. The frozen scorer does not salvage partial findings.</div>}
      {version==="v081" && row.component_score && <div className="rounded-md border border-border bg-surface px-3 py-2 text-xs"><span className="font-semibold">Component score</span><span className="ml-3 text-muted">Measurement {componentPairs.filter(pair=>pair.measurement_correct).length}/{row.reference.length}</span><span className="ml-3 text-muted">Subtype {componentPairs.filter(pair=>pair.subtype_correct).length}/{row.reference.length}</span><span className="ml-3 text-muted">Event label {componentPairs.filter(pair=>pair.event_correct).length}/{row.reference.length}</span><p className="mt-1 text-[11px] text-muted">One-to-one source-aligned findings; missing gold remains in each denominator.</p></div>}
      {mode==="raw" ? <div className="grid grid-cols-2 gap-3"><UnmatchedPanel title="Gold findings" findings={row.reference} onEvidence={onEvidence}/><UnmatchedPanel title="Predicted findings" findings={row.predicted} onEvidence={onEvidence}/></div> : <>
        {(lens==="all"||lens==="matched") && row.pairs.map(([pid,gid]) => {const g=gold.get(gid);const p=pred.get(pid);return g&&p?<MatchedCard key={`${pid}:${gid}`} gold={g} predicted={p} onEvidence={onEvidence}/>:null;})}
        {lens==="all" && componentResidual.map(pair=>{const g=gold.get(pair.gold_id);const p=pred.get(pair.prediction_id);return g&&p?<ComponentCard key={`${pair.gold_id}:${pair.prediction_id}`} gold={g} predicted={p} pair={pair} onEvidence={onEvidence}/>:null;})}
        {(lens==="all"||lens==="missed") && <UnmatchedPanel title="Missed gold findings" findings={missed} onEvidence={onEvidence}/>}
        {(lens==="all"||lens==="extra") && <UnmatchedPanel title="Extra R8 findings" findings={extra} onEvidence={onEvidence}/>}
      </>}
    </div>
  </div>;
}

export default function R8WorkbenchExplorer() {
  const search = useSearchParams();
  const requestedVersion = search.get("version");
  const version = requestedVersion === "v085" ? "v085" : requestedVersion === "v084" ? "v084" : requestedVersion === "v083" ? "v083" : requestedVersion === "v082" ? "v082" : requestedVersion === "v081" ? "v081" : requestedVersion === "v08" ? "v08" : "v07";
  const query = useQuery<ReviewBundle>({queryKey:["gan-r8-review",version],queryFn:async()=>{const response=await fetch(`/workbench/r8-data?version=${version}`,{cache:"no-store"});if(!response.ok) throw new Error(await response.text());return response.json();},staleTime:5*60*1000});
  const router = useRouter();
  const pathname = usePathname();
  const [outcome,setOutcome] = useState<Outcome>("all");
  const [lens,setLens] = useState<Lens>("all");
  const [focus,setFocus] = useState<{letter:number;quote:string}|null>(null);
  const sourceRef = useRef<HTMLDivElement>(null);
  const rows = query.data?.rows;
  const visible = useMemo(()=> (rows??[]).filter(row => {
    if(outcome==="answer") return !row.answer_correct;
    if(outcome==="missed") return row.purist_fn>0;
    if(outcome==="extra") return row.purist_fp>0;
    if(outcome==="invalid") return !row.usable;
    return true;
  }),[rows,outcome]);
  const requested = Number(search.get("letter"));
  const row = visible.find(item=>item.source_row_index===requested) ?? (outcome==="all"?visible.find(item=>item.usable):undefined) ?? visible[0];
  const quote = focus && row && focus.letter===row.source_row_index ? focus.quote : "";
  const highlightStart = quote && row ? row.note.indexOf(quote) : -1;
  useEffect(()=>{if(highlightStart>=0) sourceRef.current?.querySelector(".span-highlight")?.scrollIntoView({block:"center",behavior:"smooth"});},[highlightStart,quote]);
  if(query.isLoading) return <SurfaceLoading message="Loading saved R8 comparison…"/>;
  if(query.error||!query.data) return <SurfaceError title="R8 comparison unavailable" detail={version === "v085" ? "Build the local bundle with .venv/bin/python scripts/benchmarks/revise_findings_v085.py" : version === "v084" ? "Build the local bundle with .venv/bin/python scripts/benchmarks/revise_findings_v084.py" : version === "v083" ? "Build the local bundle with .venv/bin/python scripts/benchmarks/revise_findings_v083.py" : version === "v082" ? "Build the local bundle with .venv/bin/python scripts/benchmarks/revise_findings_v082.py" : version === "v081" ? "Build the local bundle with .venv/bin/python scripts/benchmarks/retime_findings_v081.py" : version === "v08" ? "Build the local bundle with .venv/bin/python scripts/benchmarks/score_findings_v08.py" : "Build the local bundle with .venv/bin/python scripts/benchmarks/build_r8_review.py"}/>;
  const bundle=query.data;
  const letterItems=visible.map(item=>({value:String(item.source_row_index),label:`${item.source_row_index} – ${item.usable?`${item.purist_tp} matched / ${item.reference.length} gold`:"invalid inventory"}`}));
  const items:LensItem[]=[
    {id:"all",label:"All findings",count:`${row.purist_tp}/${row.reference.length}`,tone:"foreground",fixed:true},
    {id:"matched",label:"Matched",count:row.purist_tp,tone:"success"},
    {id:"missed",label:"Missed gold",count:row.purist_fn,tone:"error"},
    {id:"extra",label:"Extra R8",count:row.purist_fp,tone:"llm"},
  ];
  function setLetter(value:string){const params=new URLSearchParams(search.toString());params.set("dataset","ganR8");params.set("letter",value);router.replace(`${pathname}?${params.toString()}`,{scroll:false});setFocus(null);}
  function setVersion(value:string){const params=new URLSearchParams(search.toString());params.set("dataset","ganR8");params.set("version",value);router.replace(`${pathname}?${params.toString()}`,{scroll:false});setFocus(null);}
  return <SurfaceLayout variant="fill">
    <ControlBar left={<>
      <ControlField label="Run"><ControlFixedValue>R8 rich · dev750</ControlFixedValue></ControlField>
      <ControlField label="Labels" htmlFor="r8-version"><ControlSelect id="r8-version" value={version} onChange={event=>setVersion(event.target.value)}><option value="v07">v0.7 · Finding Purist</option><option value="v08">v0.8 · simplified</option><option value="v081">v0.8.1 · one-year timing</option><option value="v082">v0.8.2 · claim units</option><option value="v083">v0.8.3 · owner decisions</option><option value="v084">v0.8.4 · cluster units</option><option value="v085">v0.8.5 · unscored spans</option></ControlSelect></ControlField>
      <ControlField label="Show" htmlFor="r8-outcome"><ControlSelect id="r8-outcome" value={outcome} onChange={event=>{setOutcome(event.target.value as Outcome);setFocus(null);}}>{OUTCOMES.map(item=><option key={item.id} value={item.id}>{item.label}</option>)}</ControlSelect></ControlField>
      <ControlField label="Letter" htmlFor="r8-letter" icon={<FileText className="h-3 w-3 text-muted"/>}><LetterPicker id="r8-letter" items={letterItems} value={String(row.source_row_index)} onChange={setLetter} className="min-w-0 flex-1 sm:min-w-[240px] sm:flex-none"/></ControlField>
    </>} right={<MetricChips chips={[{label:"Precision",value:bundle.aggregate.tp/(bundle.aggregate.tp+bundle.aggregate.fp),format:"rate",asPercent:true},{label:"Recall",value:bundle.aggregate.tp/(bundle.aggregate.tp+bundle.aggregate.fn),format:"rate",asPercent:true}]}/>}/>
    <LensStrip items={items} activeId={lens} onSelect={id=>setLens(id as Lens)}/>
    <ExplorerBody sourceLabel="Letter" sourceMeta={<div className="flex items-center gap-2"><span className="rounded border border-border bg-surface-raised px-1 font-mono text-[11px] text-muted">{row.source_row_index}</span><span className="text-[11px] text-muted">{row.predicted.length} predicted / {row.reference.length} gold</span></div>} source={<div ref={sourceRef}><LetterRenderer text={row.note} highlights={highlightStart>=0?[{start:highlightStart,end:highlightStart+quote.length,kind:"gold",label:"Selected evidence"}]:[]}/></div>} inspector={<Inspector row={row} lens={lens} version={version} onEvidence={value=>setFocus({letter:row.source_row_index,quote:value})}/>}/>
  </SurfaceLayout>;
}
