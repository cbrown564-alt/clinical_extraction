"""Export five-cell paper teaching fixtures for the frontend mock API."""

from clinical_extraction.architecture.export_teaching_cases import write_teaching_cases

if __name__ == "__main__":
    print(write_teaching_cases())
