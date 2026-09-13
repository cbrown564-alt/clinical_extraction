# Luna ExECT prompt-variant A/B/C test60 panel

Generated: 2026-07-31T07:54:27.961753+00:00
Readout: aggregate-only
Protocol: [exectv2_luna_prompt_variants_test60_protocol_2026-07-31.md](exectv2_luna_prompt_variants_test60_protocol_2026-07-31.md)

## Results

| Variant | Overall F1 (default repair) | SF F1 | SF model-owned correct | SF final correct | Dx final correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| A_v0924_control | 0.7950 | 0.5693 | 23/59 | 23/59 | 35/59 |
| B_luna_sf_state | 0.8030 | 0.6061 | 26/59 | 26/59 | 34/59 |
| C_luna_sf_boundary_dx | 0.8030 | 0.6260 | 28/59 | 28/59 | 33/59 |

## Deltas versus A

| Variant | Δ overall F1 | Δ SF F1 | Δ SF model-owned | Δ SF final | Δ Dx final |
| --- | ---: | ---: | ---: | ---: | ---: |
| B_luna_sf_state | +0.0080 | +0.0368 | +3 | +3 | -1 |
| C_luna_sf_boundary_dx | +0.0080 | +0.0567 | +5 | +5 | -2 |

## Claim boundary

Aggregate-only Luna-versus-Luna test60 transfer evidence for the named prompts under default Diagnosis/Prescription repair (decision 0045); not clinical validation, row-level analysis, or a rewrite of the frozen six-model v0.9.24 panel.

No test-row identifiers, notes, predictions, or failure cases are reported.
