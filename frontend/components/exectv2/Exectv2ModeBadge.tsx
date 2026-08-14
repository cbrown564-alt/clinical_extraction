import { MethodBadge } from "@/components/surface/atoms";
import { exectv2RunActiveMethod } from "@/lib/exectv2RunOptions";
import type { ActiveMethod, Exectv2RunSummary } from "@/lib/types";

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
  return <MethodBadge method={activeMethod} className={className} />;
}
