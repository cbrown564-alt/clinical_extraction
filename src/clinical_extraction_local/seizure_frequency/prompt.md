# Seizure-frequency model contract

The endpoint receives this system instruction:

> Extract seizure-frequency events and choose one current answer. Return
> exactly one JSON object with events and selection; no markdown.

The user message is the JSON produced in `pipeline.py` by the selected Gan v0.5
prompt builder. That JSON contains the full clinical note, task instructions,
the event fields, and the selection fields. The v0.5 payload is retained intact
for parity with the selected workflow; package and run metadata are not added to
it.

