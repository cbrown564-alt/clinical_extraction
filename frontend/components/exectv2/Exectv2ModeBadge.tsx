import { exectActiveMethodLabel } from "@/lib/plainLanguageLabels";
import { exectv2RunActiveMethod } from "@/lib/exectv2RunOptions";
import type { ActiveMethod, Exectv2RunSummary } from "@/lib/types";
import { Blend, Bot, Braces } from "lucide-react";

const METHOD_CLASSES: Record<ActiveMethod, string> = {
  llm_with_rules: "border-hybrid/25 bg-hybrid/8 text-hybrid",
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
      className={`inline-flex items-center gap-1 shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${METHOD_CLASSES[activeMethod]} ${className}`}
    >
      {activeMethod === "llm_with_rules" ? (
        <Blend className="h-3 w-3" aria-hidden="true" />
      ) : activeMethod === "llm" ? (
        <Bot className="h-3 w-3" aria-hidden="true" />
      ) : (
        <Braces className="h-3 w-3" aria-hidden="true" />
      )}
      {exectActiveMethodLabel(activeMethod)}
    </span>
  );
}
