# ExECTv2 Luna prompt-variant exemplar pack

Date: 2026-07-31  
Status: development seeds for A/B/C drafting only  
Source: [residual map](exectv2_luna_single_call_dev140_residual_map_2026-07-31.md)  
Machine: `experiments/exectv2_luna_single_call_dev140_residual_map_20260731/residual_exemplars.json`

These are permitted `dev140` examples used to justify plain-language prompt
blocks. They are not a new gold taxonomy and must not be copied into prompts as
labeled “gold” or “failure cases.”

## B target — SF competing states and rate construction

| Letter | Issue | Gold states (abbrev.) | Luna final states (abbrev.) | Evidence cue |
| --- | --- | --- | --- | --- |
| EA0011 | Extra / mismatched seizure-free concept beside an active rate | active-rate + seizure-free | active-rate + different seizure-free | “Focal seizures with altered awareness approximately 1 per fortnight” |
| EA0025 | Missing required unknown alongside active rate | active-rate + unknown | active-rate only | “approximately 3–4 generalised … seizures per week” |
| EA0034 | Active-rate invented beside seizure-free | seizure-free | seizure-free + active-rate | dated prior convulsive event language |
| EA0038 | Seizure-free invented beside a recent active event | active-rate | active-rate + seizure-free | “recent generalised … seizure at home” |
| EA0110 | Incomplete multi-type active-rate set | two active-rate concepts | one active-rate | “once or twice a month” / cluster language |
| EA0132 | Extra active-rate subtype | one focal active-rate | two active-rate concepts | “several per month” |

Prompt intent for B: emit the supported state set; keep countable rates;
do not invent a competing seizure-free or drop a required unknown when the
note only partly specifies current frequency.

## C target — SF boundaries and Diagnosis specificity

| Letter | Family | Issue | Evidence cue |
| --- | --- | --- | --- |
| EA0022 | SF | Omits required unknown while keeping seizure-free | improvement after lamotrigine increase; incomplete current-frequency statement |
| EA0019 | SF | Active-rate gold, empty prediction after assembly | stable epilepsy with stated GTCS rate in note (selection miss) |
| EA0005 | Dx | Over-broad / incomplete syndrome set | “genetic generalised epilepsy-epilepsy with generalised tonic chronic seizures alone” |
| EA0018 | Dx | Wrong or extra phenotype versus gold | epilepsy with focal / occipital mention conflict |
| EA0020 | Dx | Extra tonic-clonic phenotype beyond gold `epilepsy` | “lady with epilepsy” |

Prompt intent for C: prefer unknown when current frequency is not clear enough
for seizure-free or a rate; prefer the most specific diagnosis phrase the note
supports without adding broader or sibling phenotypes that the letter does not
authorize.

## Explicit non-targets

| Theme | Why excluded from prompt success |
| --- | --- |
| `rx_current_regimen` | Joint bounded policy is the fixed repair; default Rx regressions are rule-owned |
| `annotation_or_empty_gold` | Empty-gold letters remain diagnostic; not factuality prevalence |
| Further Dx/Rx residual-addition rules | Prior candidates failed predeclared gates |

## Claim boundary

Development drafting aid for Luna ExECT prompt variants on `dev140`. Not
holdout evidence and not authorization to retarget the frozen six-model panel.
