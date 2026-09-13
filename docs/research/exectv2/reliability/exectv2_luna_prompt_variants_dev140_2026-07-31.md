# ExECTv2 Luna prompt variants on `dev140`

Date: 2026-07-31
Status: development panel
Protocol: [exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md](exectv2_luna_prompt_variants_dev140_protocol_2026-07-31.md)

## Results

| Variant | Overall F1 (default repair) | SF model-owned correct | SF final correct | SF nonempty model-owned | B-target SF model-owned |
| --- | ---: | ---: | ---: | ---: | ---: |
| A_v0924_control | 0.8832 | 86 | 88 | 57/99 | 0/42 |
| B_luna_sf_state | 0.8871 | 88 | 94 | 59/99 | 6/42 |
| C_luna_sf_boundary_dx | 0.8839 | 90 | 93 | 61/99 | 8/42 |

## Deltas versus A

| Variant | Δ overall F1 | Δ SF model-owned | Δ SF final | Δ SF nonempty model-owned | Δ B-target SF | Δ Dx final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B_luna_sf_state | +0.0039 | +2 | +6 | +2 | +6 | +1 |
| C_luna_sf_boundary_dx | +0.0007 | +4 | +5 | +4 | +8 | -2 |

## Claim boundary

ExECTv2 Luna-versus-Luna development evidence on dev140 under frozen schema and default Diagnosis/Prescription repair (decision 0045). Not test60, clinical validation, or panel promotion.
