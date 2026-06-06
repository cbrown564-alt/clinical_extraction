import sys
sys.stdout.reconfigure(encoding='utf-8')
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
import re

def clean_text(text: str) -> str:
    # First, repair unicode escapes
    def replace_x02(match: re.Match[str]) -> str:
        hex_suffix = match.group(1)
        val = int("2" + hex_suffix, 16)
        return chr(val)
    text = re.sub(r"\x02([0-9a-fA-F]{3});?", replace_x02, text)
    text = re.sub(r"\x02([0-9a-fA-F]{1});?", replace_x02, text)
    def replace_x00(match: re.Match[str]) -> str:
        hex_suffix = match.group(1)
        val = int(hex_suffix, 16)
        return chr(val)
    text = re.sub(r"\x00([0-9a-fA-F]{2});?", replace_x00, text)
    
    # Map \x00 to -
    text = text.replace("\x00", "-")
    
    corruptions = (
        ("\u2011", "-"),
        ("\u2013", "-"),
        ("\u2014", "-"),
        ("\x7f", "≈"),
        ("\x022", "≈"),
        ("\x1a", "“"),
        ("\x1b", "”"),
        ("\x1c", "“"),
        ("\x1d", "”"),
        ("\x1f", "'"),
        ("\x1e", "'"),
        ("‘", "'"),
        ("’", "'"),
        ("“", '"'),
        ("”", '"'),
        ("Ã‚Â·", ""),
        ("\t6", "-"),
        ("\t", " "),
    )
    for before, after in corruptions:
        text = text.replace(before, after)
    return text

def test_locate(note_text: str, evidence: str) -> bool:
    if not evidence:
        return False
    # Direct
    if evidence in note_text:
        return True
    
    evidence_clean = clean_text(evidence)
    note_clean = clean_text(note_text)
    
    if evidence_clean in note_clean:
        return True
        
    # Word based match, stripping non-alphanumeric punctuation from start/end of words
    parts = evidence_clean.split()
    if parts:
        # Build pattern where each word allows optional surrounding punctuation and flexible spacing
        pattern_parts = []
        for part in parts:
            # strip leading/trailing non-alphanumeric from the word
            stripped = part.strip(".,;:!?\"'()[]{}“”‘’≤≥≈-")
            if stripped:
                # match the word, allowing optional non-alphanumeric chars around it
                pattern_parts.append(r"[.,;:!?\"'()\[\]{}“”‘’≤≥≈-]*" + re.escape(stripped) + r"[.,;:!?\"'()\[\]{}“”‘’≤≥≈-]*")
            else:
                pattern_parts.append(re.escape(part))
        pattern = r"\s+".join(pattern_parts)
        try:
            match = re.search(pattern, note_text, flags=re.IGNORECASE)
            if match:
                return True
        except re.error:
            pass
            
    return False

def main():
    records = load_records_for_split("validation")
    records_by_idx = {r.source_row_index: r for r in records}
    
    with open("scratch/diagnostics.txt", "r", encoding="utf-8") as f:
        content = f.read()
        
    failed_blocks = content.split("----------------------------------------")
    resolved_count = 0
    total = 0
    for block in failed_blocks:
        if not block.strip():
            continue
        total += 1
        lines = block.strip().split("\n")
        row_idx = int(lines[0].split("Row ")[1].split()[0])
        text_to_find = eval(lines[1].split("Text: ")[1])
        
        record = records_by_idx[row_idx]
        note_text = record.note_text
        
        span = test_locate(note_text, text_to_find)
        print(f"Row {row_idx}: {'RESOLVED' if span else 'FAILED'}")
        if span:
            resolved_count += 1
            
    print(f"Resolved {resolved_count}/{total} of the previously failing cases")

if __name__ == "__main__":
    main()
