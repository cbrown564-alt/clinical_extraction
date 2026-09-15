# Documentation ownership and retention

Updated: 2026-09-13. Current focus: the one-call paper.

The roadmap owns decisions and work order, the paper outline owns presentation,
and the evaluation protocol owns the study design. Annotation rules, annotation
review, schema decisions and execution records have separate owners after the
user-requested split on 2026-09-14. Navigation links these
owners; local PROJECT_STATUS.md records only current state and next actions.
Source/tests own implementation and result artifacts own measured outcomes.

Keep no more than 50 Markdown files under docs/, including generated references
and paused-prototype policies. Publication writing and frozen artifact README
files are outside that count; do not move obsolete prose there to evade it.
A new document should replace or consolidate an existing owner. The explicitly
requested 2026-09-14 protocol split is a scoped exception to the count limit; do not
remove unrelated retained documents merely to offset that split.

Retain a file only for current paper work, an executable dependency or interpretation
of preserved evidence. Recover superseded plans and historical study narratives
from Git instead of maintaining a second archive. Before deletion, verify committed
bytes, record the recovery revision/hash in the existing migration manifest and
repair current links. Never delete uncommitted user work or sole ignored copies.

Do not rewrite frozen outputs, manifests or scientific meaning while pruning.
Historical paths embedded in frozen artifacts remain historical identifiers; recover
the named original document for an audit. A historical report/validation tool that
requires removed prose needs those files restored before use. This does not
reactivate its experiment queue or authorise new calls.

Generated references change through their generator. Preserve their current drift
checks. Check documentation links and hygiene after edits; run relevant code tests
when executable dependencies change. Do not inspect sealed rows or run models merely
to maintain documentation.
