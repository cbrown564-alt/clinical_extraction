"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BookOpen,
  Check,
  ChevronLeft,
  ChevronRight,
  Keyboard,
  Scale,
  Sparkles,
} from "lucide-react";
import {
  fetchQualifiedReviewDecisions,
  fetchQualifiedReviewPackets,
  postQualifiedReviewDecision,
} from "@/lib/api";
import type {
  QualifiedEntailment,
  QualifiedReviewDecision,
  QualifiedReviewPacket,
  QualifiedValueVerdict,
} from "@/lib/types";
import LetterRenderer from "@/components/observatory/LetterRenderer";

const VERDICTS: Array<{
  value: QualifiedValueVerdict;
  label: string;
  hint: string;
  key: string;
}> = [
  { value: "correct", label: "Correct", hint: "Supported as stored", key: "1" },
  { value: "format_only_variant", label: "Format only", hint: "Same meaning", key: "2" },
  { value: "incorrect", label: "Incorrect", hint: "Wrong clinical value", key: "3" },
  { value: "ambiguous", label: "Ambiguous", hint: "Irreducible", key: "4" },
  { value: "not_assessable", label: "Not assessable", hint: "Needs more resource", key: "5" },
];

const ENTAILMENTS: Array<{ value: QualifiedEntailment; label: string; key: string }> = [
  { value: "entailed", label: "Entailed", key: "q" },
  { value: "plausible", label: "Plausible", key: "w" },
  { value: "ambiguous", label: "Ambiguous", key: "e" },
  { value: "contradicted", label: "Contradicted", key: "r" },
  { value: "absent", label: "Absent", key: "t" },
];

const CONFIDENCE = ["low", "medium", "high"] as const;

interface ReviewDraft {
  auditor: string;
  entailment: QualifiedEntailment | null;
  verdict: QualifiedValueVerdict | null;
  confidence: "low" | "medium" | "high" | null;
  interpretation: string;
  rationale: string;
}

function packetId(packet: QualifiedReviewPacket): string {
  return packet.attribute_review_id;
}

function decisionId(decision: QualifiedReviewDecision): string {
  return decision.attribute_review_id;
}

function renderedOffsets(
  absolute: number[] | undefined,
  windowOffsets: number[] | undefined,
  fullLetter: boolean,
  textLength: number
): [number, number] | null {
  if (!absolute || absolute.length < 2) return null;
  const [absStart, absEnd] = absolute;
  const winStart = fullLetter ? 0 : windowOffsets?.[0];
  if (winStart === undefined) return null;
  const start = absStart - winStart;
  const end = absEnd - winStart;
  if (start < 0 || end <= start || end > textLength) return null;
  return [start, end];
}

function verdictTone(value?: string | null): string {
  if (value === "correct") return "qr-tone-ok";
  if (value === "incorrect" || value === "contradicted") return "qr-tone-bad";
  if (value === "format_only_variant") return "qr-tone-format";
  return "qr-tone-soft";
}

export default function QualifiedReviewWorkspace() {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<"queue" | "done">("queue");
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [auditor, setAuditor] = useState("");
  const [entailment, setEntailment] = useState<QualifiedEntailment | null>(null);
  const [verdict, setVerdict] = useState<QualifiedValueVerdict | null>(null);
  const [confidence, setConfidence] = useState<"low" | "medium" | "high" | null>(null);
  const [interpretation, setInterpretation] = useState("");
  const [rationale, setRationale] = useState("");
  const [supportsOpen, setSupportsOpen] = useState(false);
  const [flash, setFlash] = useState(false);
  const [drafts, setDrafts] = useState<Record<string, ReviewDraft>>({});

  const packetsQuery = useQuery({
    queryKey: ["qualified-review-packets"],
    queryFn: fetchQualifiedReviewPackets,
  });
  const decisionsQuery = useQuery({
    queryKey: ["qualified-review-decisions"],
    queryFn: fetchQualifiedReviewDecisions,
  });

  const decisionsMap = useMemo(
    () =>
      new Map(
        (decisionsQuery.data?.decisions ?? []).map((decision) => [decisionId(decision), decision])
      ),
    [decisionsQuery.data?.decisions]
  );

  const packets = useMemo(() => packetsQuery.data?.packets ?? [], [packetsQuery.data?.packets]);
  const pending = useMemo(
    () => packets.filter((packet) => !decisionsMap.has(packetId(packet))),
    [decisionsMap, packets]
  );
  const completed = useMemo(
    () => packets.filter((packet) => decisionsMap.has(packetId(packet))),
    [decisionsMap, packets]
  );
  const visible = mode === "done" ? completed : pending;

  const current = useMemo(() => {
    if (currentId) return visible.find((packet) => packetId(packet) === currentId);
    return visible[0];
  }, [currentId, visible]);

  const existing = current ? decisionsMap.get(packetId(current)) : undefined;

  useEffect(() => {
    if (!current) return;
    const draft = drafts[packetId(current)];
    // Restore an unsaved packet draft before falling back to its durable decision.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setEntailment(draft?.entailment ?? existing?.attribute_entailment ?? null);
    setVerdict(draft?.verdict ?? existing?.value_verdict ?? null);
    setConfidence(draft?.confidence ?? existing?.reviewer_confidence ?? null);
    setInterpretation(draft?.interpretation ?? existing?.clinical_interpretation ?? "");
    setRationale(draft?.rationale ?? existing?.reviewer_rationale ?? "");
    setAuditor(draft?.auditor ?? existing?.auditor ?? "");
    setFlash(true);
    const timer = window.setTimeout(() => setFlash(false), 280);
    return () => window.clearTimeout(timer);
    // Intentionally omit auditor to avoid resetting on every keystroke.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current?.attribute_review_id, existing]);

  const preserveCurrentDraft = useCallback(() => {
    if (!current) return;
    const id = packetId(current);
    setDrafts((previous) => ({
      ...previous,
      [id]: { auditor, entailment, verdict, confidence, interpretation, rationale },
    }));
  }, [auditor, confidence, current, entailment, interpretation, rationale, verdict]);

  const saveMutation = useMutation({
    mutationFn: postQualifiedReviewDecision,
    onSuccess: async (_response, savedDecision) => {
      setDrafts((previous) => {
        const next = { ...previous };
        delete next[savedDecision.attribute_review_id];
        return next;
      });
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["qualified-review-packets"] }),
        queryClient.invalidateQueries({ queryKey: ["qualified-review-decisions"] }),
      ]);
      setCurrentId(null);
    },
  });

  const canSave = Boolean(entailment && verdict && confidence && auditor.trim());

  const handleSave = useCallback(() => {
    if (!current || !canSave || !entailment || !verdict || !confidence) return;
    saveMutation.mutate({
      attribute_review_id: current.attribute_review_id,
      fact_id: current.fact_id,
      letter_id: current.letter_id,
      attribute_name: current.attribute_name,
      attribute_value: current.attribute_value,
      attribute_entailment: entailment,
      value_verdict: verdict,
      clinical_interpretation: interpretation || null,
      reviewer_rationale: rationale || null,
      reviewer_confidence: confidence,
      auditor: auditor.trim(),
      timestamp: new Date().toISOString(),
    });
  }, [
    auditor,
    canSave,
    confidence,
    current,
    entailment,
    interpretation,
    rationale,
    saveMutation,
    verdict,
  ]);

  const goRelative = useCallback(
    (delta: number) => {
      if (!current) return;
      const index = visible.findIndex((packet) => packetId(packet) === packetId(current));
      const next = visible[index + delta];
      if (next) {
        preserveCurrentDraft();
        setCurrentId(packetId(next));
      }
    },
    [current, preserveCurrentDraft, visible]
  );

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
      const verdictMatch = VERDICTS.find((item) => item.key === event.key);
      if (verdictMatch) {
        event.preventDefault();
        setVerdict(verdictMatch.value);
        return;
      }
      const entailmentMatch = ENTAILMENTS.find((item) => item.key === event.key.toLowerCase());
      if (entailmentMatch) {
        event.preventDefault();
        setEntailment(entailmentMatch.value);
        return;
      }
      if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        handleSave();
      } else if (event.key === "j" || event.key === "ArrowRight") {
        event.preventDefault();
        goRelative(1);
      } else if (event.key === "k" || event.key === "ArrowLeft") {
        event.preventDefault();
        goRelative(-1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goRelative, handleSave]);

  const fullLetter = Boolean(current?.full_letter_text);
  const letterText =
    current?.full_letter_text ||
    current?.event_linked_context?.window_text ||
    current?.source_context ||
    "";

  const highlights = useMemo(() => {
    if (!current) return [];
    const windowOffsets = current.event_linked_context?.window_offsets;
    const focus = renderedOffsets(current.span_offsets, windowOffsets, fullLetter, letterText.length);
    const spans: Array<{ start: number; end: number; kind: string; label?: string }> = [];
    if (focus) {
      spans.push({
        start: focus[0],
        end: focus[1],
        kind: "gold",
        label: "Focus span under review",
      });
    } else if (current.source_span) {
      const start = letterText.indexOf(current.source_span);
      if (start >= 0) {
        spans.push({
          start,
          end: start + current.source_span.length,
          kind: "gold",
          label: "Focus span under review",
        });
      }
    }
    for (const event of current.event_linked_context?.linked_events ?? []) {
      const rel = renderedOffsets(event.span_offsets, windowOffsets, fullLetter, letterText.length);
      if (!rel) continue;
      spans.push({
        start: rel[0],
        end: rel[1],
        kind: "deterministic-alt",
        label: `${event.entity} · linked event`,
      });
    }
    return spans;
  }, [current, fullLetter, letterText]);

  if (packetsQuery.isLoading || decisionsQuery.isLoading) {
    return (
      <div className="qr-shell flex h-full items-center justify-center">
        <p className="qr-kicker">Loading qualified review queue…</p>
      </div>
    );
  }

  if (packetsQuery.isError || decisionsQuery.isError) {
    return (
      <div className="qr-shell flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm font-semibold text-[var(--qr-bad)]">Qualified review could not be loaded</p>
        <p className="max-w-md text-sm text-[var(--qr-mute)]">
          The queue or its saved decisions are unavailable. No review state has been changed.
        </p>
        <button
          type="button"
          className="qr-secondary-btn"
          onClick={() => void Promise.all([packetsQuery.refetch(), decisionsQuery.refetch()])}
        >
          Try again
        </button>
      </div>
    );
  }

  if (!current) {
    return (
      <div className="qr-shell flex h-full flex-col items-center justify-center gap-3">
        <Check className="h-7 w-7 text-[var(--qr-accent)]" />
        <p className="qr-display text-2xl">Queue clear</p>
        <p className="qr-kicker max-w-sm text-center">
          {mode === "done"
            ? "No completed qualified reviews are available yet."
            : "No consensus-incorrect packets remain to review."}
        </p>
      </div>
    );
  }

  const decided = decisionsMap.size;
  const total = packetsQuery.data?.total ?? packets.length;
  const progress = total ? decided / total : 0;
  const index = visible.findIndex((packet) => packetId(packet) === packetId(current)) + 1;
  const terminology = current.supports?.terminology_lookup;
  const certainty =
    current.supports?.certainty_scale || packetsQuery.data?.certainty_scale || undefined;

  return (
    <div className="qr-shell flex h-full min-h-0 flex-col">
      <header className="qr-header flex flex-wrap items-center gap-3 px-4 py-3">
        <div className="min-w-0 flex-1">
          <p className="qr-kicker">ExECTv2 · consensus-incorrect queue</p>
          <div className="mt-1 flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h1 className="qr-display text-lg leading-tight text-[var(--qr-ink)]">
              Attribute Review
            </h1>
            <span className="qr-mono text-xs text-[var(--qr-mute)]">
              {decided}/{total} saved · {pending.length} remaining
            </span>
          </div>
        </div>

        <div className="qr-progress min-w-[180px] flex-1">
          <div
            className="qr-progress-track"
            role="progressbar"
            aria-label="Qualified review progress"
            aria-valuemin={0}
            aria-valuemax={total}
            aria-valuenow={decided}
            aria-valuetext={`${decided} of ${total} reviews saved`}
          >
            <div className="qr-progress-fill" style={{ width: `${progress * 100}%` }} />
          </div>
        </div>

        <div className="flex items-center gap-1 rounded-md border border-[var(--qr-line)] bg-[var(--qr-panel)] p-1" aria-label="Review queue view">
          {(["queue", "done"] as const).map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => {
                preserveCurrentDraft();
                setMode(value);
                setCurrentId(null);
              }}
              aria-pressed={mode === value}
              className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                mode === value
                  ? "bg-[var(--qr-ink)] text-[var(--qr-paper)]"
                  : "text-[var(--qr-mute)] hover:text-[var(--qr-ink)]"
              }`}
            >
              {value}
              {value === "done" ? ` (${completed.length})` : ""}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => goRelative(-1)}
            disabled={index <= 1}
            className="qr-icon-btn"
            aria-label="Previous packet"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => goRelative(1)}
            disabled={index >= visible.length}
            className="qr-icon-btn"
            aria-label="Next packet"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto lg:flex-row lg:overflow-hidden">
        <aside className="qr-queue flex max-h-44 w-full shrink-0 flex-col border-b border-[var(--qr-line)] lg:max-h-none lg:w-[250px] lg:border-b-0 lg:border-r">
          <div className="flex items-center justify-between px-3 py-2">
            <span className="qr-kicker">Queue</span>
            <span className="qr-mono text-[11px] text-[var(--qr-mute)]">
              {index}/{visible.length}
            </span>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {visible.map((packet) => {
              const id = packetId(packet);
              const done = decisionsMap.has(id);
              const active = id === packetId(current);
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => {
                    preserveCurrentDraft();
                    setCurrentId(id);
                  }}
                  aria-current={active ? "true" : undefined}
                  className={`qr-queue-item w-full px-3 py-2.5 text-left ${active ? "is-active" : ""}`}
                >
                  <div className="flex items-center gap-2">
                    {done ? (
                      <Check className="h-3.5 w-3.5 text-[var(--qr-ok)]" />
                    ) : (
                      <span className="h-2 w-2 rounded-full border border-[var(--qr-line-strong)]" />
                    )}
                    <span className="truncate text-xs font-medium text-[var(--qr-ink)]">
                      {packet.letter_id} · {packet.attribute_name}
                    </span>
                  </div>
                  <p className="mt-1 truncate pl-5 qr-mono text-[11px] text-[var(--qr-mute)]">
                    {packet.attribute_value}
                  </p>
                </button>
              );
            })}
          </div>
        </aside>

        <section aria-label="Full clinical letter" className="relative min-h-0 w-full min-w-0 flex-none lg:flex-1 lg:overflow-y-auto">
          <div className={`qr-letter-plane mx-auto max-w-3xl px-4 py-5 sm:px-5 sm:py-6 ${flash ? "is-flash" : ""}`}>
            <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="qr-kicker mb-2 flex items-center gap-1.5">
                  <BookOpen className="h-3.5 w-3.5" />
                  Full clinical letter
                </p>
                <p className="qr-display text-lg leading-tight text-[var(--qr-ink)]">
                  {current.source_span}
                </p>
                <p className="mt-2 text-sm text-[var(--qr-mute)]">
                  {current.letter_id} · {current.entity} · focus and nearby events
                </p>
              </div>
              <div className="qr-candidate">
                <p className="qr-kicker">Candidate</p>
                <p className="mt-1 font-medium text-[var(--qr-ink)]">
                  <span className="qr-mono text-xs text-[var(--qr-mute)]">
                    {current.attribute_name}
                  </span>
                  <span className="mx-2 text-[var(--qr-line-strong)]">=</span>
                  <span className="text-base">{current.attribute_value}</span>
                </p>
              </div>
            </div>

            <div className="qr-paper">
              <LetterRenderer text={letterText} highlights={highlights} />
            </div>

            {(current.event_linked_context?.linked_events?.length ?? 0) > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {(current.event_linked_context?.linked_events ?? []).slice(0, 8).map((event) => (
                  <span key={`${event.fact_id}-${event.span_offsets.join("-")}`} className="qr-chip">
                    {event.entity}: {event.source_span}
                  </span>
                ))}
              </div>
            )}
          </div>
        </section>

        <aside className="qr-rail flex w-full shrink-0 flex-col border-t border-[var(--qr-line)] lg:w-[380px] lg:border-l lg:border-t-0">
          <div className="border-b border-[var(--qr-line)] px-4 py-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="qr-kicker">Your judgment</p>
                <h2 className="mt-1 text-base font-semibold text-[var(--qr-ink)]">
                  Decide the stored value
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setSupportsOpen((open) => !open)}
                className="qr-chip inline-flex items-center gap-1"
                aria-expanded={supportsOpen}
                aria-controls="qualified-review-supports"
              >
                <Scale className="h-3 w-3" />
                Review supports {supportsOpen ? "open" : "closed"}
              </button>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-[var(--qr-mute)]">
              Queue membership is triage only. Keyboard: 1–5 verdict · Q–T entailment · ⌘/Ctrl+Enter
              save.
            </p>
          </div>

          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-4">
            {supportsOpen && (
              <div id="qualified-review-supports" className="qr-supports space-y-3">
                {certainty && current.attribute_name === "Certainty" && (
                  <section>
                    <p className="qr-kicker mb-2 flex items-center gap-1">
                      <Sparkles className="h-3 w-3" />
                      Certainty scale
                    </p>
                    <div className="space-y-1.5">
                      {Object.entries(certainty.levels ?? {}).map(([level, meta]) => (
                        <div key={level} className="qr-support-row">
                          <span className="qr-mono w-4 shrink-0">{level}</span>
                          <div>
                            <p className="text-sm font-medium text-[var(--qr-ink)]">
                              {meta.label}
                            </p>
                            <p className="text-xs text-[var(--qr-mute)]">{meta.meaning}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                )}
                {terminology && (
                  <section>
                    <p className="qr-kicker mb-2">Terminology lookup</p>
                    <p className="mb-2 text-xs leading-relaxed text-[var(--qr-mute)]">
                      {terminology.review_rule}
                    </p>
                    {(terminology.closed_vocab?.length ?? 0) > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {terminology.closed_vocab?.map((value) => (
                          <span
                            key={value}
                            className={`qr-chip ${value === current.attribute_value ? "is-candidate" : ""}`}
                          >
                            {value}
                          </span>
                        ))}
                      </div>
                    )}
                  </section>
                )}
                <p className="flex items-start gap-1.5 text-[11px] leading-relaxed text-[var(--qr-mute)]">
                  <Keyboard className="mt-0.5 h-3 w-3 shrink-0" />
                  AI rationales, scores, and issue ledgers stay hidden by protocol.
                </p>
              </div>
            )}

            <label className="block space-y-1.5">
              <span className="qr-kicker">Named reviewer ID</span>
              <input
                value={auditor}
                onChange={(event) => setAuditor(event.target.value)}
                className="qr-input"
                placeholder="Named reviewer"
                required
              />
            </label>

            <fieldset className="space-y-2">
              <legend className="qr-kicker">Value verdict</legend>
              <p className="text-xs text-[var(--qr-mute)]">
                Is the stored attribute value clinically correct?
              </p>
              <div className="grid grid-cols-1 gap-1.5">
                {VERDICTS.map((item) => (
                  <button
                    key={item.value}
                    type="button"
                    aria-pressed={verdict === item.value}
                    onClick={() => setVerdict(item.value)}
                    className={`qr-choice ${verdict === item.value ? verdictTone(item.value) : ""}`}
                  >
                    <span className="flex items-center justify-between gap-2">
                      <span className="font-medium">{item.label}</span>
                      <span className="qr-mono text-[11px] opacity-70">{item.key}</span>
                    </span>
                    <span className="mt-0.5 block text-[11px] opacity-70">{item.hint}</span>
                  </button>
                ))}
              </div>
            </fieldset>

            <fieldset className="space-y-2">
              <legend className="qr-kicker">Attribute entailment</legend>
              <p className="text-xs text-[var(--qr-mute)]">
                How strongly does the letter support that attribute?
              </p>
              <div className="flex flex-wrap gap-1.5">
                {ENTAILMENTS.map((item) => (
                  <button
                    key={item.value}
                    type="button"
                    aria-pressed={entailment === item.value}
                    onClick={() => setEntailment(item.value)}
                    className={`qr-pill ${entailment === item.value ? verdictTone(item.value) : ""}`}
                  >
                    {item.label}
                    <span className="qr-mono ml-1 opacity-60">{item.key}</span>
                  </button>
                ))}
              </div>
            </fieldset>

            <fieldset className="space-y-2">
              <legend className="qr-kicker">Reviewer confidence</legend>
              <div className="flex gap-1.5">
                {CONFIDENCE.map((level) => (
                  <button
                    key={level}
                    type="button"
                    aria-pressed={confidence === level}
                    onClick={() => setConfidence(level)}
                    className={`qr-pill capitalize ${confidence === level ? "qr-tone-soft is-selected" : ""}`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </fieldset>

            <label className="block space-y-1.5">
              <span className="qr-kicker">Clinical interpretation</span>
              <textarea
                value={interpretation}
                onChange={(event) => setInterpretation(event.target.value)}
                className="qr-input min-h-[72px] resize-y"
                placeholder="What does the source mean for this attribute?"
              />
            </label>

            <label className="block space-y-1.5">
              <span className="qr-kicker">Rationale</span>
              <textarea
                value={rationale}
                onChange={(event) => setRationale(event.target.value)}
                className="qr-input min-h-[96px] resize-y"
                placeholder="Cite the source language that supports your verdict…"
              />
            </label>

          </div>

          <div className="border-t border-[var(--qr-line)] p-3">
            <button
              type="button"
              onClick={handleSave}
              disabled={!canSave || saveMutation.isPending}
              className="qr-save"
            >
              {saveMutation.isPending
                ? "Saving…"
                : existing
                  ? "Update review"
                  : "Save and advance"}
              <span className="qr-mono text-[11px] opacity-70">⌘/Ctrl+Enter</span>
            </button>
            {saveMutation.isError && (
              <p className="mt-2 text-center text-xs text-[var(--qr-bad)]">
                Could not save: {String(saveMutation.error)}
              </p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
