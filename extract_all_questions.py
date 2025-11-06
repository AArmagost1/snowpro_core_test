"""
Complete SnowPro Core Question Extractor
Extracts all 400+ questions from the PDF text and creates a complete JSON file.

Usage:
    python extract_all_questions.py
"""

import re
import json
from pathlib import Path


def parse_answer_key(text):
    """Parse the answer key section into a dictionary."""
    answers = {}
    
    # Find answers section - it starts with "Answers" and has lines like "q1 b"
    lines = text.split('\n')
    in_answers = False
    
    for line in lines:
        line = line.strip()
        
        if line == "Answers":
            in_answers = True
            continue
        
        if not in_answers:
            continue
        
        # Match pattern: q<number> <letters> (optional: - <url>)
        match = re.match(r'^q(\d+)\s+([a-f]+)', line, re.IGNORECASE)
        if match:
            qnum = int(match.group(1))
            answer_chars = [c.upper() for c in match.group(2)]
            answers[qnum] = answer_chars
    
    return answers


def extract_all_questions(text, answers_dict):
    """Extract all questions from the PDF text."""
    questions = []
    
    # Pattern to match "Question #<number> Topic"
    question_pattern = r'Question #(\d+)'
    
    # Split by question markers
    parts = re.split(question_pattern, text)
    
    # Process pairs (qnum, content)
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
        
        qnum = int(parts[i])
        content = parts[i + 1]
        
        # Stop if we hit the answers section
        if 'Answers' in content and content.index('Answers') < 100:
            break
        
        try:
            q_obj = parse_single_question(qnum, content, answers_dict)
            if q_obj:
                questions.append(q_obj)
        except Exception as e:
            print(f"Warning: Error parsing Q{qnum}: {e}")
    
    return sorted(questions, key=lambda x: x['qnum'])


def parse_single_question(qnum, content, answers_dict):
    """Parse a single question block into structured data."""
    
    # Remove "Topic X" prefix
    content = re.sub(r'^[\s\n]*Topic\s+\d+[\s\n]+', '', content)
    
    # Find where answer options start
    # Look for "\nA." or "\nA:" or "\nA "
    option_match = re.search(r'\n\s*A[\.\:\s]', content)
    
    if not option_match:
        return None
    
    # Split into question text and options
    q_text = content[:option_match.start()].strip()
    options_section = content[option_match.start():]
    
    # Clean question text
    q_text = ' '.join(q_text.split())  # Normalize whitespace
    
    # Extract options A-F
    options = {}
    
    # Find all option markers
    option_pattern = r'\n\s*([A-F])[\.\:\s]+'
    option_matches = list(re.finditer(option_pattern, '\n' + options_section))
    
    for idx, match in enumerate(option_matches):
        letter = match.group(1)
        start = match.end()
        
        # Find where this option ends (at next option or end of string)
        if idx + 1 < len(option_matches):
            end = option_matches[idx + 1].start()
        else:
            end = len('\n' + options_section)
        
        option_text = ('\n' + options_section)[start:end].strip()
        
        # Clean the option text
        option_text = ' '.join(option_text.split())
        
        # Remove trailing content that looks like next options
        option_text = re.sub(r'\s+[A-F][\.\:].*$', '', option_text)
        
        options[letter] = option_text
    
    # Count non-empty options
    n_choices = sum(1 for v in options.values() if v)
    
    # Build result object
    result = {
        "qnum": qnum,
        "question": q_text,
        "A": options.get('A', ''),
        "B": options.get('B', ''),
        "C": options.get('C', ''),
        "D": options.get('D', ''),
        "E": options.get('E', ''),
        "correct": answers_dict.get(qnum),
        "n_choices": n_choices
    }
    
    # Add F if present
    if options.get('F'):
        result['F'] = options['F']
    
    return result


def main():
    """Main extraction function."""
    
    # Read the PDF text file
    pdf_path = Path("SnowPro Core Test Prep.pdf")
    
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        print("\nMake sure the PDF file is in the current directory.")
        return
    
    print(f"Reading {pdf_path}...")
    
    # Read the content
    # Note: For actual PDF reading, you'd use PyPDF2 or similar
    # Since you provided the text, we'll work with that
    with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
        pdf_text = f.read()
    
    print("Parsing answer key...")
    answers_dict = parse_answer_key(pdf_text)
    print(f"  Found {len(answers_dict)} answers")
    
    print("Extracting questions...")
    questions = extract_all_questions(pdf_text, answers_dict)
    print(f"  Extracted {len(questions)} questions")
    
    # Save to JSON
    output_path = Path("snowpro_questions.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved to {output_path}")
    
    # Statistics
    with_answers = sum(1 for q in questions if q['correct'])
    multi_choice = sum(1 for q in questions if q['correct'] and len(q['correct']) > 1)
    
    print(f"\nStatistics:")
    print(f"  Total questions: {len(questions)}")
    print(f"  With answers: {with_answers}")
    print(f"  Single answer: {with_answers - multi_choice}")
    print(f"  Multiple answer: {multi_choice}")
    
    # Show samples
    if questions:
        print(f"\nFirst question:")
        print(f"  Q{questions[0]['qnum']}: {questions[0]['question'][:80]}...")
        print(f"  Answer: {questions[0]['correct']}")
        
        print(f"\nLast question:")
        print(f"  Q{questions[-1]['qnum']}: {questions[-1]['question'][:80]}...")
        print(f"  Answer: {questions[-1]['correct']}")


if __name__ == "__main__":
    main()