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
    "CT_Performed",
    "CT_Results",
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
};

const FAMILY_PRIMARY_KEYS: Record<string, readonly string[]> = {
  Diagnosis: ["DiagCategory"],
  Prescription: ["DrugName"],
  SeizureFrequency: ["FrequencyChange", "NumberOfSeizures", "LowerNumberOfSeizures"],
  Investigations: ["CT_Results", "EEG_Results", "MRI_Results"],
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
