# Clinical-findings model contract

The endpoint receives this system instruction:

> Read one clinical letter and return one JSON object with a clinical_events
> list. Do not include markdown or hidden reasoning.

The user message is the JSON produced in `pipeline.py` by the selected full
one-call ExECT prompt builder. It asks for Diagnosis, Seizure Frequency,
Prescription, and Investigations events. The model call stays separate from the
Gan-derived current seizure-frequency call.

