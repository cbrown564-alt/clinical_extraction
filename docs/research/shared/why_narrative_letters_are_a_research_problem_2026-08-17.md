# Why narrative epilepsy letters are a research problem

Date: 2026-08-17
Status: literature-grounded paper source; motivation only

## The short answer

Clinic letters hold epilepsy facts that structured records often omit:
current seizure burden, how a diagnosis was hedged, what was prescribed
and when, and what an investigation showed. Two public programmes
already tried to unlock those letters for research, and they did it for
different downstream uses. That is the paper's clinical-research
motivation. It is not a claim that this system has been used for cohort
finding, longitudinal analysis, or modelling.

## What the letters contain that tables often do not

ExECT's opening claim is operational. Routinely collected healthcare
data are a research resource, but they lack the disease-specific detail
that lives in clinic free text (Fonferko-Shadrach et al. 2019). The
thesis states the research use: letters are where aetiology,
comorbidity, and treatment can be studied together once they are turned
into a detailed disease-specific dataset (Fonferko-Shadrach 2023,
Abstract and Ch. 1).

Gan starts from a narrower endpoint. Seizure frequency is one of the
most used indicators of disease control and treatment response, and it
is temporally more complex than discrete attributes such as a
medication list (Gan et al. 2026, 1.1 and 4.2). The same letters that
support an inventory can therefore also support an outcome.

Neither paper claims that a finished extractor is already running those
studies. They claim that the information is in the letter and is
costly to recover by hand.

## Two programmes, two research uses

ExECT treated the letter as a source of a **wide variable set**:
diagnosis, history, prescriptions, investigations, seizure frequency,
and related attributes, coded so they can be linked and validated
automatically (Fonferko-Shadrach 2023, 3.1 and 8.2; 2024 Introduction).
The 2019 system extracted nine categories from Welsh clinic letters and
compared them with clinician review. The later public corpus exists
because identifiable letters could not be shared.

Gan treated the letter as a source of **one current frequency
endpoint**, then built a shareable synthetic framework so models could
be trained without distributing patient text (Gan et al. 2026, 1.1–1.2).
Privacy and memorisation risk, not only annotation cost, are part of
the problem statement.

The 2024 ExECT paper already names the contrast Gan later designed
around: seizure frequency “relays a story,” appears in many formats,
and is a disadvantage for a rule-based inventory system compared with
classifying phrases for a machine-learning model (2024 Discussion,
citing Xie et al. 2023).

## What this permits the paper to say

| Supported interpretation | Unsupported extension |
| --- | --- |
| Narrative letters contain research-useful epilepsy facts that structured fields often omit. | This system has been used for cohort finding or longitudinal analysis. |
| Prior programmes already defined two research uses: a coded inventory and a current-frequency endpoint. | Those uses have been clinically validated here. |
| Shareable public sets exist because real letters are identifiable. | The public synthetic sets are interchangeable with real-letter gold. |

This source belongs to the literature and dataset lane. It motivates
the clinical-research problem. It does not describe this
implementation or its scores.

## Sources

- Fonferko-Shadrach B, et al. *Using natural language processing to
  extract structured epilepsy data from unstructured clinic letters:
  development and validation of the ExECT (extraction of epilepsy
  clinical text) system*. *BMJ Open*. 2019;9:e023232.
  (`literature/Epilepsy Extraction/Rules-Based/ExECT.pdf`)
- Fonferko-Shadrach B. PhD thesis, Swansea University, 2023, especially
  Abstract, Ch. 1, 3.1, and 8.2.
  (`literature/Epilepsy Extraction/Rules-Based/2023_Fonferko-Shadrach_B.final.65061.pdf`)
- Fonferko-Shadrach B, et al. *Annotation of epilepsy clinic letters for
  natural language processing*. *J Biomed Semantics*. 2024;15:17.
  (`data/ExECTv2 (2025)/Annotation of Epilepsy Clinic Letters for NLP
  (Fonferko-Shadrach 2024).pdf`)
- Gan Y, et al. *Reproducible Synthetic Clinical Letters for Seizure
  Frequency Information Extraction*. arXiv:2603.11407. 2026.
  (`data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf`)

The fuller account of how those aims became two golds is
[what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md).
The citation map is
[related-work sources](related_work_seed_2026-08-17.md).

## Writing test

**Question:** can the author write the opening problem paragraph from
the two programmes' own aims, without claiming this system is in
clinical or epidemiological use?

**Success:** the paragraph names letters as the source of missing
structured facts, names inventory versus current-frequency as two
prior research uses, and keeps deployment language out.
