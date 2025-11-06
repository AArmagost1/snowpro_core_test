"""
Quick fixer to add missing answers to existing snowpro_questions.json
"""

import json
from pathlib import Path

# Missing answers from the PDF answer key
MISSING_ANSWERS = {
    278: ["D", "E", "F"],
    364: ["B", "D", "F"],
    368: ["B", "F"],
    373: ["C", "E", "F"],
    # 353 is intentionally left without answer (debated in community)
}

def fix_json():
    """Fix the existing JSON file with missing answers."""
    
    json_path = Path("snowpro_questions.json")
    
    if not json_path.exists():
        print("Error: snowpro_questions.json not found!")
        return
    
    # Load existing data
    with open(json_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    print(f"Loaded {len(questions)} questions")
    
    # Fix missing answers
    fixed_count = 0
    for q in questions:
        qnum = q['qnum']
        if qnum in MISSING_ANSWERS and q.get('correct') is None:
            q['correct'] = MISSING_ANSWERS[qnum]
            fixed_count += 1
            print(f"  Fixed Q{qnum}: {MISSING_ANSWERS[qnum]}")
    
    # Save back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Fixed {fixed_count} questions")
    print(f"✓ Saved to {json_path}")
    
    # Statistics
    total = len(questions)
    with_answers = sum(1 for q in questions if q.get('correct'))
    without = total - with_answers
    
    print(f"\nStatistics:")
    print(f"  Total: {total}")
    print(f"  With answers: {with_answers}")
    print(f"  Without answers: {without}")
    
    if without > 0:
        missing = [q['qnum'] for q in questions if not q.get('correct')]
        print(f"  Missing answer for: {missing}")


if __name__ == "__main__":
    fix_json()