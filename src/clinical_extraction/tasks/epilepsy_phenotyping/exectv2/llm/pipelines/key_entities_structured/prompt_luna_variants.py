"""Luna-only ExECT prompt instruction blocks for controlled A/B/C studies.

These candidates keep the frozen v0.9.24 schema and joint repair stack. Extra
text is intentional for the prompt-shape experiment. Keep experiment names,
gold labels, residual taxonomy, and scoring language out of the model-facing
strings.
"""

from __future__ import annotations

# Variant B: competing seizure-frequency states and countable rate sets.
LUNA_SF_STATE_GUIDANCE: tuple[str, ...] = (
    (
        "For seizure frequency, emit every current state the letter clearly "
        "supports, and only those states. Common states are an active rate, "
        "seizure-free, changed, and unknown."
    ),
    (
        "If the letter gives a current or recent countable rate, keep that "
        "active-rate mention. Do not also invent a seizure-free mention unless "
        "the letter clearly says the patient is now seizure-free."
    ),
    (
        "If the letter leaves the current frequency only partly clear, keep an "
        "unknown mention together with any supported active-rate or "
        "seizure-free mention. Do not drop unknown only to make the set look "
        "complete."
    ),
    (
        "When several seizure types have their own rates, keep the types the "
        "letter supports. Do not add a sibling seizure type or drop a stated "
        "type to simplify the set."
    ),
    (
        "Prefer a clear count over a stated period, such as once or twice a "
        "month or several per month, over vague control language when both "
        "describe the same current burden."
    ),
)

# Variant C: seizure-free / unknown boundaries plus light diagnosis specificity.
LUNA_SF_BOUNDARY_DX_GUIDANCE: tuple[str, ...] = (
    (
        "Do not mark seizure-free when the letter only describes a short quiet "
        "spell, improvement without a clear current state, or a single dated "
        "past event. Use unknown when the current frequency is not clear."
    ),
    (
        "Do not invent an active-rate mention beside seizure-free just because "
        "an older seizure date or prior event is named. Keep the older event "
        "out of the current frequency set unless the letter still treats it as "
        "current."
    ),
    (
        "If the letter supports both a current rate for one seizure type and "
        "uncertainty for another, keep both the active-rate and unknown "
        "mentions. Do not collapse the uncertain type into seizure-free."
    ),
    (
        "For diagnosis, prefer the most specific syndrome or seizure-type "
        "phrase the letter supports. Do not replace a specific phrase with a "
        "broader word such as epilepsy alone when the specific phrase is "
        "stated."
    ),
    (
        "Do not add an extra diagnosis phenotype that the letter does not "
        "authorize. If the letter names one diagnosis concept, do not also "
        "render a related but unstated sibling concept."
    ),
)
