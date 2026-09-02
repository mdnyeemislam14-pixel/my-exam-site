import streamlit as st
import pandas as pd
import random
import os
import time
from datetime import datetime

st.set_page_config(
    page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম",
    page_icon="📝",
    layout="centered"
)

# ==========================================
# 🎨 CSS DESIGN
# ==========================================
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppToolbar {visibility: hidden;}
div[data-testid="stStatusWidget"] {visibility: hidden;}
.viewerBadge_container__1QSob {visibility: hidden;}
#GithubIcon {visibility: hidden;}

html, body, [class*="css"] {
    font-size: 14px !important;
}

.question-card {
    background-color: #fcfcfc;
    border: 1px solid #e0e0e0;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.result-box {
    background: linear-gradient(135deg, #f6d365, #fda085);
    color: #2c3e50;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.fixed-timer {
    position: sticky;
    top: 0;
    z-index: 99999;
    background: linear-gradient(135deg, #ff4b4b, #ff9068);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 15px;
    font-size: 14px;
}

@media (max-width: 600px) {
    .question-card {
        padding: 14px;
        border-radius: 12px;
    }

    .stButton button {
        width: 100%;
    }

    .fixed-timer {
        top: 7px;
        padding: 7px 11px;
        font-size: 15px;
    }
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================
# 🏷️ HEADER
# ==========================================
st.markdown("""
<div style="
text-align:center;
padding:15px;
background:linear-gradient(135deg,#654ea3,#eaafc8);
border-radius:8px;
margin-bottom:15px;
color:white;
">
<h2 style="margin:0;font-size:22px;font-weight:bold;">
📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম
</h2>

<p style="margin:5px 0 8px 0;font-size:13px;">
বিসিএস, ব্যাংক, প্রাথমিক সহকারী শিক্ষক নিয়োগ এবং NTRCA সহ সকল সরকারি চাকরির প্রস্তুতির বিশ্বস্ত মাধ্যম
</p>

<h4 style="margin:0;font-size:15px;letter-spacing:1px;">
✨ Powered by
<span style="
background-color:#ffcc00;
color:#000;
padding:2px 8px;
border-radius:4px;
">
Job Efforts
</span>
</h4>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📁 FILE SETTINGS
# ==========================================
RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"
ADMIN_PASSWORD = "1234"

# ==========================================
# 🔐 SESSION STATE
# ==========================================
if "is_admin_logged_in" not in st.session_state:
    st.session_state["is_admin_logged_in"] = False

if "confirmed_student_name" not in st.session_state:
    st.session_state["confirmed_student_name"] = ""

if "exam_submitted" not in st.session_state:
    st.session_state["exam_submitted"] = False

if "last_result_data" not in st.session_state:
    st.session_state["last_result_data"] = None

if "selected_exam_subject" not in st.session_state:
    st.session_state["selected_exam_subject"] = ""

if "exam_in_progress" not in st.session_state:
    st.session_state["exam_in_progress"] = False

if "exam_start_time" not in st.session_state:
    st.session_state["exam_start_time"] = None

# ==========================================
# 🧭 NAVIGATION
# ==========================================
if (
    not st.session_state["is_admin_logged_in"]
    and not st.session_state["exam_in_progress"]
):
    mobile_nav = st.radio(
        "নেভিগেশন ট্যাব:",
        [
            "📝 পরীক্ষা দিন",
            "🏆 ক্লাসের মেধা তালিকা (Leaderboard)"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    student_menu = mobile_nav
    is_admin = False

elif st.session_state["exam_in_progress"]:
    student_menu = "📝 পরীক্ষা দিন"
    is_admin = False

else:
    student_menu = None
    is_admin = True

# ==========================================
# ⚙️ SIDEBAR
# ==========================================
st.sidebar.header("⚙️ কন্ট্রোল প্যানেল")

admin_menu = None

# ==========================================
# 🔐 ADMIN LOGIN
# ==========================================
if st.session_state["is_admin_logged_in"]:

    st.sidebar.success("✅ অ্যাডমিন মোড সক্রিয়!")

    if st.sidebar.button("🚪 লগ আউট করুন"):

        st.session_state["is_admin_logged_in"] = False
        st.session_state["confirmed_student_name"] = ""
        st.session_state["exam_submitted"] = False
        st.session_state["selected_exam_subject"] = ""
        st.session_state["exam_in_progress"] = False
        st.session_state["last_result_data"] = None

        st.rerun()

    admin_menu = st.sidebar.radio(
        "অ্যাডমিন মেনু:",
        [
            "📝 প্রশ্ন আপলোড ও সেটআপ",
            "📊 সকল শিক্ষার্থীর ফলাফল"
        ]
    )

    is_admin = True

else:

    if not st.session_state["exam_in_progress"]:

        with st.sidebar.expander("🔐 শিক্ষক/অ্যাডমিন লগইন"):

            entered_password = st.text_input(
                "পাসওয়ার্ড দিন:",
                type="password",
                key="admin_pwd_input"
            )

            if st.button("🔑 লগইন"):

                if entered_password == ADMIN_PASSWORD:

                    st.session_state["is_admin_logged_in"] = True
                    st.rerun()

                else:
                    st.error("❌ ভুল পাসওয়ার্ড!")

# ==========================================
# 📊 ADMIN RESULT PAGE
# ==========================================
if is_admin and admin_menu == "📊 সকল শিক্ষার্থীর ফলাফল":

    st.subheader("🏆 সকল শিক্ষার্থীর ফলাফল তালিকা")
    st.write("---")

    if os.path.exists(RESULT_FILE):

        res_df = pd.read_csv(RESULT_FILE)

        if not res_df.empty:

            if "Subject" in res_df.columns:

                subjects_list = (
                    ["সকল বিষয়"]
                    + res_df["Subject"].dropna().unique().tolist()
                )

                selected_filter_sub = st.selectbox(
                    "বিষয় সিলেক্ট করুন:",
                    subjects_list
                )

                if selected_filter_sub != "সকল বিষয়":
                    res_df = res_df[
                        res_df["Subject"] == selected_filter_sub
                    ]

            st.info(f"মোট খাতা জমা পড়েছে: {len(res_df)} টি")

            sorted_res = res_df.sort_values(
                by="Score",
                ascending=False
            ).reset_index(drop=True)

            sorted_res.index = sorted_res.index + 1

            st.dataframe(
                sorted_res,
                use_container_width=True
            )

            csv_data = sorted_res.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="📥 মেধা তালিকা ডাউনলোড (CSV)",
                data=csv_data,
                file_name="merit_list.csv",
                mime="text/csv"
            )

            st.write("---")

            if st.button(
                "🗑️ সব ফলাফল রিসেট করুন",
                type="secondary"
            ):

                if os.path.exists(RESULT_FILE):
                    os.remove(RESULT_FILE)

                st.success("সব ফলাফল মুছে ফেলা হয়েছে!")
                st.rerun()

        else:
            st.warning("এখনো কেউ পরীক্ষা দেয়নি।")

    else:
        st.warning("কোনো ফলাফল জমা হয়নি।")

# ==========================================
# 🏆 STUDENT LEADERBOARD
# ==========================================
elif (
    not is_admin
    and student_menu == "🏆 ক্লাসের মেধা তালিকা (Leaderboard)"
):

    st.subheader("🏆 ক্লাসের লাইভ মেধা তালিকা")
    st.write("---")

    if os.path.exists(RESULT_FILE):

        res_df = pd.read_csv(RESULT_FILE)

        if not res_df.empty:

            if "Subject" in res_df.columns:

                subjects_list = (
                    res_df["Subject"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                leaderboard_sub = st.selectbox(
                    "বিষয় সিলেক্ট করুন:",
                    subjects_list,
                    key="lb_sub"
                )

                res_df = res_df[
                    res_df["Subject"] == leaderboard_sub
                ]

            sorted_res = res_df.sort_values(
                by="Score",
                ascending=False
            ).reset_index(drop=True)

            sorted_res.index = sorted_res.index + 1

            st.dataframe(
                sorted_res,
                use_container_width=True
            )

        else:
            st.info("এখনো কোনো ফলাফল প্রকাশিত হয়নি।")

    else:
        st.info("এখনো কেউ পরীক্ষা দেয়নি।")

# ==========================================
# 📝 ADMIN QUESTION SETUP / STUDENT EXAM
# ==========================================
else:

    # ======================================
    # 👨‍🏫 ADMIN QUESTION UPLOAD
    # ======================================
    if is_admin:

        st.sidebar.markdown("### 📚 নতুন প্রশ্ন সংযোজন")

        subject_options = [
            "বাংলা",
            "English",
            "গণিত",
            "বিজ্ঞান",
            "বাংলাদেশের বিষয়াবলি",
            "আন্তর্জাতিক বিষয়াবলি",
            "ICT"
        ]

        subject_name = st.sidebar.selectbox(
            "বিষয়ের নাম:",
            subject_options
        )

        exam_duration = st.sidebar.number_input(
            "⏱️ সময় (মিনিট):",
            min_value=1,
            max_value=300,
            value=10
        )

        st.sidebar.markdown("---")

        input_mode = st.sidebar.radio(
            "পদ্ধতি:",
            [
                "টেক্সট পেস্ট (Easy Paste)",
                "ফাইল আপলোড"
            ],
            key="admin_input_mode"
        )

        # ==================================
        # TEXT IMPORT
        # ==================================
        if input_mode == "টেক্সট পেস্ট (Easy Paste)":

            pasted_text = st.sidebar.text_area(
                "প্রশ্ন পেস্ট করুন:",
                height=200,
                placeholder=(
                    "১. প্রশ্ন...\n"
                    "ক) ...\n"
                    "খ) ...\n"
                    "গ) ...\n"
                    "ঘ) ...\n"
                    "উত্তর: ক"
                )
            )

            if st.sidebar.button("📌 সেভ করুন"):

                if not pasted_text:

                    st.sidebar.error("⚠️ প্রশ্ন দিন।")

                else:

                    parsed_questions = []

                    blocks = pasted_text.strip().split("\n\n")

                    for block in blocks:

                        lines = [
                            line.strip()
                            for line in block.split("\n")
                            if line.strip()
                        ]

                        if len(lines) >= 5:

                            q_text = lines[0]
                            opt_a = lines[1]
                            opt_b = lines[2]
                            opt_c = lines[3]
                            opt_d = lines[4]

                            correct_ans = opt_a
                            explanation = "ব্যাখ্যা নেই।"

                            for line in lines[5:]:

                                if (
                                    line.startswith("উত্তর:")
                                    or line.startswith("Answer:")
                                ):

                                    ans_key = (
                                        line
                                        .replace("উত্তর:", "")
                                        .replace("Answer:", "")
                                        .strip()
                                        .lower()
                                    )

                                    if ans_key in ["ক", "a"]:
                                        correct_ans = opt_a

                                    elif ans_key in ["খ", "b"]:
                                        correct_ans = opt_b

                                    elif ans_key in ["গ", "c"]:
                                        correct_ans = opt_c

                                    elif ans_key in ["ঘ", "d"]:
                                        correct_ans = opt_d

                                    else:
                                        correct_ans = ans_key

                                elif (
                                    line.startswith("ব্যাখ্যা:")
                                    or line.startswith("Explanation:")
                                ):

                                    explanation = (
                                        line
                                        .replace("ব্যাখ্যা:", "")
                                        .replace("Explanation:", "")
                                        .strip()
                                    )

                            parsed_questions.append({
                                "Subject": subject_name,
                                "Question": q_text,
                                "Option_A": opt_a,
                                "Option_B": opt_b,
                                "Option_C": opt_c,
                                "Option_D": opt_d,
                                "Correct_Answer": correct_ans,
                                "Explanation": explanation
                            })

                    if parsed_questions:

                        new_df = pd.DataFrame(parsed_questions)

                        if os.path.exists(QUESTIONS_FILE):

                            existing_q_df = pd.read_csv(
                                QUESTIONS_FILE
                            )

                            existing_q_df = existing_q_df[
                                existing_q_df["Subject"]
                                != subject_name
                            ]

                            final_q_df = pd.concat(
                                [
                                    existing_q_df,
                                    new_df
                                ],
                                ignore_index=True
                            )

                        else:
                            final_q_df = new_df

                        final_q_df.to_csv(
                            QUESTIONS_FILE,
                            index=False
                        )

                        config_df = pd.DataFrame([
                            {
                                "Subject": subject_name,
                                "Duration": exam_duration
                            }
                        ])

                        if os.path.exists(CONFIG_FILE):

                            existing_conf = pd.read_csv(
                                CONFIG_FILE
                            )

                            existing_conf = existing_conf[
                                existing_conf["Subject"]
                                != subject_name
                            ]

                            final_conf = pd.concat(
                                [
                                    existing_conf,
                                    config_df
                                ],
                                ignore_index=True
                            )

                        else:
                            final_conf = config_df

                        final_conf.to_csv(
                            CONFIG_FILE,
                            index=False
                        )

                        st.sidebar.success(
                            "✅ সফলভাবে সেভ হয়েছে!"
                        )

        # ==================================
        # FILE UPLOAD
        # ==================================
        else:

            uploaded_file = st.sidebar.file_uploader(
                "ফাইল আপলোড (xlsx/csv):",
                type=["xlsx", "csv"]
            )

            if uploaded_file is not None:

                try:

                    if uploaded_file.name.endswith(".csv"):
                        raw_df = pd.read_csv(uploaded_file)
                    else:
                        raw_df = pd.read_excel(uploaded_file)

                    column_ranges = {
                        "বাংলা (A-F)": (0, 6),
                        "English (G-L)": (6, 12),
                        "গণিত (M-R)": (12, 18),
                        "বিজ্ঞান (S-X)": (18, 24),
                        "বাংলাদেশ (Y-AD)": (24, 30),
                        "আন্তর্জাতিক (AE-AJ)": (30, 36),
                        "ICT (AK-AP)": (36, 42)
                    }

                    selected_range_name = st.sidebar.selectbox(
                        "কলাম রেঞ্জ সিলেক্ট করুন:",
                        options=list(column_ranges.keys())
                    )

                    start_idx, end_idx = column_ranges[
                        selected_range_name
                    ]

                    if end_idx <= len(raw_df.columns):

                        sub_df = raw_df.iloc[
                            :,
                            start_idx:end_idx
                        ].copy()

                        sub_df.columns = [
                            "Question",
                            "Option_A",
                            "Option_B",
                            "Option_C",
                            "Option_D",
                            "Correct_Answer"
                        ]

                        sub_df = sub_df.dropna(
                            subset=["Question"]
                        ).reset_index(drop=True)

                        sub_df["Explanation"] = "ব্যাখ্যা নেই।"

                        st.sidebar.write(
                            f"🔍 ফাইল থেকে মোট প্রশ্ন পাওয়া গেছে: "
                            f"{len(sub_df)}টি"
                        )

                        upload_sub_mode = st.sidebar.radio(
                            "আপলোড করার পদ্ধতি বেছে নিন:",
                            [
                                "সব প্রশ্ন একসাথে (Bulk Import)",
                                "রেন্ডমলি এলোমেলোভাবে প্রশ্ন বাছাই",
                                "একটি একটি করে দেখে সিলেক্ট করুন (Manual)"
                            ]
                        )

                        questions_to_save = pd.DataFrame()

                        if (
                            upload_sub_mode
                            == "সব প্রশ্ন একসাথে (Bulk Import)"
                        ):

                            questions_to_save = sub_df

                        elif (
                            upload_sub_mode
                            == "রেন্ডমলি এলোমেলোভাবে প্রশ্ন বাছাই"
                        ):

                            sample_size = st.sidebar.number_input(
                                "কতটি প্রশ্ন রেন্ডমলি নিতে চান?",
                                min_value=1,
                                max_value=len(sub_df),
                                value=min(10, len(sub_df))
                            )

                            questions_to_save = (
                                sub_df
                                .sample(n=sample_size)
                                .reset_index(drop=True)
                            )

                            st.sidebar.success(
                                f"✨ স্বয়ংক্রিয়ভাবে "
                                f"{sample_size}টি প্রশ্ন বাছাই করা হয়েছে!"
                            )

                        else:

                            st.sidebar.markdown("---")

                            st.markdown(
                                "### 🔍 ম্যানুয়াল প্রশ্ন সিলেকশন প্রিভিউ"
                            )

                            selected_indices = []

                            for idx, row in sub_df.iterrows():

                                selected = st.checkbox(
                                    f"প্রশ্ন {idx+1}: "
                                    f"{str(row['Question'])[:50]}...",
                                    value=True,
                                    key=f"chk_q_{idx}"
                                )

                                if selected:
                                    selected_indices.append(idx)

                            questions_to_save = (
                                sub_df
                                .loc[selected_indices]
                                .reset_index(drop=True)
                            )

                        if st.sidebar.button(
                            "📌 ফাইল থেকে সেভ করুন"
                        ):

                            if not questions_to_save.empty:

                                questions_to_save[
                                    "Subject"
                                ] = subject_name

                                if os.path.exists(QUESTIONS_FILE):

                                    existing_q_df = pd.read_csv(
                                        QUESTIONS_FILE
                                    )

                                    existing_q_df = existing_q_df[
                                        existing_q_df["Subject"]
                                        != subject_name
                                    ]

                                    final_q_df = pd.concat(
                                        [
                                            existing_q_df,
                                            questions_to_save
                                        ],
                                        ignore_index=True
                                    )

                                else:
                                    final_q_df = questions_to_save

                                final_q_df.to_csv(
                                    QUESTIONS_FILE,
                                    index=False
                                )

                                config_df = pd.DataFrame([
                                    {
                                        "Subject": subject_name,
                                        "Duration": exam_duration
                                    }
                                ])

                                if os.path.exists(CONFIG_FILE):

                                    existing_conf = pd.read_csv(
                                        CONFIG_FILE
                                    )

                                    existing_conf = existing_conf[
                                        existing_conf["Subject"]
                                        != subject_name
                                    ]

                                    final_conf = pd.concat(
                                        [
                                            existing_conf,
                                            config_df
                                        ],
                                        ignore_index=True
                                    )

                                else:
                                    final_conf = config_df

                                final_conf.to_csv(
                                    CONFIG_FILE,
                                    index=False
                                )

                                st.sidebar.success(
                                    "✅ ফাইল থেকে সফলভাবে সেভ হয়েছে!"
                                )

                            else:

                                st.sidebar.error(
                                    "⚠️ কোনো প্রশ্ন সিলেক্ট করা হয়নি।"
                                )

                    else:

                        st.sidebar.error(
                            "⚠️ আপনার ফাইলের কলাম সংখ্যা "
                            "নির্ধারিত রেঞ্জের চেয়ে কম। "
                            "সঠিক ফাইল বা কলাম রেঞ্জ নির্বাচন করুন।"
                        )

                except Exception as e:

                    st.sidebar.error(
                        f"ত্রুটি: {e}"
                    )

        # ==================================
        # SAVED QUESTIONS PREVIEW
        # ==================================
        st.write("---")
        st.subheader("📂 সংরক্ষিত বিষয়সমূহ (প্রশ্ন প্রিভিউ সহ)")

        if os.path.exists(QUESTIONS_FILE):

            q_check_df = pd.read_csv(QUESTIONS_FILE)

            if (
                not q_check_df.empty
                and "Subject" in q_check_df.columns
            ):

                for sub in q_check_df["Subject"].unique().tolist():

                    sub_q_df = (
                        q_check_df[
                            q_check_df["Subject"] == sub
                        ]
                        .reset_index(drop=True)
                    )

                    count = len(sub_q_df)

                    with st.expander(
                        f"📁 {sub} (প্রশ্ন: {count}টি)"
                    ):

                        for i, q_row in sub_q_df.iterrows():

                            st.markdown(
                                f"""
                                <div style="
                                background-color:#fcfcfc;
                                border:1px solid #e0e0e0;
                                padding:12px;
                                border-radius:6px;
                                margin-bottom:10px;
                                ">
                                <strong>
                                প্রশ্ন {i+1}: {q_row['Question']}
                                </strong><br>
                                • {q_row['Option_A']}<br>
                                • {q_row['Option_B']}<br>
                                • {q_row['Option_C']}<br>
                                • {q_row['Option_D']}<br>
                                <span style="
                                color:green;
                                font-weight:bold;
                                ">
                                সঠিক উত্তর:
                                {q_row['Correct_Answer']}
                                </span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if st.button(
                            f"❌ '{sub}' এর সব প্রশ্ন মুছুন",
                            key=f"del_{sub}"
                        ):

                            q_check_df[
                                q_check_df["Subject"] != sub
                            ].to_csv(
                                QUESTIONS_FILE,
                                index=False
                            )

                            st.rerun()

    # ======================================
    # 👨‍🎓 STUDENT EXAM
    # ======================================
    else:

        all_q_df = (
            pd.read_csv(QUESTIONS_FILE)
            if os.path.exists(QUESTIONS_FILE)
            else pd.DataFrame()
        )

        if (
            not all_q_df.empty
            and "Subject" in all_q_df.columns
        ):

            available_subjects = (
                all_q_df["Subject"]
                .dropna()
                .unique()
                .tolist()
            )

            # ==================================
            # RESULT PAGE
            # ==================================
            if st.session_state["exam_submitted"]:

                res_info = st.session_state["last_result_data"]

                if res_info:

                    if st.button(
                        "⬅️ নতুন পরীক্ষা / হোম",
                        type="secondary"
                    ):

                        st.session_state["exam_submitted"] = False
                        st.session_state["confirmed_student_name"] = ""
                        st.session_state["selected_exam_subject"] = ""
                        st.session_state["exam_in_progress"] = False
                        st.session_state["last_result_data"] = None

                        st.rerun()

                    st.markdown(
                        f"""
                        <div class="result-box">
                        <h2>
                        🎉 অভিনন্দন, {res_info['student_name']}!
                        </h2>

                        <p style="font-size:18px;">
                        বিষয়: {res_info['subject']}
                        </p>

                        <h1>
                        প্রাপ্ত নম্বর:
                        {res_info['score']} / {res_info['total']}
                        </h1>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.subheader(
                        "📊 বিস্তারিত উত্তরমালা "
                        "(৪ অপশনসহ সঠিক ও ভুল মার্কিং)"
                    )

                    st.write("---")

                    for i, row in res_info["active_df"].iterrows():

                        ans = res_info["user_answers"].get(i)

                        raw_correct = str(
                            row["Correct_Answer"]
                        ).strip()

                        raw_correct_lower = raw_correct.lower()

                        opts = [
                            str(row["Option_A"]).strip(),
                            str(row["Option_B"]).strip(),
                            str(row["Option_C"]).strip(),
                            str(row["Option_D"]).strip()
                        ]

                        correct_val = ""

                        for opt in opts:

                            opt_lower = opt.lower()

                            if (
                                raw_correct_lower in ["ক", "a"]
                                and (
                                    opt.startswith("ক")
                                    or opt_lower.startswith("a.")
                                )
                            ):
                                correct_val = opt

                            elif (
                                raw_correct_lower in ["খ", "b"]
                                and (
                                    opt.startswith("খ")
                                    or opt_lower.startswith("b.")
                                )
                            ):
                                correct_val = opt

                            elif (
                                raw_correct_lower in ["গ", "c"]
                                and (
                                    opt.startswith("গ")
                                    or opt_lower.startswith("c.")
                                )
                            ):
                                correct_val = opt

                            elif (
                                raw_correct_lower in ["ঘ", "d"]
                                and (
                                    opt.startswith("ঘ")
                                    or opt_lower.startswith("d.")
                                )
                            ):
                                correct_val = opt

                            elif (
                                raw_correct_lower == opt_lower
                                or raw_correct_lower in opt_lower
                                or opt_lower in raw_correct_lower
                            ):
                                correct_val = opt

                        if not correct_val:
                            correct_val = raw_correct

                        options_html = ""

                        for opt in opts:

                            opt_lower = opt.lower()
                            c_val_lower = correct_val.lower()

                            is_correct_option = (
                                opt == correct_val
                                or opt_lower == c_val_lower
                                or c_val_lower in opt_lower
                                or opt_lower in c_val_lower
                                or (
                                    raw_correct_lower in ["ক", "a"]
                                    and (
                                        opt.startswith("ক")
                                        or opt_lower.startswith("a.")
                                    )
                                )
                                or (
                                    raw_correct_lower in ["খ", "b"]
                                    and (
                                        opt.startswith("খ")
                                        or opt_lower.startswith("b.")
                                    )
                                )
                                or (
                                    raw_correct_lower in ["গ", "c"]
                                    and (
                                        opt.startswith("গ")
                                        or opt_lower.startswith("c.")
                                    )
                                )
                                or (
                                    raw_correct_lower in ["ঘ", "d"]
                                    and (
                                        opt.startswith("ঘ")
                                        or opt_lower.startswith("d.")
                                    )
                                )
                            )

                            is_user_choice = (
                                ans is not None
                                and str(ans).strip() == opt
                            )

                            if (
                                is_correct_option
                                and is_user_choice
                            ):

                                options_html += (
                                    "<div style='color:green;"
                                    "font-weight:bold;'>"
                                    f"✅ {opt} "
                                    "(আপনার সঠিক উত্তর)"
                                    "</div>"
                                )

                            elif is_correct_option:

                                options_html += (
                                    "<div style='color:green;"
                                    "font-weight:bold;'>"
                                    f"✅ {opt} (সঠিক উত্তর)"
                                    "</div>"
                                )

                            elif (
                                is_user_choice
                                and not is_correct_option
                            ):

                                options_html += (
                                    "<div style='color:red;"
                                    "font-weight:bold;'>"
                                    f"❌ {opt} "
                                    "(আপনার ভুল উত্তর)"
                                    "</div>"
                                )

                            else:

                                options_html += (
                                    "<div style='color:#555;'>"
                                    f"• {opt}"
                                    "</div>"
                                )

                        st.markdown(
                            f"""
                            <div class="question-card">
                            <strong>
                            প্রশ্ন {i+1}: {str(row['Question'])}
                            </strong><br><br>
                            {options_html}
                            <hr>
                            <small>
                            💡 ব্যাখ্যা:
                            {row['Explanation']}
                            </small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # ==================================
            # HOME / START EXAM
            # ==================================
            else:

                if not st.session_state["exam_in_progress"]:

                    st.subheader(
                        "📚 পরীক্ষার বিষয় নির্বাচন করুন"
                    )

                    selected_subject = st.selectbox(
                        "বিষয়:",
                        available_subjects
                    )

                    st.write("---")

                    df = (
                        all_q_df[
                            all_q_df["Subject"]
                            == selected_subject
                        ]
                        .reset_index(drop=True)
                    )

                    duration = 10

                    if os.path.exists(CONFIG_FILE):

                        conf_df = pd.read_csv(CONFIG_FILE)

                        match_conf = conf_df[
                            conf_df["Subject"]
                            == selected_subject
                        ]

                        if not match_conf.empty:
                            duration = int(
                                match_conf.iloc[0]["Duration"]
                            )

                    if not df.empty:

                        st.info(
                            f"📌 বিষয়: {selected_subject} | "
                            f"⏱️ সময়: {duration} মিনিট | "
                            f"🎯 প্রশ্ন: {len(df)}টি"
                        )

                        with st.container(border=True):

                            st.markdown(
                                "#### ✍️ পরীক্ষার্থীর তথ্য"
                            )

                            student_name = st.text_input(
                                "আপনার পূর্ণ নাম লিখুন:",
                                placeholder="এখানে নাম লিখুন",
                                key="input_student_name"
                            )

                            if st.button(
                                "➔ পরীক্ষা শুরু করুন",
                                type="primary"
                            ):

                                if student_name.strip():

                                    st.session_state[
                                        "confirmed_student_name"
                                    ] = student_name.strip()

                                    st.session_state[
                                        "selected_exam_subject"
                                    ] = selected_subject

                                    st.session_state[
                                        "exam_start_time"
                                    ] = time.time()

                                    st.session_state[
                                        "exam_in_progress"
                                    ] = True

                                    st.session_state[
                                        "exam_submitted"
                                    ] = False

                                    st.rerun()

                                else:
                                    st.error("⚠️ নাম লিখুন।")

                # ==================================
                # EXAM IN PROGRESS
                # ==================================
                else:

                    selected_subject = st.session_state.get(
                        "selected_exam_subject",
                        available_subjects[0]
                    )

                    df = (
                        all_q_df[
                            all_q_df["Subject"]
                            == selected_subject
                        ]
                        .reset_index(drop=True)
                    )

                    duration = 10

                    if os.path.exists(CONFIG_FILE):

                        conf_df = pd.read_csv(CONFIG_FILE)

                        match_conf = conf_df[
                            conf_df["Subject"]
                            == selected_subject
                        ]

                        if not match_conf.empty:
                            duration = int(
                                match_conf.iloc[0]["Duration"]
                            )

                    current_student = (
                        st.session_state[
                            "confirmed_student_name"
                        ]
                    )

                    active_df = df.copy()

                    total_seconds = duration * 60

                    if (
                        st.session_state.get(
                            "exam_start_time"
                        ) is None
                    ):

                        st.session_state[
                            "exam_start_time"
                        ] = time.time()

                    elapsed_seconds = int(
                        time.time()
                        - st.session_state["exam_start_time"]
                    )

                    remaining_seconds = max(
                        0,
                        total_seconds - elapsed_seconds
                    )

                    mins = remaining_seconds // 60
                    secs = remaining_seconds % 60

                    # ==================================
                    # ⏱️ TIMER
                    # ==================================
                    st.markdown(
                        f"""
                        <div class="fixed-timer">
                        ⏳ বাকি সময়:
                        <span id="live-timer">
                        {mins:02d}:{secs:02d}
                        </span>
                        </div>

                        <script>
                        (function() {{
                            let remaining = {remaining_seconds};

                            const timer =
                                document.getElementById(
                                    "live-timer"
                                );

                            function updateTimer() {{

                                if (remaining <= 0) {{

                                    timer.innerHTML = "00:00";

                                    const buttons =
                                        window.parent.document
                                        .querySelectorAll(
                                            "button"
                                        );

                                    buttons.forEach(
                                        function(button) {{

                                            if (
                                                button.innerText
                                                .includes(
                                                    "পরীক্ষা জমা দিন"
                                                )
                                            ) {{
                                                button.click();
                                            }}

                                        }}
                                    );

                                    return;
                                }}

                                let m =
                                    Math.floor(
                                        remaining / 60
                                    );

                                let s =
                                    remaining % 60;

                                timer.innerHTML =
                                    String(m).padStart(2, "0")
                                    + ":"
                                    + String(s).padStart(2, "0");

                                remaining--;
                            }}

                            updateTimer();

                            setInterval(
                                updateTimer,
                                1000
                            );
                        }})();
                        </script>
                        """,
                        unsafe_allow_html=True
                    )

                    st.success(
                        f"পরীক্ষার্থী: **{current_student}** "
                        f"({selected_subject})"
                    )

                    st.write("---")

                    # ==================================
                    # QUESTIONS
                    # ==================================
                    user_answers = {}

                    for i, row in active_df.iterrows():

                        options_list = [
                            str(row["Option_A"]),
                            str(row["Option_B"]),
                            str(row["Option_C"]),
                            str(row["Option_D"])
                        ]

                        with st.container():

                            st.markdown(
                                f"""
                                <div class="question-card">
                                <strong>
                                প্রশ্ন {i+1}:
                                {str(row['Question'])}
                                </strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            user_answers[i] = st.radio(
                                f"উত্তর নির্বাচন করুন "
                                f"(প্রশ্ন {i+1}):",
                                options_list,
                                index=None,
                                key=f"q_{i}_{selected_subject}",
                                label_visibility="collapsed"
                            )

                    # ==================================
                    # SUBMIT EXAM
                    # ==================================
                    if st.button(
                        "পরীক্ষা জমা দিন",
                        type="primary"
                    ):

                        score = 0

                        for i, row in active_df.iterrows():

                            ans = user_answers.get(i)

                            raw_c = str(
                                row["Correct_Answer"]
                            ).strip().lower()

                            options = [
                                str(row["Option_A"]).strip(),
                                str(row["Option_B"]).strip(),
                                str(row["Option_C"]).strip(),
                                str(row["Option_D"]).strip()
                            ]

                            correct_v = options[0]

                            for option in options:

                                option_lower = option.lower()

                                if (
                                    raw_c in ["ক", "a"]
                                    and (
                                        option.startswith("ক")
                                        or option_lower.startswith("a.")
                                    )
                                ):
                                    correct_v = option

                                elif (
                                    raw_c in ["খ", "b"]
                                    and (
                                        option.startswith("খ")
                                        or option_lower.startswith("b.")
                                    )
                                ):
                                    correct_v = option

                                elif (
                                    raw_c in ["গ", "c"]
                                    and (
                                        option.startswith("গ")
                                        or option_lower.startswith("c.")
                                    )
                                ):
                                    correct_v = option

                                elif (
                                    raw_c in ["ঘ", "d"]
                                    and (
                                        option.startswith("ঘ")
                                        or option_lower.startswith("d.")
                                    )
                                ):
                                    correct_v = option

                                elif (
                                    raw_c == option_lower
                                    or raw_c in option_lower
                                    or option_lower in raw_c
                                ):
                                    correct_v = option

                            if (
                                ans is not None
                                and (
                                    str(ans).strip()
                                    == correct_v
                                    or
                                    str(ans).strip().lower()
                                    == correct_v.lower()
                                )
                            ):
                                score += 1

                        current_time = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        new_result = pd.DataFrame([
                            {
                                "Student Name": current_student,
                                "Subject": selected_subject,
                                "Score": score,
                                "Total Marks": len(active_df),
                                "Submission Time": current_time
                            }
                        ])

                        if os.path.exists(RESULT_FILE):

                            updated_res = pd.concat(
                                [
                                    pd.read_csv(RESULT_FILE),
                                    new_result
                                ],
                                ignore_index=True
                            )

                        else:
                            updated_res = new_result

                        updated_res.to_csv(
                            RESULT_FILE,
                            index=False
                        )

                        st.session_state[
                            "exam_submitted"
                        ] = True

                        st.session_state[
                            "exam_in_progress"
                        ] = False

                        st.session_state[
                            "last_result_data"
                        ] = {
                            "student_name": current_student,
                            "subject": selected_subject,
                            "score": score,
                            "total": len(active_df),
                            "active_df": active_df,
                            "user_answers": user_answers
                        }

                        st.balloons()

                        st.rerun()

        else:

            st.warning(
                "⚠️ বর্তমানে কোনো প্রশ্ন সেট করা নেই।"
            )
