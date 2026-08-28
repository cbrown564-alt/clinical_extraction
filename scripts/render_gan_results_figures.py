#!/usr/bin/env python3
"""Render the living Gan results figures."""

from __future__ import annotations

import json

from clinical_extraction.paper.gan_result_figures import render_living_figures


def main() -> None:
    print(json.dumps(render_living_figures(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
