/** Reading order and visual rank for ExECT attribute tables. */

export type AttributeRank = "identity" | "primary" | "payload" | "qualifier";

export function compareAttributeKeys(left: string, right: string): number {
  return left.localeCompare(right, undefined, { sensitivity: "base" });
}

const IDENTITY_KEYS = ["CUI", "CUIPhrase"] as const;
const QUALIFIER_KEYS = ["Certainty", "Negation"] as const;
const IDENTITY_SET = new Set<string>(IDENTITY_KEYS);
const QUALIFIER_SET = new Set<string>(QUALIFIER_KEYS);

/** Clinical payload after CUI/CUIPhrase, before Certainty/Negation. */
const FAMILY_PAYLOAD_ORDER: Record<string, readonly string[]> = {
  Diagnosis: ["DiagCategory"],
  Prescription: ["DrugName", "DrugDose", "DoseUnit", "Frequency"],
  Investigations: [
    "CT_Results",
    "CT_Performed",
    "EEG_Performed",
    "EEG_Results",
    "EEG_Type",
    "MRI_Performed",
    "MRI_Results",
  ],
  SeizureFrequency: [
    "FrequencyChange",
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "TimePeriod",
    "TimeSince_or_TimeOfEvent",
    "PointInTime",
    "DayDate",
    "MonthDate",
    "YearDate",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
  ],
  GanEvent: [
    "event_id",
    "kind",
    "raw_value",
    "label",
    "normalized_label",
    "semantic_kind",
    "assertion_status",
    "temporality",
    "applies_to",
    "time_window",
    "notes",
    "rule_id",
    "rule_group",
    "selected_event_ids",
    "final_kind",
    "final_label",
    "model_final_label",
    "resolved_label",
    "confidence",
    "rationale",
  ],
};

const FAMILY_PRIMARY_KEYS: Record<string, readonly string[]> = {
  Diagnosis: ["DiagCategory"],
  Prescription: ["DrugName"],
  SeizureFrequency: [
    "FrequencyChange",
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
  ],
  Investigations: ["CT_Results", "EEG_Results", "MRI_Results"],
  GanEvent: ["kind", "normalized_label", "final_label", "label"],
};

export function isIdentityAttributeKey(key: string): boolean {
  return IDENTITY_SET.has(key);
}

export function isQualifierAttributeKey(key: string): boolean {
  return QUALIFIER_SET.has(key);
}

export function attributeRank(key: string, family?: string): AttributeRank {
  if (IDENTITY_SET.has(key)) return "identity";
  if (QUALIFIER_SET.has(key)) return "qualifier";
  const primary = FAMILY_PRIMARY_KEYS[family ?? ""];
  if (primary?.includes(key)) return "primary";
  return "payload";
}

export function sortedAttributeKeys(
  keys: Iterable<string>,
  family?: string
): string[] {
  const unique = Array.from(new Set(keys));
  const payloadOrder = FAMILY_PAYLOAD_ORDER[family ?? ""] ?? [];
  const payloadRank = new Map(payloadOrder.map((key, index) => [key, index]));

  const identity = IDENTITY_KEYS.filter((key) => unique.includes(key));
  const qualifiers = QUALIFIER_KEYS.filter((key) => unique.includes(key));
  const middle = unique.filter(
    (key) => !IDENTITY_SET.has(key) && !QUALIFIER_SET.has(key)
  );
  middle.sort((left, right) => {
    const leftRank = payloadRank.get(left);
    const rightRank = payloadRank.get(right);
    if (leftRank !== undefined && rightRank !== undefined) return leftRank - rightRank;
    if (leftRank !== undefined) return -1;
    if (rightRank !== undefined) return 1;
    return compareAttributeKeys(left, right);
  });
  return [...identity, ...middle, ...qualifiers];
}

/** ExECT workbench tables no longer display Certainty or Negation. */
export function workbenchAttributeKeys(
  keys: Iterable<string>,
  family?: string
): string[] {
  return sortedAttributeKeys(keys, family).filter(
    (key) => !isQualifierAttributeKey(key)
  );
}

/** Filled workbench attributes for an unscored inventory card.

  Diagnosis keeps CUI, CUIPhrase, and DiagCategory. Seizure frequency keeps
  the filled count and time fields. Prescription and Investigations keep every
  filled workbench field.
  */
export function inventoryCardAttributeKeys(
  attributes: Record<string, string>,
  family?: string
): string[] {
  const filled = Object.entries(attributes).flatMap(([key, value]) =>
    value ? [key] : []
  );
  return workbenchAttributeKeys(filled, family);
}
