import type { EnrichedRow } from "@/lib/gallery-utils";

export const ERROR_TYPE_DESCRIPTIONS: Record<EnrichedRow["errorType"], string> = {
  correct: "Predictions that exactly match the gold standard.",
  false_negative:
    "The model predicted 'no seizure' or 'unknown' when the clinical note actually describes a seizure frequency. These are the most clinically dangerous misses.",
  false_positive:
    "The model invented a seizure frequency when the gold standard is 'no seizure' or 'unknown'. These suggest over-extraction from irrelevant text.",
  over_estimate:
    "The model predicted a higher frequency than the gold standard. For example, '1 per day' instead of '1 per week'.",
  under_estimate:
    "The model predicted a lower frequency than the gold standard. For example, '1 per year' instead of '1 per month'.",
  near_miss:
    "The model was off by exactly one category bucket – close, but not correct. These are the easiest errors to fix.",
};

export const ERROR_TYPE_ORDER: EnrichedRow["errorType"][] = [
  "false_negative",
  "false_positive",
  "over_estimate",
  "under_estimate",
  "near_miss",
  "correct",
];
