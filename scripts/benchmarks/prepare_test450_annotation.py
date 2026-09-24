"""Build the source-only test450 annotation package under the locked guide.

.venv/bin/python -m scripts.benchmarks.prepare_test450_annotation
"""

from scripts.benchmarks.prepare_annotation_package import main

if __name__ == "__main__":
    main("test")
