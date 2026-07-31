"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Check, ChevronLeft, ChevronRight, EyeOff, FileText, Sparkles } from "lucide-react";
import {
  fetchQualifiedReviewDecisions,
  fetchQualifiedReviewPackets,
  postQualifiedReviewDecision,
} from "@/lib/api";
import type {
  CorrectnessVerdict,
  QualifiedReviewDecision,
  QualifiedReviewPacket,
} from "@/lib/types";
import LetterRenderer from "@/components/observatory/LetterRenderer";
import { shouldSaveReviewShortcut } from "@/lib/semanticSupportPresentation";

const CORRECTNESS_OPTIONS = [
  { value: "correct", label: "Correct", shortcut: "C", hint: "The complete stored value is clinically correct" },
  { value: "incorrect", label: "Incorrect", shortcut: "I", hint: "One or more parts of the stored value are clinically incorrect" },
] as const;

interface Draft {
  correctness: CorrectnessVerdict | null;
  notes: string;
}

const EMPTY_DRAFT: Draft = { correctness: null, notes: "" };

function packetId(value: QualifiedReviewPacket | QualifiedReviewDecision): string {
  return value.attribute_review_id;
}

function decisionToDraft(decision?: QualifiedReviewDecision): Draft {
  if (!decision) return EMPTY_DRAFT;
  return { correctness: decision.correctness, notes: decision.review_notes ?? "" };
}

function correctnessFromShortcut(key: string): CorrectnessVerdict | null {
  if (key.toLowerCase() === "c") return "correct";
  if (key.toLowerCase() === "i") return "incorrect";
  return null;
}

export default function QualifiedReviewWorkspace({ reviewerId }: { reviewerId: string }) {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<"queue" | "done">("queue");
  const [entity, setEntity] = useState("all");
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});

  const packetsQuery = useQuery({
    queryKey: ["qualified-review-packets", reviewerId],
    queryFn: () => fetchQualifiedReviewPackets(reviewerId),
  });
  const decisionsQuery = useQuery({
    queryKey: ["qualified-review-decisions", reviewerId],
    queryFn: () => fetchQualifiedReviewDecisions(reviewerId),
  });

  const packets = useMemo(() => packetsQuery.data?.packets ?? [], [packetsQuery.data?.packets]);
  const decisionsMap = useMemo(
    () => new Map((decisionsQuery.data?.decisions ?? []).map((decision) => [packetId(decision), decision])),
    [decisionsQuery.data?.decisions]
  );
  const pending = useMemo(() => packets.filter((packet) => !decisionsMap.has(packetId(packet))), [decisionsMap, packets]);
  const completed = useMemo(() => packets.filter((packet) => decisionsMap.has(packetId(packet))), [decisionsMap, packets]);
  const entities = useMemo(() => Array.from(new Set(packets.map((packet) => packet.entity))).sort(), [packets]);
  const visible = useMemo(
    () => (mode === "queue" ? pending : completed).filter((packet) => entity === "all" || packet.entity === entity),
    [completed, entity, mode, pending]
  );
  const current = useMemo(
    () => visible.find((packet) => packetId(packet) === currentId) ?? visible[0],
    [currentId, visible]
  );
  const existing = current ? decisionsMap.get(packetId(current)) : undefined;

  useEffect(() => {
    if (!current) return;
    // Hydrate the selected queue item from its unsaved draft or latest revision.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDraft(drafts[packetId(current)] ?? decisionToDraft(existing));
  }, [current, drafts, existing]);

  const stashDraft = useCallback(() => {
    if (!current) return;
    setDrafts((stored) => ({ ...stored, [packetId(current)]: draft }));
  }, [current, draft]);

  const selectPacket = useCallback((packet?: QualifiedReviewPacket) => {
    if (!packet) return;
    stashDraft();
    setCurrentId(packetId(packet));
  }, [stashDraft]);

  const currentIndex = current ? visible.findIndex((packet) => packetId(packet) === packetId(current)) : -1;
  const goRelative = useCallback((offset: number) => selectPacket(visible[currentIndex + offset]), [currentIndex, selectPacket, visible]);
  const canSave = Boolean(current && draft.correctness);

  const saveMutation = useMutation({
    mutationFn: postQualifiedReviewDecision,
    onSuccess: async (_, submitted) => {
      setDrafts((stored) => {
        const next = { ...stored };
        delete next[submitted.attribute_review_id];
        return next;
      });
      const next = pending.find((packet) => packetId(packet) !== submitted.attribute_review_id);
      setCurrentId(next ? packetId(next) : null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["qualified-review-packets", reviewerId] }),
        queryClient.invalidateQueries({ queryKey: ["qualified-review-decisions", reviewerId] }),
      ]);
    },
  });

  const handleSave = useCallback(() => {
    if (!current || !draft.correctness) return;
    saveMutation.mutate({
      attribute_review_id: packetId(current),
      fact_id: current.fact_id,
      letter_id: current.letter_id,
      attribute_name: current.attribute_name,
      attribute_value: current.attribute_value,
      reviewer_id: reviewerId,
      correctness: draft.correctness,
      review_notes: draft.notes.trim() || null,
    });
  }, [current, draft, reviewerId, saveMutation]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.tagName === "INPUT" || target?.tagName === "SELECT") return;
      const shortcut = correctnessFromShortcut(event.key);
      if (shouldSaveReviewShortcut(event.key, target?.tagName)) {
        event.preventDefault();
        handleSave();
      } else if (shortcut) {
        event.preventDefault();
        setDraft((value) => ({ ...value, correctness: shortcut }));
      } else if (event.key === "ArrowLeft") {
        goRelative(-1);
      } else if (event.key === "ArrowRight") {
        goRelative(1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goRelative, handleSave]);

  if (packetsQuery.isLoading || decisionsQuery.isLoading) {
    return <div className="qr-shell flex h-full items-center justify-center"><p className="qr-kicker">Loading correctness review queue…</p></div>;
  }

  if (packetsQuery.isError || decisionsQuery.isError) {
    return <div className="qr-shell flex h-full items-center justify-center"><p className="text-sm text-[var(--qr-bad)]">Correctness review could not be loaded.</p></div>;
  }

  const total = packetsQuery.data?.total ?? packets.length;
  const decided = decisionsMap.size;
  const progress = total ? (decided / total) * 100 : 0;
  const evidenceStart = current?.full_letter_text?.indexOf(current.source_span) ?? -1;
  const highlights = current && evidenceStart >= 0
    ? [{ start: evidenceStart, end: evidenceStart + current.source_span.length, kind: "gold", label: "Cited evidence" }]
    : [];

  return (
    <div className="qr-shell flex h-full min-h-0 flex-col">
      <header className="qr-header flex flex-wrap items-center gap-3 px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2"><p className="qr-kicker">ExECTv2 · correctness</p><span className="ssr-blind-chip"><EyeOff className="h-3 w-3" /> blinded</span></div>
          <div className="mt-1 flex flex-wrap items-baseline gap-3"><h1 className="qr-display text-lg">Clinical Review</h1><span className="qr-mono text-xs text-[var(--qr-mute)]">{decided}/{total} saved · {pending.length} remaining</span></div>
        </div>
        <div className="min-w-[180px] flex-1"><div className="qr-progress-track" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={decided}><div className="qr-progress-fill" style={{ width: `${progress}%` }} /></div></div>
        <span className="qr-chip">{reviewerId}</span>
      </header>

      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <aside className="qr-queue flex max-h-56 w-full shrink-0 flex-col border-b border-[var(--qr-line)] lg:max-h-none lg:w-[270px] lg:border-b-0 lg:border-r">
          <div className="space-y-2 border-b border-[var(--qr-line)] p-3">
            <div className="flex rounded-md border border-[var(--qr-line)] bg-[var(--qr-surface)] p-1">
              {(["queue", "done"] as const).map((value) => <button key={value} type="button" onClick={() => { stashDraft(); setMode(value); setCurrentId(null); }} className={`flex-1 rounded px-2 py-1.5 text-xs font-medium ${mode === value ? "bg-[var(--qr-ink)] text-[var(--qr-paper)]" : "text-[var(--qr-mute)]"}`}>{value === "queue" ? `Queue ${pending.length}` : `Done ${completed.length}`}</button>)}
            </div>
            <select value={entity} onChange={(event) => { stashDraft(); setEntity(event.target.value); setCurrentId(null); }} className="qr-input" aria-label="Filter by clinical family"><option value="all">All clinical families</option>{entities.map((value) => <option key={value} value={value}>{value}</option>)}</select>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {visible.map((packet) => {
              const active = current && packetId(packet) === packetId(current);
              const done = decisionsMap.has(packetId(packet));
              return <button key={packetId(packet)} type="button" onClick={() => selectPacket(packet)} aria-current={active ? "true" : undefined} className={`qr-queue-item w-full px-3 py-3 text-left ${active ? "is-active" : ""}`}><div className="flex items-center gap-2">{done ? <Check className="h-3.5 w-3.5 text-[var(--qr-ok)]" /> : <span className="h-2 w-2 rounded-full border border-[var(--qr-line-strong)]" />}<span className="truncate text-xs font-medium">{packet.letter_id} · {packet.entity}</span></div><p className="mt-1.5 line-clamp-2 pl-5 text-[11px] text-[var(--qr-mute)]">{packet.attribute_name}: {packet.attribute_value}</p></button>;
            })}
          </div>
        </aside>

        {!current ? (
          <section className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6 text-center"><Check className="h-8 w-8 text-[var(--qr-ok)]" /><p className="qr-display text-2xl">Queue clear</p></section>
        ) : (
          <section aria-label="Extracted value and clinical source" className="w-full min-w-0 flex-none overflow-visible lg:min-h-0 lg:flex-1 lg:overflow-y-auto">
            <div className="mx-auto max-w-4xl px-4 py-5 sm:px-7 sm:py-7">
              <div className="mb-5 flex items-center justify-between gap-3"><div><p className="qr-kicker">Item {current.queue_position ?? currentIndex + 1} of {total}</p><h2 className="qr-display mt-1 text-xl">{current.letter_id} · {current.entity}</h2></div><div className="flex gap-1"><button type="button" className="qr-icon-btn" aria-label="Previous item" disabled={currentIndex <= 0} onClick={() => goRelative(-1)}><ChevronLeft className="h-4 w-4" /></button><button type="button" className="qr-icon-btn" aria-label="Next item" disabled={currentIndex >= visible.length - 1} onClick={() => goRelative(1)}><ChevronRight className="h-4 w-4" /></button></div></div>
              <div className="ssr-comparison">
                <article className="ssr-claim-card">
                  <div className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-[var(--qr-focus)]" /><h3 className="text-sm font-semibold">System extracted</h3></div>
                  <div className="ssr-finding-headline mt-4"><p className="text-[10px] font-semibold uppercase tracking-[0.06em] text-[var(--qr-focus)]">Stored value</p><p className="mt-1 text-lg font-semibold leading-snug">{current.attribute_value}</p></div>
                  <div className="ssr-metadata-branch"><p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.06em] text-[var(--qr-mute)]">Associated metadata</p><dl className="divide-y divide-[var(--qr-line)]"><div className="grid grid-cols-[minmax(100px,0.7fr)_minmax(0,1.3fr)] gap-3 py-2"><dt className="text-xs text-[var(--qr-mute)]">Clinical family</dt><dd className="text-sm font-medium">{current.entity}</dd></div><div className="grid grid-cols-[minmax(100px,0.7fr)_minmax(0,1.3fr)] gap-3 py-2"><dt className="text-xs text-[var(--qr-mute)]">Attribute</dt><dd className="text-sm font-medium">{current.attribute_name}</dd></div></dl></div>
                </article>
                <article className="ssr-evidence-card"><div className="flex items-center gap-2"><FileText className="h-4 w-4 text-[var(--qr-accent)]" /><h3 className="text-sm font-semibold">Source says</h3></div><blockquote className="mt-4 font-serif text-lg leading-relaxed">“{current.source_span}”</blockquote><p className="mt-4 text-xs leading-relaxed text-[var(--qr-mute)]">Use the full letter below when the excerpt is not enough to judge the complete stored value.</p></article>
              </div>
              <div className="mt-7 mb-3 flex items-center justify-between"><p className="qr-kicker flex items-center gap-2"><BookOpen className="h-3.5 w-3.5" />Full letter context</p><span className="text-[11px] text-[var(--qr-mute)]">Cited text highlighted</span></div>
              <div className="qr-paper"><LetterRenderer text={current.full_letter_text || current.source_context || ""} highlights={highlights} /></div>
            </div>
          </section>
        )}

        <aside className="qr-rail flex w-full shrink-0 flex-col border-t border-[var(--qr-line)] lg:w-[400px] lg:border-l lg:border-t-0">
          <div className="border-b border-[var(--qr-line)] px-4 py-3"><div className="flex items-start justify-between"><div><p className="qr-kicker">Your judgment</p><h2 className="mt-1 text-base font-semibold">Correctness review</h2></div>{existing && <span className="ssr-revision">revision {existing.revision ?? 1}</span>}</div></div>
          <div className="min-h-0 flex-1 space-y-7 overflow-y-auto px-4 py-5">
            <fieldset className="space-y-2.5"><legend className="qr-kicker">1 · Correctness</legend><p className="text-xs leading-relaxed text-[var(--qr-mute)]">Is the complete stored value clinically correct given the cited text and full letter context?</p><div className="grid grid-cols-1 gap-2">{CORRECTNESS_OPTIONS.map((option) => <button key={option.value} type="button" aria-pressed={draft.correctness === option.value} aria-keyshortcuts={option.shortcut} onClick={() => setDraft((value) => ({ ...value, correctness: option.value }))} className={`qr-choice min-h-[48px] ${draft.correctness === option.value ? option.value === "correct" ? "qr-tone-ok" : "qr-tone-bad" : ""}`}><span className="flex items-center justify-between gap-3 font-medium">{option.label}<kbd className="qr-shortcut">{option.shortcut}</kbd></span><span className="mt-0.5 block text-[10px] leading-snug opacity-70">{option.hint}</span></button>)}</div></fieldset>
            <label className="block space-y-1.5"><span className="qr-kicker">2 · Any additional notes? · optional</span><textarea value={draft.notes} onChange={(event) => setDraft((value) => ({ ...value, notes: event.target.value }))} className="qr-input min-h-[140px] resize-y" placeholder="Add any context that may help later review…" /></label>
          </div>
          <div className="border-t border-[var(--qr-line)] p-3"><button type="button" onClick={handleSave} disabled={!canSave || saveMutation.isPending} className="qr-save">{saveMutation.isPending ? "Saving revision…" : existing ? "Update and advance" : "Save and advance"}<span className="qr-mono text-[11px] opacity-70">Enter</span></button>{saveMutation.isError && <p className="mt-2 text-center text-xs text-[var(--qr-bad)]">Could not save: {String(saveMutation.error)}</p>}<p className="mt-2 text-center text-[10px] text-[var(--qr-mute)]"><EyeOff className="mr-1 inline h-3 w-3" />Other reviewer decisions remain hidden.</p></div>
        </aside>
      </div>
    </div>
  );
}
