
import json
from pathlib import Path
import random
from typing import List, Dict
import streamlit as st
import pandas as pd

DATA_PATH = Path(__file__).parent / "snowpro_questions.json"

@st.cache_data
def load_data() -> pd.DataFrame:
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Normalize "correct" into list[str]
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

def display_question(row: pd.Series, idx: int, multiselect: bool):
    st.subheader(f"Q{int(row.qnum)}")
    st.write(row.question)
    options = []
    labels = ["A","B","C","D","E"]
    for lab in labels:
        txt = str(row.get(lab, "") or "").strip()
        if txt:
            options.append(f"{lab}. {txt}")
    key = f"sel_{int(row.qnum)}_{idx}"
    if multiselect:
        chosen = st.multiselect("Select all that apply:", options, key=key)
    else:
        chosen = st.radio("Choose one:", options, key=key, index=None)
        chosen = [chosen] if chosen else []
    return chosen

def to_labels(selected: List[str]) -> List[str]:
    labs = []
    for s in selected:
        if isinstance(s, str) and len(s) > 1 and s[1] == ".":
            labs.append(s[0].upper())
    return labs

def verdict(selected_labels: List[str], correct_labels: List[str]) -> bool:
    return sorted(selected_labels) == sorted(correct_labels)

def render_footer():
    st.markdown("---")
    st.caption("SnowPro Core Study Helper • Generated for personal exam prep use.")

def main():
    st.set_page_config(page_title="SnowPro Core Study Helper", layout="wide")
    st.title("❄️ SnowPro Core Study Helper")
    st.caption("400-question practice bank with instant feedback, review list, and progress tracking (local).")

    df = load_data()
    total = len(df)
    st.sidebar.header("Filters")
    # Filter: single vs multi-answer, question range
    multi_mask = df["correct"].apply(lambda xs: len(xs) > 1)
    filter_mode = st.sidebar.radio("Question type", ["All", "Single-answer only", "Multi-answer only"], index=0)
    if filter_mode == "Single-answer only":
        df = df[~multi_mask]
    elif filter_mode == "Multi-answer only":
        df = df[multi_mask]

    qmin, qmax = int(df["qnum"].min()), int(df["qnum"].max())
    rmin, rmax = st.sidebar.slider("Question # range", min_value=qmin, max_value=qmax, value=(qmin, qmax))
    df = df[(df["qnum"] >= rmin) & (df["qnum"] <= rmax)]

    order = st.sidebar.radio("Order", ["Ascending", "Random"], index=0)
    if order == "Random":
        df = df.sample(frac=1, random_state=st.session_state.get("seed", 42))

    st.sidebar.markdown("---")
    show_answers = st.sidebar.checkbox("Show answers immediately", value=True)
    review_only   = st.sidebar.checkbox("Review incorrect only", value=False)

    # Session stores
    if "results" not in st.session_state:
        st.session_state["results"] = {}  # qnum -> {"correct": bool, "selected": List[str]}
    if "seed" not in st.session_state:
        st.session_state["seed"] = random.randint(0, 10_000)

    results = st.session_state["results"]

    # Review filter
    if review_only:
        bad_ids = [q for q, res in results.items() if not res.get("correct", False)]
        df = df[df["qnum"].isin(bad_ids)]

    # Empty edge case
    if len(df) == 0:
        st.info("No questions to show with the current filters.")
        render_footer()
        return

    # Progress header
    attempted = len(results)
    correct_count = sum(1 for v in results.values() if v.get("correct", False))
    col1, col2, col3 = st.columns(3)
    col1.metric("Questions in view", len(df))
    col2.metric("Attempted (all-time)", attempted)
    col3.metric("Correct (all-time)", correct_count)

    # Quiz rendering
    for idx, row in df.reset_index(drop=True).iterrows():
        correct_labs = row["correct"]
        multiselect = len(correct_labs) > 1
        selected = display_question(row, idx, multiselect)

        # Evaluate
        selected_labs = to_labels(selected)
        # Show "check" button per question
        btn = st.button(f"Check Q{int(row.qnum)}", key=f"btn_{int(row.qnum)}")
        if btn:
            ok = verdict(selected_labs, correct_labs)
            results[int(row.qnum)] = {"correct": ok, "selected": selected_labs, "answer": correct_labs}

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
                # If never checked but show_answers=True, compute on the fly
                ok = verdict(selected_labs, correct_labs)
                if selected_labs:
                    if ok:
                        st.success(f"✅ Correct. Answer: {', '.join(correct_labs)}")
                    else:
                        st.info(f"Answer: {', '.join(correct_labs)}")
            st.markdown("---")

    # Sidebar: export review list
    st.sidebar.markdown("---")
    if st.sidebar.button("Export incorrect as CSV"):
        wrong = []
        for q in df.itertuples(index=False):
            qn = int(q.qnum)
            res = results.get(qn)
            if res and not res.get("correct", False):
                wrong.append({
                    "qnum": qn,
                    "question": q.question,
                    "A": q.A, "B": q.B, "C": q.C, "D": q.D, "E": q.E,
                    "your": ",".join(res.get("selected", [])),
                    "answer": ",".join(res.get("answer", [])),
                })
        if wrong:
            wdf = pd.DataFrame(wrong).sort_values("qnum")
            csv = wdf.to_csv(index=False)
            st.sidebar.download_button("Download incorrect.csv", data=csv, file_name="incorrect.csv", mime="text/csv")
        else:
            st.sidebar.info("No incorrect answers to export.")

    render_footer()

if __name__ == "__main__":
    main()
