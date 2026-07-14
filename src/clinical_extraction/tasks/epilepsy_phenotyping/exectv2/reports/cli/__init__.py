"""Thin CLI entry points for ExECTv2 report builders.

Each module under this package owns the argparse plumbing and output writing for
exactly one report module under ``..reports``. The report modules themselves
expose only importable builder/render functions and define no ``main`` and no
``if __name__ == "__main__"`` block (policy gate P2-2: reports are importable
libraries, not CLI apps). Run a report with, e.g.::

    python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cli.\
deterministic_all9_scorecard
"""
