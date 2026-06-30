"""Canonical per-concept clinical adjudication of the 209 Diagnosis disagreements
(92 missed + 117 spurious concept keys, 88 letters) on the OFFICIAL clinical_headline
Diagnosis scorer (``score_concept_identity(..., "Diagnosis").concept_only``).

Each verdict is a clinical judgment over a single (letter, direction, concept) triple,
made by five parallel reviewers each reading the full letter text, the gold Diagnosis
mentions, the model's predicted Diagnosis mentions, and the located context snippet —
written by ``experiments/exectv2_dx_canonical_row_analysis.py`` to ``_dx_canonical/``.
Mirrors ``experiments/exectv2_sf_canonical_adjudication.py``'s verdict taxonomy and
self-validation discipline, extended to per-concept (not per-letter) granularity because
a single letter routinely carries both a genuine miss and a defensible spurious call.

verdict in {GOLD_RIGHT, MODEL_DEFENSIBLE, BOTH_DEFENSIBLE}
  GOLD_RIGHT       - genuine model error (gold is clinically correct; the model truly
                      missed a stated diagnosis, or fabricated/over-read one the letter
                      does not support -- frequently a NEGATION-as-diagnosis error, or an
                      EEG/Investigations finding mis-tagged as Diagnosis).
  MODEL_DEFENSIBLE - model is clinically correct; the score is wrong because gold
                      double/over-tagged co-present concepts from one diagnostic
                      statement (consolidation), under-annotated a stated diagnosis the
                      model correctly emitted, or the mismatch is pure canonicalization
                      (singular/plural, synonym, wording-variant) of the identical text.
  BOTH_DEFENSIBLE  - genuine ambiguity: hedged/queried diagnoses ("?"), differential vs
                      confirmed, or a real granularity coin-flip.

See docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md
for the prose. Five parallel clinical reviews, one per ~18-letter slice of the 88
disagreement letters; raw verdicts embedded below verbatim for auditability.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Pipe-delimited LETTER|DIRECTION|CONCEPT|VERDICT|REASON, one row per adjudicated
# (letter, direction, concept) triple. Embedded verbatim from five parallel review
# passes over experiments/exectv2_dx_canonical_row_analysis.py's _dx_canonical/ output.
RAW_VERDICTS = r"""
EA0002|MISSED|temporal lobe epilepsy|MODEL_DEFENSIBLE|"Diagnosis: focal epilepsy-Probable temporal" - model tagged generic "focal epilepsy" covering same single statement gold split into the specific "temporal lobe epilepsy".
EA0002|SPURIOUS|focal epilepsy|MODEL_DEFENSIBLE|Same "focal epilepsy-Probable temporal" diagnosis line; model's generic tag is the parent of gold's consolidated specific concept, not a fabrication.
EA0002|SPURIOUS|focal seizures with altered awareness|BOTH_DEFENSIBLE|"She will have a change in awareness" textually grounds a distinct awareness-status variant, but it may just restate the already-credited "focal seizures without change in awareness" episode - genuine granularity coin-flip.
EA0002|SPURIOUS|focal to bilateral convulsive seizures|MODEL_DEFENSIBLE|"before one of her have bigger convulsive seizures" describes the same event already matched as "secondary generalised seizures" - old vs new ILAE terminology synonym.
EA0006|MISSED|generalised epilepsy|MODEL_DEFENSIBLE|Predicted text "Epilepsy - unclassified, possibly generalised" canonicalizes to the identical display concept as gold; mismatch is a concept-ID/representation artifact, not omission.
EA0006|SPURIOUS|absence like seizures|MODEL_DEFENSIBLE|"absence like seizures 2014" is explicitly listed in the structured "Seizure type and frequency" line and narrated - textually supported, gold simply didn't tag it.
EA0006|SPURIOUS|epilepsy|MODEL_DEFENSIBLE|Decomposition fragment of the single matched-but-mismatched "generalised epilepsy" mention (no separate context span); not an independent claim.
EA0006|SPURIOUS|generalised|MODEL_DEFENSIBLE|Same decomposition fragment of the single "Epilepsy - unclassified, possibly generalised" mention as above.
EA0007|MISSED|focal epilepsy|MODEL_DEFENSIBLE|"epilepsy - unclassified ... possibly focal onset" - model's two separate tags (epilepsy + focal seizures) together capture the info gold consolidated into "focal epilepsy".
EA0007|SPURIOUS|epilepsy|MODEL_DEFENSIBLE|"Diagnosis: epilepsy - unclassified" header text; same single statement gold folded into consolidated "focal epilepsy".
EA0007|SPURIOUS|focal seizures|MODEL_DEFENSIBLE|"seizures every 3 to 4 weeks, possibly focal onset" - same consolidation, gold merged this hedge into "focal epilepsy" rather than crediting separately.
EA0009|MISSED|focal to bilateral convulsive seizures|MODEL_DEFENSIBLE|Model's own phrase "focal seizures with impaired awareness progressing to bilateral convulsive seizures" describes the identical event in verbose wording vs gold's terse label.
EA0009|SPURIOUS|focal seizures|MODEL_DEFENSIBLE|Decomposition fragment of the same single compound prediction already covering the matched event, not a separate fabricated diagnosis.
EA0009|SPURIOUS|impaired awareness progressing to bilateral convulsive seizures|MODEL_DEFENSIBLE|Same single compound mention fragment describing the identical "bilateral convulsive seizure" event, not a new fabricated fact.
EA0018|MISSED|epilepsy|MODEL_DEFENSIBLE|"this 42 year old lady with epilepsy" - model gave two specific seizure-type diagnoses that subsume the generic background "epilepsy" mention; reasonable consolidation.
EA0018|MISSED|focal seizures|MODEL_DEFENSIBLE|"temporal lobe onset focal seizures" - one phrase; gold tags both generic and specific parent+child, model consolidated to the specific term only.
EA0020|SPURIOUS|tonic clonic seizures|MODEL_DEFENSIBLE|"has not had any further generalised tonic clonic seizures since August 2016" documents her established seizure type even though currently controlled; gold under-annotation.
EA0025|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|"generalised tonic clonic seizures with myoclonic jerks, possible JME" - myoclonic jerks is the eponymous defining seizure type of JME, already captured by the JME tag.
EA0026|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|Same "...with myoclonic jerks, possible JME" pattern as EA0025; defining feature of JME subsumed into the syndrome tag.
EA0033|SPURIOUS|absences|MODEL_DEFENSIBLE|"presenting with generalised tonic clonic seizures, absences and myoclonic jerks" - absences is one of the classic JME triad seizure types, subsumed by the already-tagged JME diagnosis.
EA0033|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|Same JME-triad sentence; myoclonic jerks is the defining seizure type of juvenile myoclonic epilepsy, gold consolidated into the syndrome tag.
EA0034|MISSED|focal to bilateral convulsive seizures|MODEL_DEFENSIBLE|Model predicted singular form - pure singular/plural canonicalization mismatch with gold's plural form.
EA0034|MISSED|occipital lobe epilepsy|MODEL_DEFENSIBLE|"Diagnosis: focal onset epilepsy (occipital)" - one diagnosis line; model consolidated to generic "focal epilepsy", gold additionally split out the specific "occipital lobe epilepsy".
EA0034|SPURIOUS|focal to bilateral convulsive seizure|MODEL_DEFENSIBLE|Same singular/plural mismatch paired with the MISSED entry above - one underlying fact, not two.
EA0035|MISSED|epilepsy with generalised tonic clonic seizures alone|MODEL_DEFENSIBLE|syndrome name; model already separately captured "epilepsy" + "tonic clonic seizures" conveying the same info - reasonable consolidation vs a third composite tag.
EA0035|MISSED|generalised epilepsy|MODEL_DEFENSIBLE|"Diagnosis: epilepsy, probably generalised" - model tagged generic "epilepsy"; gold additionally split "generalised epilepsy" from the same hedged qualifier, nested over-tagging.
EA0035|SPURIOUS|epilepsy|MODEL_DEFENSIBLE|Same "epilepsy, probably generalised" statement underlies the nested generalised-epilepsy/GTCS-alone consolidation issue above, not a separate fabrication.
EA0038|MISSED|tonic clonic seizures|MODEL_DEFENSIBLE|Letter has its own typo "tonic chronic seizure" (for "tonic clonic"); model faithfully transcribed the letter's typo, canonicalizer didn't map it to gold's form.
EA0038|SPURIOUS|generalised tonic chronic seizure|MODEL_DEFENSIBLE|Same typo-laden mention as the MISSED entry above - one fact, not an independent second seizure type.
EA0039|SPURIOUS|convulsive seizure|BOTH_DEFENSIBLE|"He has had a convulsive seizure approximately every five years" documents his established epilepsy's seizure type, but the letter's focus is differentiating new syncope-like events from old epilepsy - genuine scope/granularity judgment call.
EA0040|MISSED|secondary generalised seizures|MODEL_DEFENSIBLE|model transcribed "secondarily generalised" verbatim, a wording-variant of gold's canonical "secondary generalised seizures".
EA0040|SPURIOUS|secondarily generalised seizures|MODEL_DEFENSIBLE|Same adverb/adjective wording-variant mismatch as the MISSED entry above, not a separate fact.
EA0043|MISSED|epilepsy with generalised tonic clonic seizures alone|GOLD_RIGHT|"I think that Miss Clark has the syndrome of epilepsy with tonic clonic seizures alone" is the clinician's definitive closing diagnostic conclusion, entirely absent from the model's output - genuine recall failure.
EA0043|MISSED|epileptic seizures|MODEL_DEFENSIBLE|"these episodes are probably epileptic seizures" is near-duplicative confirmation of the already-tagged generic "epilepsy" diagnosis, reasonable consolidation.
EA0043|SPURIOUS|absence seizures|GOLD_RIGHT|"There is no obvious history of absence or myoclonic seizures" explicitly negates this; model incorrectly extracted a ruled-out finding as a positive diagnosis.
EA0043|SPURIOUS|myoclonic seizures|GOLD_RIGHT|Same negated sentence - model fabricated a positive diagnosis from an explicit denial.
EA0044|MISSED|epilepsy with generalised tonic clonic seizures alone|MODEL_DEFENSIBLE|Model extracted the full diagnosis-header text verbatim, but its canonicalizer truncated this to just "generalised epilepsy" - a normalization artifact, not an extraction omission.
EA0044|SPURIOUS|generalised epilepsy|MODEL_DEFENSIBLE|Truncated-canonicalization fragment of the same correctly-extracted full diagnosis text above, not an independent fabrication.
EA0044|SPURIOUS|tonic clonic seizures alone|MODEL_DEFENSIBLE|Second fragment of the same single correctly-extracted mention, decomposed by the scorer.
EA0044|SPURIOUS|generalised spike|GOLD_RIGHT|"EEG 2019: generalised spike and wave with photosensitivity" is an EEG investigation finding, not a diagnosis; model mis-tagged it under the Diagnosis entity.
EA0044|SPURIOUS|photosensitivity|GOLD_RIGHT|Same EEG investigation finding mis-classified as a Diagnosis fact rather than an Investigations result.
EA0044|SPURIOUS|wave|GOLD_RIGHT|Third fragment of the same mis-classified EEG investigation finding tagged under Diagnosis.
EA0046|SPURIOUS|symptomatic structural epilepsy|BOTH_DEFENSIBLE|etiology vs onset-type are arguably two legitimate classification axes from one narrative - genuine consolidation-vs-distinct-concept ambiguity.
EA0047|SPURIOUS|absences|MODEL_DEFENSIBLE|"The absences and jerks happen more frequently" - absences are a classic defining seizure type of JME, already captured by the JME tag.
EA0047|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|Same sentence; "jerks" is the eponymous seizure type of JME, subsumed by the already-tagged syndrome diagnosis.
EA0049|SPURIOUS|absences|MODEL_DEFENSIBLE|"Occasional absences" explicitly listed as the patient's own seizure type; gold never tagged it.
EA0049|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|"Myoclonic jerks daily" restates the same fact gold tagged once as 'myoclonic seizures'; model tagged both surface mentions, gold consolidated to one.
EA0050|SPURIOUS|absences|MODEL_DEFENSIBLE|"Occasional absences" stated as patient's own seizure type; gold simply never tagged it.
EA0050|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|"Myoclonic jerks weekly" is the specific seizure type subsumed by the already-tagged "juvenile myoclonic epilepsy"; gold consolidated to the syndrome name only.
EA0054|MISSED|focal epilepsy|MODEL_DEFENSIBLE|"symptomatic structural frontal lobe epilepsy" - gold split this one diagnosis line into generic+specific concepts; model's single consolidated tag already covers both.
EA0054|MISSED|frontal lobe epilepsy|MODEL_DEFENSIBLE|same phrase as above; gold's specific half of its own split, already covered by model's one consolidated tag.
EA0054|MISSED|focal to bilateral convulsive seizure|MODEL_DEFENSIBLE|narrative restates the same seizure type already matched from the diagnosis-line plural mention; gold double-tagged singular+plural mentions of one fact.
EA0054|SPURIOUS|symptomatic structural frontal lobe epilepsy|MODEL_DEFENSIBLE|model's single consolidated tag accurately captures the diagnosis line; gold split it into two narrower concepts instead.
EA0056|MISSED|focal epilepsy|MODEL_DEFENSIBLE|"Localisation related epilepsy secondary to previous cerebral abcess" - model tagged the full literal phrase rather than gold's normalized "focal epilepsy"; same statement, canonicalization mismatch.
EA0056|SPURIOUS|localisation related epilepsy secondary to previous cerebral abcess|MODEL_DEFENSIBLE|same diagnosis-line phrase, literally quoted from the letter; gold just normalized it to a shorter canonical form.
EA0056|SPURIOUS|non epileptic psychogenic seizures|MODEL_DEFENSIBLE|"1. Non-epileptic psychogenic seizures" is explicit Diagnosis-line item #1; gold never tagged it.
EA0056|SPURIOUS|retained awareness|GOLD_RIGHT|"left arm twitching with retained awareness" is a seizure-awareness descriptor, not a distinct diagnosis; over-fragmented into a spurious pseudo-concept.
EA0057|MISSED|epileptic seizures|MODEL_DEFENSIBLE|generic Comments-section restatement of the already-tagged specific seizure types; model consolidated rather than re-tagging the redundant generic.
EA0057|MISSED|focal epilepsy|MODEL_DEFENSIBLE|same canonicalization mismatch as EA0056 (same patient); model's longer literal phrase vs gold's normalized "focal epilepsy".
EA0057|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|literal Diagnosis-line text; gold normalized to "focal epilepsy" instead of tagging the literal phrase.
EA0059|MISSED|focal epilepsy|MODEL_DEFENSIBLE|model tagged the literal diagnosis-line phrase, gold normalized to "focal epilepsy"; same statement.
EA0059|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|same phrase as above, literally quoted from the Diagnosis line; canonicalization mismatch, not a clinical disagreement.
EA0061|MISSED|focal to bilateral convulsive seizures|MODEL_DEFENSIBLE|model tagged the letter's literal wording (no "convulsive"); gold's canonical form added "convulsive" - same single fact.
EA0061|MISSED|parietal lobe epilepsy|MODEL_DEFENSIBLE|"focal epilepsy, probable parietal onset" - gold split one diagnosis line into generic (matched) + specific; model consolidated to the generic only.
EA0061|SPURIOUS|focal to bilateral seizures|MODEL_DEFENSIBLE|same phrase, literal text vs gold's "convulsive"-added canonical form.
EA0071|SPURIOUS|epilepsy|BOTH_DEFENSIBLE|no explicit diagnosis statement in this nurse follow-up note; service names not an asserted patient diagnosis, though recurring "seizure" + lamotrigine make epilepsy a reasonable inference either way.
EA0072|MISSED|focal motor seizure|MODEL_DEFENSIBLE|narrative singular restates the header's plural (matched); gold double-tagged singular+plural mentions of one fact.
EA0073|SPURIOUS|seizure|GOLD_RIGHT|letter concludes "more suggestive of a cardiac cause ... no significant seizure markers" - explicitly rules OUT seizure; model fabricated a seizure diagnosis the letter denies.
EA0073|SPURIOUS|no significant seizure markers|GOLD_RIGHT|a negation phrase tagged as if it were a positive diagnosis entity - clear fabrication.
EA0076|SPURIOUS|epileptic seizures|GOLD_RIGHT|"I do not think that these are epileptic seizures and are more likely to be dissociative seizures" - letter explicitly rules out epileptic seizures; model tagged the negated differential.
EA0079|MISSED|epilepsy|MODEL_DEFENSIBLE|generic restatement subsumed by the already-tagged "He has symptomatic epilepsy"; consolidation of a redundant generic mention.
EA0079|MISSED|nocturnal seizures|MODEL_DEFENSIBLE|gold split "nocturnal generalised tonic clonic seizures" into "tonic clonic seizures" (matched) plus a separate "nocturnal" temporal-qualifier concept from the same single seizure fact.
EA0082|SPURIOUS|dissociative seizures|MODEL_DEFENSIBLE|explicit Diagnosis-line item #2; gold never tagged it.
EA0082|SPURIOUS|absences|MODEL_DEFENSIBLE|specific seizure-type restatement of the already-tagged "juvenile absence epilepsy"; consolidation.
EA0087|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|specific seizure type subsumed by the already-tagged "Juvenile myoclonic epilepsy"; gold consolidated to the syndrome name only.
EA0092|MISSED|epilepsy|MODEL_DEFENSIBLE|"Diagnosis: Genetic epilepsy" - model tagged the literal, more specific phrase; gold normalized to generic "epilepsy"; same single statement.
EA0092|SPURIOUS|genetic epilepsy|MODEL_DEFENSIBLE|same Diagnosis-line phrase, literally quoted; canonicalization-granularity mismatch with gold's generic "epilepsy".
EA0096|MISSED|epilepsy|MODEL_DEFENSIBLE|"Diagnosis: Severe epilepsy" - model tagged the literal phrase, gold normalized to generic "epilepsy"; same statement.
EA0096|SPURIOUS|severe epilepsy|MODEL_DEFENSIBLE|same Diagnosis-line "Severe epilepsy" phrase, literally quoted from the letter.
EA0096|SPURIOUS|absences|MODEL_DEFENSIBLE|"frequent drops and absences throughout the day" explicitly describes the patient's seizure types beyond the gold-tagged GTCS; gold never tagged this additional symptom.
EA0096|SPURIOUS|drops|MODEL_DEFENSIBLE|same sentence; explicit symptom description gold did not tag.
EA0100|SPURIOUS|single seizure|MODEL_DEFENSIBLE|the letter's own explicit Diagnosis field; gold simply did not tag it.
EA0102|SPURIOUS|non epileptic psychogenic seizures|MODEL_DEFENSIBLE|explicit field, "confirmed on EEG"; gold never tagged it.
EA0106|MISSED|focal epilepsy|MODEL_DEFENSIBLE|model tagged the literal phrase "symptomatic structural epilepsy"; gold's 'focal' label is an inferred canonicalization of the same single statement, not an added fact.
EA0106|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|same diagnosis line; model used the literal text, gold canonicalized it as 'focal epilepsy' instead.
EA0107|MISSED|generalised seizures|MODEL_DEFENSIBLE|directly follows and restates the already-tagged "4 generalised tonic clonic seizures" - same seizures, gold double-tagged.
EA0107|MISSED|intractable epilepsy|GOLD_RIGHT|"long-standing intractable epilepsy" is an explicit, distinct severity descriptor the model never captured at all.
EA0108|MISSED|epilepsy|MODEL_DEFENSIBLE|"His epilepsy was well controlled" is a generic restatement of the already-matched 'symptomatic epilepsy' diagnosis, not a new fact.
EA0108|MISSED|tonic clonic convulsion|MODEL_DEFENSIBLE|narratively restates the header's already-matched "secondary generalised tonic clonic seizures."
EA0109|MISSED|temporal lobe seizure|MODEL_DEFENSIBLE|same diagnosis stated twice; model matched the body occurrence, gold split singular/plural into two concepts.
EA0111|MISSED|focal epilepsy|MODEL_DEFENSIBLE|"Refractory focal epilepsy" split by gold into 'refractory epilepsies' + 'focal epilepsy'; model emitted the literal compound.
EA0111|MISSED|refractory epilepsies|MODEL_DEFENSIBLE|Same bullet - gold's second half of its split, model consolidated into one term.
EA0111|SPURIOUS|refractory focal epilepsy|MODEL_DEFENSIBLE|Model's literal compound phrase from the diagnosis bullet; gold tagged the two halves separately instead.
EA0111|SPURIOUS|nocturnal generalised tonic clonic seizures|MODEL_DEFENSIBLE|literal diagnosis-header text; gold consolidated it with the body's "tonic clonic seizures" mention into one concept.
EA0113|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|textually grounded JME semiology; gold only tagged the syndrome name, not its component seizure types.
EA0113|SPURIOUS|tonic clonic seizures|MODEL_DEFENSIBLE|GTC semiology grounded in text; gold consolidated all seizure-type detail into the single JME syndrome tag.
EA0114|MISSED|temporal lobe onset seizure|BOTH_DEFENSIBLE|"?" marks it as an explicit query/uncertain differential, a genuine coin-flip on whether to tag it as confirmed.
EA0114|SPURIOUS|focal to bilateral tonic clonic seizures|GOLD_RIGHT|Text explicitly states "but no focal to bilateral tonic clonic seizures" - model fabricated a diagnosis from an explicitly negated finding.
EA0116|MISSED|focal seizures|BOTH_DEFENSIBLE|explicitly hedged ("possible", "needs further investigations"), a genuine differential-vs-confirmed call.
EA0116|MISSED|frontal lobe onset seizure|BOTH_DEFENSIBLE|Same hedged sentence as above - explicit uncertainty language makes tagging vs not tagging defensible either way.
EA0116|MISSED|generalised epilepsy|MODEL_DEFENSIBLE|one phrase; model captured the seizure-type half, gold separately tagged the epilepsy-classification half.
EA0121|MISSED|drug resistant epilepsy|MODEL_DEFENSIBLE|"Drug resistant focal epilepsy" split by gold into two; model emitted the literal compound term.
EA0121|MISSED|focal epilepsy|MODEL_DEFENSIBLE|Same diagnosis line, gold's other half of the split compound.
EA0121|SPURIOUS|drug resistant focal epilepsy|MODEL_DEFENSIBLE|Model's literal compound; gold tagged the two component concepts instead of the compound phrase.
EA0123|MISSED|epilepsy|MODEL_DEFENSIBLE|model's 'longstanding epilepsy' canonicalizes differently than gold's plain 'epilepsy' for the same mention.
EA0123|MISSED|generalised|MODEL_DEFENSIBLE|Gold split "generalised tonic clonic seizures" into a standalone concept plus 'tonic clonic seizures'; model reasonably kept it as one phrase.
EA0123|SPURIOUS|longstanding epilepsy|MODEL_DEFENSIBLE|Same diagnosis-line mention as the missed 'epilepsy' above - literal text supported, gold just canonicalized to plain 'epilepsy'.
EA0123|SPURIOUS|myoclonic jerks|GOLD_RIGHT|Text states "There is no history of any myoclonic jerks or absences" - model fabricated a diagnosis from an explicitly negated finding.
EA0124|SPURIOUS|absence seizures|MODEL_DEFENSIBLE|clear, current, well-supported absence-seizure semiology gold never tagged.
EA0125|SPURIOUS|absences|MODEL_DEFENSIBLE|listed alongside the seizure type gold did tag - inconsistent gold under-annotation.
EA0125|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|Same diagnosis sentence - co-listed with equally-supported tagged content, gold simply omitted it.
EA0126|MISSED|focal epilepsy|MODEL_DEFENSIBLE|model tagged whole compound; gold split out 'focal epilepsy' as a sub-concept.
EA0126|MISSED|focal seizures|MODEL_DEFENSIBLE|model tagged whole; gold split this into 'focal seizures' + 'frontal lobe seizures'.
EA0126|MISSED|frontal lobe seizures|MODEL_DEFENSIBLE|Same sentence as above - gold's other half of its split of the compound.
EA0126|SPURIOUS|drop attacks|GOLD_RIGHT|"As a child he also had drop attacks but they haven't happened in adulthood" - explicitly resolved childhood-only history, model over-extracted it as a current concept.
EA0126|SPURIOUS|focal epilepsy secondary to tuberous sclerosis|MODEL_DEFENSIBLE|Model's literal compound from the diagnosis header; gold split it instead of tagging the compound.
EA0126|SPURIOUS|focal frontal lobe seizures|MODEL_DEFENSIBLE|Model's literal compound; gold split it into 'focal seizures' + 'frontal lobe seizures'.
EA0128|MISSED|generalised|MODEL_DEFENSIBLE|Gold split into standalone 'generalised' + 'tonic clonic seizures'; model kept the natural compound phrase.
EA0128|SPURIOUS|longstanding epilepsy|MODEL_DEFENSIBLE|literal text, gold canonicalized to plain 'epilepsy'.
EA0128|SPURIOUS|myoclonic jerks|MODEL_DEFENSIBLE|Diagnosis header lists it explicitly and body confirms - clearly supported, gold simply didn't tag it.
EA0128|SPURIOUS|no febrile seizures|GOLD_RIGHT|"She has not had any febrile seizures..." is a negative-history statement; packaging an absent finding as a Diagnosis concept is a categorization error.
EA0128|SPURIOUS|no history of absences|GOLD_RIGHT|same negation-as-diagnosis error; the model tagged an explicitly absent finding as a Diagnosis entity.
EA0129|SPURIOUS|focal seizures with altered awareness|GOLD_RIGHT|no grounding text describes altered-awareness focal seizures; letter only describes a convulsive generalized event with explicit uncertainty about its nature.
EA0129|SPURIOUS|no history of febrile seizures|GOLD_RIGHT|negated finding mis-tagged as a Diagnosis concept, a categorization error not a real diagnosis.
EA0129|SPURIOUS|tonic clonic seizures|BOTH_DEFENSIBLE|plausibly reads as tonic-clonic, but the letter itself says "the nature of these is not very clear" - genuine diagnostic ambiguity.
EA0133|MISSED|epileptic seizure|MODEL_DEFENSIBLE|narratively restates the same event later clarified as the already-matched "focal to bilateral convulsive seizures."
EA0133|MISSED|focal epilepsy|MODEL_DEFENSIBLE|same EA0106-style mismatch: model's literal text vs gold's inferred canonicalization of one mention.
EA0133|MISSED|focal seizures|MODEL_DEFENSIBLE|restates the identical "left arm jerks" already captured under the header's matched 'focal motor seizures'.
EA0133|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|Model's literal diagnosis-header text; gold canonicalized the same mention as 'focal epilepsy' instead.
EA0135|MISSED|epileptic seizures|MODEL_DEFENSIBLE|the doctor's conclusion supporting the already-tagged "Focal onset epilepsy" header diagnosis - redundant restatement.
EA0135|SPURIOUS|dissociative seizures|MODEL_DEFENSIBLE|explicitly lists it as a confirmed co-diagnosis in the header; gold simply omitted it.
EA0136|MISSED|generalised seizures|MODEL_DEFENSIBLE|elaborates the same condition already matched as 'generalised epilepsy' in the header - redundant restatement.
EA0136|SPURIOUS|generalised convulsions|GOLD_RIGHT|"He has not had any generalised convulsions now for several years" is an explicit negation/remission statement; model tagged it as an active diagnostic concept.
EA0137|MISSED|epilepsy|GOLD_RIGHT|"she was diagnosed with epilepsy at the age of 4" is a separate, explicit, independently stated diagnosis the model never emitted.
EA0141|MISSED|epileptic seizures|MODEL_DEFENSIBLE|model's own "epilepsy" + "probable focal onset epilepsy" tags capture the same clinical content as a consolidated pair.
EA0141|SPURIOUS|focal seizures|MODEL_DEFENSIBLE|redundant duplicate fragment of the already-tagged "Epilepsy, probable focal onset" - textually grounded, just over-fragmented.
EA0143|MISSED|epilepsy|GOLD_RIGHT|"she was diagnosed with epilepsy at the age of 22" is a distinct, independent sentence the model never captured at all.
EA0143|MISSED|focal|MODEL_DEFENSIBLE|gold atomized the word "Focal" out of a phrase while model tagged the whole phrase as one coherent concept - granularity split.
EA0143|SPURIOUS|focal seizures with altered awareness|MODEL_DEFENSIBLE|model's single composite tag is the clinically more useful unit, gold instead atomized to bare "focal".
EA0146|MISSED|grand mal|MODEL_DEFENSIBLE|model translated the lay term to standard "generalised tonic clonic seizures," a defensible synonym the canonicalizer failed to map.
EA0146|SPURIOUS|myoclonic jerks|GOLD_RIGHT|letter explicitly attributes the jerk episodes to non-epileptic origin ("consistent with dissociative seizures"); model fabricated an epileptic label contradicted by the text.
EA0146|SPURIOUS|tonic clonic seizures|MODEL_DEFENSIBLE|paired with the "grand mal" miss above - same synonym/canonicalization gap, not a separate error.
EA0148|SPURIOUS|no history of myoclonic jerks|GOLD_RIGHT|"There is no history of myoclonic jerks" is an explicit NEGATION; model extracted a negated absence-of-finding as if it were a present diagnosis.
EA0148|SPURIOUS|staring episodes|GOLD_RIGHT|reported third-hand and never diagnostically classified ("not clear whether they are focal or generalised"); model over-read an unclassified symptom as a diagnosis.
EA0150|MISSED|focal epilepsy|MODEL_DEFENSIBLE|identical source text canonicalized by gold differently than by the model-side tagger - pure normalization mismatch.
EA0150|MISSED|secondary|MODEL_DEFENSIBLE|gold atomizes into a bare 'secondary' plus the full phrase; model only emitted the full phrase - atomization artifact.
EA0150|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|same canonicalization gap as the paired miss above.
EA0151|SPURIOUS|olfactory aura|MODEL_DEFENSIBLE|genuinely described; redundant duplicate of the already-matched combined concept.
EA0152|MISSED|focal epilepsy|MODEL_DEFENSIBLE|gold canonicalizes a two-line header to one concept; model split it into two separately-named entities, neither string-matching gold's label.
EA0152|SPURIOUS|focal cortical dysplasia right temporal lobe|MODEL_DEFENSIBLE|same header text as above, same canonicalization/atomization gap, not a fabrication.
EA0152|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|same header text/root cause as the missed 'focal epilepsy' entry.
EA0153|MISSED|temporal lobe epilepsy|BOTH_DEFENSIBLE|"?" marks genuine localization uncertainty; reasonable for model to commit only to "focal" and for gold to record the suspected specific lobe.
EA0153|SPURIOUS|focal epilepsy|BOTH_DEFENSIBLE|same hedged line - model's more conservative tag is a defensible coin-flip against gold's specific (but qualified) localization.
EA0157|MISSED|complex partial seizure|MODEL_DEFENSIBLE|model emitted plural vs gold's singular canonical form; trivial pluralization mismatch, same content.
EA0157|SPURIOUS|complex partial seizures|MODEL_DEFENSIBLE|paired with the above - singular/plural canonicalization artifact, not a real discrepancy.
EA0157|SPURIOUS|loss of awareness seizure|GOLD_RIGHT|presentation is explicitly undiagnosed/pending workup, not a confirmed diagnosis; model prematurely tagged it as one.
EA0158|MISSED|focal epilepsy|MODEL_DEFENSIBLE|gold canonicalized to 'focal epilepsy' but tagged by the model with the literal header text as its own concept - normalization gap.
EA0158|SPURIOUS|symptomatic structural epilepsy|MODEL_DEFENSIBLE|same header text/root cause as the paired miss above.
EA0161|SPURIOUS|absences|MODEL_DEFENSIBLE|fragment of the header diagnosis line, redundant with the already-matched body-derived "absence seizures" tag; text-supported.
EA0161|SPURIOUS|gtcs|MODEL_DEFENSIBLE|same header fragment as above, redundant with the already-matched "generalised tonic clonic seizure" tag.
EA0162|MISSED|epilepsy|GOLD_RIGHT|explicit header diagnosis entirely unaddressed; model only extracted from the body's seizure-cluster narrative.
EA0162|MISSED|status epilepticus|GOLD_RIGHT|"Previous episode of status epilepticus" is unambiguous and was never emitted by the model.
EA0162|SPURIOUS|tonic clonic seizures|MODEL_DEFENSIBLE|genuinely supported body text; gold simply didn't tag this body description, only the formal Problem-list items.
EA0164|SPURIOUS|unclassified|GOLD_RIGHT|"unclassified" alone is a qualifier word, not a standalone diagnosis concept - a meaningless fragment improperly extracted as its own Diagnosis entity.
EA0166|MISSED|juvenile myoclonic epilepsy|GOLD_RIGHT|stated plainly at the top; model produced zero Diagnosis predictions for this letter - a clean miss.
EA0167|MISSED|temporal lobe epilepsy|MODEL_DEFENSIBLE|gold canonicalized but kept verbatim by the model as a longer, distinct concept string - same text, normalization gap.
EA0167|SPURIOUS|symptomatic structural temporal lobe epilepsy|MODEL_DEFENSIBLE|identical source phrase as the paired miss above.
EA0168|SPURIOUS|absences|MODEL_DEFENSIBLE|explicitly present parenthetical of the JME diagnosis line; gold bundled these under the single JME tag rather than itemizing.
EA0168|SPURIOUS|myoclonus|MODEL_DEFENSIBLE|same parenthetical JME diagnosis line as above; text-supported, gold under-annotated the sub-components.
EA0169|MISSED|dyscognitive seizures|MODEL_DEFENSIBLE|gold canonicalizes to bare form, model kept the "focal" qualifier in its own concept string; same text, normalization granularity gap.
EA0169|SPURIOUS|focal dyscognitive seizures|MODEL_DEFENSIBLE|identical phrase as the paired miss above - canonicalization mismatch, not a real discrepancy.
EA0171|MISSED|focal seizures|MODEL_DEFENSIBLE|model tagged it as 'focal epileptic seizures', gold canonicalized identical text differently; canonicalization mismatch not omission.
EA0171|SPURIOUS|focal epileptic seizures|MODEL_DEFENSIBLE|model correctly extracted the verbatim phrase; gold's canon dictionary mapped the same span differently.
EA0172|MISSED|drug refractory epilepsy|MODEL_DEFENSIBLE|gold split into two atomic tags; model emitted one consolidated tag covering the same phrase.
EA0172|MISSED|focal epilepsy|MODEL_DEFENSIBLE|same phrase - gold's second atomic split, model's single consolidated tag already covers it.
EA0172|SPURIOUS|drug refractory focal epilepsy|MODEL_DEFENSIBLE|model's consolidated tag vs gold's two-way split of the identical phrase.
EA0172|SPURIOUS|nocturnal seizures|MODEL_DEFENSIBLE|appears verbatim under the letter's own "Diagnosis:" header; gold simply never tagged it.
EA0175|MISSED|drug refractory epilepsies|MODEL_DEFENSIBLE|split by gold into two atoms; model's single tag already captures it.
EA0175|MISSED|focal epilepsy|MODEL_DEFENSIBLE|same diagnosis-line phrase, gold's other atomic split already covered by model's consolidated tag.
EA0175|SPURIOUS|drug refractory focal epilepsy|MODEL_DEFENSIBLE|model's reasonable single-tag consolidation vs gold's two-tag atomization.
EA0176|SPURIOUS|generalised seizures|GOLD_RIGHT|model inferred a seizure-type diagnosis from an EEG abnormality finding, not a stated clinical seizure-type diagnosis.
EA0179|MISSED|epilepsy|BOTH_DEFENSIBLE|unconfirmed differential (clinician favors syncope) - genuinely ambiguous whether to tag as Diagnosis.
EA0180|SPURIOUS|absences|MODEL_DEFENSIBLE|gold tagged JME + only one of its three listed seizure types; model tagged all three components of the same phrase.
EA0180|SPURIOUS|myoclonus|MODEL_DEFENSIBLE|same parenthetical listing JME's component seizure types; gold under-tagged the co-listed types.
EA0181|MISSED|dyscognitive seizures|MODEL_DEFENSIBLE|model retained "focal" specificity from the same span, gold canonicalized to a shorter form; same text, different granularity.
EA0181|SPURIOUS|focal dyscognitive seizures|MODEL_DEFENSIBLE|paired with the missed concept above - same underlying mention, more specific consolidation choice by model.
EA0182|MISSED|temporal|MODEL_DEFENSIBLE|gold split the queried localizer into a separate atomic tag; model's single tag is a reasonable consolidation.
EA0183|MISSED|epilepsy|MODEL_DEFENSIBLE|generic background already covered by the specific seizure-type diagnoses the model tagged.
EA0183|MISSED|generalised|MODEL_DEFENSIBLE|gold atomized to 'generalised' alone; model canonicalized the same span as 'tonic clonic seizures'.
EA0183|SPURIOUS|tonic clonic seizures|MODEL_DEFENSIBLE|model's reasonable canon of the same span vs gold's atomic split.
EA0186|MISSED|focal to bilateral convulsive seizure|MODEL_DEFENSIBLE|gold double-tagged the same seizure type from two mentions; model consolidated to one Diagnosis tag for one seizure type.
EA0188|MISSED|drug|MODEL_DEFENSIBLE|gold atomized into word-level fragments; model's single tag is a reasonable consolidation of the whole phrase.
EA0188|MISSED|focal|MODEL_DEFENSIBLE|same phrase, another of gold's atomic fragments already covered by model's consolidated tag.
EA0188|MISSED|occipital|MODEL_DEFENSIBLE|same phrase, gold's atomic fragment already implied by model's tag + diagnosis-line context.
EA0188|MISSED|occipital lobe epilepsy|MODEL_DEFENSIBLE|gold double-tagged consolidated form alongside atoms; model tagged the equivalent concept once.
EA0188|MISSED|secondary|MODEL_DEFENSIBLE|gold atomized to 'secondary' alone; model tagged the full consolidated phrase instead.
EA0188|SPURIOUS|secondary generalised seizure|MODEL_DEFENSIBLE|model's full-phrase consolidation vs gold's atomic tag for the same span.
EA0189|MISSED|epileptic|MODEL_DEFENSIBLE|gold tagged the bare word; model tagged the fuller phrase covering the same span.
EA0189|SPURIOUS|single epileptic seizure|MODEL_DEFENSIBLE|paired with the missed concept above - same mention, model's more complete canonicalization.
EA0189|SPURIOUS|myoclonic seizures|GOLD_RIGHT|model fabricated a confirmed-sounding diagnosis tag from explicitly hedged, partly-contradicted speculation.
EA0190|MISSED|focal|MODEL_DEFENSIBLE|duplicates content already captured via the more specific tags.
EA0190|SPURIOUS|right hippocampal sclerosis|MODEL_DEFENSIBLE|literally listed under the Diagnosis header; gold under-annotation.
EA0195|MISSED|generalised|MODEL_DEFENSIBLE|gold atomized to 'generalised'; model's tag already covers the same span.
EA0195|MISSED|symptomatic|MODEL_DEFENSIBLE|gold's atomic fragment already covered by model's consolidated tag.
EA0195|SPURIOUS|symptomatic epilepsy|MODEL_DEFENSIBLE|model's reasonable consolidation vs gold's atomic split.
EA0195|SPURIOUS|tonic clonic seizures|MODEL_DEFENSIBLE|model's reasonable consolidation vs gold's atomic split.
EA0198|MISSED|epilepsy|MODEL_DEFENSIBLE|generic background already covered by the specific tags.
EA0198|SPURIOUS|non epileptic psychogenic seizures|MODEL_DEFENSIBLE|stated verbatim as a co-diagnosis in the letter's own Diagnosis line; gold under-annotation.
EA0200|MISSED|epilepsy|MODEL_DEFENSIBLE|apposition restating one diagnosis at two specificity levels; model tagged only the specific form.
"""


def parse_rows() -> list[dict]:
    rows = []
    for line in RAW_VERDICTS.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        letter, direction, concept, verdict, reason = line.split("|", 4)
        rows.append({
            "letter": letter, "direction": direction, "concept": concept,
            "verdict": verdict, "reason": reason,
        })
    return rows


def main() -> None:
    rows = parse_rows()
    index = json.loads((ROOT / "_dx_canonical" / "_index.json").read_text(encoding="utf-8"))

    # Coverage assertion: every missed/spurious concept in the index has exactly one
    # adjudicated verdict, and there are no extra verdicts for non-existent disagreements.
    expected = set()
    for r in index:
        for c in r["missed_concepts"]:
            expected.add((r["letter_id"], "MISSED", c))
        for c in r["spurious_concepts"]:
            expected.add((r["letter_id"], "SPURIOUS", c))
    got = {(r["letter"], r["direction"], r["concept"]) for r in rows}
    missing = expected - got
    extra = got - expected
    assert not missing, f"un-adjudicated disagreements: {sorted(missing)[:10]} (+{max(0, len(missing) - 10)} more)"
    assert not extra, f"verdicts for non-disagreements: {sorted(extra)[:10]} (+{max(0, len(extra) - 10)} more)"

    out = ROOT / "_dx_canonical" / "_adjudication.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["letter", "direction", "concept", "verdict", "reason"])
        w.writeheader()
        w.writerows(rows)

    vc = Counter(r["verdict"] for r in rows)
    by_dir = {
        d: Counter(r["verdict"] for r in rows if r["direction"] == d)
        for d in ("MISSED", "SPURIOUS")
    }
    n = len(rows)
    defensible = vc["MODEL_DEFENSIBLE"] + vc["BOTH_DEFENSIBLE"]

    print(f"adjudicated {n}/{len(expected)} Diagnosis disagreements (88 letters)\n")
    print("VERDICT TALLY (of 209 missed+spurious concepts):")
    for k in ("GOLD_RIGHT", "MODEL_DEFENSIBLE", "BOTH_DEFENSIBLE"):
        print(f"  {k:18s} {vc[k]:3d}  ({vc[k] / n:.1%})")
    print(f"\n  -> genuine model error (GOLD_RIGHT)  : {vc['GOLD_RIGHT']}/{n} ({vc['GOLD_RIGHT'] / n:.1%})")
    print(f"  -> NOT a model mistake (MODEL+BOTH)  : {defensible}/{n} ({defensible / n:.1%})")

    print("\nby direction:")
    for d in ("MISSED", "SPURIOUS"):
        c = by_dir[d]
        nd = sum(c.values())
        print(f"  {d:9s} n={nd:3d}  GOLD_RIGHT={c['GOLD_RIGHT']:3d}  MODEL_DEFENSIBLE={c['MODEL_DEFENSIBLE']:3d}  BOTH_DEFENSIBLE={c['BOTH_DEFENSIBLE']:3d}")

    # --- Adjusted aggregate: treat MODEL_DEFENSIBLE + BOTH_DEFENSIBLE as correct. ---
    summary = json.loads((ROOT / "_dx_canonical" / "_summary.json").read_text(encoding="utf-8"))
    official = summary["official_concept_only"]
    precision_tp, recall_tp = official["precision_tp"], official["recall_tp"]
    pred_count, gold_count = official["pred_count"], official["gold_count"]

    missed_defensible = by_dir["MISSED"]["MODEL_DEFENSIBLE"] + by_dir["MISSED"]["BOTH_DEFENSIBLE"]
    spurious_defensible = by_dir["SPURIOUS"]["MODEL_DEFENSIBLE"] + by_dir["SPURIOUS"]["BOTH_DEFENSIBLE"]
    adj_recall_tp = recall_tp + missed_defensible
    adj_precision_tp = precision_tp + spurious_defensible
    adj_precision = adj_precision_tp / pred_count if pred_count else 0.0
    adj_recall = adj_recall_tp / gold_count if gold_count else 0.0
    adj_f1 = (2 * adj_precision * adj_recall / (adj_precision + adj_recall)) if (adj_precision + adj_recall) else 0.0

    print(f"\nOFFICIAL  concept_only   : P={official['precision']:.4f} R={official['recall']:.4f} F1={official['f1']:.4f}")
    print(f"CLINICALLY-ADJUSTED      : P={adj_precision:.4f} R={adj_recall:.4f} F1={adj_f1:.4f}")
    print(f"  (treats {missed_defensible} defensible misses as recall_tp and "
          f"{spurious_defensible} defensible spurious predictions as precision_tp)")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
