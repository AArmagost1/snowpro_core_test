"""
Extract questions from text file (not PDF)
Works with snowpro_raw.txt
"""

import re
import json
from pathlib import Path


def parse_answer_key(text):
    """Extract answer key from the text."""
    answers = {}
    
    # Find the "Answers" section
    answer_section_match = re.search(r'\nAnswers\s*\n(.+)', text, re.DOTALL)
    if not answer_section_match:
        print("Warning: Could not find Answers section")
        return answers
    
    answer_text = answer_section_match.group(1)
    
    # Parse each line like "q1 b", "q32 abd", etc.
    for line in answer_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Match "q<number> <letters>"
        match = re.match(r'q(\d+)\s+([a-f]+)', line, re.IGNORECASE)
        if match:
            qnum = int(match.group(1))
            letters = [c.upper() for c in match.group(2)]
            answers[qnum] = letters
    
    return answers


def extract_questions(text, answers_dict):
    """Extract all questions from the text."""
    questions = []
    
    # Split by "Question #<number>"
    parts = re.split(r'Question #(\d+)', text)
    
    print(f"Found {len(parts)//2} potential question blocks")
    
    # Process each question
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
        
        qnum = int(parts[i])
        content = parts[i + 1]
        
        # Stop if we hit the Answers section
        if content.strip().startswith('Answers'):
            break
        
        q_obj = parse_question(qnum, content, answers_dict)
        if q_obj:
            questions.append(q_obj)
            if len(questions) % 50 == 0:
                print(f"  Extracted {len(questions)} questions...")
    
    return questions


def parse_question(qnum, content, answers_dict):
    """Parse a single question."""
    
    # Remove "Topic X" header
    content = re.sub(r'^\s*Topic\s+\d+\s+', '', content, flags=re.MULTILINE)
    
    # Find where options start (look for \nA. or \nA: or \nA )
    option_start = re.search(r'\n\s*A[\.\:\s]', content)
    
    if not option_start:
        return None
    
    # Split question and options
    question_text = content[:option_start.start()].strip()
    options_text = content[option_start.start():]
    
    # Clean question text
    question_text = re.sub(r'\s+', ' ', question_text)
    question_text = question_text.replace('\n', ' ')
    
    # Extract options
    options = {}
    
    # Split by option letters A-F
    option_parts = re.split(r'\n\s*([A-F])[\.\:\s]+', '\n' + options_text)
    
    current_letter = None
    for j, part in enumerate(option_parts):
        if j == 0:
            continue
        
        if j % 2 == 1:  # This is a letter
            current_letter = part
        else:  # This is the option text
            if current_letter:
                text = part.strip()
                # Stop at next option or question
                text = re.split(r'\n\s*[A-F][\.\:]', text)[0]
                text = re.sub(r'\s+', ' ', text).strip()
                options[current_letter] = text
    
    # Count options
    n_choices = sum(1 for k, v in options.items() if v and k in 'ABCDEF')
    
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
    """Main extraction function."""
    
    # Try to read from text file first
    text_file = Path("snowpro_raw.txt")
    
    if not text_file.exists():
        print("Error: snowpro_raw.txt not found!")
        print("\nPlease create this file by:")
        print("1. Open 'SnowPro Core Test Prep.pdf'")
        print("2. Select All (Cmd+A)")
        print("3. Copy (Cmd+C)")
        print("4. Create 'snowpro_raw.txt' and paste the content")
        print("5. Run this script again")
        return
    
    print("Reading snowpro_raw.txt...")
    with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    print(f"Read {len(text):,} characters")
    
    print("\nParsing answer key...")
    answers_dict = parse_answer_key(text)
    print(f"Found {len(answers_dict)} answers")
    
    print("\nExtracting questions...")
    questions = extract_questions(text, answers_dict)
    print(f"Extracted {len(questions)} questions")
    
    if len(questions) == 0:
        print("\n⚠️  No questions found!")
        print("The text file might not be formatted correctly.")
        print("Make sure it contains the full PDF text including 'Question #' markers")
        return
    
    # Sort by question number
    questions.sort(key=lambda x: x['qnum'])
    
    # Backup existing file
    existing = Path("snowpro_questions.json")
    if existing.exists():
        backup = Path("snowpro_questions_backup.json")
        print(f"\nBacking up existing file to {backup}")
        import shutil
        shutil.copy(existing, backup)
    
    # Save new file
    output_file = Path("snowpro_questions.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved {len(questions)} questions to {output_file}")
    
    # Statistics
    with_answers = sum(1 for q in questions if q.get('correct'))
    multi_choice = sum(1 for q in questions if q.get('correct') and len(q.get('correct', [])) > 1)
    
    print(f"\nStatistics:")
    print(f"  Total questions: {len(questions)}")
    print(f"  With answers: {with_answers}")
    print(f"  Without answers: {len(questions) - with_answers}")
    print(f"  Multi-choice: {multi_choice}")
    
    # Show range
    if questions:
        print(f"\nQuestion range: Q{questions[0]['qnum']} to Q{questions[-1]['qnum']}")


if __name__ == "__main__":
    main()