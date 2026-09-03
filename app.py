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
# CONSTANTS
# =========================================================

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"

ADMIN_PASSWORD = "1234"

SUBJECTS = [
    "বাংলা",
    "English",
    "গণিত",
    "বিজ্ঞান",
    "বাংলাদেশের বিষয়াবলি",
    "আন্তর্জাতিক বিষয়াবলি",
    "ICT"
]


# =========================================================
# SESSION STATE
# =========================================================

if "is_admin_logged_in" not in st.session_state:
    st.session_state["is_admin_logged_in"] = False

if "admin_login_open" not in st.session_state:
    st.session_state["admin_login_open"] = False

if "confirmed_student_name" not in st.session_state:
    st.session_state["confirmed_student_name"] = ""

if "exam_submitted" not in st.session_state:
    st.session_state["exam_submitted"] = False

if "last_result_data" not in st.session_state:
    st.session_state["last_result_data"] = None

if "selected_exam_subject" not in st.session_state:
    st.session_state["selected_exam_subject"] = None

if "exam_in_progress" not in st.session_state:
    st.session_state["exam_in_progress"] = False

if "exam_start_time" not in st.session_state:
    st.session_state["exam_start_time"] = None


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
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

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .main-title {
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 15px;
        margin-bottom: 5px;
    }

    .powered {
        text-align: center;
        font-size: 13px;
        margin-bottom: 25px;
    }

    .question-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #dddddd;
        margin-bottom: 15px;
    }

    .result-card {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #dddddd;
        text-align: center;
        margin-top: 20px;
    }

    .admin-login-box {
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 15px;
    }

    .admin-top-space {
        margin-bottom: 8px;
    }

    @media (max-width: 768px) {

        .main-title {
            font-size: 25px;
        }

        .subtitle {
            font-size: 13px;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def load_questions():

    columns = [
        "Subject",
        "Question",
        "Option_A",
        "Option_B",
        "Option_C",
        "Option_D",
        "Correct_Answer",
        "Explanation"
    ]

    if os.path.exists(QUESTIONS_FILE):

        try:

            df = pd.read_csv(
                QUESTIONS_FILE,
                encoding="utf-8-sig"
            )

            for col in columns:

                if col not in df.columns:
                    df[col] = ""

            return df[columns]

        except Exception:
            pass

    return pd.DataFrame(columns=columns)


def load_results():

    columns = [
        "Student Name",
        "Subject",
        "Score",
        "Total Marks",
        "Submission Time"
    ]

    if os.path.exists(RESULT_FILE):

        try:

            return pd.read_csv(
                RESULT_FILE,
                encoding="utf-8-sig"
            )

        except Exception:
            pass

    return pd.DataFrame(columns=columns)


def load_configs():

    columns = [
        "Subject",
        "Duration"
    ]

    if os.path.exists(CONFIG_FILE):

        try:

            return pd.read_csv(
                CONFIG_FILE,
                encoding="utf-8-sig"
            )

        except Exception:
            pass

    return pd.DataFrame(columns=columns)


def get_duration(subject):

    config_df = load_configs()

    if not config_df.empty:

        row = config_df[
            config_df["Subject"] == subject
        ]

        if not row.empty:

            try:

                return int(
                    row.iloc[0]["Duration"]
                )

            except Exception:
                pass

    return 30


def save_questions(df):

    df.to_csv(
        QUESTIONS_FILE,
        index=False,
        encoding="utf-8-sig"
    )


def save_results(df):

    df.to_csv(
        RESULT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


def save_configs(df):

    df.to_csv(
        CONFIG_FILE,
        index=False,
        encoding="utf-8-sig"
    )


def normalize_answer(answer):

    if pd.isna(answer):
        return ""

    return str(
        answer
    ).strip().lower()


def answer_matches(
    selected_answer,
    row
):

    if not selected_answer:
        return False

    selected = normalize_answer(
        selected_answer
    )

    correct = normalize_answer(
        row["Correct_Answer"]
    )

    option_map = {

        "ক": normalize_answer(
            row["Option_A"]
        ),

        "খ": normalize_answer(
            row["Option_B"]
        ),

        "গ": normalize_answer(
            row["Option_C"]
        ),

        "ঘ": normalize_answer(
            row["Option_D"]
        ),

        "a": normalize_answer(
            row["Option_A"]
        ),

        "b": normalize_answer(
            row["Option_B"]
        ),

        "c": normalize_answer(
            row["Option_C"]
        ),

        "d": normalize_answer(
            row["Option_D"]
        )
    }

    if selected in option_map:
        selected = option_map[selected]

    if correct in option_map:
        correct = option_map[correct]

    return selected == correct


# =========================================================
# TOP RIGHT ADMIN LOGIN
# =========================================================

if not st.session_state["exam_in_progress"]:

    top_left, top_right = st.columns(
        [5, 1]
    )

    with top_right:

        if not st.session_state[
            "is_admin_logged_in"
        ]:

            if st.button(
                "🔐 Admin",
                use_container_width=True
            ):

                st.session_state[
                    "admin_login_open"
                ] = not st.session_state[
                    "admin_login_open"
                ]

                st.rerun()

        else:

            st.success(
                "✅ Admin"
            )


    # -----------------------------------------------------
    # ADMIN LOGIN BOX
    # -----------------------------------------------------

    if (
        st.session_state[
            "admin_login_open"
        ]
        and
        not st.session_state[
            "is_admin_logged_in"
        ]
    ):

        st.markdown(
            """
            <div class="admin-login-box">
                <b>🔐 Admin Login</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        login_col1, login_col2 = st.columns(
            [3, 1]
        )

        with login_col1:

            admin_password = st.text_input(
                "🔑 Admin Password",
                type="password",
                key="admin_login_password",
                placeholder="Password লিখুন"
            )

        with login_col2:

            st.write("")

            if st.button(
                "🔓 LOGIN",
                use_container_width=True
            ):

                if admin_password == ADMIN_PASSWORD:

                    st.session_state[
                        "is_admin_logged_in"
                    ] = True

                    st.session_state[
                        "admin_login_open"
                    ] = False

                    st.success(
                        "✅ Admin Login সফল হয়েছে!"
                    )

                    time.sleep(0.5)

                    st.rerun()

                else:

                    st.error(
                        "❌ ভুল পাসওয়ার্ড!"
                    )

    st.markdown(
        '<div class="admin-top-space"></div>',
        unsafe_allow_html=True
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">বিসিএস, ব্যাংক, প্রাথমিক সহকারী শিক্ষক নিয়োগ এবং NTRCA সহ সকল সরকারি চাকরির প্রস্তুতির বিশ্বস্ত মাধ্যম</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="powered">Powered by <b>Job Efforts</b></div>',
    unsafe_allow_html=True
)


# =========================================================
# ADMIN PANEL
# =========================================================

admin_menu = None

if st.session_state[
    "is_admin_logged_in"
]:

    st.markdown("---")

    st.header(
        "⚙️ Admin Control Panel"
    )

    admin_menu = st.radio(
        "অ্যাডমিন মেনু",
        [
            "📝 প্রশ্ন আপলোড ও সেটআপ",
            "📊 সকল শিক্ষার্থীর ফলাফল"
        ],
        horizontal=True
    )

    if st.button(
        "🚪 LOGOUT",
        use_container_width=True
    ):

        st.session_state[
            "is_admin_logged_in"
        ] = False

        st.session_state[
            "admin_login_open"
        ] = False

        st.rerun()


# =========================================================
# ADMIN: QUESTION UPLOAD
# =========================================================

if st.session_state[
    "is_admin_logged_in"
]:

    if admin_menu == "📝 প্রশ্ন আপলোড ও সেটআপ":

        st.header(
            "📝 প্রশ্ন আপলোড ও পরীক্ষার সেটআপ"
        )

        st.subheader(
            "১. বিষয় নির্বাচন"
        )

        admin_subject = st.selectbox(
            "বিষয়",
            SUBJECTS,
            key="admin_subject"
        )

        st.subheader(
            "২. পরীক্ষার সময় নির্ধারণ"
        )

        current_duration = get_duration(
            admin_subject
        )

        duration = st.number_input(
            "পরীক্ষার সময় (মিনিট)",
            min_value=1,
            max_value=300,
            value=current_duration,
            step=1
        )

        if st.button(
            "💾 পরীক্ষার সময় সংরক্ষণ"
        ):

            config_df = load_configs()

            new_row = pd.DataFrame(
                [
                    {
                        "Subject": admin_subject,
                        "Duration": duration
                    }
                ]
            )

            config_df = config_df[
                config_df["Subject"]
                != admin_subject
            ]

            config_df = pd.concat(
                [
                    config_df,
                    new_row
                ],
                ignore_index=True
            )

            save_configs(
                config_df
            )

            st.success(
                f"✅ {admin_subject} বিষয়ের সময় "
                f"{duration} মিনিট সংরক্ষণ হয়েছে।"
            )

        st.markdown("---")


        # =================================================
        # QUESTION INPUT
        # =================================================

        st.subheader(
            "৩. প্রশ্ন আপলোড"
        )

        upload_method = st.radio(
            "প্রশ্ন যোগ করার পদ্ধতি নির্বাচন করুন",
            [
                "✍️ Text Paste",
                "📂 Excel / CSV Upload"
            ]
        )


        # =================================================
        # TEXT PASTE
        # =================================================

        if upload_method == "✍️ Text Paste":

            st.info(
                "প্রতি প্রশ্নের জন্য প্রথম ৫ লাইনে "
                "প্রশ্ন + ৪টি অপশন দিন। "
                "পরবর্তী লাইনে সঠিক উত্তর ও ব্যাখ্যা দিতে পারেন।"
            )

            text_data = st.text_area(
                "প্রশ্নগুলো এখানে Paste করুন",
                height=350,
                placeholder=(
                    "প্রশ্ন ১\n"
                    "ক) অপশন ১\n"
                    "খ) অপশন ২\n"
                    "গ) অপশন ৩\n"
                    "ঘ) অপশন ৪\n"
                    "ক\n"
                    "ব্যাখ্যা\n\n"
                    "প্রশ্ন ২\n"
                    "ক) অপশন ১\n"
                    "খ) অপশন ২\n"
                    "গ) অপশন ৩\n"
                    "ঘ) অপশন ৪\n"
                    "খ\n"
                    "ব্যাখ্যা"
                )
            )

            if st.button(
                "📥 প্রশ্ন সংরক্ষণ করুন"
            ):

                if not text_data.strip():

                    st.warning(
                        "⚠️ আগে প্রশ্ন লিখুন।"
                    )

                else:

                    blocks = (
                        text_data
                        .strip()
                        .split("\n\n")
                    )

                    new_questions = []

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
                        correct_answer = lines[5]

                        explanation = (
                            lines[6]
                            if len(lines) > 6
                            else "ব্যাখ্যা নেই।"
                        )

                        new_questions.append(
                            {
                                "Subject": admin_subject,
                                "Question": question,
                                "Option_A": option_a,
                                "Option_B": option_b,
                                "Option_C": option_c,
                                "Option_D": option_d,
                                "Correct_Answer": correct_answer,
                                "Explanation": explanation
                            }
                        )

                    if new_questions:

                        old_df = load_questions()

                        new_df = pd.DataFrame(
                            new_questions
                        )

                        final_df = pd.concat(
                            [
                                old_df,
                                new_df
                            ],
                            ignore_index=True
                        )

                        save_questions(
                            final_df
                        )

                        st.success(
                            f"✅ {len(new_questions)}টি "
                            f"প্রশ্ন সংরক্ষণ হয়েছে।"
                        )

                    else:

                        st.error(
                            "❌ সঠিক ফরম্যাটে কোনো প্রশ্ন পাওয়া যায়নি।"
                        )


        # =================================================
        # EXCEL / CSV UPLOAD
        # =================================================

        else:

            uploaded_file = st.file_uploader(
                "Excel / CSV ফাইল নির্বাচন করুন",
                type=[
                    "xlsx",
                    "xls",
                    "csv"
                ]
            )

            if uploaded_file is not None:

                try:

                    # -------------------------------------
                    # READ FILE
                    # -------------------------------------

                    if uploaded_file.name.lower().endswith(
                        ".csv"
                    ):

                        excel_df = pd.read_csv(
                            uploaded_file,
                            header=None
                        )

                    else:

                        excel_df = pd.read_excel(
                            uploaded_file,
                            header=None
                        )

                    st.success(
                        "✅ ফাইল সফলভাবে পড়া হয়েছে।"
                    )


                    # -------------------------------------
                    # COLUMN MAPPING
                    # -------------------------------------

                    subject_column_map = {

                        "বাংলা": (0, 6),

                        "English": (6, 12),

                        "গণিত": (12, 18),

                        "বিজ্ঞান": (18, 24),

                        "বাংলাদেশের বিষয়াবলি": (24, 30),

                        "আন্তর্জাতিক বিষয়াবলি": (30, 36),

                        "ICT": (36, 42)

                    }


                    start_col, end_col = (
                        subject_column_map[
                            admin_subject
                        ]
                    )


                    # -------------------------------------
                    # CHECK COLUMNS
                    # -------------------------------------

                    if excel_df.shape[1] < end_col:

                        st.error(
                            f"❌ {admin_subject} বিষয়ের জন্য "
                            f"কমপক্ষে {end_col}টি কলাম থাকতে হবে।"
                        )

                    else:

                        st.subheader(
                            f"📋 {admin_subject} বিষয়ের Excel Preview"
                        )


                        # ---------------------------------
                        # PREVIEW
                        # ---------------------------------

                        preview_df = excel_df.iloc[
                            :10,
                            start_col:end_col
                        ].copy()

                        preview_df.columns = [
                            "Question",
                            "Option_A",
                            "Option_B",
                            "Option_C",
                            "Option_D",
                            "Correct_Answer"
                        ]

                        st.dataframe(
                            preview_df,
                            use_container_width=True
                        )


                        st.info(
                            f"📌 নির্বাচিত বিষয়: "
                            f"**{admin_subject}**\n\n"
                            f"এই বিষয়ের জন্য Excel-এর "
                            f"**কলাম {start_col + 1}–{end_col}** "
                            f"ব্যবহার করা হবে।"
                        )


                        # ---------------------------------
                        # IMPORT
                        # ---------------------------------

                        if st.button(
                            f"📥 {admin_subject} প্রশ্ন Import করুন"
                        ):

                            imported = []

                            selected_columns = (
                                excel_df.iloc[
                                    :,
                                    start_col:end_col
                                ]
                            )

                            for _, row in selected_columns.iterrows():

                                values = list(row)

                                if len(values) < 6:
                                    continue

                                if pd.isna(values[0]):
                                    continue

                                question = str(
                                    values[0]
                                ).strip()

                                option_a = str(
                                    values[1]
                                ).strip()

                                option_b = str(
                                    values[2]
                                ).strip()

                                option_c = str(
                                    values[3]
                                ).strip()

                                option_d = str(
                                    values[4]
                                ).strip()

                                correct_answer = str(
                                    values[5]
                                ).strip()


                                # -------------------------
                                # SKIP HEADER
                                # -------------------------

                                if not question:
                                    continue

                                if question.lower() == "question":
                                    continue

                                if question.lower() == "প্রশ্ন":
                                    continue


                                # -------------------------
                                # ADD QUESTION
                                # -------------------------

                                imported.append(
                                    {
                                        "Subject": admin_subject,

                                        "Question": question,

                                        "Option_A": option_a,

                                        "Option_B": option_b,

                                        "Option_C": option_c,

                                        "Option_D": option_d,

                                        "Correct_Answer":
                                            correct_answer,

                                        "Explanation":
                                            "ব্যাখ্যা নেই।"
                                    }
                                )


                            # ---------------------------------
                            # SAVE
                            # ---------------------------------

                            if imported:

                                old_df = load_questions()

                                imported_df = pd.DataFrame(
                                    imported
                                )

                                final_df = pd.concat(
                                    [
                                        old_df,
                                        imported_df
                                    ],
                                    ignore_index=True
                                )

                                save_questions(
                                    final_df
                                )

                                st.success(
                                    f"✅ {len(imported)}টি "
                                    f"{admin_subject} প্রশ্ন "
                                    f"সফলভাবে Import হয়েছে।"
                                )

                            else:

                                st.warning(
                                    f"⚠️ {admin_subject} বিষয়ের "
                                    f"কোনো প্রশ্ন পাওয়া যায়নি।"
                                )

                except Exception as e:

                    st.error(
                        f"❌ ফাইল পড়তে সমস্যা হয়েছে: {e}"
                    )


        st.markdown("---")


        # =================================================
        # QUESTION PREVIEW
        # =================================================

        st.subheader(
            "📚 সংরক্ষিত প্রশ্ন"
        )

        questions_df = load_questions()

        if questions_df.empty:

            st.info(
                "এই মুহূর্তে কোনো প্রশ্ন সংরক্ষিত নেই।"
            )

        else:

            subject_questions = questions_df[
                questions_df["Subject"]
                == admin_subject
            ]

            st.write(
                f"**{admin_subject} বিষয়ে মোট প্রশ্ন: "
                f"{len(subject_questions)}টি**"
            )

            if not subject_questions.empty:

                preview_df = subject_questions[
                    [
                        "Question",
                        "Option_A",
                        "Option_B",
                        "Option_C",
                        "Option_D",
                        "Correct_Answer"
                    ]
                ]

                st.dataframe(
                    preview_df,
                    use_container_width=True
                )

                st.markdown("---")

                if st.button(
                    f"🗑️ {admin_subject} বিষয়ের সব প্রশ্ন মুছুন"
                ):

                    remaining_df = questions_df[
                        questions_df["Subject"]
                        != admin_subject
                    ]

                    save_questions(
                        remaining_df
                    )

                    st.success(
                        f"✅ {admin_subject} বিষয়ের "
                        f"সব প্রশ্ন মুছে দেওয়া হয়েছে।"
                    )

                    st.rerun()


# =========================================================
# ADMIN: RESULTS
# =========================================================

if st.session_state[
    "is_admin_logged_in"
]:

    if admin_menu == "📊 সকল শিক্ষার্থীর ফলাফল":

        st.header(
            "📊 সকল শিক্ষার্থীর ফলাফল"
        )

        results_df = load_results()

        if results_df.empty:

            st.info(
                "এখনও কোনো শিক্ষার্থীর ফলাফল নেই।"
            )

        else:

            st.dataframe(
                results_df,
                use_container_width=True
            )

            csv_data = (
                results_df
                .to_csv(index=False)
                .encode("utf-8-sig")
            )

            st.download_button(
                "⬇️ ফলাফল CSV Download",
                data=csv_data,
                file_name="results.csv",
                mime="text/csv"
            )

            st.markdown("---")

            if st.button(
                "🗑️ সকল ফলাফল মুছে ফেলুন"
            ):

                empty_results = pd.DataFrame(
                    columns=[
                        "Student Name",
                        "Subject",
                        "Score",
                        "Total Marks",
                        "Submission Time"
                    ]
                )

                save_results(
                    empty_results
                )

                st.success(
                    "✅ সকল ফলাফল মুছে দেওয়া হয়েছে।"
                )

                st.rerun()


# =========================================================
# STUDENT HOME
# =========================================================

if (
    not st.session_state["exam_in_progress"]
    and
    not st.session_state["is_admin_logged_in"]
):

    st.header(
        "🎯 পরীক্ষা শুরু করুন"
    )

    selected_subject = st.selectbox(
        "বিষয় নির্বাচন করুন",
        SUBJECTS,
        key="student_subject"
    )

    all_questions = load_questions()

    subject_questions = all_questions[
        all_questions["Subject"]
        == selected_subject
    ]

    duration = get_duration(
        selected_subject
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "⏱️ সময়",
            f"{duration} মিনিট"
        )

    with col2:

        st.metric(
            "📝 প্রশ্ন",
            len(subject_questions)
        )

    if len(subject_questions) == 0:

        st.warning(
            "⚠️ এই বিষয়ে এখনো কোনো প্রশ্ন যোগ করা হয়নি।"
        )

    else:

        student_name = st.text_input(
            "👤 শিক্ষার্থীর নাম"
        )

        if st.button(
            "🚀 পরীক্ষা শুরু করুন",
            use_container_width=True
        ):

            if not student_name.strip():

                st.warning(
                    "⚠️ পরীক্ষার্থীর নাম লিখুন।"
                )

            else:

                st.session_state[
                    "confirmed_student_name"
                ] = student_name.strip()

                st.session_state[
                    "selected_exam_subject"
                ] = selected_subject

                st.session_state[
                    "exam_in_progress"
                ] = True

                st.session_state[
                    "exam_submitted"
                ] = False

                st.session_state[
                    "exam_start_time"
                ] = time.time()

                st.rerun()


# =========================================================
# EXAM PAGE
# =========================================================

if st.session_state[
    "exam_in_progress"
]:

    subject = st.session_state[
        "selected_exam_subject"
    ]

    student_name = st.session_state[
        "confirmed_student_name"
    ]

    duration = get_duration(
        subject
    )

    all_questions = load_questions()

    active_df = all_questions[
        all_questions["Subject"]
        == subject
    ].copy()

    active_df = active_df.reset_index(
        drop=True
    )

    st.header(
        "📝 পরীক্ষা চলছে"
    )

    st.write(
        f"👤 পরীক্ষার্থী: **{student_name}**"
    )

    st.write(
        f"📚 বিষয়: **{subject}**"
    )


    # =====================================================
    # TIMER
    # =====================================================

    start_time = st.session_state[
        "exam_start_time"
    ]

    elapsed = (
        time.time()
        - start_time
    )

    remaining_seconds = max(
        0,
        int(
            duration * 60
            - elapsed
        )
    )

    minutes = (
        remaining_seconds // 60
    )

    seconds = (
        remaining_seconds % 60
    )

    timer_placeholder = st.empty()

    timer_placeholder.markdown(
        f"""
        <div style="
            position:sticky;
            top:0;
            z-index:999;
            background:white;
            border:2px solid #ddd;
            border-radius:12px;
            padding:12px;
            text-align:center;
            margin-bottom:15px;
        ">

            <div style="font-size:14px;">
                ⏱️ সময় বাকি
            </div>

            <div style="
                font-size:30px;
                font-weight:bold;
            ">
                {minutes:02d}:{seconds:02d}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # QUESTIONS
    # =====================================================

    answers = {}

    for i, row in active_df.iterrows():

        st.markdown(
            f"""
            <div class="question-card">

                <b>প্রশ্ন {i + 1}:</b>

                <br><br>

                {row["Question"]}

            </div>
            """,
            unsafe_allow_html=True
        )

        options = [
            row["Option_A"],
            row["Option_B"],
            row["Option_C"],
            row["Option_D"]
        ]

        answer = st.radio(
            "উত্তর নির্বাচন করুন:",
            options,
            key=f"question_{i}",
            index=None
        )

        answers[i] = answer

        st.markdown("---")


    # =====================================================
    # SUBMIT
    # =====================================================

    if st.button(
        "📤 পরীক্ষা জমা দিন",
        use_container_width=True
    ):

        score = 0

        for i, row in active_df.iterrows():

            selected_answer = answers.get(
                i
            )

            if answer_matches(
                selected_answer,
                row
            ):

                score += 1

        total_marks = len(
            active_df
        )

        submission_time = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        new_result = pd.DataFrame(
            [
                {
                    "Student Name": student_name,
                    "Subject": subject,
                    "Score": score,
                    "Total Marks": total_marks,
                    "Submission Time":
                        submission_time
                }
            ]
        )

        old_results = load_results()

        final_results = pd.concat(
            [
                old_results,
                new_result
            ],
            ignore_index=True
        )

        save_results(
            final_results
        )

        st.session_state[
            "last_result_data"
        ] = {

            "student_name":
                student_name,

            "subject":
                subject,

            "score":
                score,

            "total_marks":
                total_marks

        }

        st.session_state[
            "exam_submitted"
        ] = True

        st.session_state[
            "exam_in_progress"
        ] = False

        st.session_state[
            "exam_start_time"
        ] = None

        st.rerun()


# =========================================================
# RESULT PAGE
# =========================================================

if (
    st.session_state[
        "exam_submitted"
    ]
    and
    st.session_state[
        "last_result_data"
    ] is not None
):

    result = st.session_state[
        "last_result_data"
    ]

    st.header(
        "🏆 পরীক্ষার ফলাফল"
    )

    score = result[
        "score"
    ]

    total = result[
        "total_marks"
    ]

    percentage = (
        (score / total) * 100
        if total > 0
        else 0
    )

    st.markdown(
        f"""
        <div class="result-card">

            <h2>
                🎉 পরীক্ষা সম্পন্ন
            </h2>

            <p>
                👤 <b>শিক্ষার্থী:</b>
                {result["student_name"]}
            </p>

            <p>
                📚 <b>বিষয়:</b>
                {result["subject"]}
            </p>

            <h1>
                {score} / {total}
            </h1>

            <h3>
                শতকরা নম্বর:
                {percentage:.2f}%
            </h3>

        </div>
        """,
        unsafe_allow_html=True
    )

    if percentage >= 80:

        st.success(
            "🌟 অসাধারণ ফলাফল!"
        )

    elif percentage >= 60:

        st.info(
            "👍 খুব ভালো ফলাফল।"
        )

    elif percentage >= 33:

        st.warning(
            "✅ পাস করেছেন। আরও ভালো করার সুযোগ আছে।"
        )

    else:

        st.error(
            "📚 আরও বেশি অনুশীলন করুন।"
        )

    if st.button(
        "🏠 হোমে ফিরে যান",
        use_container_width=True
    ):

        st.session_state[
            "exam_submitted"
        ] = False

        st.session_state[
            "last_result_data"
        ] = None

        st.rerun()


# =========================================================
# LEADERBOARD
# =========================================================

if (
    not st.session_state[
        "exam_in_progress"
    ]
    and
    not st.session_state[
        "is_admin_logged_in"
    ]
    and
    not st.session_state[
        "exam_submitted"
    ]
):

    st.markdown("---")

    st.header(
        "🏆 Leaderboard"
    )

    leaderboard_subject = st.selectbox(
        "Leaderboard-এর বিষয় নির্বাচন করুন",
        SUBJECTS,
        key="leaderboard_subject"
    )

    results_df = load_results()

    if results_df.empty:

        st.info(
            "এখনও কোনো ফলাফল পাওয়া যায়নি।"
        )

    else:

        subject_results = results_df[
            results_df["Subject"]
            == leaderboard_subject
        ].copy()

        if subject_results.empty:

            st.info(
                "এই বিষয়ে এখনো কোনো ফলাফল নেই।"
            )

        else:

            subject_results[
                "Score"
            ] = pd.to_numeric(
                subject_results["Score"],
                errors="coerce"
            )

            subject_results = (
                subject_results
                .sort_values(
                    by="Score",
                    ascending=False
                )
            )

            subject_results = (
                subject_results
                .reset_index(
                    drop=True
                )
            )

            subject_results.insert(
                0,
                "Position",
                range(
                    1,
                    len(subject_results) + 1
                )
            )

            st.dataframe(
                subject_results[
                    [
                        "Position",
                        "Student Name",
                        "Score",
                        "Total Marks",
                        "Submission Time"
                    ]
                ],
                use_container_width=True
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        font-size:13px;
    ">

        📝 <b>Job Efforts</b>

        <br>

        Smart preparation for competitive examinations

    </div>
    """,
    unsafe_allow_html=True
)
