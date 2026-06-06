import json
from pathlib import Path
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.core.evidence import locate_evidence

def main():
    jsonl_path = Path("experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_context_v1_2026-06-06.jsonl")
    records = load_records_for_split("validation")
    records_by_idx = {r.source_row_index: r for r in records}
    
    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
                
    diagnostics = []
    for row in rows:
        source_row_index = row["source_row_index"]
        record = records_by_idx.get(source_row_index)
        if not record:
            continue
        note_text = record.note_text
        
        candidates = row["candidate_set"]["candidates"]
        for c in candidates:
            unresolved_source_ids = [sid for sid in c["source_ids"] if "unresolved" in sid]
            if unresolved_source_ids:
                text_to_find = c["evidence_span"]["text"]
                span = locate_evidence(note_text, text_to_find)
                if not span:
                    diagnostics.append(f"Row {source_row_index} failed to resolve text:")
                    diagnostics.append(f"  Text: {repr(text_to_find)}")
                    diagnostics.append(f"  Note: {repr(note_text)}")
                    diagnostics.append("-" * 40)
                    
    with open("scratch/diagnostics.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(diagnostics))
    print(f"Diagnostics written to scratch/diagnostics.txt, total remaining unresolved: {len(diagnostics)//4}")
                    
if __name__ == "__main__":
    main()
