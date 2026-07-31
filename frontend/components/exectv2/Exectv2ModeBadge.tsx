import { comparisonModeLabel } from "@/lib/exectv2RunOptions";
import type { Exectv2ComparisonMode } from "@/lib/types";

const MODE_CLASSES: Record<Exectv2ComparisonMode, string> = {
  llm_plus_rules: "border-success/25 bg-success/10 text-success",
  llm_only: "border-llm/25 bg-llm/8 text-llm",
  deterministic_only:
    "border-deterministic/25 bg-deterministic/8 text-deterministic",
};

export function Exectv2ModeBadge({
  mode,
  className = "",
}: {
  mode: Exectv2ComparisonMode;
  className?: string;
}) {
  return (
    <span
      className={`shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${MODE_CLASSES[mode]} ${className}`}
    >
      {comparisonModeLabel(mode)}
    </span>
  );
}
