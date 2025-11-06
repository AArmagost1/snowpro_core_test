
import json
from pathlib import Path
import random
from typing import List, Dict, Tuple
import streamlit as st
import pandas as pd

# Optional PDF generation for review sheet
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

DATA_PATH = Path(__file__).parent / "snowpro_questions.json"

@st.cache_data
def load_data() -> pd.DataFrame:
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    def norm(x):
        if x is None:
            return []
        if isinstance(x, list):
            return [str(y).upper() for y in x]
        if isinstance(x, str):
            return [c for c in x.upper() if c in "ABCDE"]
        return []
    df["correct"] = df["correct"].apply(norm)
    return df.sort_values("qnum").reset_index(drop=True)

def to_labels(selected: List[str]) -> List[str]:
    labs = []
    for s in selected:
        if isinstance(s, str) and len(s) > 1 and s[1] == ".":
            labs.append(s[0].upper())
    return labs

def verdict(selected_labels: List[str], correct_labels: List[str]) -> bool:
    return sorted(selected_labels) == sorted(correct_labels)

def spaced_priority(history: Dict[str, Dict]) -> int:
    """Small Leitner-like boxes: 0 (new), 1 (wrong last), 2 (right once), 3+ (mastered). Lower = higher priority."""
    box = history.get("box", 0)
    last_ok = history.get("last_ok", None)
    if last_ok is False:
        return 0
    return max(1, 5 - int(box))

def build_spaced_order(df: pd.DataFrame) -> pd.DataFrame:
    results = st.session_state.get("results", {})
    # Build a priority value per question
    priorities = []
    for q in df.itertuples(index=False):
        hist = results.get(int(q.qnum), {})
        prio = spaced_priority(hist)
        priorities.append((int(q.qnum), prio))
    priomap = dict(priorities)
    df2 = df.copy()
    df2["priority"] = df2["qnum"].map(priomap).fillna(3)
    return df2.sort_values(["priority","qnum"])

def score_report(df_all: pd.DataFrame):
    results = st.session_state.get("results", {})
    attempted = len(results)
    correct = sum(1 for r in results.values() if r.get("correct"))
    acc = (correct / attempted * 100) if attempted else 0.0

    st.subheader("Score Report")
    c1, c2, c3 = st.columns(3)
    c1.metric("Attempted", attempted)
    c2.metric("Correct", correct)
    c3.metric("Accuracy", f"{acc:.1f}%")

    if attempted:
        # Most missed
        wrong_rows = []
        for q in df_all.itertuples(index=False):
            qn = int(q.qnum)
            r  = results.get(qn)
            if r and not r.get("correct"):
                wrong_rows.append({
                    "qnum": qn,
                    "question": q.question,
                    "answer": ",".join(r.get("answer", [])),
                    "your": ",".join(r.get("selected", [])),
                })
        if wrong_rows:
            st.markdown("#### Most Recent Incorrect")
            st.dataframe(pd.DataFrame(wrong_rows).sort_values("qnum"))

def make_review_pdf(rows: pd.DataFrame) -> bytes:
    """Create a simple PDF containing missed questions and answers. Requires reportlab."""
    from io import BytesIO
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 0.75 * inch
    x = margin
    y = height - margin
    def write_line(txt, leading=14):
        nonlocal y
        lines = []
        # wrap manually at ~95 chars
        while len(txt) > 0:
            if len(txt) <= 95:
                lines.append(txt)
                break
            cut = txt.rfind(" ", 0, 95)
            if cut <= 0:
                cut = 95
            lines.append(txt[:cut])
            txt = txt[cut:].lstrip()
        for ln in lines:
            c.drawString(x, y, ln)
            y -= leading
            if y < margin:
                c.showPage()
                y = height - margin
    c.setFont("Helvetica", 12)
    write_line("SnowPro Core — Review Sheet")
    y -= 10
    for r in rows.itertuples(index=False):
        y -= 6
        write_line(f"Q{int(r.qnum)}: {r.question}")
        for lab in ["A","B","C","D","E"]:
            opt = getattr(r, lab)
            if isinstance(opt, str) and opt.strip():
                write_line(f"  {lab}. {opt}")
        write_line(f"Answer: {','.join(r.correct)}")
        y -= 6
        if y < margin:
            c.showPage()
            y = height - margin
    c.save()
    buffer.seek(0)
    return buffer.read()

def display_question(row: pd.Series, idx: int, mode: str):
    st.subheader(f"Q{int(row.qnum)}")
    st.write(row.question)
    options = []
    labels = ["A","B","C","D","E"]
    for lab in labels:
        txt = str(row.get(lab, "") or "").strip()
        if txt:
            options.append(f"{lab}. {txt}")
    key = f"sel_{int(row.qnum)}_{idx}_{mode}"
    multiselect = len(row["correct"]) > 1
    if multiselect:
        chosen = st.multiselect("Select all that apply:", options, key=key)
    else:
        chosen = st.radio("Choose one:", options, key=key, index=None)
        chosen = [chosen] if chosen else []
    return chosen

def main():
    st.set_page_config(page_title="SnowPro Core Study Helper", layout="wide")
    st.title("❄️ SnowPro Core Study Helper")
    st.caption("Full bank with Score Report, Spaced Repetition, and Review Sheet export.")

    df_all = load_data()
    total = len(df_all)

    mode = st.sidebar.radio("Mode", ["Practice", "Spaced Repetition", "Score Report"], index=0)

    if "results" not in st.session_state:
        st.session_state["results"] = {}  # qnum -> {"correct": bool, "selected": List[str], "answer": List[str], "box": int, "last_ok": bool}

    results = st.session_state["results"]

    if mode == "Score Report":
        score_report(df_all)
        st.markdown("---")
        # Export missed questions
        wrong = df_all[df_all["qnum"].isin([q for q,v in results.items() if not v.get("correct", False)])]
        if len(wrong):
            st.subheader("Export Review Sheet")
            if REPORTLAB_AVAILABLE:
                if st.button("Generate PDF of missed questions"):
                    pdf_bytes = make_review_pdf(wrong)
                    st.download_button("Download review_sheet.pdf", data=pdf_bytes, file_name="review_sheet.pdf", mime="application/pdf")
            else:
                st.info("To export as PDF, please install ReportLab: `pip install reportlab` and restart the app.")
        return

    # Shared filters
    multi_mask = df_all["correct"].apply(lambda xs: len(xs) > 1)
    filter_mode = st.sidebar.radio("Question type", ["All", "Single-answer only", "Multi-answer only"], index=0)
    df = df_all.copy()
    if filter_mode == "Single-answer only":
        df = df[~multi_mask]
    elif filter_mode == "Multi-answer only":
        df = df[multi_mask]

    qmin, qmax = int(df["qnum"].min()), int(df["qnum"].max())
    rmin, rmax = st.sidebar.slider("Question # range", min_value=qmin, max_value=qmax, value=(qmin, qmax))

    df = df[(df["qnum"] >= rmin) & (df["qnum"] <= rmax)]
    order = st.sidebar.radio("Order", ["Ascending", "Random"], index=0)

    if mode == "Spaced Repetition":
        df = build_spaced_order(df)
    else:
        if order == "Random":
            df = df.sample(frac=1, random_state=st.session_state.get("seed", 42))
        else:
            df = df.sort_values("qnum")

    # Progress header
    attempted = len(results)
    correct_count = sum(1 for v in results.values() if v.get("correct", False))
    col1, col2, col3 = st.columns(3)
    col1.metric("Questions in view", len(df))
    col2.metric("Attempted (all-time)", attempted)
    col3.metric("Correct (all-time)", correct_count)

    show_answers = st.sidebar.checkbox("Show answers immediately", value=True)
    review_only   = st.sidebar.checkbox("Review incorrect only", value=False)
    if review_only:
        bad_ids = [q for q, res in results.items() if not res.get("correct", False)]
        df = df[df["qnum"].isin(bad_ids)]

    # Render loop
    for idx, row in df.reset_index(drop=True).iterrows():
        selected = display_question(row, idx, mode)
        selected_labs = to_labels(selected)
        btn = st.button(f"Check Q{int(row.qnum)}", key=f"btn_{int(row.qnum)}_{mode}")
        if btn:
            ok = verdict(selected_labs, row["correct"])
            hist = results.get(int(row.qnum), {"box":0})
            # Update Leitner box
            if ok:
                hist["box"] = min(hist.get("box", 0) + 1, 5)
            else:
                hist["box"] = max(hist.get("box", 0) - 1, 0)
            hist["last_ok"] = ok
            hist["correct"] = ok
            hist["selected"] = selected_labs
            hist["answer"] = row["correct"]
            results[int(row.qnum)] = hist

        # Feedback
        if show_answers or int(row.qnum) in results:
            res = results.get(int(row.qnum))
            if res:
                ok = res["correct"]
                if ok:
                    st.success(f"✅ Correct. Answer: {', '.join(res['answer'])}")
                else:
                    st.error(f"❌ Incorrect. Your pick: {', '.join(res['selected']) or '—'} | Answer: {', '.join(res['answer'])}")
            else:
                ok = verdict(selected_labs, row['correct'])
                if selected_labs:
                    if ok:
                        st.success(f"✅ Correct. Answer: {', '.join(row['correct'])}")
                    else:
                        st.info(f"Answer: {', '.join(row['correct'])}")
            st.markdown('---')

    st.sidebar.markdown("---")
    if st.sidebar.button("Reset history (local)"):
        st.session_state["results"] = {}
        st.experimental_rerun()

    st.markdown("---")
    st.caption("SnowPro Core Study Helper • Generated for personal exam prep use.")

if __name__ == "__main__":
    main()
