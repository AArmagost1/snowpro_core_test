"""
Build complete snowpro_questions.json with all 401 questions
Based on the PDF content provided
"""

import json
from pathlib import Path

# This will merge your existing 240 questions with the missing ones
# The missing question numbers from your current JSON

def get_answer_key():
    """Complete answer key from the PDF"""
    answers = {
        1: ["B"], 2: ["B", "D"], 3: ["B"], 4: ["B"], 5: ["A"], 6: ["A", "B", "C"],
        7: ["B"], 8: ["B"], 9: ["B", "D"], 10: ["A"], 11: ["B"], 12: ["C"],
        13: ["A", "B", "C", "E"], 14: ["B"], 15: ["A", "C"], 16: ["A", "C", "D"],
        17: ["D"], 18: ["B"], 19: ["A", "B", "C", "D", "E"], 20: ["B"],
        21: ["B", "C", "D"], 22: ["A"], 23: ["D"], 24: ["B"], 25: ["A"],
        26: ["A", "B", "C", "D"], 27: ["C", "D"], 28: ["A"], 29: ["D"], 30: ["A"],
        31: ["D"], 32: ["A", "B", "D"], 33: ["B"], 34: ["B"], 35: ["A"],
        36: ["B"], 37: ["A", "C", "D"], 38: ["A", "C"], 39: ["A"], 40: ["B", "D"],
        41: ["C"], 42: ["A"], 43: ["C"], 44: ["A", "B"], 45: ["B"],
        46: ["A", "C", "D"], 47: ["D"], 48: ["A", "C"], 49: ["A", "B", "C"],
        50: ["A"], 51: ["B"], 52: ["A", "C"], 53: ["B"], 54: ["D"],
        55: ["D"], 56: ["A", "B"], 57: ["A"], 58: ["D"], 59: ["B"], 60: ["C"],
        61: ["D"], 62: ["C"], 63: ["C", "D"], 64: ["B"], 65: ["A", "B"],
        66: ["D"], 67: ["A"], 68: ["B", "D"], 69: ["C", "D"], 70: ["D"],
        71: ["C"], 72: ["B"], 73: ["B"], 74: ["A"], 75: ["A", "B", "C", "D"],
        76: ["B", "C"], 77: ["A", "B", "C", "D"], 78: ["D"], 79: ["B"],
        80: ["A", "C"], 81: ["B", "D"], 82: ["D"], 83: ["B", "D", "E"],
        84: ["A"], 85: ["A"], 86: ["A"], 87: ["A"], 88: ["A"], 89: ["C"],
        90: ["A"], 91: ["B"], 92: None, 93: ["B"], 94: ["A"], 95: ["C"],
        96: ["D"], 97: ["C"], 98: ["B", "C"], 99: ["A"], 100: ["D"],
        101: ["C"], 102: ["B"], 103: ["B"], 104: ["D"], 105: ["B"],
        106: ["B"], 107: ["B"], 108: ["A"], 109: ["B"], 110: ["B"],
        111: ["B"], 112: ["A", "B"], 113: ["A", "C"], 114: ["B"], 115: ["B"],
        116: ["A"], 117: ["A", "B", "C", "D"], 118: ["A"], 119: ["A"],
        120: ["C"], 121: ["B", "C", "D"], 122: ["A"], 123: ["A"], 124: ["A"],
        125: ["B"], 126: ["B"], 127: ["A"], 128: ["B"], 129: ["B"], 130: ["B"],
        131: ["A", "C"], 132: ["B"], 133: ["A"], 134: ["B"], 135: ["A", "C", "D"],
        136: ["B"], 137: ["A", "E"], 138: ["B"], 139: ["A"], 140: ["B", "D"],
        141: ["A"], 142: ["D"], 143: ["D"], 144: ["C"], 145: ["C", "D"],
        146: ["C", "E"], 147: ["D"], 148: ["C"], 149: ["A"], 150: ["B", "C"],
        151: ["B", "C", "F"], 152: ["B", "C"], 153: ["C"], 154: ["B", "E"],
        155: ["B"], 156: ["A"], 157: ["B", "C", "D"], 158: ["C"], 159: ["A"],
        160: ["A"], 161: ["D", "E"], 162: ["B"], 163: ["A", "B", "D"],
        164: ["A"], 165: ["B"], 166: ["C"], 167: ["C"], 168: ["D"],
        169: ["C", "E"], 170: ["D"], 171: ["B", "D"], 172: ["B", "E"],
        173: ["B"], 174: ["D"], 175: ["B", "D"], 176: ["B"], 177: ["A"],
        178: ["A"], 179: ["C"], 180: ["D"], 181: ["A", "C"], 182: ["C", "D"],
        183: ["A", "D", "E"], 184: ["B"], 185: ["A"], 186: ["B"], 187: ["B"],
        188: ["A", "D"], 189: ["D"], 190: ["D", "E"], 191: ["C"], 192: ["C", "D"],
        193: ["D"], 194: ["B", "C"], 195: ["B"], 196: ["B"], 197: ["D"],
        198: ["C"], 199: ["C"], 200: ["C"], 201: ["B", "D"], 202: ["A"],
        203: ["A", "E"], 204: ["C"], 205: ["B", "E"], 206: ["C"], 207: ["D", "E"],
        208: ["B"], 209: ["D"], 210: ["C", "D"], 211: ["A", "D", "E"],
        212: ["D"], 213: ["D"], 214: ["B"], 215: ["C", "E"], 216: ["B"],
        217: ["B"], 218: ["A", "E"], 219: ["C", "E"], 220: ["A"], 221: ["D"],
        222: ["A"], 223: ["A", "D"], 224: ["A", "C"], 225: ["B"], 226: ["D"],
        227: ["D"], 228: ["A", "D"], 229: ["C", "D"], 230: ["D"], 231: ["D"],
        232: ["A"], 233: ["A", "D"], 234: ["A"], 235: ["B"], 236: ["B"],
        237: ["A", "B"], 238: ["B", "C"], 239: ["B"], 240: ["A"], 241: ["A", "C"],
        243: ["D", "E"], 244: ["A", "C"], 245: ["B"], 246: ["A", "D"],
        247: ["B"], 248: ["D"], 249: ["D"], 250: ["B"], 251: ["C", "D"],
        252: ["C"], 253: ["D"], 254: ["B"], 255: ["C"], 256: ["B"], 257: ["D"],
        258: ["D"], 259: ["A", "C"], 260: ["B", "C"], 261: ["C"], 262: ["B"],
        263: ["C"], 264: ["C"], 265: ["B"], 266: ["A"], 270: ["D"],
        271: ["A", "D"], 272: ["B", "E"], 273: ["B"], 274: ["B", "D"],
        275: ["D"], 276: ["C", "E"], 277: ["A"], 278: ["D", "E", "F"],
        279: ["D"], 280: ["B"], 281: ["D"], 282: ["D"], 283: ["B", "D"],
        284: ["A"], 285: ["D", "E"], 286: ["B"], 287: ["B"], 288: ["C", "E"],
        289: ["B"], 290: ["A", "D"], 291: ["B", "E"], 292: ["C"], 293: ["A"],
        294: ["B", "C"], 295: ["C"], 296: ["D"], 297: ["A", "C"],
        298: ["B", "C"], 299: ["C"], 300: ["A"], 301: ["A", "D"], 302: ["D"],
        303: ["D"], 304: ["C"], 305: ["A"], 306: ["C"], 307: ["C"],
        308: ["C", "D"], 309: ["C"], 310: ["A"], 311: ["C"], 312: ["A"],
        313: ["A"], 314: ["D", "E"], 315: ["D"], 316: ["A", "E"], 317: ["D"],
        318: ["A"], 319: ["C"], 320: ["C"], 321: ["B", "C"], 322: ["B", "E"],
        323: ["A"], 324: ["C"], 325: ["D"], 326: ["C"], 327: ["C", "D"],
        328: ["B", "E"], 329: ["A"], 330: ["A"], 331: ["D"], 332: ["A"],
        333: ["B"], 334: ["A"], 335: ["B"], 336: ["A"], 337: ["D"],
        338: ["B", "D"], 339: ["C"], 340: ["B"], 341: ["C"], 342: ["B"],
        343: ["C"], 344: ["D"], 345: ["B", "D"], 346: ["A"], 347: ["D"],
        348: ["C", "D"], 349: ["B", "C"], 350: ["B"], 351: ["D", "E"],
        352: ["C"], 353: None, 354: ["A"], 355: ["A"], 356: ["B", "D", "E"],
        357: ["D"], 358: ["C"], 359: ["C"], 360: ["A"], 361: ["B", "E"],
        362: ["C"], 363: ["B", "C", "E"], 364: ["B", "D", "F"], 365: ["D"],
        366: ["B", "D"], 367: ["A"], 368: ["B", "F"], 369: ["B", "D"],
        370: ["A"], 371: ["D"], 372: ["D"], 373: ["C", "E", "F"], 374: ["B"],
        375: ["A"], 376: ["C"], 377: ["A", "E"], 378: ["B", "D", "E"],
        379: ["C", "D"], 380: ["C", "D"], 381: ["D", "E"], 382: ["C"],
        383: ["B"], 384: ["A"], 385: ["D"], 386: ["D"], 387: ["B"], 388: ["A"],
        389: ["A"], 390: ["B"], 391: ["A"], 392: ["C"], 393: ["C", "E"],
        394: ["C"], 395: ["A"], 396: ["C", "E"], 397: ["A"], 398: ["B"],
        399: ["B"], 400: ["B", "C"], 401: ["D", "E"]
    }
    return answers


def main():
    """Update existing JSON with all answers"""
    
    json_path = Path("snowpro_questions.json")
    
    if not json_path.exists():
        print("Error: snowpro_questions.json not found!")
        return
    
    # Load existing questions
    with open(json_path, 'r') as f:
        questions = json.load(f)
    
    print(f"Current JSON has {len(questions)} questions")
    
    # Get complete answer key
    all_answers = get_answer_key()
    
    # Update answers for existing questions
    updated = 0
    for q in questions:
        qnum = q['qnum']
        if qnum in all_answers:
            if q.get('correct') != all_answers[qnum]:
                q['correct'] = all_answers[qnum]
                updated += 1
    
    print(f"Updated {updated} answers")
    
    # Find missing question numbers
    existing_qnums = {q['qnum'] for q in questions}
    all_qnums = set(all_answers.keys())
    missing_qnums = sorted(all_qnums - existing_qnums)
    
    if missing_qnums:
        print(f"\nMissing {len(missing_qnums)} questions:")
        print(f"  Question numbers: {missing_qnums[:20]}{'...' if len(missing_qnums) > 20 else ''}")
        print("\n⚠️  To get ALL questions, you need to:")
        print("  1. Use OCR software on the PDF")
        print("  2. Or manually type the missing questions")
        print("  3. Or request the text-based version of the PDF")
    
    # Save updated file
    backup_path = Path("snowpro_questions_backup.json")
    import shutil
    shutil.copy(json_path, backup_path)
    print(f"\nBacked up to {backup_path}")
    
    with open(json_path, 'w') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {json_path}")
    print(f"\nCurrent status:")
    print(f"  Total questions: {len(questions)}")
    print(f"  With answers: {sum(1 for q in questions if q.get('correct'))}")
    print(f"  Missing questions: {len(missing_qnums)}")


if __name__ == "__main__":
    main()