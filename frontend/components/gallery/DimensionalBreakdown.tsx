import { ArrowRight, Activity } from "lucide-react";
import { type ConfusedPair, CATEGORY_SHORT_NAMES } from "@/lib/gallery-utils";

export function DimensionalBreakdown({
  confusedPairs,
}: {
  confusedPairs: ConfusedPair[];
}) {
  const maxPairCount = Math.max(...confusedPairs.map((p) => p.count), 1);

  return (
    <div className="grid grid-cols-1 gap-4">
      <div className="rounded-lg border border-border bg-surface p-4 space-y-3">
        <div className="flex items-center gap-2">
          <Activity className="h-3.5 w-3.5 text-muted" />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Top Category Confusions
          </span>
        </div>
        {confusedPairs.length === 0 ? (
          <p className="text-[11px] text-muted">No confusions found.</p>
        ) : (
          <div className="space-y-2">
            {confusedPairs.map((pair, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <div className="flex items-center gap-1">
                    <span className="font-medium text-foreground">
                      {CATEGORY_SHORT_NAMES[pair.gold] ?? pair.gold}
                    </span>
                    <ArrowRight className="h-2.5 w-2.5 text-muted" />
                    <span className="font-medium text-error">
                      {CATEGORY_SHORT_NAMES[pair.predicted] ?? pair.predicted}
                    </span>
                  </div>
                  <span className="text-muted tabular-nums">{pair.count}</span>
                </div>
                <div className="h-1.5 bg-surface-raised rounded-full overflow-hidden">
                  <div
                    className="h-full bg-error/60 rounded-full"
                    style={{ width: `${(pair.count / maxPairCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
