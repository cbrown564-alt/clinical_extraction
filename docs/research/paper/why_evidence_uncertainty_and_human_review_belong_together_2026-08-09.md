# Why evidence, uncertainty, and human review belong together

Date: 2026-08-09  
Revised: 2026-08-19 (evidence strength distinctions made explicit)  
Status: literature-grounded paper source; not clinical validation

## The short answer

A structured clinical fact is reviewable only when a person can judge it. The
reviewer needs to see the source statement, the system's relevant uncertainty
and limits, and the decision that still belongs to a person. Evidence,
uncertainty, and reviewer authority form one review process.

This does not mean that every internal model calculation must be explained.
It means that the information needed for the intended clinical or research
decision must be available at the point of review.

## A useful output answers three questions

### What in the letter supports this fact?

The joint FDA, Health Canada, and MHRA transparency principles say that users
should receive the basis of an output when it is available and understandable,
along with the system's intended use, inputs, outputs, performance, and place in
the workflow. They connect this information to critical assessment of an output
and to the detection and investigation of errors.

For clinical extraction, the practical unit of review is therefore not the
structured value alone. It is the value together with the relevant source text
and any consequential transformation between them.

Evidence support has several different strengths:

| Question | Meaning |
| --- | --- |
| Is evidence present? | The quoted or indexed text occurs in the letter. |
| Is it relevant? | The text concerns the fact being extracted. |
| Is it decisive? | It supports this task answer over competing readings. |
| Is it sufficient? | It contains enough information for the asserted state and attributes. |
| Is it complete? | No additional supported fact required by an inventory task has been omitted. |

An exact-substring check establishes presence only. Gan particularly tests
whether evidence is decisive among temporal alternatives. ExECT particularly
tests whether the retained evidence and facts are complete as a set.

### What could make this fact wrong or incomplete?

The same regulatory principles call for clinically relevant limitations to be
communicated, including known failure modes, confidence intervals where they
apply, gaps in data characterisation, and circumstances that differ from the
development setting. FUTURE-AI likewise recommends traceability, robustness,
and explainability across the system lifecycle.

Uncertainty must change what happens next. Depending on the task, that may be
an explicit unknown state, preservation of competing
readings, a warning that the inventory may be incomplete, or referral for
review. A confidence number that does not identify failures or change the next
action is not sufficient by itself.

### Who makes the consequential decision?

WHO's guidance for AI in health places human autonomy, transparency, and
accountability among its core principles. It states that humans should remain
in control of health-care systems and medical decisions. DECIDE-AI makes the
same point operationally: early clinical evaluation must examine safety and
human factors, not only offline model performance. FUTURE-AI adds that human
oversight should be specific to the use case.

Human review works only when the system gives the reviewer enough evidence and
limitation information to exercise judgment. Evaluation must then test how that
human–system combination behaves.

## What this permits the paper to say

The literature supports a design rationale: health-related AI should make the
basis, limitations, and intended human role visible enough for informed use and
evaluation. It also supports studying the human–AI workflow rather than treating
model accuracy as the whole system.

The project can then show, using its own evidence lane, whether the selected
research system exposes source spans, intermediate changes, uncertainty states,
component ownership, and known failures. Literature cannot prove that this
implementation is clinically usable, and project traces cannot prove that
clinicians find them useful.

That distinction keeps the paper's language precise:

| Supported interpretation | Unsupported extension |
| --- | --- |
| Evidence-grounded reviewability is a justified design objective. | The current interface has been validated for clinical review. |
| Uncertainty should result in an explicit state or review action. | The current confidence or abstention policy is clinically safe. |
| Human–system performance matters in clinical evaluation. | Human oversight makes an otherwise unsafe system safe. |
| Known limits and failure modes should remain visible. | Transparency proves correctness, trustworthiness, or deployment readiness. |

## Sources and boundary

- World Health Organization,
  [*Ethics and governance of artificial intelligence for health*](https://www.who.int/publications/i/item/9789240029200),
  2021. Establishes the health-AI principles of human autonomy,
  transparency, explainability, responsibility, and accountability.
- Vasey B, et al.,
  [DECIDE-AI reporting guideline](https://www.bmj.com/content/377/bmj-2022-070904),
  *BMJ* 2022;377:e070904. Establishes that early live clinical evaluation must
  address safety and human factors as well as small-scale clinical utility.
- Lekadir K, et al.,
  [FUTURE-AI international consensus guideline](https://pubmed.ncbi.nlm.nih.gov/39909534/),
  *BMJ* 2025;388:e081554. Establishes lifecycle guidance organised around
  fairness, universality, traceability, usability, robustness, and
  explainability, including use-case-specific oversight.
- FDA, Health Canada, and MHRA,
  [*Transparency for Machine Learning-Enabled Medical Devices: Guiding Principles*](https://www.fda.gov/medical-devices/software-medical-device-samd/transparency-machine-learning-enabled-medical-devices-guiding-principles),
  2024. Establishes a regulatory transparency rationale for communicating an
  output's basis, intended use, performance, limitations, and place in the
  human workflow. The project is not represented here as a medical device.

This source belongs to the literature evidence lane. It motivates requirements;
it does not show that the project satisfies them. Project implementation and
measured behaviour remain with the
[system architecture](../../canon/01_system_architecture.md),
[cross-task reliability owner](../../canon/09_cross_task_reliability.md), and
[paper claim status](../../canon/10_paper_provenance.md).

## Writing test

**Question:** can the author explain, without reopening the source guidelines,
why evidence, uncertainty handling, and human review must be presented as one
review process?

**Success:** the explanation preserves the difference between an external
design requirement, a project implementation fact, and clinical validation.
