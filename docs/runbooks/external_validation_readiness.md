# Restricted external-validation readiness record template

Decision 0048 milestone 6. This template is the required gate for any run on
restricted external or real-patient data. It is a research-validation record,
not an authorization for clinical deployment, clinical care, or production use.

Copy this template into the run-record directory as one run-specific file;
complete it without changing the template's control sections. The template
itself is not a readiness approval and does not mark milestone 6 complete.

## Record location and lifecycle

Run-specific records belong in `docs/runbooks/external_validation_records/`
with the naming convention
`YYYY-MM-DD_<run-id>_external-validation-readiness_vNN.md`. `<run-id>` must be
stable, unique, and free of patient or note identifiers; `vNN` starts at
`v01` and increments for every amendment. Do not store private data in the
record.

Once any person signs a record, that version is immutable. Amendments create a
new dated version and must state the reason, affected sections, new decision,
and links to the prior version; never overwrite a signed record. Preserve all
prior versions and their signatures, including blocked or superseded
decisions. A revision may not authorize execution until the required
signatures and checks are completed again. The run history must retain the
record version used for execution.

- **Revision/amendment number:** `[REQUIRED: vNN]`
- **Revision date:** `[REQUIRED: YYYY-MM-DD]`
- **Amends record/version:** `[REQUIRED: path and version, or INITIAL]`
- **Amendment reason and affected sections:** `[REQUIRED: reason and sections]`

## Gate status

- **Overall state:** `NOT READY`
- **Record owner:** `[REQUIRED: name and date]`
- **Planned run identifier:** `[REQUIRED: stable identifier]`
- **Last reviewed:** `[REQUIRED: date]`
- **Sign-off state:** `UNSIGNED`

Every `[REQUIRED: ...]` blank blocks the run. `READY` may be recorded only when
all required fields are completed, the checks below pass, the independent
clinical reviewer has signed off on the review plan, and the data owner and
technical run owner have authorized the specific run. A completed record does
not establish clinical validity or permit clinical deployment.

## People and accountability

- **Data owner:** `[REQUIRED: person, organization, contact, authorization]`
- **Technical run owner:** `[REQUIRED: person, team, contact]`
- **Independent clinical reviewer:** `[REQUIRED: person, credentials, independence, contact]`
- **Review/adjudication process:** `[REQUIRED: blinded reviewer roles, review unit, disagreement handling, adjudicator, audit trail, completion rule]`
- **Data access approver, if separate:** `[REQUIRED: person and approval reference, or N/A with reason]`

No person may serve as the sole technical operator, clinical reviewer, and
adjudicator. Reviewer identities and revisions must remain separable from the
technical run record.

## Data and split authorization

- **Permitted dataset:** `[REQUIRED: dataset name/version, source, purpose, row or patient count]`
- **Permitted split policy:** `[REQUIRED: exact inclusion/exclusion and development/validation/holdout policy]`
- **Row-access policy:** `[REQUIRED: what may be inspected, by whom, and when]`
- **Data dictionary/label policy:** `[REQUIRED: governing annotation and scoring definition]`
- **Dataset authorization and expiry:** `[REQUIRED: approval/reference and end date]`

The run must not access locked rows, unapproved patients, or a split outside
this record. Any split or row-policy change requires a new readiness record.

## Exact technical configuration

- **Task and route:** `[REQUIRED: task, method, provider/endpoint or local route]`
- **Model and version:** `[REQUIRED: model identifier/version]`
- **Prompt/program version:** `[REQUIRED: path, version or commit, schema version]`
- **Scorer and metric:** `[REQUIRED: scorer path/version and named metric]`
- **Repair policy:** `[REQUIRED: raw selection, format-only, selected-evidence, semantic deterministic repair, or none; versions]`
- **Code and environment:** `[REQUIRED: repository commit, Python/dependency versions, run command]`
- **Cache/replay mode and run metadata:** `[REQUIRED: cache policy, seed/temperature if applicable, timestamps, run manifest]`
- **Raw-output retention location and hash:** `[REQUIRED: controlled location and integrity identifier]`

The run owner must preserve enough metadata and raw output to reproduce the
reported result without another model call. Clinical meaning, selected event,
sentinel state, category, timeframe, denominator, or scorer changes require a
new predeclared study and readiness review.

## Privacy and retention controls

- **Approved processing environment:** `[REQUIRED: system, access boundary, encryption]`
- **Minimum-necessary fields and de-identification:** `[REQUIRED: fields and method]`
- **Access control and audit logging:** `[REQUIRED: named group, authentication, log location]`
- **Transfer/export restrictions:** `[REQUIRED: allowed destinations and prohibition details]`
- **Retention period and deletion owner:** `[REQUIRED: duration, deletion method, accountable person]`
- **Incident/breach escalation:** `[REQUIRED: contact and procedure]`

No private data, raw notes, or derived identifiers may be copied into source
control, issue comments, general-purpose artifacts, or this repository unless
the approved data policy explicitly permits it.

## Readiness checks and stop rules

Before execution, the technical run owner records pass/fail evidence for:

- all required fields and signatures are complete;
- dataset membership and split policy are verified without inspecting
  unauthorized rows;
- code, route, model, prompt, scorer, repair, environment, and run manifest
  are frozen;
- privacy, access, retention, and incident controls are active;
- reviewer independence, blinding, adjudication, and audit-trail checks pass;
- dry-run/schema/trace checks pass on approved non-private fixtures; and
- the claim boundary and planned report are approved by the data owner and
  independent clinical reviewer.

| Check | Status | Evidence/reference | Owner | Date |
| --- | --- | --- | --- | --- |
| Required fields and signatures complete | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |
| Dataset membership and split policy verified | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |
| Technical configuration and run manifest frozen | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |
| Privacy, access, retention, and incident controls active | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |
| Reviewer independence, blinding, and adjudication ready | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |
| Dry-run, schema, and trace checks pass on fixtures | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |
| Claim boundary and report plan approved | `NOT CHECKED` | `[REQUIRED: reference]` | `[REQUIRED]` | `[REQUIRED]` |

Every `NOT CHECKED`, `BLOCKED`, or blank status blocks execution.

**Stop immediately** and set the state to `BLOCKED` if any required field is
blank, authorization expires, dataset membership is uncertain, an unauthorized
row is accessed, privacy controls fail, a technical configuration drifts, raw
outputs cannot be retained, reviewer independence is compromised, a clinical
safety concern is identified, or the observed data require an unplanned
semantic rule or scoring change. Preserve the audit trail; do not resume until
the record is amended and re-signed, or a new record is opened.

## Claim boundary and sign-off

- **Permitted claim:** `[REQUIRED: the exact research-validation claim and population/split]`
- **Explicitly excluded claims:** `[REQUIRED: clinical validity, clinical utility, deployment, generalization, or other exclusions]`
- **Reporting owner:** `[REQUIRED: person and destination]`
- **Data-owner sign-off:** `[REQUIRED: name, date, decision: APPROVED/BLOCKED]`
- **Technical run-owner sign-off:** `[REQUIRED: name, date, decision: APPROVED/BLOCKED]`
- **Independent clinical-reviewer sign-off:** `[REQUIRED: name, credentials, date, decision: APPROVED/BLOCKED]`
- **Final readiness decision:** `[REQUIRED: READY/BLOCKED, approver, date]`

The only executable state is `READY`. `UNSIGNED`, `NOT READY`, and `BLOCKED`
are non-executable states. Results must be reported as research validation
within the approved claim boundary and must not be described as clinical
deployment or clinical validity.
