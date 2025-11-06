# snowpro_core_test# ❄️ SnowPro Core Study Helper

An interactive study application for preparing for the Snowflake SnowPro Core Certification exam. Built with Python and Streamlit, featuring spaced repetition learning and comprehensive progress tracking.

## 🎯 Features

- **240+ Practice Questions** - Comprehensive question bank covering all SnowPro Core exam topics
- **Spaced Repetition Learning** - Intelligent algorithm prioritizes questions you got wrong for maximum retention
- **Multiple Study Modes**:
  - Practice Mode - Study questions in order or randomly
  - Spaced Repetition Mode - Focus on your weak areas with Leitner box system
  - Score Report - Track your progress and identify areas for improvement
- **Question Filtering**:
  - Filter by question number range
  - Filter by single-answer or multi-answer questions
  - Review incorrect answers only
- **Progress Tracking** - View accuracy, attempted questions, and detailed score reports
- **PDF Export** - Generate review sheets of missed questions for offline study

## 📋 Prerequisites

- Python 3.7+
- pip3

## 🚀 Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd snowpro_core_test
```

2. Install required packages:
```bash
pip3 install streamlit pandas
```

3. (Optional) For PDF export functionality:
```bash
pip3 install reportlab
```

## 💻 Usage

Start the study app:
```bash
streamlit run snowpro_app.py
```

Or:
```bash
python3 -m streamlit run snowpro_app.py
```

The app will open in your default web browser at `http://localhost:8501`

## 📚 Study Modes

### Practice Mode
- Study questions in ascending order or randomly
- Immediate feedback on answers
- Filter by question type or number range

### Spaced Repetition Mode
- Uses Leitner box algorithm to prioritize difficult questions
- Questions you miss appear more frequently
- Questions you master appear less often
- Optimal for long-term retention

### Score Report
- View overall accuracy and progress
- See all incorrect answers
- Export missed questions as PDF for review

## 📊 Question Topics Covered

- Snowflake Architecture & Core Concepts
- Virtual Warehouses & Compute
- Storage & Micro-partitions
- Data Loading & Unloading (COPY, Snowpipe)
- Time Travel & Fail-safe
- Clustering & Query Performance
- Security & Access Control (RBAC, Masking, Row Access Policies)
- Data Sharing & Marketplace
- Semi-structured Data (VARIANT, JSON, Parquet)
- Account Management & Resource Monitors
- Snowflake Editions & Features

## 🗂️ Project Structure

```
snowpro_core_test/
├── snowpro_app.py              # Main Streamlit application
├── snowpro_questions.json      # Question bank with answers
├── json_fixer.py              # Utility to fix missing answers
├── extract_from_text.py       # PDF text extraction utility
└── README.md                  # This file
```

## 🎓 Exam Preparation Tips

1. **Aim for 85%+ accuracy** before taking the real exam
2. **Focus on multi-answer questions** - they're more challenging and worth understanding deeply
3. **Use Spaced Repetition mode** consistently for best retention
4. **Review incorrect answers** regularly using the Score Report
5. **Understand concepts, not just memorization** - the exam tests application of knowledge

## 📝 Data Sources

Questions compiled from SnowPro Core certification study materials and practice tests. Answer key verified against official Snowflake documentation.

## 🛠️ Utilities

### Fix Missing Answers
```bash
python3 json_fixer.py
```

### Count Questions
```bash
python3 -c "import json; print(f'Total questions: {len(json.load(open(\"snowpro_questions.json\")))}')"
```

### Reset Progress
Click "Reset history (local)" in the sidebar of the app, or delete browser localStorage.

## 🤝 Contributing

Feel free to submit issues or pull requests if you find errors in questions or have suggestions for improvements.

## 📄 License

This project is for educational purposes only. Snowflake and SnowPro are trademarks of Snowflake Inc.

## ✨ Acknowledgments

Built for personal exam preparation. Good luck on your SnowPro Core certification! 🏔️

---

**Note**: This study tool is meant to supplement, not replace, official Snowflake training and documentation. Always refer to [official Snowflake documentation](https://docs.snowflake.com) for the most up-to-date information.