import {
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Target,
  ArrowUpCircle,
  ArrowDownCircle,
  MinusCircle,
} from "lucide-react";
import type { EnrichedRow, ComparisonResult } from "@/lib/gallery-utils";

export function CorrectnessBadge({ correct, label }: { correct: boolean; label: string }) {
  return (
    <span className="flex items-center gap-1 text-[11px]">
      {correct ? (
        <CheckCircle className="h-3 w-3 text-success" />
      ) : (
        <XCircle className="h-3 w-3 text-error" />
      )}
      <span className={correct ? "text-success" : "text-error"}>{label}</span>
    </span>
  );
}

export function ErrorTypeIcon({ type }: { type: EnrichedRow["errorType"] }) {
  const className = "h-4 w-4 shrink-0";
  switch (type) {
    case "correct":
      return <CheckCircle className={`${className} text-success`} />;
    case "false_negative":
      return <AlertTriangle className={`${className} text-error`} />;
    case "false_positive":
      return <AlertCircle className={`${className} text-llm-alt`} />;
    case "over_estimate":
      return <TrendingUp className={`${className} text-error`} />;
    case "under_estimate":
      return <TrendingDown className={`${className} text-deterministic-alt`} />;
    case "near_miss":
      return <Target className={`${className} text-error/70`} />;
  }
}

export function ComparisonIcon({ status }: { status: ComparisonResult["status"] }) {
  const className = "h-3 w-3";
  switch (status) {
    case "fix":
      return <ArrowUpCircle className={`${className} text-success`} />;
    case "regression":
      return <ArrowDownCircle className={`${className} text-error`} />;
    case "both_wrong":
    case "both_right":
      return <MinusCircle className={`${className} text-muted`} />;
    case "no_compare":
      return <MinusCircle className={`${className} text-muted/50`} />;
  }
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
      <Eye className="h-8 w-8 text-muted/40 mb-3" />
      <p className="text-sm font-medium text-muted">{message}</p>
    </div>
  );
}
