"use client";

import { FormEvent, useEffect, useState } from "react";
import { CheckCircle2, FileCheck2, ShieldCheck } from "lucide-react";
import QualifiedReviewWorkspace from "@/components/qualified-review/QualifiedReviewWorkspace";
import SemanticSupportReviewWorkspace from "@/components/semantic-support-review/SemanticSupportReviewWorkspace";

type ReviewTask = "correctness" | "semantic";

export default function ClinicalReviewWorkspace({ defaultTask = "semantic" }: { defaultTask?: ReviewTask }) {
  const [task, setTask] = useState<ReviewTask>(defaultTask);
  const [reviewerInput, setReviewerInput] = useState("");
  const [reviewerId, setReviewerId] = useState("");

  useEffect(() => {
    const stored = window.localStorage.getItem("semantic-support-reviewer-id") ?? "";
    if (stored) {
      // Restore the local reviewer identity after client hydration.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setReviewerInput(stored);
      setReviewerId(stored);
    }
  }, []);

  function startSession(event: FormEvent) {
    event.preventDefault();
    const normalized = reviewerInput.trim();
    if (!normalized) return;
    window.localStorage.setItem("semantic-support-reviewer-id", normalized);
    setReviewerId(normalized);
  }

  if (!reviewerId) {
    return (
      <div className="ssr-welcome qr-shell flex h-full items-center justify-center overflow-y-auto px-5 py-10">
        <div className="w-full max-w-4xl">
          <div className="grid gap-8 lg:grid-cols-[1.35fr_0.65fr] lg:items-center">
            <section>
              <p className="qr-kicker flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-[var(--qr-accent)]" />Independent clinical review</p>
              <h1 className="qr-display mt-5 max-w-xl text-4xl leading-tight text-[var(--qr-ink)]">Review extracted clinical findings against their source.</h1>
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-[var(--qr-mute)]">Use one reviewer identity for the correctness and semantic-support queues. Other reviewers’ decisions remain hidden.</p>
            </section>
            <form onSubmit={startSession} className="ssr-session-card">
              <p className="qr-kicker">Begin a blinded queue</p>
              <h2 className="mt-2 text-lg font-semibold">Your reviewer ID</h2>
              <label className="mt-4 block">
                <span className="sr-only">Reviewer ID</span>
                <input value={reviewerInput} onChange={(event) => setReviewerInput(event.target.value)} className="qr-input" placeholder="e.g. clinician-a" autoFocus />
              </label>
              <button type="submit" className="qr-save mt-3" disabled={!reviewerInput.trim()}>Enter clinical review</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <nav className="flex shrink-0 gap-1 border-b border-[var(--color-border)] bg-[var(--color-surface-raised)] px-3 py-2" aria-label="Clinical review task">
        <button type="button" aria-pressed={task === "correctness"} onClick={() => setTask("correctness")} className={`inline-flex items-center gap-2 rounded-md px-3 py-2 text-xs font-semibold ${task === "correctness" ? "bg-[var(--color-foreground)] text-[var(--color-background)]" : "text-[var(--color-muted)] hover:text-[var(--color-foreground)]"}`}>
          <FileCheck2 className="h-4 w-4" /> Correctness review
        </button>
        <button type="button" aria-pressed={task === "semantic"} onClick={() => setTask("semantic")} className={`inline-flex items-center gap-2 rounded-md px-3 py-2 text-xs font-semibold ${task === "semantic" ? "bg-[var(--color-foreground)] text-[var(--color-background)]" : "text-[var(--color-muted)] hover:text-[var(--color-foreground)]"}`}>
          <CheckCircle2 className="h-4 w-4" /> Semantic support
        </button>
      </nav>
      <div className="min-h-0 flex-1">
        {task === "correctness" ? <QualifiedReviewWorkspace reviewerId={reviewerId} /> : <SemanticSupportReviewWorkspace reviewerId={reviewerId} />}
      </div>
    </div>
  );
}
