"""Standard-dictionary translation layer for the simplified single-GPT engine.

This module is the one deterministic place that translates *clinical facts* the
model has already extracted into *scoring-convention* surfaces: drug-name
mapping, dose-unit and frequency variants, diagnosis benchmark/CUIPhrase
convention repair, and the small set of SeizureFrequency benchmark rewrites.

Design contract:

- The prompt owns clinical extraction and selection (which findings exist).
- This module owns convention translation (how an existing finding's surface
  should read for scoring). It never invents clinical content from nothing
  except for the explicitly-bounded, dev-derived diagnosis residual additions,
  which are labelled ``benchmark_format`` exactly as in the v05 lens.

Functions operate on plain strings / mappings (not ``ClinicalFinding``) so the
dictionary is decoupled and unit-testable. Assembly lenses are thin wrappers
that call into here (see ``assembly/lenses.py``).

Provenance: the diagnosis convention/residual tables are migrated verbatim from
the v04/v05 ``DiagnosisConventionAliasLens`` / ``DiagnosisResidualBenchmarkLens``
logic; the SF rewrites come from the retired hybrid SF-union arbitration lane;
the prescription primitives mirror ``deterministic.all_entities``. Parity with
those sources is the floor and is guarded by tests.

Implementation is split across ``conventions/``; this module re-exports the
public API for backward compatibility.
"""

from __future__ import annotations

from .conventions import *  # noqa: F403
from .conventions import __all__ as _CONVENTIONS_ALL

__all__ = list(_CONVENTIONS_ALL)
