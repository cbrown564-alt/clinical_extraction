# Current-stack replay sidecars

Stripped holdout inputs for no-call remasure. Promoted out of `scratch/` so
selected primary fills do not depend on a gitignored dump.

Each Gan row keeps `source_row_index`, `prompt_version`, `raw_output`, and
boolean comparison flags. Each ExECT row keeps `letter_id`, `prompt_version`,
and `structured_events`. Note text, gold, prompt payloads, and sealed rows
stay in `scratch/`.

These files are machine replay inputs. Do not browse them for holdout errors.
Public reports stay aggregate-only.

Rebuild from scratch, if those trees are still present:

```powershell
.venv\Scripts\python.exe scripts/promote_current_stack_sidecars.py
```

Then point `SOURCES.json` at the sidecar paths (already the living inventory).
