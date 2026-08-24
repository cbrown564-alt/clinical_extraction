# ExECT vs Gan similar seizure-frequency letter pair

**Verdict:** IDEAL pair (near-identical phrase; multi-clause text; multi-row attributed ExECT gold vs one normalised Gan current-state label).

| | ExECT | Gan 2026 (public synthetic, train) |
|---|---|---|
| **ID** | `EA0195` | `source_row_index` **13517** |
| **Split** | Public synthetic gold 1–200 (not a sealed ExECT holdout file) | `gan2026` **train_v1** (not test450) |
| **Letter path** | `/Users/cobro/code/clinical-extraction/data/ExECTv2 (2025)/Gold1-200_corrected_spelling/EA0195.txt` | Embedded as `clinic_date` in `/Users/cobro/code/clinical-extraction/data/Gan (2026)/synthetic_data_subset_1500.json` (row with `source_row_index` 13517) |
| **Gold path** | `/Users/cobro/code/clinical-extraction/data/ExECTv2 (2025)/Gold1-200_corrected_spelling/EA0195.ann` | Same JSON, field `check__Seizure Frequency Number` |
| **Also** | `/Users/cobro/code/clinical-extraction/data/ExECTv2 (2025)/Json/EA0195.json` | Train membership: `/Users/cobro/code/clinical-extraction/data/Gan (2026)/splits/train_v1.json` → `source_row_indices` |

## Shared / similar phrase

**“seizure free for three years” / “seizure free for 3 years”**

- ExECT body: `This man has remained seizure free for three years`
- Gan body and gold quote: `she has now been seizure free for 3 years`

Both letters also carry a **second** frequency statement (ExECT: dated breakthrough seizure; Gan: historical `1 to 2 times per year`).

## Relevant SF excerpts (not full letters)

### ExECT EA0195

```
This man has remained seizure free for three years and he had return to drive.
However he had another seizure whilst he was asleep on the 2nd November.
...
He understands the DVLA driving regulations which state that he needs to be
a year free of seizures before driving again.
```

### Gan 13517

```
She has a past history of atonic seizures, drop attacks and generalised
tonic-clonic seizures 1 to 2 times per year, but seizure control has been
excellent, and she has now been seizure free for 3 years.
```

(Gan plan/DVLA lines also mention “sustained seizure freedom” / “prolonged remission”; they are not extra numeric rates.)

## ExECT gold SeizureFrequency rows (facts + attributes)

From `EA0195.ann`:

1. **T6** span `seizure-free-for-three-years`
   - `NumberOfSeizures` = **0**
   - `TimePeriod` = **Year**
   - `NumberOfTimePeriods` = **3**
   - `CUIPhrase` = seizure-freedom; `CUI` = C1299590
   - Context: “remained seizure free for three years”

2. **T9** span `seizure-`
   - `NumberOfSeizures` = **1**
   - `DayDate` = **2**, `MonthDate` = **11**
   - `TimeSince_or_TimeOfEvent` = **During**
   - `CUIPhrase` = seizure; `CUI` = C0036572
   - Context: “another seizure whilst he was asleep on the 2nd November”

Two separate event-level items, each with its own counts/dates. The DVLA “a year free of seizures” advice line is **not** a third SF entity.

## Gan gold (single normalised current state)

`check__Seizure Frequency Number.seizure_frequency_number`:

- **Label:** `seizure free for 3 year`
- **Supporting quote:** `she has now been seizure free for 3 years`

`reference`: same label + the sentence that also contains historical `1 to 2 times per year`.

`analysis` (abridged): past `1 to 2 per year` is acknowledged, but **current** status is seizure-free for 3 years; because current frequency is zero with a stated duration, label is `seizure free for 3 years`. One row only — monthly-equivalent is 0 with a 3-year duration band, not a list of historical rates.

## Why the guidelines force different labels

ExECT v2 is an **event/mention annotation** scheme: every distinct frequency statement that is clinically stated as a countable history item is its own `SeizureFrequency` markable, with attributes (`NumberOfSeizures`, `TimePeriod`, calendar dates, change). So “seizure free for three years” is a complete 0-in-3-years fact, and the November breakthrough is a second fact (1 seizure on 2 Nov). Gan 2026 gold is a **single current-state normalisation**: when several rates appear, the annotator keeps the **present** highest/current frequency (here zero with duration) and folds or drops historical/advice material. The same “seizure free for 3 years” phrase is therefore a first-class attributed row in ExECT and the **entire** label in Gan; Gan’s extra “1 to 2 times per year” clause never becomes a second gold item.

## Closest alternative (if a weekly-rate pair is preferred)

- ExECT **EA0194** (`…/EA0194.txt|.ann`): `Focal dyscognitive seizures 2-3 per week` **and** `1-2 per year` (plus “fairly frequent”); five SF gold rows with `Lower/UpperNumberOfSeizures`, `TimePeriod` Week/Year, `FrequencyChange` Frequent, last-event date.
- Gan **7194** (train): text has `2–3 times per week for the past six weeks` **and** `previously once every 2–3 weeks` **and** one longer episode three weeks ago; gold is **one** label `2 to 3 per week`.
- Shared phrase: **“2-3 per week” / “2–3 times per week”**. Slightly less verbatim than the 3-year seizure-free pair; still a strong guideline contrast (type-specific multi-row vs max-current-rate).

Search used only ExECT Gold1–200 and Gan `synthetic_data_subset_1500.json` rows whose `source_row_index` is in `train_v1.json` or `validation_v1.json`. Sealed test60 / test450 / Real(300) files were not opened.


---

## Rate pair (Gan **validation** only)

Conor asked for a rate comparison using only Gan `validation_v1` (750 public synthetics). Train row 7194 is out.

| | ExECT | Gan 2026 validation |
|---|---|---|
| **ID** | `EA0194` | `source_row_index` **15639** |
| **Split** | Public synthetic gold 1–200 | `gan2026` **validation_v1** |
| **Shared phrase** | **“2-3 per week” / “2 times per week”** |
| **Second rate in the letter** | Focal to bilateral convulsive **1-2 per year** (last 23 May 2019) | Previously **once or twice a month**; also **two GTCS over eight weeks** |

### ExECT EA0194 gold (five SF rows, attributes)

- Focal dyscognitive seizures: `Lower/UpperNumberOfSeizures` 2–3, `TimePeriod` Week
- Focal to bilateral convulsive seizures: `Lower/Upper` 1–2, `TimePeriod` Year
- Same convulsive type: `NumberOfSeizures` 0 since 23 May 2019 (`DayDate`/`MonthDate`/`YearDate`, `TimeSince` Since)
- Narrative “fairly frequent focal seizures”: `FrequencyChange` Frequent (two marks)

### Gan 15639 gold (one normalised rate)

- Label: **`2 per week`**
- Quote: “focal impaired-awareness seizures have been occurring more often, **2 times per week**, whereas previously they only happened **once or twice a month**”
- The monthly historical rate and the two recent GTCS are not extra gold items.

### Sharper select on val (same 2–3/week phrase, different winner)

Gan **12556** (also validation): text has **“2 - 3 generalised tonic-clonic seizures per week”**, **daily drop attacks**, and FIAS **every four to six weeks**. Gold is **`1 per day`** (drop attacks). The near-identical weekly phrase is present and is *not* the Gan label.

EA0008 vs Gan **218** also share “every 3 weeks”; ExECT has that rate plus `FrequencyChange` Increased (“seizures have returned”). Weaker as a *rate* pair because the second ExECT item is a change, not a second numeric rate. The earlier “daily” overlap on EA0008 was medication (“twice daily”), not seizure frequency.
