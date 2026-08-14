"use client";

import { FormEvent, useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import SemanticSupportReviewWorkspace from "@/components/semantic-support-review/SemanticSupportReviewWorkspace";

export default function ClinicalReviewWorkspace() {
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
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-[var(--qr-mute)]">Use one reviewer identity for the semantic-support queue. Other reviewers’ decisions remain hidden.</p>
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
    <div className="h-full min-h-0">
      <SemanticSupportReviewWorkspace reviewerId={reviewerId} />
    </div>
  );
}

