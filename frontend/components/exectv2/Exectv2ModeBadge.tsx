import { activeMethodLabel } from "@/lib/plainLanguageLabels";
import { exectv2RunActiveMethod } from "@/lib/exectv2RunOptions";
import type { ActiveMethod, Exectv2RunSummary } from "@/lib/types";

const METHOD_CLASSES: Record<ActiveMethod, string> = {
  llm_with_rules: "border-success/25 bg-success/10 text-success",
  llm: "border-llm/25 bg-llm/8 text-llm",
  rules: "border-deterministic/25 bg-deterministic/8 text-deterministic",
};

export function Exectv2ModeBadge({
  run,
  method,
  className = "",
}: {
  run?: Exectv2RunSummary;
  method?: ActiveMethod;
  className?: string;
}) {
  const activeMethod = method ?? (run ? exectv2RunActiveMethod(run) : "llm_with_rules");
  return (
    <span
      className={`shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${METHOD_CLASSES[activeMethod]} ${className}`}
    >
      {activeMethodLabel(activeMethod)}
    </span>
  );
}
