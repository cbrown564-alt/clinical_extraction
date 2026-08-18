"use client";

import { ASSEMBLY_BANDS } from "@/lib/assemblyLineTypes";
import {
  isEmptyPayload,
  isShapeCompareStage,
  sameOutgoing,
  stepsForBand,
} from "@/lib/assemblyLine";
import StationFactCard from "./StationFactCard";
import type {
  AssemblyBand,
  FactGoldData,
  FactTransformData,
  PredictedFactData,
} from "@/lib/assemblyLineTypes";
import AssemblyBandStrip from "./AssemblyBandStrip";

function GoldPlate({ gold }: { gold: FactGoldData }) {
  return (
    <section className="rounded-xl border border-gold/30 bg-gold/10 px-4 py-3">
      <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-gold">Gold</p>
      <p className="mt-1 font-serif text-base leading-snug text-foreground">{gold.label}</p>
      {!gold.has_counterpart && (
        <p className="mt-1 text-xs text-gold-ghost">No gold counterpart for this fact.</p>
      )}
      {gold.note ? <p className="mt-1 text-xs text-gold-ghost">{gold.note}</p> : null}
    </section>
  );
}

function StationCard({
  step,
  previousOut,
}: {
  step: FactTransformData;
  previousOut?: string;
}) {
  const emptyIn = isEmptyPayload(step.entered);
  const echo = sameOutgoing(previousOut, step.left);
  const changed = !step.idle && !echo && step.entered.trim() !== step.left.trim();
  const compare =
    isShapeCompareStage(step.stage_id) &&
    previousOut !== undefined &&
    !isEmptyPayload(previousOut);

  if ((step.idle || echo) && step.band !== "leave") {
    return (
      <div className="relative flex items-center gap-2 py-1.5 text-xs text-muted">
        <span aria-hidden className="absolute top-2.5 -left-[1.22rem] h-2 w-2 rounded-full bg-border" />
        <span className="min-w-0 flex-1 truncate">{step.stage_name}</span>
        <span className="text-[10px] font-semibold uppercase tracking-wider">
          {echo ? "Same" : "Idle"}
        </span>
      </div>
    );
  }

  return (
    <article className="relative rounded-md border border-border bg-surface px-3.5 py-3">
      <span
        aria-hidden
        className="absolute top-4 -left-[1.3rem] h-2.5 w-2.5 rounded-full bg-border"
      />
      <header className="flex items-baseline justify-between gap-3">
        <h4 className="text-sm font-semibold text-foreground">{step.stage_name}</h4>
        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
          {changed && !emptyIn ? "Changed" : "On"}
        </span>
      </header>
      <StationFactCard raw={step.left} compareRaw={compare ? previousOut : undefined} />
      {step.note ? <p className="mt-2 text-xs leading-relaxed text-muted">{step.note}</p> : null}
    </article>
  );
}

function BandBlock({
  band,
  steps,
  previousOutFor,
}: {
  band: { id: AssemblyBand; label: string };
  steps: FactTransformData[];
  previousOutFor: (step: FactTransformData) => string | undefined;
}) {
  if (steps.length === 0) return null;
  return (
    <section id={`assembly-band-${band.id}`} className="space-y-2">
      <h3 className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted">
        {band.label}
      </h3>
      <div className="space-y-2">
        {steps.map((step) => (
          <StationCard
            key={step.stage_id}
            step={step}
            previousOut={previousOutFor(step)}
          />
        ))}
      </div>
    </section>
  );
}

export default function AssemblyLineSidebar({
  fact,
  fallbackGold,
}: {
  fact: PredictedFactData | undefined;
  fallbackGold: FactGoldData | undefined;
}) {
  const gold = fact?.gold ?? fallbackGold;

  if (!fact) {
    return (
      <div className="flex h-full min-h-0 flex-1 flex-col bg-surface">
        <div className="px-5 pt-4 pb-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted">
            One fact
          </p>
          <p className="mt-1 font-serif text-xl leading-snug text-foreground">
            Pick a phrase in the letter
          </p>
          <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted">
            Highlighted spans are predicted facts. Gold waits at the end of the line.
          </p>
        </div>
        <AssemblyBandStrip fact={undefined} />
        <div className="min-h-0 flex-1 overflow-y-auto px-5 pb-6">
          {gold ? <GoldPlate gold={gold} /> : null}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col bg-surface">
      <div className="px-5 pt-4 pb-3">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-muted">
          One fact
        </p>
        <p className="mt-1 font-serif text-xl leading-snug text-foreground">{fact.label}</p>
      </div>
      <AssemblyBandStrip fact={fact} />
      <div className="min-h-0 flex-1 overflow-y-auto px-5 pb-6">
        <div className="space-y-5 border-l border-border pl-4">
          {ASSEMBLY_BANDS.map((band) => (
            <BandBlock
              key={band.id}
              band={band}
              steps={stepsForBand(fact, band.id)}
              previousOutFor={(step) => {
                const index = fact.transforms.findIndex((item) => item.stage_id === step.stage_id);
                return index > 0 ? fact.transforms[index - 1].left : undefined;
              }}
            />
          ))}
          {gold ? <GoldPlate gold={gold} /> : null}
        </div>
      </div>
    </div>
  );
}
