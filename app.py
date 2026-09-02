import streamlit as st
import pandas as pd
import random
import os
import time
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম",
    page_icon="📝",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

hide_streamlit_style = """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 3rem;
    max-width: 900px;
}

.question-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.result-box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.fixed-timer {
    position: fixed;
    top: 10px;
    right: 15px;
    background: white;
    padding: 10px 16px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    z-index: 9999;
    font-weight: bold;
    font-size: 18px;
}

.question-palette {
    background: white;
    padding: 15px;
    border-radius: 14px;
    margin-top: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.palette-info {
    text-align: center;
    font-size: 14px;
    margin-bottom: 10px;
}

@media (max-width: 600px) {

    .block-container {
        padding-left: 10px;
        padding-right: 10px;
    }

    .question-card {
        padding: 14px;
        border-radius: 12px;
    }

    .stButton button {
        width: 100%;
    }

    .fixed-timer {
        top: 7px;
        right: 8px;
        padding: 7px 11px;
        font-size: 15px;
    }

}

</style>
"""

st.markdown(
    hide_streamlit_style,
    unsafe_allow_html=True
)


# =========================================================
# FILE SETTINGS
# =========================================================

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"

ADMIN_PASSWORD = "1234"


# =========================================================
# SESSION STATE
# =========================================================

if "is_admin_logged_in" not in st.session_state:
    st.session_state.is_admin_logged_in = False

if "confirmed_student_name" not in st.session_state:
    st.session_state.confirmed_student_name = ""

if "exam_submitted" not in st.session_state:
    st.session_state.exam_submitted = False

if "last_result_data" not in st.session_state:
    st.session_state.last_result_data = None

if "selected_exam_subject" not in st.session_state:
    st.session_state.selected_exam_subject = None

if "exam_in_progress" not in st.session_state:
    st.session_state.exam_in_progress = False

if "exam_questions" not in st.session_state:
    st.session_state.exam_questions = []

if "exam_start_time" not in st.session_state:
    st.session_state.exam_start_time = None

if "exam_duration" not in st.session_state:
    st.session_state.exam_duration = 30

if "student_answers" not in st.session_state:
    st.session_state.student_answers = {}

if "current_question" not in st.session_state:
    st.session_state.current_question = 0


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def ensure_questions_file():

    if not os.path.exists(QUESTIONS_FILE):

        df = pd.DataFrame(columns=[
            "Subject",
            "Question",
            "Option A",
            "Option B",
            "Option C",
            "Option D",
            "Answer",
            "Explanation"
        ])

        df.to_csv(
            QUESTIONS_FILE,
            index=False,
            encoding="utf-8-sig"
        )


def ensure_results_file():

    if not os.path.exists(RESULT_FILE):

        df = pd.DataFrame(columns=[
            "Student Name",
            "Subject",
            "Score",
            "Total Marks",
            "Correct",
            "Wrong",
            "Unanswered",
            "Date"
        ])

        df.to_csv(
            RESULT_FILE,
            index=False,
            encoding="utf-8-sig"
        )


def ensure_config_file():

    if not os.path.exists(CONFIG_FILE):

        df = pd.DataFrame(columns=[
            "Subject",
            "Duration"
        ])

        df.to_csv(
            CONFIG_FILE,
            index=False,
            encoding="utf-8-sig"
        )


def load_questions():

    ensure_questions_file()

    try:
        return pd.read_csv(
            QUESTIONS_FILE,
            encoding="utf-8-sig"
        )
    except Exception:
        return pd.DataFrame()


def load_results():

    ensure_results_file()

    try:
        return pd.read_csv(
            RESULT_FILE,
            encoding="utf-8-sig"
        )
    except Exception:
        return pd.DataFrame()


def load_configs():

    ensure_config_file()

    try:
        return pd.read_csv(
            CONFIG_FILE,
            encoding="utf-8-sig"
        )
    except Exception:
        return pd.DataFrame()


def get_duration(subject):

    df = load_configs()

    if df.empty:
        return 30

    row = df[df["Subject"] == subject]

    if row.empty:
        return 30

    try:
        return int(row.iloc[0]["Duration"])
    except Exception:
        return 30


def save_duration(subject, duration):

    df = load_configs()

    df = df[df["Subject"] != subject]

    new_row = pd.DataFrame([{
        "Subject": subject,
        "Duration": duration
    }])

    df = pd.concat(
        [df, new_row],
        ignore_index=True
    )

    df.to_csv(
        CONFIG_FILE,
        index=False,
        encoding="utf-8-sig"
    )


def normalize_answer(answer):

    if pd.isna(answer):
        return ""

    answer = str(answer).strip()

    mapping = {
        "ক": "A",
        "খ": "B",
        "গ": "C",
        "ঘ": "D",

        "ক)": "A",
        "খ)": "B",
        "গ)": "C",
        "ঘ)": "D",

        "ক.": "A",
        "খ.": "B",
        "গ.": "C",
        "ঘ.": "D",

        "A": "A",
        "B": "B",
        "C": "C",
        "D": "D",

        "a": "A",
        "b": "B",
        "c": "C",
        "d": "D"
    }

    return mapping.get(answer, answer)


def answer_matches(correct_answer, selected_answer):

    if not selected_answer:
        return False

    correct = normalize_answer(correct_answer)
    selected = normalize_answer(selected_answer)

    if correct == selected:
        return True

    option_map = {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
    }

    if correct in option_map:

        if selected == option_map[correct]:
            return True

    return str(correct).strip().lower() == str(selected).strip().lower()


def parse_text_questions(text, subject):

    questions = []

    blocks = text.strip().split("\n\n")

    for block in blocks:

        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if len(lines) < 6:
            continue

        question = lines[0]

        option_a = lines[1]
        option_b = lines[2]
        option_c = lines[3]
        option_d = lines[4]

        answer = normalize_answer(lines[5])

        explanation = ""

        if len(lines) >= 7:
            explanation = lines[6]

        questions.append({
            "Subject": subject,
            "Question": question,
            "Option A": option_a,
            "Option B": option_b,
            "Option C": option_c,
            "Option D": option_d,
            "Answer": answer,
            "Explanation": explanation
        })

    return pd.DataFrame(questions)


def save_questions(df):

    ensure_questions_file()

    old_df = load_questions()

    final_df = pd.concat(
        [old_df, df],
        ignore_index=True
    )

    final_df.to_csv(
        QUESTIONS_FILE,
        index=False,
        encoding="utf-8-sig"
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div style="
        background:white;
        padding:25px 18px;
        border-radius:16px;
        text-align:center;
        margin-bottom:20px;
        box-shadow:0 2px 10px rgba(0,0,0,0.06);
    ">

    <h1 style="margin-bottom:8px;">
        📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম
    </h1>

    <p style="margin-bottom:5px;">
        বিসিএস, ব্যাংক, প্রাথমিক সহকারী শিক্ষক নিয়োগ,
        NTRCA সহ সকল সরকারি চাকরির প্রস্তুতি
    </p>

    <small>
        Powered by <b>Job Efforts</b>
    </small>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ADMIN LOGIN
# =========================================================

with st.sidebar:

    st.markdown("### 🔐 Admin")

    with st.expander("Admin Login"):

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            if password == ADMIN_PASSWORD:

                st.session_state.is_admin_logged_in = True

                st.success("Login successful")

                st.rerun()

            else:

                st.error("ভুল Password")


# =========================================================
# ADMIN PANEL
# =========================================================

if st.session_state.is_admin_logged_in:

    st.sidebar.markdown("---")

    admin_menu = st.sidebar.radio(
        "Admin Menu",
        [
            "📚 প্রশ্ন যোগ/সেটআপ",
            "📊 ফলাফল",
            "👀 প্রশ্ন দেখুন"
        ]
    )

    if admin_menu == "📚 প্রশ্ন যোগ/সেটআপ":

        st.header("📚 প্রশ্ন যোগ ও পরীক্ষা সেটআপ")

        subjects = [
            "বাংলা",
            "English",
            "গণিত",
            "বিজ্ঞান",
            "বাংলাদেশের বিষয়াবলি",
            "আন্তর্জাতিক বিষয়াবলি",
            "ICT"
        ]

        subject = st.selectbox(
            "বিষয় নির্বাচন করুন",
            subjects
        )

        duration = st.number_input(
            "পরীক্ষার সময় (মিনিট)",
            min_value=1,
            max_value=300,
            value=get_duration(subject)
        )

        if st.button("💾 সময় সংরক্ষণ করুন"):

            save_duration(
                subject,
                duration
            )

            st.success(
                "পরীক্ষার সময় সংরক্ষণ হয়েছে।"
            )

        st.markdown("---")

        upload_mode = st.radio(
            "প্রশ্ন যোগ করার পদ্ধতি",
            [
                "📝 Text Paste",
                "📊 Excel / CSV"
            ]
        )

        if upload_mode == "📝 Text Paste":

            st.info(
                "প্রতি প্রশ্নের জন্য ৭টি লাইন ব্যবহার করুন: "
                "প্রশ্ন, ৪টি অপশন, সঠিক উত্তর, ব্যাখ্যা। "
                "প্রশ্নগুলোর মাঝে একটি blank line দিন।"
            )

            text = st.text_area(
                "প্রশ্ন এখানে Paste করুন",
                height=350
            )

            if st.button("➕ প্রশ্ন যোগ করুন"):

                if not text.strip():

                    st.warning(
                        "প্রথমে প্রশ্ন দিন।"
                    )

                else:

                    new_df = parse_text_questions(
                        text,
                        subject
                    )

                    if new_df.empty:

                        st.error(
                            "প্রশ্নের format সঠিক নয়।"
                        )

                    else:

                        save_questions(new_df)

                        st.success(
                            f"{len(new_df)}টি প্রশ্ন যোগ হয়েছে।"
                        )

                        st.dataframe(
                            new_df,
                            use_container_width=True
                        )

        else:

            uploaded_file = st.file_uploader(
                "Excel অথবা CSV ফাইল আপলোড করুন",
                type=["xlsx", "csv"]
            )

            if uploaded_file:

                try:

                    if uploaded_file.name.endswith(".xlsx"):

                        excel_df = pd.read_excel(
                            uploaded_file
                        )

                    else:

                        excel_df = pd.read_csv(
                            uploaded_file
                        )

                    st.success(
                        f"{len(excel_df)}টি row পাওয়া গেছে।"
                    )

                    st.dataframe(
                        excel_df.head(20),
                        use_container_width=True
                    )

                    st.markdown("### Import Settings")

                    import_mode = st.radio(
                        "Import Mode",
                        [
                            "সব প্রশ্ন Import",
                            "Random Sample",
                            "Manual Selection"
                        ]
                    )

                    if import_mode == "Random Sample":

                        sample_size = st.number_input(
                            "কতটি প্রশ্ন নিতে চান?",
                            min_value=1,
                            max_value=max(
                                1,
                                len(excel_df)
                            ),
                            value=min(
                                20,
                                len(excel_df)
                            )
                        )

                    if import_mode == "Manual Selection":

                        selected_rows = st.multiselect(
                            "প্রশ্ন নির্বাচন করুন",
                            list(range(len(excel_df)))
                        )

                    if st.button(
                        "📥 Import Questions"
                    ):

                        df_to_import = excel_df.copy()

                        if import_mode == "Random Sample":

                            df_to_import = excel_df.sample(
                                n=int(sample_size)
                            )

                        elif import_mode == "Manual Selection":

                            if not selected_rows:

                                st.warning(
                                    "প্রশ্ন নির্বাচন করুন।"
                                )

                                st.stop()

                            df_to_import = excel_df.iloc[
                                selected_rows
                            ]

                        if len(df_to_import.columns) >= 6:

                            columns = list(
                                df_to_import.columns
                            )

                            converted = pd.DataFrame()

                            converted["Subject"] = subject

                            converted["Question"] = (
                                df_to_import[
                                    columns[0]
                                ]
                            )

                            converted["Option A"] = (
                                df_to_import[
                                    columns[1]
                                ]
                            )

                            converted["Option B"] = (
                                df_to_import[
                                    columns[2]
                                ]
                            )

                            converted["Option C"] = (
                                df_to_import[
                                    columns[3]
                                ]
                            )

                            converted["Option D"] = (
                                df_to_import[
                                    columns[4]
                                ]
                            )

                            converted["Answer"] = (
                                df_to_import[
                                    columns[5]
                                ].apply(
                                    normalize_answer
                                )
                            )

                            if len(columns) >= 7:

                                converted["Explanation"] = (
                                    df_to_import[
                                        columns[6]
                                    ]
                                )

                            else:

                                converted["Explanation"] = ""

                            save_questions(
                                converted
                            )

                            st.success(
                                f"{len(converted)}টি প্রশ্ন Import হয়েছে।"
                            )

                        else:

                            st.error(
                                "Excel/CSV-তে কমপক্ষে ৬টি column থাকতে হবে।"
                            )

        st.markdown("---")

        st.subheader("🗑️ প্রশ্ন মুছে ফেলুন")

        all_questions = load_questions()

        subject_questions = all_questions[
            all_questions["Subject"] == subject
        ]

        st.write(
            f"এই বিষয়ে মোট প্রশ্ন: "
            f"{len(subject_questions)}"
        )

        if st.button(
            f"⚠️ {subject} এর সব প্রশ্ন মুছে ফেলুন"
        ):

            remaining = all_questions[
                all_questions["Subject"] != subject
            ]

            remaining.to_csv(
                QUESTIONS_FILE,
                index=False,
                encoding="utf-8-sig"
            )

            st.success(
                f"{subject} এর সব প্রশ্ন মুছে ফেলা হয়েছে।"
            )

            st.rerun()

    elif admin_menu == "📊 ফলাফল":

        st.header("📊 পরীক্ষার ফলাফল")

        results = load_results()

        if results.empty:

            st.info(
                "এখনও কোনো ফলাফল পাওয়া যায়নি।"
            )

        else:

            st.dataframe(
                results,
                use_container_width=True
            )

            st.download_button(
                "📥 Results CSV Download",
                data=results.to_csv(
                    index=False,
                    encoding="utf-8-sig"
                ),
                file_name="results.csv",
                mime="text/csv"
            )

            st.markdown("---")

            if st.button(
                "⚠️ সব ফলাফল মুছে ফেলুন"
            ):

                empty_df = pd.DataFrame(
                    columns=results.columns
                )

                empty_df.to_csv(
                    RESULT_FILE,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.success(
                    "সব ফলাফল মুছে ফেলা হয়েছে।"
                )

                st.rerun()

    elif admin_menu == "👀 প্রশ্ন দেখুন":

        st.header("👀 সংরক্ষিত প্রশ্ন")

        questions = load_questions()

        if questions.empty:

            st.info(
                "কোনো প্রশ্ন নেই।"
            )

        else:

            selected_subject = st.selectbox(
                "বিষয়",
                sorted(
                    questions["Subject"]
                    .dropna()
                    .unique()
                )
            )

            filtered = questions[
                questions["Subject"]
                == selected_subject
            ]

            st.write(
                f"মোট প্রশ্ন: {len(filtered)}"
            )

            st.dataframe(
                filtered,
                use_container_width=True
            )

    st.sidebar.markdown("---")

    if st.sidebar.button("Logout"):

        st.session_state.is_admin_logged_in = False

        st.rerun()


# =========================================================
# STUDENT SECTION
# =========================================================

else:

    # =====================================================
    # EXAM RUNNING
    # =====================================================

    if st.session_state.exam_in_progress:

        subject = st.session_state.selected_exam_subject

        questions = st.session_state.exam_questions

        duration = st.session_state.exam_duration

        start_time = st.session_state.exam_start_time

        total_seconds = int(duration * 60)

        elapsed = int(
            time.time() - start_time
        )

        remaining = max(
            0,
            total_seconds - elapsed
        )

        minutes = remaining // 60
        seconds = remaining % 60

        # -------------------------------------------------
        # LIVE TIMER
        # -------------------------------------------------

        if not st.session_state.exam_submitted:

            timer_html = f"""
            <div class="fixed-timer">
                ⏱️ <span id="timer">
                    {minutes:02d}:{seconds:02d}
                </span>
            </div>

            <script>

            let remaining = {remaining};

            function updateTimer() {{

                let min = Math.floor(
                    remaining / 60
                );

                let sec = remaining % 60;

                let display =
                    String(min).padStart(2, '0')
                    + ":"
                    + String(sec).padStart(2, '0');

                const timer =
                    window.parent.document
                    .getElementById("timer");

                if (timer) {{
                    timer.innerHTML = display;
                }}

                if (remaining <= 0) {{

                    clearInterval(timerInterval);

                    const buttons =
                        window.parent.document
                        .querySelectorAll(
                            'button'
                        );

                    for (
                        let button of buttons
                    ) {{

                        if (
                            button.innerText
                            .includes(
                                'পরীক্ষা জমা দিন'
                            )
                        ) {{

                            button.click();

                            break;
                        }}
                    }}

                }}

                remaining--;

            }}

            let timerInterval =
                setInterval(
                    updateTimer,
                    1000
                );

            </script>
            """

            st.markdown(
                timer_html,
                unsafe_allow_html=True
            )

        st.header(
            f"📝 {subject} পরীক্ষা"
        )

        st.write(
            f"পরীক্ষার্থী: "
            f"**{st.session_state.confirmed_student_name}**"
        )

        st.markdown("---")

        total_questions = len(questions)

        # =================================================
        # QUESTION NAVIGATOR
        # =================================================

        answered_count = sum(
            1
            for i in range(total_questions)
            if st.session_state.student_answers.get(i)
        )

        unanswered_count = (
            total_questions - answered_count
        )

        st.markdown(
            """
            <div class="question-palette">
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="palette-info">
                📊 উত্তর দেওয়া: <b>{answered_count}</b>
                &nbsp;&nbsp; | &nbsp;&nbsp;
                ⭕ বাকি: <b>{unanswered_count}</b>
                &nbsp;&nbsp; | &nbsp;&nbsp;
                📝 মোট: <b>{total_questions}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        palette_columns = st.columns(
            min(5, total_questions)
        )

        for i in range(total_questions):

            col = palette_columns[
                i % len(palette_columns)
            ]

            question_number = i + 1

            if st.session_state.student_answers.get(i):

                label = f"🟢 {question_number}"

            else:

                label = f"⚪ {question_number}"

            if col.button(
                label,
                key=f"palette_{i}",
                use_container_width=True
            ):

                st.session_state.current_question = i

                st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        # =================================================
        # CURRENT QUESTION
        # =================================================

        current = st.session_state.current_question

        if current < 0:
            current = 0

        if current >= total_questions:
            current = total_questions - 1

        q = questions[current]

        st.markdown(
            '<div class="question-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            f"### {current + 1}. {q['Question']}"
        )

        options = [
            f"A. {q['Option A']}",
            f"B. {q['Option B']}",
            f"C. {q['Option C']}",
            f"D. {q['Option D']}"
        ]

        previous_answer = (
            st.session_state.student_answers.get(
                current
            )
        )

        option_index = None

        if previous_answer in options:

            option_index = options.index(
                previous_answer
            )

        selected_answer = st.radio(
            "উত্তর নির্বাচন করুন",
            options,
            index=option_index,
            key=f"question_{current}"
        )

        if selected_answer:

            st.session_state.student_answers[
                current
            ] = selected_answer

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        # =================================================
        # PREVIOUS / NEXT
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            if current > 0:

                if st.button(
                    "⬅️ আগের প্রশ্ন",
                    use_container_width=True
                ):

                    st.session_state.current_question = (
                        current - 1
                    )

                    st.rerun()

        with col2:

            st.write(
                f"**{current + 1} / {total_questions}**"
            )

        with col3:

            if current < total_questions - 1:

                if st.button(
                    "পরের প্রশ্ন ➡️",
                    use_container_width=True
                ):

                    st.session_state.current_question = (
                        current + 1
                    )

                    st.rerun()

        st.markdown("---")

        # =================================================
        # SUBMIT
        # =================================================

        if st.button(
            "✅ পরীক্ষা জমা দিন",
            type="primary",
            use_container_width=True
        ):

            st.session_state.exam_submitted = True

            st.rerun()

        # =================================================
        # TIME CHECK
        # =================================================

        if remaining <= 0:

            st.session_state.exam_submitted = True

            st.rerun()

    # =====================================================
    # RESULT
    # =====================================================

    elif st.session_state.exam_submitted:

        subject = st.session_state.selected_exam_subject

        questions = st.session_state.exam_questions

        correct = 0
        wrong = 0
        unanswered = 0

        review_data = []

        for i, q in enumerate(questions):

            selected = (
                st.session_state.student_answers
                .get(i)
            )

            correct_answer = normalize_answer(
                q["Answer"]
            )

            if selected is None:

                unanswered += 1

                status = "⏺️ উত্তর দেওয়া হয়নি"

            else:

                selected_letter = selected[0]

                if selected_letter == correct_answer:

                    correct += 1

                    status = "✅ সঠিক"

                else:

                    wrong += 1

                    status = "❌ ভুল"

            review_data.append({
                "Question": q["Question"],
                "Your Answer":
                    selected
                    if selected
                    else "উত্তর দেওয়া হয়নি",
                "Correct Answer":
                    correct_answer,
                "Status":
                    status,
                "Explanation":
                    q.get(
                        "Explanation",
                        ""
                    )
            })

        total = len(questions)

        score = correct

        percentage = (
            (score / total) * 100
            if total > 0
            else 0
        )

        st.markdown(
            f"""
            <div class="result-box">

            <h2>🎉 পরীক্ষা সম্পন্ন</h2>

            <h1>{score} / {total}</h1>

            <p>
            সঠিক: <b>{correct}</b>
            &nbsp; | &nbsp;
            ভুল: <b>{wrong}</b>
            &nbsp; | &nbsp;
            উত্তরহীন: <b>{unanswered}</b>
            </p>

            <h3>
            Percentage: {percentage:.2f}%
            </h3>

            </div>
            """,
            unsafe_allow_html=True
        )

        new_result = pd.DataFrame([{
            "Student Name":
                st.session_state.confirmed_student_name,

            "Subject":
                subject,

            "Score":
                score,

            "Total Marks":
                total,

            "Correct":
                correct,

            "Wrong":
                wrong,

            "Unanswered":
                unanswered,

            "Date":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        }])

        old_results = load_results()

        old_results = pd.concat(
            [
                old_results,
                new_result
            ],
            ignore_index=True
        )

        old_results.to_csv(
            RESULT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        st.markdown("---")

        st.subheader(
            "📖 উত্তর বিশ্লেষণ"
        )

        for i, item in enumerate(
            review_data
        ):

            st.markdown(
                f"### {i + 1}. {item['Question']}"
            )

            st.write(
                f"**আপনার উত্তর:** "
                f"{item['Your Answer']}"
            )

            st.write(
                f"**সঠিক উত্তর:** "
                f"{item['Correct Answer']}"
            )

            st.write(
                f"**ফলাফল:** "
                f"{item['Status']}"
            )

            if item["Explanation"]:

                st.info(
                    f"ব্যাখ্যা: "
                    f"{item['Explanation']}"
                )

            st.markdown("---")

        if st.button(
            "🏠 নতুন পরীক্ষা শুরু করুন",
            use_container_width=True
        ):

            st.session_state.exam_in_progress = False
            st.session_state.exam_submitted = False
            st.session_state.exam_questions = []
            st.session_state.exam_start_time = None
            st.session_state.student_answers = {}
            st.session_state.selected_exam_subject = None
            st.session_state.current_question = 0

            st.rerun()

    # =====================================================
    # STUDENT HOME
    # =====================================================

    else:

        tab = st.radio(
            "",
            [
                "📝 পরীক্ষা দিন",
                "🏆 Leaderboard"
            ],
            horizontal=True
        )

        if tab == "📝 পরীক্ষা দিন":

            st.header(
                "📝 পরীক্ষা দিন"
            )

            questions_df = load_questions()

            if questions_df.empty:

                st.warning(
                    "এখনও কোনো প্রশ্ন যোগ করা হয়নি।"
                )

            else:

                subjects = sorted(
                    questions_df[
                        "Subject"
                    ].dropna().unique()
                )

                selected_subject = st.selectbox(
                    "বিষয় নির্বাচন করুন",
                    subjects
                )

                subject_questions = questions_df[
                    questions_df["Subject"]
                    == selected_subject
                ]

                duration = get_duration(
                    selected_subject
                )

                st.info(
                    f"⏱️ সময়: {duration} মিনিট  |  "
                    f"📚 প্রশ্ন: "
                    f"{len(subject_questions)}টি"
                )

                student_name = st.text_input(
                    "পরীক্ষার্থীর নাম"
                )

                number_of_questions = st.number_input(
                    "কতটি প্রশ্ন দিয়ে পরীক্ষা দিতে চান?",
                    min_value=1,
                    max_value=len(subject_questions),
                    value=min(
                        20,
                        len(subject_questions)
                    )
                )

                if st.button(
                    "🚀 পরীক্ষা শুরু করুন",
                    type="primary",
                    use_container_width=True
                ):

                    if not student_name.strip():

                        st.warning(
                            "পরীক্ষা শুরু করার আগে নাম দিন।"
                        )

                    else:

                        selected_questions = (
                            subject_questions.sample(
                                n=int(
                                    number_of_questions
                                )
                            ).to_dict(
                                "records"
                            )
                        )

                        st.session_state.confirmed_student_name = (
                            student_name.strip()
                        )

                        st.session_state.selected_exam_subject = (
                            selected_subject
                        )

                        st.session_state.exam_questions = (
                            selected_questions
                        )

                        st.session_state.exam_duration = (
                            duration
                        )

                        st.session_state.exam_start_time = (
                            time.time()
                        )

                        st.session_state.exam_submitted = False

                        st.session_state.student_answers = {}

                        st.session_state.current_question = 0

                        st.session_state.exam_in_progress = True

                        st.rerun()

        else:

            st.header(
                "🏆 ক্লাসের মেধা তালিকা"
            )

            results = load_results()

            if results.empty:

                st.info(
                    "এখনও কোনো ফলাফল নেই।"
                )

            else:

                selected_subject = st.selectbox(
                    "বিষয় নির্বাচন করুন",
                    sorted(
                        results[
                            "Subject"
                        ].dropna().unique()
                    )
                )

                leaderboard = results[
                    results["Subject"]
                    == selected_subject
                ].copy()

                leaderboard["Percentage"] = (
                    leaderboard["Score"]
                    /
                    leaderboard["Total Marks"]
                    *
                    100
                )

                leaderboard = leaderboard.sort_values(
                    by=[
                        "Percentage",
                        "Score"
                    ],
                    ascending=False
                )

                leaderboard = (
                    leaderboard.reset_index(
                        drop=True
                    )
                )

                leaderboard.insert(
                    0,
                    "Rank",
                    range(
                        1,
                        len(leaderboard) + 1
                    )
                )

                st.dataframe(
                    leaderboard[
                        [
                            "Rank",
                            "Student Name",
                            "Score",
                            "Total Marks",
                            "Percentage",
                            "Date"
                        ]
                    ],
                    use_container_width=True
                )
