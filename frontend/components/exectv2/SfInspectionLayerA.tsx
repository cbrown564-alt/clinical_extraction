"use client";

import { CheckCircle2 } from "lucide-react";
import type { SfInspectionLetter, SfLayerAPair } from "@/lib/types";
import { fmtVal, phraseSurfaceKind } from "@/lib/sfPresentation";
import { AttributeSchemaCard } from "./SfAttributeSchema";
import { describePairDivergence } from "@/lib/sfSchema";

export function LayerA({
  letter,
  hideClean = false,
}: {
  letter: SfInspectionLetter;
  hideClean?: boolean;
}) {
  const isDirty = (p: SfLayerAPair) => {
    if (p.side !== "pair") return true;
    const attrsDirty = p.attributes.some(
      (a) => a.key !== "CUIPhrase" && a.match !== "ok" && a.match !== "absent"
    );
    if (attrsDirty) return true;
    return phraseSurfaceKind(p.gold_phrase, p.pred_phrase) === "substantive";
  };

  const pairs = hideClean ? letter.layer_a.pairs.filter(isDirty) : letter.layer_a.pairs;
  const hiddenClean = letter.layer_a.pairs.length - pairs.length;

  if (!letter.layer_a.pairs.length) {
    return <p className="py-2 text-[11px] text-muted">No SF mentions</p>;
  }
  if (!pairs.length) {
    return <p className="py-2 text-[11px] text-muted">All pairs match</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      {pairs.map((pair, i) => (
        <AttrPair key={i} pair={pair} />
      ))}
      {hiddenClean > 0 && (
        <p className="text-[11px] text-muted">+{hiddenClean} full match</p>
      )}
    </div>
  );
}

function AttrPair({ pair }: { pair: SfLayerAPair }) {
  const phraseOk = pair.phrase_match === "ok";
  const nonCui = pair.attributes.filter((a) => a.key !== "CUIPhrase");
  const attrsClean = nonCui.every((a) => a.match === "ok" || a.match === "absent");
  const surface =
    pair.side === "pair" ? phraseSurfaceKind(pair.gold_phrase, pair.pred_phrase) : "identical";
  const isFullyClean =
    pair.side === "pair" && attrsClean && (phraseOk || surface !== "substantive");

  if (isFullyClean) {
    const phrase =
      surface === "identical" || surface === "surface"
        ? fmtVal(pair.pred_phrase || pair.gold_phrase)
        : fmtVal(pair.gold_phrase);
    return (
      <div className="flex items-center gap-2.5 border-l-[3px] border-l-success/60 px-3 py-2 text-[12px]">
        <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-success" />
        <span className="min-w-0 flex-1 font-semibold text-foreground">{phrase}</span>
        <span className="ml-auto shrink-0 text-[10px] font-semibold text-success">
          {surface === "surface" ? "attrs match · spelling differs" : "match"}
        </span>
      </div>
    );
  }

  const accent =
    pair.side === "fp" || pair.side === "fn" || surface === "substantive" || !attrsClean
      ? "border-l-error"
      : "border-l-border";

  const divergence = pair.side === "pair" ? describePairDivergence(pair) : null;
  const showAttrs = pair.side === "pair" && (!attrsClean || divergence !== null);

  return (
    <div className={`border-l-[3px] ${accent} bg-surface px-3 py-3`}>
      <PhraseCompare pair={pair} surface={surface} phraseOk={phraseOk} attrsClean={attrsClean} />
      {showAttrs && (
        <div className="mt-3">
          <AttributeSchemaCard pair={pair} />
        </div>
      )}
      {pair.side === "pair" && attrsClean && surface === "substantive" && (
        <p className="mt-2.5 text-[11px] text-muted">Attributes match — only the phrase text differs.</p>
      )}
    </div>
  );
}

function PhraseCompare({
  pair,
  surface,
  phraseOk,
  attrsClean,
}: {
  pair: SfLayerAPair;
  surface: ReturnType<typeof phraseSurfaceKind>;
  phraseOk: boolean;
  attrsClean: boolean;
}) {
  if (pair.side === "fp") {
    return (
      <div className="overflow-hidden rounded-md border border-error/25 bg-error/5">
        <PhraseLane side="pred" phrase={fmtVal(pair.pred_phrase)} status="FP · no gold" />
      </div>
    );
  }
  if (pair.side === "fn") {
    return (
      <div className="overflow-hidden rounded-md border border-error/25 bg-error/5">
        <PhraseLane side="gold" phrase={fmtVal(pair.gold_phrase)} status="FN · no pred" />
      </div>
    );
  }

  if (surface === "identical" || (phraseOk && surface !== "substantive")) {
    return (
      <div className="overflow-hidden rounded-md border border-border bg-surface-raised">
        <PhraseLane side="both" phrase={fmtVal(pair.gold_phrase)} />
      </div>
    );
  }

  const banner =
    surface === "surface"
      ? {
          cls: "border-t border-border bg-surface-raised text-muted",
          text: "Spelling / hyphenation only",
        }
      : {
          cls: "border-t border-error/20 bg-error/10 text-error",
          text: attrsClean ? "Different phrase text" : "Phrase mismatch",
        };

  return (
    <div className="overflow-hidden rounded-md border border-border">
      <PhraseLane side="gold" phrase={fmtVal(pair.gold_phrase)} />
      <div className="border-t border-border" />
      <PhraseLane side="pred" phrase={fmtVal(pair.pred_phrase)} />
      <div className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-wide ${banner.cls}`}>
        {banner.text}
      </div>
    </div>
  );
}

function PhraseLane({
  side,
  phrase,
  status,
}: {
  side: "gold" | "pred" | "both";
  phrase: string;
  status?: string;
}) {
  const badge =
    side === "gold"
      ? "border-gold/60 bg-gold text-foreground"
      : side === "pred"
        ? "border-llm/60 bg-llm text-white"
        : "border-border bg-foreground text-background";
  const label = side === "gold" ? "Gold" : side === "pred" ? "Pred" : "Match";
  const rowBg =
    side === "gold" ? "bg-gold/12" : side === "pred" ? "bg-llm/12" : "bg-surface-raised";
  const rail = side === "gold" ? "bg-gold" : side === "pred" ? "bg-llm" : "bg-success";

  return (
    <div className={`flex items-stretch ${rowBg}`}>
      <span className={`w-1 shrink-0 ${rail}`} aria-hidden />
      <div className="flex min-w-0 flex-1 items-start gap-3 px-3 py-3">
        <span
          className={`shrink-0 rounded border px-2 py-1 text-[10px] font-extrabold uppercase tracking-wider ${badge}`}
        >
          {label}
        </span>
        <span className="min-w-0 flex-1 text-[15px] font-semibold leading-snug text-foreground">
          {phrase}
        </span>
        {status && (
          <span className="shrink-0 pt-1 text-[10px] font-bold uppercase tracking-wide text-error">
            {status}
          </span>
        )}
      </div>
    </div>
  );
}
