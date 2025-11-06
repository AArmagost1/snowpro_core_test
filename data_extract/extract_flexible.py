"""
Flexible extractor that handles different PDF text formats
"""

import re
import json
from pathlib import Path


def parse_answer_key(text):
    """Extract answer key - try multiple patterns."""
    answers = {}
    
    # Look for answer patterns
    patterns = [
        r'q(\d+)\s+([a-f]+)',  # q1 b
        r'Question\s+(\d+).*?answer[:\s]+([a-f]+)',  # Question 1 answer: b
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            qnum = int(match.group(1))
            letters = [c.upper() for c in match.group(2)]
            answers[qnum] = letters
    
    return answers


def find_question_markers(text):
    """Find all question number markers in the text."""
    
    # Try different patterns
    patterns = [
        r'Question\s*#(\d+)',  # Question #10
        r'Question\s+(\d+)',   # Question 10
        r'Q(\d+)[:\.]',        # Q10: or Q10.
        r'^(\d+)\.',           # Line starting with number
    ]
    
    all_matches = []
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
        if matches:
            print(f"  Pattern '{pattern}' found {len(matches)} matches")
            all_matches.extend([(m.group(1), m.start(), m.end()) for m in matches])
    
    # Remove duplicates and sort by position
    all_matches = list(set(all_matches))
    all_matches.sort(key=lambda x: x[1])
    
    return all_matches


def extract_questions_flexible(text, answers_dict):
    """Extract questions using flexible matching."""
    
    print("Searching for question markers...")
    markers = find_question_markers(text)
    
    if not markers:
        print("No question markers found!")
        return []
    
    print(f"Found {len(markers)} question markers")
    
    questions = []
    
    # Process each marker
    for i, (qnum_str, start, end) in enumerate(markers):
        qnum = int(qnum_str)
        
        # Get content between this marker and the next one
        if i + 1 < len(markers):
            content = text[end:markers[i+1][1]]
        else:
            content = text[end:]
        
        # Stop at answers section
        if 'Answers' in content[:100]:
            break
        
        q_obj = parse_question_flexible(qnum, content, answers_dict)
        if q_obj:
            questions.append(q_obj)
            
            if len(questions) % 50 == 0:
                print(f"  Extracted {len(questions)} questions...")
    
    return questions


def parse_question_flexible(qnum, content, answers_dict):
    """Parse question with flexible option detection."""
    
    # Remove common headers
    content = re.sub(r'Topic\s+\d+', '', content, flags=re.IGNORECASE)
    
    # Look for option markers (A, B, C, D, E, F)
    # Try multiple patterns
    option_patterns = [
        r'(?:^|\n)\s*([A-F])[\.\:]\s*(.+?)(?=\n\s*[A-F][\.\:]|\n\s*Question|\Z)',
        r'(?:^|\n)\s*([A-F])\s+(.+?)(?=\n\s*[A-F]\s|\n\s*Question|\Z)',
    ]
    
    options = {}
    question_text = content
    
    for pattern in option_patterns:
        matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
        for match in matches:
            letter = match.group(1)
            text = match.group(2).strip()
            text = re.sub(r'\s+', ' ', text)
            options[letter] = text
        
        if options:
            # Found options, extract question text
            first_option = re.search(r'\n\s*A[\.\:\s]', content)
            if first_option:
                question_text = content[:first_option.start()].strip()
            break
    
    # Clean question text
    question_text = re.sub(r'\s+', ' ', question_text)
    
    # If no options found, skip this question
    if not options:
        return None
    
    # Count options
    n_choices = len([k for k in 'ABCDEF' if options.get(k)])
    
    # Build result
    result = {
        "qnum": qnum,
        "question": question_text,
        "A": options.get('A', ''),
        "B": options.get('B', ''),
        "C": options.get('C', ''),
        "D": options.get('D', ''),
        "E": options.get('E', ''),
        "correct": answers_dict.get(qnum),
        "n_choices": n_choices
    }
    
    if options.get('F'):
        result['F'] = options['F']
    
    return result


def main():
    """Main extraction with debugging."""
    
    text_file = Path("snowpro_raw.txt")
    
    if not text_file.exists():
        print("Error: snowpro_raw.txt not found!")
        return
    
    print("Reading snowpro_raw.txt...")
    with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    print(f"Read {len(text):,} characters\n")
    
    # Show a sample of the text
    print("Sample of text (first 500 chars):")
    print("=" * 60)
    print(text[:500])
    print("=" * 60)
    print()
    
    print("Parsing answer key...")
    answers_dict = parse_answer_key(text)
    print(f"Found {len(answers_dict)} answers\n")
    
    print("Extracting questions...")
    questions = extract_questions_flexible(text, answers_dict)
    print(f"\nExtracted {len(questions)} questions")
    
    if len(questions) == 0:
        print("\n⚠️  Still no questions found!")
        print("\nLet's try manual text extraction:")
        print("1. Open 'SnowPro Core Test Prep.pdf' in Preview")
        print("2. Select All (Cmd+A)")
        print("3. Copy (Cmd+V)")
        print("4. Create new file 'snowpro_manual.txt'")
        print("5. Paste and save")
        print("6. Run: mv snowpro_manual.txt snowpro_raw.txt")
        print("7. Run this script again")
        return
    
    # Sort by question number
    questions.sort(key=lambda x: x['qnum'])
    
    # Backup existing
    existing = Path("snowpro_questions.json")
    if existing.exists():
        backup = Path("snowpro_questions_backup.json")
        print(f"\nBacking up to {backup}")
        import shutil
        shutil.copy(existing, backup)
    
    # Save
    output_file = Path("snowpro_questions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(questions)} questions to {output_file}")
    
    # Stats
    with_answers = sum(1 for q in questions if q.get('correct'))
    
    print(f"\nStatistics:")
    print(f"  Total: {len(questions)}")
    print(f"  With answers: {with_answers}")
    print(f"  Question range: Q{questions[0]['qnum']} to Q{questions[-1]['qnum']}")


if __name__ == "__main__":
    main()