"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookOpen,
  Check,
  ChevronLeft,
  ChevronRight,
  Download,
  EyeOff,
  FileText,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  fetchSemanticSupportReviewDecisions,
  fetchSemanticSupportReviewExport,
  fetchSemanticSupportReviewPackets,
  postSemanticSupportReviewDecision,
} from "@/lib/api";
import type {
  CurrentFactWarrant,
  EvidenceDecisiveness,
  ReviewConfidence,
  SemanticSupportReviewDecision,
  SemanticSupportReviewPacket,
  SemanticSupportVerdict,
  UnsupportedInference,
} from "@/lib/types";
import LetterRenderer from "@/components/observatory/LetterRenderer";

const SEMANTIC_OPTIONS = [
  { value: "supported", label: "Supported", hint: "The conclusion follows from the source" },
  { value: "unsupported", label: "Unsupported", hint: "The conclusion does not follow" },
  { value: "uncertain", label: "Uncertain", hint: "More than one judgment is reasonable" },
  { value: "not_assessable", label: "Not assessable", hint: "The supplied record cannot resolve it" },
] as const;

const DECISIVE_OPTIONS = [
  { value: "decisive", label: "Decisive" },
  { value: "compatible_only", label: "Compatible only" },
  { value: "insufficient", label: "Insufficient" },
  { value: "uncertain", label: "Uncertain" },
  { value: "not_assessable", label: "Not assessable" },
] as const;

const CURRENT_FACT_OPTIONS = [
  { value: "warranted", label: "Warranted" },
  { value: "not_warranted", label: "Not warranted" },
  { value: "not_applicable", label: "Not applicable" },
  { value: "uncertain", label: "Uncertain" },
  { value: "not_assessable", label: "Not assessable" },
] as const;

const INFERENCE_OPTIONS = [
  { value: "absent", label: "No added inference" },
  { value: "present", label: "Unsupported inference" },
  { value: "uncertain", label: "Uncertain" },
  { value: "not_assessable", label: "Not assessable" },
] as const;

const CONFIDENCE_OPTIONS: ReviewConfidence[] = ["low", "medium", "high"];

interface Draft {
  semanticSupport: SemanticSupportVerdict | null;
  evidenceDecisive: EvidenceDecisiveness | null;
  currentFactWarranted: CurrentFactWarrant | null;
  unsupportedInference: UnsupportedInference | null;
  confidence: ReviewConfidence | null;
  notes: string;
}

const EMPTY_DRAFT: Draft = {
  semanticSupport: null,
  evidenceDecisive: null,
  currentFactWarranted: null,
  unsupportedInference: null,
  confidence: null,
  notes: "",
};

function decisionId(value: SemanticSupportReviewPacket | SemanticSupportReviewDecision): string {
  return value.review_item_id;
}

function decisionToDraft(decision?: SemanticSupportReviewDecision): Draft {
  if (!decision) return EMPTY_DRAFT;
  return {
    semanticSupport: decision.semantic_support,
    evidenceDecisive: decision.evidence_decisive,
    currentFactWarranted: decision.current_fact_warranted,
    unsupportedInference: decision.unsupported_inference,
    confidence: decision.reviewer_confidence,
    notes: decision.review_notes ?? "",
  };
}

function selectedTone(value: string): string {
  if (["supported", "decisive", "warranted", "not_applicable", "absent", "high"].includes(value)) {
    return "qr-tone-ok";
  }
  if (["unsupported", "insufficient", "not_warranted", "present"].includes(value)) {
    return "qr-tone-bad";
  }
  return "qr-tone-format";
}

function ChoiceGroup<T extends string>({
  label,
  prompt,
  value,
  options,
  onChange,
}: {
  label: string;
  prompt: string;
  value: T | null;
  options: ReadonlyArray<{ value: T; label: string; hint?: string }>;
  onChange: (value: T) => void;
}) {
  return (
    <fieldset className="space-y-2.5">
      <legend className="qr-kicker">{label}</legend>
      <p className="text-xs leading-relaxed text-[var(--qr-mute)]">{prompt}</p>
      <div className="grid grid-cols-2 gap-1.5">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            aria-pressed={value === option.value}
            onClick={() => onChange(option.value)}
            className={`qr-choice min-h-[48px] ${value === option.value ? selectedTone(option.value) : ""}`}
          >
            <span className="font-medium">{option.label}</span>
            {option.hint && <span className="mt-0.5 block text-[10px] leading-snug opacity-70">{option.hint}</span>}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

export default function SemanticSupportReviewWorkspace() {
  const queryClient = useQueryClient();
  const [reviewerInput, setReviewerInput] = useState("");
  const [reviewerId, setReviewerId] = useState("");
  const [mode, setMode] = useState<"queue" | "done">("queue");
  const [family, setFamily] = useState("all");
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState("");

  useEffect(() => {
    const stored = window.localStorage.getItem("semantic-support-reviewer-id") ?? "";
    if (stored) {
      // Restore only the local reviewer identity; decisions remain server-side.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setReviewerInput(stored);
      setReviewerId(stored);
    }
  }, []);

  const packetsQuery = useQuery({
    queryKey: ["semantic-support-review-packets", reviewerId],
    queryFn: () => fetchSemanticSupportReviewPackets(reviewerId),
    enabled: Boolean(reviewerId),
  });
  const decisionsQuery = useQuery({
    queryKey: ["semantic-support-review-decisions", reviewerId],
    queryFn: () => fetchSemanticSupportReviewDecisions(reviewerId),
    enabled: Boolean(reviewerId),
  });

  const packets = useMemo(() => packetsQuery.data?.packets ?? [], [packetsQuery.data?.packets]);
  const decisionsMap = useMemo(
    () => new Map((decisionsQuery.data?.decisions ?? []).map((decision) => [decisionId(decision), decision])),
    [decisionsQuery.data?.decisions]
  );
  const pending = useMemo(() => packets.filter((packet) => !decisionsMap.has(decisionId(packet))), [decisionsMap, packets]);
  const completed = useMemo(() => packets.filter((packet) => decisionsMap.has(decisionId(packet))), [decisionsMap, packets]);
  const families = useMemo(() => Array.from(new Set(packets.map((packet) => packet.family))).sort(), [packets]);
  const visible = useMemo(
    () => (mode === "queue" ? pending : completed).filter((packet) => family === "all" || packet.family === family),
    [completed, family, mode, pending]
  );
  const current = useMemo(
    () => visible.find((packet) => decisionId(packet) === currentId) ?? visible[0],
    [currentId, visible]
  );
  const existing = current ? decisionsMap.get(decisionId(current)) : undefined;

  useEffect(() => {
    if (!current) return;
    const next = drafts[decisionId(current)] ?? decisionToDraft(existing);
    // Hydrate the selected queue item from its unsaved draft or latest revision.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDraft(next);
  }, [current, drafts, existing]);

  const stashDraft = useCallback(() => {
    if (!current) return;
    setDrafts((stored) => ({ ...stored, [decisionId(current)]: draft }));
  }, [current, draft]);

  const selectPacket = useCallback(
    (packet: SemanticSupportReviewPacket | undefined) => {
      if (!packet) return;
      stashDraft();
      setCurrentId(decisionId(packet));
    },
    [stashDraft]
  );

  const currentIndex = current ? visible.findIndex((packet) => decisionId(packet) === decisionId(current)) : -1;
  const goRelative = useCallback(
    (offset: number) => selectPacket(visible[currentIndex + offset]),
    [currentIndex, selectPacket, visible]
  );

  const cleanPositive = Boolean(
    draft.semanticSupport === "supported" &&
      draft.evidenceDecisive === "decisive" &&
      ["warranted", "not_applicable"].includes(draft.currentFactWarranted ?? "") &&
      draft.unsupportedInference === "absent"
  );
  const allJudgments = Boolean(
    draft.semanticSupport &&
      draft.evidenceDecisive &&
      draft.currentFactWarranted &&
      draft.unsupportedInference &&
      draft.confidence
  );
  const requiresNote = allJudgments && !cleanPositive;
  const canSave = Boolean(current && allJudgments && (!requiresNote || draft.notes.trim()));

  const saveMutation = useMutation({
    mutationFn: postSemanticSupportReviewDecision,
    onSuccess: async (_, submitted) => {
      setDrafts((stored) => {
        const next = { ...stored };
        delete next[submitted.review_item_id];
        return next;
      });
      const next = pending.find((packet) => decisionId(packet) !== submitted.review_item_id);
      setCurrentId(next ? decisionId(next) : null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["semantic-support-review-packets", reviewerId] }),
        queryClient.invalidateQueries({ queryKey: ["semantic-support-review-decisions", reviewerId] }),
      ]);
    },
  });

  const handleSave = useCallback(() => {
    if (!current || !canSave) return;
    saveMutation.mutate({
      review_item_id: decisionId(current),
      reviewer_id: reviewerId,
      semantic_support: draft.semanticSupport!,
      evidence_decisive: draft.evidenceDecisive!,
      current_fact_warranted: draft.currentFactWarranted!,
      unsupported_inference: draft.unsupportedInference!,
      reviewer_confidence: draft.confidence!,
      review_notes: draft.notes.trim() || null,
    });
  }, [canSave, current, draft, reviewerId, saveMutation]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.tagName === "TEXTAREA" || target?.tagName === "INPUT" || target?.tagName === "SELECT") return;
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        handleSave();
      } else if (event.key.toLowerCase() === "p") {
        setDraft((value) => ({
          ...value,
          semanticSupport: "supported",
          evidenceDecisive: "decisive",
          currentFactWarranted: "warranted",
          unsupportedInference: "absent",
          confidence: "high",
        }));
      } else if (event.key === "ArrowLeft") {
        goRelative(-1);
      } else if (event.key === "ArrowRight") {
        goRelative(1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goRelative, handleSave]);

  function startSession(event: FormEvent) {
    event.preventDefault();
    const normalized = reviewerInput.trim();
    if (!normalized) return;
    window.localStorage.setItem("semantic-support-reviewer-id", normalized);
    setReviewerId(normalized);
  }

  async function downloadExport() {
    setExporting(true);
    setExportError("");
    try {
      const payload = await fetchSemanticSupportReviewExport(reviewerId);
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `exectv2-semantic-support-${reviewerId}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setExportError(String(error));
    } finally {
      setExporting(false);
    }
  }

  if (!reviewerId) {
    return (
      <div className="ssr-welcome qr-shell flex h-full items-center justify-center overflow-y-auto px-5 py-10">
        <div className="w-full max-w-4xl">
          <div className="mb-8 flex items-center gap-2 text-[var(--qr-accent)]">
            <ShieldCheck className="h-5 w-5" />
            <span className="qr-kicker text-[var(--qr-accent)]">Independent clinical review</span>
          </div>
          <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
            <section>
              <h1 className="qr-display max-w-xl text-4xl leading-[1.08] text-[var(--qr-ink)] sm:text-5xl">
                Decide whether the evidence truly supports the clinical conclusion.
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-relaxed text-[var(--qr-mute)]">
                A frozen 48-item ExECTv2 development sample. Model scores, gold correctness, and other reviewers’ decisions stay hidden.
              </p>
              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                {[
                  ["48", "review items"],
                  ["4", "clinical families"],
                  ["2", "independent reviewers"],
                ].map(([value, label]) => (
                  <div key={label} className="ssr-stat">
                    <p className="qr-display text-2xl text-[var(--qr-ink)]">{value}</p>
                    <p className="qr-kicker mt-1">{label}</p>
                  </div>
                ))}
              </div>
            </section>
            <form onSubmit={startSession} className="ssr-session-card self-end">
              <p className="qr-kicker">Begin a blinded queue</p>
              <h2 className="mt-2 text-lg font-semibold text-[var(--qr-ink)]">Your reviewer ID</h2>
              <p className="mt-2 text-xs leading-relaxed text-[var(--qr-mute)]">
                Use the ID assigned in the review protocol. It keeps your decisions separate and revisioned.
              </p>
              <input
                autoFocus
                value={reviewerInput}
                onChange={(event) => setReviewerInput(event.target.value)}
                className="qr-input mt-5"
                placeholder="e.g. clinician-a"
                aria-label="Reviewer ID"
              />
              <button type="submit" disabled={!reviewerInput.trim()} className="qr-save mt-3 justify-center">
                Enter review workspace
              </button>
              <div className="mt-5 flex items-start gap-2 border-t border-[var(--qr-line)] pt-4 text-[11px] leading-relaxed text-[var(--qr-mute)]">
                <EyeOff className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                Do not share reviewer IDs until both independent queues are complete.
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (packetsQuery.isLoading || decisionsQuery.isLoading) {
    return <div className="qr-shell flex h-full items-center justify-center"><p className="qr-kicker">Loading blinded review queue…</p></div>;
  }

  if (packetsQuery.isError || decisionsQuery.isError) {
    return (
      <div className="qr-shell flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm font-semibold text-[var(--qr-bad)]">The review queue could not be loaded</p>
        <p className="max-w-md text-sm text-[var(--qr-mute)]">No decision state was changed. Confirm that the local API is running.</p>
        <button type="button" className="qr-secondary-btn" onClick={() => void Promise.all([packetsQuery.refetch(), decisionsQuery.refetch()])}>Try again</button>
      </div>
    );
  }

  const total = packetsQuery.data?.total ?? packets.length;
  const decided = decisionsMap.size;
  const progress = total ? (decided / total) * 100 : 0;
  const evidenceStart = current?.full_letter_text.indexOf(current.evidence_text) ?? -1;
  const highlights = current && evidenceStart >= 0
    ? [{ start: evidenceStart, end: evidenceStart + current.evidence_text.length, kind: "gold", label: "Cited evidence" }]
    : [];
  const attributes = Object.entries(current?.selected_conclusion.attributes ?? {});

  return (
    <div className="qr-shell flex h-full min-h-0 flex-col">
      <header className="qr-header flex flex-wrap items-center gap-3 px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="qr-kicker">ExECTv2 · semantic support</p>
            <span className="ssr-blind-chip"><EyeOff className="h-3 w-3" /> blinded</span>
          </div>
          <div className="mt-1 flex flex-wrap items-baseline gap-3">
            <h1 className="qr-display text-lg text-[var(--qr-ink)]">Evidence Review</h1>
            <span className="qr-mono text-xs text-[var(--qr-mute)]">{decided}/{total} saved · {pending.length} remaining</span>
          </div>
        </div>
        <div className="min-w-[180px] flex-1">
          <div className="qr-progress-track" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={decided}>
            <div className="qr-progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
        <button type="button" className="qr-secondary-btn flex items-center gap-2" onClick={() => void downloadExport()} disabled={exporting}>
          <Download className="h-3.5 w-3.5" /> {exporting ? "Preparing…" : "Export mine"}
        </button>
        <button type="button" className="qr-chip" onClick={() => { stashDraft(); setReviewerId(""); }} title="Switch reviewer">
          {reviewerId}
        </button>
      </header>

      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <aside className="qr-queue flex max-h-56 w-full shrink-0 flex-col border-b border-[var(--qr-line)] lg:max-h-none lg:w-[270px] lg:border-b-0 lg:border-r">
          <div className="space-y-2 border-b border-[var(--qr-line)] p-3">
            <div className="flex rounded-md border border-[var(--qr-line)] bg-[var(--qr-surface)] p-1">
              {(["queue", "done"] as const).map((value) => (
                <button key={value} type="button" onClick={() => { stashDraft(); setMode(value); setCurrentId(null); }} className={`flex-1 rounded px-2 py-1.5 text-xs font-medium ${mode === value ? "bg-[var(--qr-ink)] text-[var(--qr-paper)]" : "text-[var(--qr-mute)]"}`}>
                  {value === "queue" ? `Queue ${pending.length}` : `Done ${completed.length}`}
                </button>
              ))}
            </div>
            <select value={family} onChange={(event) => { stashDraft(); setFamily(event.target.value); setCurrentId(null); }} className="qr-input" aria-label="Filter by clinical family">
              <option value="all">All clinical families</option>
              {families.map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {visible.map((packet) => {
              const active = current && decisionId(packet) === decisionId(current);
              const done = decisionsMap.has(decisionId(packet));
              return (
                <button key={decisionId(packet)} type="button" onClick={() => selectPacket(packet)} aria-current={active ? "true" : undefined} className={`qr-queue-item w-full px-3 py-3 text-left ${active ? "is-active" : ""}`}>
                  <div className="flex items-center gap-2">
                    {done ? <Check className="h-3.5 w-3.5 text-[var(--qr-ok)]" /> : <span className="h-2 w-2 rounded-full border border-[var(--qr-line-strong)]" />}
                    <span className="truncate text-xs font-medium text-[var(--qr-ink)]">{packet.letter_id} · {packet.family}</span>
                  </div>
                  <p className="mt-1.5 line-clamp-2 pl-5 text-[11px] leading-snug text-[var(--qr-mute)]">{packet.selected_conclusion.text || packet.selected_conclusion.normalized_concept}</p>
                </button>
              );
            })}
          </div>
        </aside>

        {!current ? (
          <section className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
            <Check className="h-8 w-8 text-[var(--qr-ok)]" />
            <p className="qr-display text-2xl">{mode === "queue" ? "Queue clear" : "No saved reviews in this view"}</p>
            <p className="max-w-sm text-sm text-[var(--qr-mute)]">Choose another family or switch queue views.</p>
          </section>
        ) : (
          <section aria-label="Evidence and full clinical letter" className="w-full min-w-0 flex-none overflow-visible lg:min-h-0 lg:flex-1 lg:overflow-y-auto">
            <div className="mx-auto max-w-4xl px-4 py-5 sm:px-7 sm:py-7">
              <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="qr-kicker">Item {current.queue_position} of {total}</p>
                  <h2 className="qr-display mt-1 text-xl text-[var(--qr-ink)]">{current.letter_id} · {current.family}</h2>
                </div>
                <div className="flex items-center gap-1">
                  <button type="button" className="qr-icon-btn" aria-label="Previous item" disabled={currentIndex <= 0} onClick={() => goRelative(-1)}><ChevronLeft className="h-4 w-4" /></button>
                  <button type="button" className="qr-icon-btn" aria-label="Next item" disabled={currentIndex >= visible.length - 1} onClick={() => goRelative(1)}><ChevronRight className="h-4 w-4" /></button>
                </div>
              </div>

              <article className="ssr-claim-card">
                <div className="flex items-center gap-2 text-[var(--qr-focus)]"><Sparkles className="h-4 w-4" /><p className="qr-kicker text-[var(--qr-focus)]">Conclusion under review</p></div>
                <p className="mt-3 text-xl font-semibold leading-snug text-[var(--qr-ink)]">{current.selected_conclusion.text || current.selected_conclusion.normalized_concept || "Unlabelled conclusion"}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {current.selected_conclusion.assertion && <span className="qr-chip is-candidate">{current.selected_conclusion.assertion}</span>}
                  {attributes.map(([key, value]) => <span key={key} className="qr-chip"><span className="qr-mono mr-1 opacity-65">{key}</span>{String(value)}</span>)}
                </div>
              </article>

              <article className="ssr-evidence-card mt-4">
                <div className="flex items-center gap-2"><FileText className="h-4 w-4 text-[var(--qr-accent)]" /><p className="qr-kicker">Cited evidence</p></div>
                <blockquote className="mt-3 font-serif text-lg leading-relaxed text-[var(--qr-ink)]">“{current.evidence_text}”</blockquote>
              </article>

              <div className="mt-7 mb-3 flex items-center justify-between gap-3">
                <p className="qr-kicker flex items-center gap-2"><BookOpen className="h-3.5 w-3.5" />Full letter context</p>
                <span className="text-[11px] text-[var(--qr-mute)]">Cited text highlighted</span>
              </div>
              <div className="qr-paper"><LetterRenderer text={current.full_letter_text} highlights={highlights} /></div>
            </div>
          </section>
        )}

        <aside className="qr-rail flex w-full shrink-0 flex-col border-t border-[var(--qr-line)] lg:w-[400px] lg:border-l lg:border-t-0">
          <div className="border-b border-[var(--qr-line)] px-4 py-3">
            <div className="flex items-start justify-between gap-3">
              <div><p className="qr-kicker">Your judgment</p><h2 className="mt-1 text-base font-semibold text-[var(--qr-ink)]">Four-part evidence check</h2></div>
              {existing && <span className="ssr-revision">revision {existing.revision ?? 1}</span>}
            </div>
            <button type="button" onClick={() => setDraft((value) => ({ ...value, semanticSupport: "supported", evidenceDecisive: "decisive", currentFactWarranted: "warranted", unsupportedInference: "absent", confidence: "high" }))} className="qr-secondary-btn mt-3 flex w-full items-center justify-center gap-2">
              <Check className="h-3.5 w-3.5" /> Mark clean support <span className="qr-mono opacity-60">P</span>
            </button>
          </div>
          <div className="min-h-0 flex-1 space-y-5 overflow-y-auto px-4 py-4">
            <ChoiceGroup label="1 · Semantic support" prompt="Does the cited text support the selected clinical conclusion?" value={draft.semanticSupport} options={SEMANTIC_OPTIONS} onChange={(value) => setDraft((currentDraft) => ({ ...currentDraft, semanticSupport: value }))} />
            <ChoiceGroup label="2 · Evidence strength" prompt="Is the evidence sufficient, rather than merely compatible?" value={draft.evidenceDecisive} options={DECISIVE_OPTIONS} onChange={(value) => setDraft((currentDraft) => ({ ...currentDraft, evidenceDecisive: value }))} />
            <ChoiceGroup label="3 · Assertion and time" prompt="Is the stored assertion and current-fact status warranted?" value={draft.currentFactWarranted} options={CURRENT_FACT_OPTIONS} onChange={(value) => setDraft((currentDraft) => ({ ...currentDraft, currentFactWarranted: value }))} />
            <ChoiceGroup label="4 · Added meaning" prompt="Does the conclusion introduce unsupported clinical meaning?" value={draft.unsupportedInference} options={INFERENCE_OPTIONS} onChange={(value) => setDraft((currentDraft) => ({ ...currentDraft, unsupportedInference: value }))} />
            <fieldset className="space-y-2"><legend className="qr-kicker">Confidence</legend><div className="flex gap-1.5">{CONFIDENCE_OPTIONS.map((value) => <button key={value} type="button" aria-pressed={draft.confidence === value} onClick={() => setDraft((currentDraft) => ({ ...currentDraft, confidence: value }))} className={`qr-pill flex-1 capitalize ${draft.confidence === value ? selectedTone(value) : ""}`}>{value}</button>)}</div></fieldset>
            <label className="block space-y-1.5">
              <span className="qr-kicker">Source-based note {requiresNote ? "· required" : "· optional"}</span>
              <textarea value={draft.notes} onChange={(event) => setDraft((currentDraft) => ({ ...currentDraft, notes: event.target.value }))} className="qr-input min-h-[96px] resize-y" placeholder={requiresNote ? "Explain the exception or uncertainty using the source…" : "Add a note if it will help adjudication…"} />
            </label>
          </div>
          <div className="border-t border-[var(--qr-line)] p-3">
            <button type="button" onClick={handleSave} disabled={!canSave || saveMutation.isPending} className="qr-save">
              {saveMutation.isPending ? "Saving revision…" : existing ? "Update and advance" : "Save and advance"}
              <span className="qr-mono text-[11px] opacity-70">⌘/Ctrl+Enter</span>
            </button>
            {saveMutation.isError && <p className="mt-2 text-center text-xs text-[var(--qr-bad)]">Could not save: {String(saveMutation.error)}</p>}
            {exportError && <p className="mt-2 text-center text-xs text-[var(--qr-bad)]">Could not export: {exportError}</p>}
            <p className="mt-2 text-center text-[10px] text-[var(--qr-mute)]"><EyeOff className="mr-1 inline h-3 w-3" />Other reviewer decisions remain hidden.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
