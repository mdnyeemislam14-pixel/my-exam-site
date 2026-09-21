from datetime import datetime
import os
import random
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম", page_icon="📝", layout="wide"
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {visibility: hidden;}
    
    html, body, [class*="css"] {
        font-size: 14px !important;
    }
    
    .stApp::before {
        content: "Job Efforts";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-30deg);
        font-size: 8vw;
        font-weight: bold;
        color: rgba(100, 100, 100, 0.05);
        z-index: 0;
        pointer-events: none;
        white-space: nowrap;
        user-select: none;
    }
    
    .question-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        position: relative;
        z-index: 1;
    }
    
    .result-box {
        background: linear-gradient(135deg, #f6d365, #fda085);
        color: #2c3e50;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# শীর্ষ ব্যানার
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #4e54c8, #8f94fb); border-radius: 10px; margin-bottom: 20px; color: white; position: relative; z-index: 1;">
        <h2 style="margin: 0; font-size: 26px; font-weight: bold;">📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম</h2>
        <p style="margin: 8px 0 10px 0; font-size: 14px; opacity: 0.95;">বিসিএস, ব্যাংক, প্রাথমিক সহকারী শিক্ষক নিয়োগ এবং NTRCA সহ সকল সরকারি চাকরির প্রস্তুতির বিশ্বস্ত মাধ্যম</p>
        <h4 style="margin: 0; font-size: 16px; letter-spacing: 1px;">✨ Powered by <span style="background-color: #ffcc00; color: #000; padding: 2px 10px; border-radius: 4px;">Job Efforts</span></h4>
    </div>
""",
    unsafe_allow_html=True,
)

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"
ADMIN_PASSWORD = "1234"

# জীববিজ্ঞানের অধ্যায়সমূহ
bio_chapters_master = [
    "প্রথম অধ্যায়: জীবনপাঠ",
    "দ্বিতীয় অধ্যায়: জীবকোষ ও টিস্যু",
    "তৃতীয় অধ্যায়: কোষ বিভাজন",
    "চতুর্থ অধ্যায়: জীবনীশক্তি",
    "পঞ্চম অধ্যায়: খাদ্য, পুষ্টি এবং পরিপাক",
    "ষষ্ঠ অধ্যায়: জীবে পরিবহন",
    "সপ্তম অধ্যায়: গ্যাসীয় বিনিময়",
    "অষ্টম অধ্যায়: রেচন প্রক্রিয়া",
]

# সেশন স্টেট ইনিশিয়ালাইজেশন
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
if "selected_bio_chapter" not in st.session_state:
    st.session_state["selected_bio_chapter"] = ""
if "exam_in_progress" not in st.session_state:
    st.session_state["exam_in_progress"] = False

# টপ নেভিগেশন বার
col_nav1, col_nav2, col_nav3 = st.columns([6, 3, 3])

with col_nav3:
    if not st.session_state["exam_in_progress"]:
        if st.session_state["is_admin_logged_in"]:
            if st.button("🚪 অ্যাডমিন লগ আউট", use_container_width=True):
                st.session_state["is_admin_logged_in"] = False
                st.session_state["confirmed_student_name"] = ""
                st.session_state["exam_submitted"] = False
                st.session_state["selected_exam_subject"] = ""
                st.session_state["selected_bio_chapter"] = ""
                st.session_state["exam_in_progress"] = False
                st.rerun()
        else:
            with st.popover("🔐 অ্যাডমিন লগইন", use_container_width=True):
                entered_password = st.text_input(
                    "পাসওয়ার্ড দিন:", type="password", key="admin_pwd_input"
                )
                if st.button("🔑 লগইন করুন", use_container_width=True):
                    if entered_password == ADMIN_PASSWORD:
                        st.session_state["is_admin_logged_in"] = True
                        st.rerun()
                    else:
                        st.error("❌ ভুল পাসওয়ার্ড!")

st.write("---")

is_admin = st.session_state["is_admin_logged_in"]
all_subjects_master = [
    "বাংলা",
    "English",
    "গণিত",
    "বিজ্ঞান",
    "জীববিজ্ঞান",
    "বাংলাদেশের বিষয়াবলি",
    "আন্তর্জাতিক বিষয়াবলি",
    "ICT",
]

if is_admin:
    admin_menu = st.radio(
        "অ্যাডমিন নেভিগেশন:",
        [
            "📊 অ্যাডমিন ড্যাশবোর্ড ও প্রশ্ন ম্যানেজমেন্ট",
            "📝 বিষয়ভিত্তিক প্রশ্ন আপলোড ও স্ট্যাটাস",
            "📊 সকল শিক্ষার্থীর ফলাফল",
        ],
        horizontal=True,
    )
    st.write("")

    # --- অ্যাডমিন ড্যাশবোর্ড ও প্রশ্ন ম্যানেজমেন্ট পেজ ---
    if admin_menu == "📊 অ্যাডমিন ড্যাশবোর্ড ও প্রশ্ন ম্যানেজমেন্ট":
        st.subheader("📊 এডমিন ওভারভিউ ও প্রশ্ন এডিট/ডিলিট প্যানেল")
        st.write("---")

        q_df = (
            pd.read_csv(QUESTIONS_FILE) if os.path.exists(QUESTIONS_FILE) else pd.DataFrame()
        )
        res_df = (
            pd.read_csv(RESULT_FILE) if os.path.exists(RESULT_FILE) else pd.DataFrame()
        )

        total_q_count = len(q_df) if not q_df.empty else 0
        total_exam_given = len(res_df) if not res_df.empty else 0
        active_subs_count = (
            q_df["Subject"].nunique()
            if not q_df.empty and "Subject" in q_df.columns
            else 0
        )

        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.metric("📚 মোট সংরক্ষিত প্রশ্ন", f"{total_q_count} টি")
        col_d2.metric("🟢 চালু থাকা বিষয়", f"{active_subs_count} টি")
        col_d3.metric("📝 মোট পরীক্ষা সম্পন্ন", f"{total_exam_given} বার")

        st.write("---")
        st.markdown("##### 📌 বিষয়ভিত্তিক প্রশ্ন সংখ্যা:")
        if not q_df.empty and "Subject" in q_df.columns:
            sub_counts = q_df["Subject"].value_counts().reset_index()
            sub_counts.columns = ["বিষয়", "প্রশ্ন সংখ্যা"]
            st.dataframe(sub_counts, use_container_width=True)

            st.write("---")
            st.subheader("⚙️ প্রশ্ন ম্যানেজমেন্ট (এডিট বা ডিলিট করুন)")
            
            subjects_list_for_view = ["সকল বিষয়"] + q_df["Subject"].unique().tolist()
            selected_view_sub = st.selectbox(
                "বিষয় নির্বাচন করুন:", subjects_list_for_view, key="view_q_sub"
            )

            if selected_view_sub == "সকল বিষয়":
                filtered_df = q_df.copy()
            else:
                filtered_df = q_df[q_df["Subject"] == selected_view_sub].copy()

            for idx, row in filtered_df.iterrows():
                with st.expander(f"প্রশ্ন {idx+1}: {str(row['Question'])[:60]}... (বিষয়: {row['Subject']})"):
                    with st.form(key=f"edit_form_{idx}"):
                        new_subject = st.text_input("বিষয়/অধ্যায়:", value=row["Subject"])
                        new_q = st.text_area("প্রশ্ন:", value=row["Question"])
                        new_a = st.text_input("অপশন ক:", value=row["Option_A"])
                        new_b = st.text_input("অপশন খ:", value=row["Option_B"])
                        new_c = st.text_input("অপশন গ:", value=row["Option_C"])
                        new_d = st.text_input("অপশন ঘ:", value=row["Option_D"])
                        new_ans = st.text_input("সঠিক উত্তর:", value=str(row["Correct_Answer"]))
                        new_exp = st.text_area("ব্যাখ্যা:", value=str(row["Explanation"]))

                        col_f1, col_f2 = st.columns(2)
                        update_btn = col_f1.form_submit_button("💾 আপডেট করুন", use_container_width=True)
                        delete_btn = col_f2.form_submit_button("🗑️ এই প্রশ্নটি ডিলিট করুন", use_container_width=True, type="secondary")

                        if update_btn:
                            q_df.at[idx, "Subject"] = new_subject
                            q_df.at[idx, "Question"] = new_q
                            q_df.at[idx, "Option_A"] = new_a
                            q_df.at[idx, "Option_B"] = new_b
                            q_df.at[idx, "Option_C"] = new_c
                            q_df.at[idx, "Option_D"] = new_d
                            q_df.at[idx, "Correct_Answer"] = new_ans
                            q_df.at[idx, "Explanation"] = new_exp
                            q_df.to_csv(QUESTIONS_FILE, index=False)
                            st.success("✅ প্রশ্ন সফলভাবে আপডেট করা হয়েছে!")
                            st.rerun()

                        if delete_btn:
                            q_df = q_df.drop(idx).reset_index(drop=True)
                            q_df.to_csv(QUESTIONS_FILE, index=False)
                            st.success("🗑️ প্রশ্নটি সফলভাবে মুছে ফেলা হয়েছে!")
                            st.rerun()
        else:
            st.info("এখনো কোনো বিষয়ে প্রশ্ন আপলোড করা হয়নি।")

    elif admin_menu == "📊 সকল শিক্ষার্থীর ফলাফল":
        st.subheader("🏆 সকল শিক্ষার্থীর ফলাফল তালিকা")
        st.write("---")
        if os.path.exists(RESULT_FILE):
            res_df = pd.read_csv(RESULT_FILE)
            if not res_df.empty:
                if "Subject" in res_df.columns:
                    subjects_list = ["সকল বিষয়"] + res_df["Subject"].unique().tolist()
                    selected_filter_sub = st.selectbox(
                        "বিষয় সিলেক্ট করুন:", subjects_list
                    )
                    if selected_filter_sub != "সকল বিষয়":
                        res_df = res_df[res_df["Subject"] == selected_filter_sub]

                st.info(f"মোট খাতা জমা পড়েছে: {len(res_df)} টি")
                sorted_res = (
                    res_df.sort_values(by="Score", ascending=False)
                    .reset_index(drop=True)
                )
                sorted_res.index = sorted_res.index + 1
                st.dataframe(sorted_res, use_container_width=True)

                csv_data = sorted_res.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 মেধা তালিকা ডাউনলোড (CSV)",
                    data=csv_data,
                    file_name="merit_list.csv",
                    mime="text/csv",
                )

                st.write("---")
                if st.button("🗑️ সব ফলাফল রিসেট করুন", type="secondary"):
                    if os.path.exists(RESULT_FILE):
                        os.remove(RESULT_FILE)
                        st.success("সব ফলাফল মুছে ফেলা হয়েছে!")
                        st.rerun()
            else:
                st.warning("এখনো কেউ পরীক্ষা দেয়নি।")
        else:
            st.warning("কোনো ফলাফল জমা হয়নি।")

    else:
        st.subheader("📚 আলাদা বিষয়ভিত্তিক প্রশ্ন সংযোজন ও স্ট্যাটাস নিয়ন্ত্রণ")

        saved_q_df = (
            pd.read_csv(QUESTIONS_FILE) if os.path.exists(QUESTIONS_FILE) else pd.DataFrame()
        )
        active_subjects = (
            saved_q_df["Subject"].unique().tolist()
            if not saved_q_df.empty and "Subject" in saved_q_df.columns
            else []
        )

        st.markdown("##### 📌 সকল বিষয়ের লাইভ স্ট্যাটাস ওভারভিউ:")
        status_cols = st.columns(len(all_subjects_master))
        for idx, sub in enumerate(all_subjects_master):
            with status_cols[idx]:
                if sub in active_subjects or any(s.startswith(f"{sub} -") for s in active_subjects):
                    st.markdown(
                        f"<div style='background:#f0f4ff; border: 1.5px solid #2563eb;"
                        f" padding:6px; border-radius:6px; text-align:center;"
                        f" font-size:11px;'><b"
                        f" style='color:#1e3d59;'>{sub}</b><br><span"
                        f" style='color:#137333;'>🟢 পরীক্ষা আছে</span></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div style='background:#f8f9fa; border: 1.5px solid #dadce0;"
                        f" padding:6px; border-radius:6px; text-align:center;"
                        f" font-size:11px;'><b"
                        f" style='color:#5f6368;'>{sub}</b><br><span"
                        f" style='color:#5f6368;'>⚪ পরীক্ষা নেই</span></div>",
                        unsafe_allow_html=True,
                    )

        st.write("---")
        subject_name = st.selectbox("বিষয় নির্বাচন করুন:", all_subjects_master)

        current_subject_key = subject_name
        if subject_name == "জীববিজ্ঞান":
            selected_chapter = st.selectbox("অধ্যায় নির্বাচন করুন:", bio_chapters_master)
            current_subject_key = f"জীববিজ্ঞান - {selected_chapter}"
        else:
            selected_chapter = ""

        exam_duration = st.number_input(
            "⏱️ পরীক্ষার সময় (মিনিট):", min_value=1, max_value=300, value=10
        )

        st.markdown("---")
        input_mode = st.radio(
            "ইনপুট পদ্ধতি:",
            ["টেক্সট পেস্ট (Easy Paste)", "ফাইল আপলোড (এক্সেল/সিএসভি)"],
            key="admin_input_mode",
            horizontal=True,
        )

        if input_mode == "টেক্সট পেস্ট (Easy Paste)":
            # পূর্বে সেভ করা প্রশ্নগুলো লোড করে টেক্সট ফরমেটে রূপান্তর করা যাতে বক্সে দেখা যায়
            existing_text_for_subject = ""
            if not saved_q_df.empty and "Subject" in saved_q_df.columns:
                sub_matched_df = saved_q_df[saved_q_df["Subject"] == current_subject_key]
                if not sub_matched_df.empty:
                    block_list = []
                    for _, r in sub_matched_df.iterrows():
                        q_block = f"{r['Question']}\n{r['Option_A']}\n{r['Option_B']}\n{r['Option_C']}\n{r['Option_D']}\nউত্তর: {r['Correct_Answer']}\nব্যাখ্যা: {r['Explanation']}"
                        block_list.append(q_block)
                    existing_text_for_subject = "\n\n".join(block_list)

            pasted_text = st.text_area(
                f"'{current_subject_key}'-এর সংরক্ষিত প্রশ্নসমূহ (এখানে দেখতে পাবেন, নতুন যোগ করতে চাইলে নিচে লিখতে পারেন):",
                value=existing_text_for_subject,
                height=250,
                placeholder=(
                    "১. প্রশ্ন...\nক) ...\nখ) ...\nগ) ...\nঘ) ...\nউত্তর: ক"
                ),
            )

            if st.button("📌 এই বিষয়ের প্রশ্ন সেভ/আপডেট করুন"):
                if not pasted_text:
                    st.error("⚠️ প্রশ্ন দিন।")
                else:
                    parsed_questions = []
                    blocks = pasted_text.strip().split("\n\n")
                    for block in blocks:
                        lines = [
                            line.strip() for line in block.split("\n") if line.strip()
                        ]
                        if len(lines) >= 5:
                            q_text, opt_a, opt_b, opt_c, opt_d = (
                                lines[0],
                                lines[1],
                                lines[2],
                                lines[3],
                                lines[4],
                            )
                            correct_ans, explanation = opt_a, "ব্যাখ্যা নেই।"

                            for l in lines[5:]:
                                if l.startswith("উত্তর:") or l.startswith("Answer:"):
                                    ans_key = (
                                        l.replace("উত্তর:", "")
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
                                elif l.startswith("ব্যাখ্যা:") or l.startswith("Explanation:"):
                                    explanation = (
                                        l.replace("ব্যাখ্যা:", "")
                                        .replace("Explanation:", "")
                                        .strip()
                                    )

                            parsed_questions.append({
                                "Subject": current_subject_key,
                                "Question": q_text,
                                "Option_A": opt_a,
                                "Option_B": opt_b,
                                "Option_C": opt_c,
                                "Option_D": opt_d,
                                "Correct_Answer": correct_ans,
                                "Explanation": explanation,
                            })

                    if parsed_questions:
                        new_df = pd.DataFrame(parsed_questions)
                        if os.path.exists(QUESTIONS_FILE):
                            existing_q_df = pd.read_csv(QUESTIONS_FILE)
                            # বর্তমান সাবজেক্টের পুরোনো প্রশ্ন বাদ দিয়ে নতুন ও আপডেট করা প্রশ্নগুলো একবারে বসিয়ে দেওয়া হলো
                            existing_q_df = existing_q_df[
                                existing_q_df["Subject"] != current_subject_key
                            ]
                            final_q_df = pd.concat(
                                [existing_q_df, new_df], ignore_index=True
                            )
                        else:
                            final_q_df = new_df

                        final_q_df.to_csv(QUESTIONS_FILE, index=False)
                        config_df = pd.DataFrame(
                            [{"Subject": current_subject_key, "Duration": exam_duration}]
                        )

                        if os.path.exists(CONFIG_FILE):
                            existing_conf = pd.read_csv(CONFIG_FILE)
                            existing_conf = existing_conf[
                                existing_conf["Subject"] != current_subject_key
                            ]
                            final_conf = pd.concat(
                                [existing_conf, config_df], ignore_index=True
                            )
                        else:
                            final_conf = config_df
                        final_conf.to_csv(CONFIG_FILE, index=False)
                        st.success(
                            f"✅ '{current_subject_key}' এর প্রশ্নসমূহ সফলভাবে আপডেট ও সেভ হয়েছে!"
                        )
                        st.rerun()

        else:
            uploaded_file = st.file_uploader(
                "ফাইল আপলোড (xlsx/csv):",
                type=["xlsx", "csv"],
                key="admin_file_uploader_main",
            )
            if uploaded_file is not None:
                try:
                    raw_df = (
                        pd.read_csv(uploaded_file)
                        if uploaded_file.name.endswith(".csv")
                        else pd.read_excel(uploaded_file)
                    )
                    column_ranges = {
                        "বাংলা (A-F)": (0, 6),
                        "English (G-L)": (6, 12),
                        "গণিত (M-R)": (12, 18),
                        "বিজ্ঞান (S-X)": (18, 24),
                        "বাংলাদেশের বিষয়াবলি (Y-AD)": (24, 30),
                        "আন্তর্জাতিক বিষয়াবলি (AE-AJ)": (30, 36),
                        "ICT (AK-AP)": (36, 42),
                    }
                    selected_range_name = st.selectbox(
                        "ফাইলের কলাম রেঞ্জ সিলেক্ট করুন:",
                        options=list(column_ranges.keys()),
                        key="admin_col_range_select",
                    )
                    start_idx, end_idx = column_ranges[selected_range_name]

                    if end_idx <= len(raw_df.columns):
                        sub_df = raw_df.iloc[:, start_idx:end_idx].copy()
                        sub_df.columns = [
                            "Question",
                            "Option_A",
                            "Option_B",
                            "Option_C",
                            "Option_D",
                            "Correct_Answer",
                        ]
                        sub_df = sub_df.dropna(subset=["Question"]).reset_index(drop=True)

                        if "Explanation" in sub_df.columns:
                            sub_df["Explanation"] = sub_df["Explanation"].fillna(
                                "ব্যাখ্যা নেই।"
                            )
                        else:
                            sub_df["Explanation"] = "ব্যাখ্যা নেই।"

                        total_found = len(sub_df)
                        st.info(
                            f"🔍 এই কলাম রেঞ্জ থেকে মোট প্রশ্ন পাওয়া গেছে: {total_found}টি"
                        )

                        st.markdown("---")
                        st.markdown("##### ⚙️ প্রশ্ন ফিল্টারিং অপশন:")
                        question_mode = st.radio(
                            "পরীক্ষায় প্রশ্ন কীভাবে থাকবে?",
                            [
                                "সবগুলো প্রশ্ন রাখবো",
                                "নির্দিষ্ট সংখ্যক প্রশ্ন রেন্ডমলি (Randomly) সিলেক্ট করবো",
                            ],
                            key="admin_q_selection_mode",
                        )

                        selected_count = total_found
                        is_random = False

                        if (
                            question_mode
                            == "নির্দিষ্ট সংখ্যক প্রশ্ন রেন্ডমলি (Randomly) সিলেক্ট করবো"
                        ):
                            selected_count = st.number_input(
                                "কতটি প্রশ্ন রেন্ডমলি সিলেক্ট করতে চান?",
                                min_value=1,
                                max_value=total_found,
                                value=min(20, total_found),
                                key="admin_random_count_input",
                            )
                            is_random = True

                        if st.button(
                            "📌 ফাইল থেকে এই বিষয়ের প্রশ্ন সেভ করুন",
                            key="admin_save_from_file_btn",
                        ):
                            if not sub_df.empty:
                                if is_random:
                                    sub_df = sub_df.sample(n=selected_count).reset_index(
                                        drop=True
                                    )

                                sub_df["Subject"] = current_subject_key
                                if os.path.exists(QUESTIONS_FILE):
                                    existing_q_df = pd.read_csv(QUESTIONS_FILE)
                                    existing_q_df = existing_q_df[
                                        existing_q_df["Subject"] != current_subject_key
                                    ]
                                    final_q_df = pd.concat(
                                        [existing_q_df, sub_df], ignore_index=True
                                    )
                                else:
                                    final_q_df = sub_df
                                final_q_df.to_csv(QUESTIONS_FILE, index=False)

                                config_df = pd.DataFrame(
                                    [{"Subject": current_subject_key, "Duration": exam_duration}]
                                )
                                if os.path.exists(CONFIG_FILE):
                                    existing_conf = pd.read_csv(CONFIG_FILE)
                                    existing_conf = existing_conf[
                                        existing_conf["Subject"] != current_subject_key
                                    ]
                                    final_conf = pd.concat(
                                        [existing_conf, config_df], ignore_index=True
                                    )
                                else:
                                    final_conf = config_df
                                final_conf.to_csv(CONFIG_FILE, index=False)
                                st.success(
                                    f"✅ '{current_subject_key}' এর ফাইল থেকে {len(sub_df)}টি প্রশ্ন"
                                    " সফলভাবে সেভ হয়েছে!"
                                )
                                st.rerun()
                            else:
                                st.error("⚠️ কোনো প্রশ্ন পাওয়া যায়নি।")
                    else:
                        st.error("⚠️ ফাইলের কলাম সংখ্যা কম।")
                except Exception as e:
                    st.error(f"ত্রুটি: {e}")

else:
    if not st.session_state["exam_in_progress"]:
        student_menu = st.radio(
            "নেভিগেশন মেনু:",
            ["📝 পরীক্ষা দিন", "🏆 ক্লাসের মেধা তালিকা (Leaderboard)"],
            horizontal=True,
        )
        st.write("")
    else:
        student_menu = "📝 পরীক্ষা দিন"

    all_q_df = (
        pd.read_csv(QUESTIONS_FILE) if os.path.exists(QUESTIONS_FILE) else pd.DataFrame()
    )
    active_subjects = (
        all_q_df["Subject"].unique().tolist()
        if not all_q_df.empty and "Subject" in all_q_df.columns
        else []
    )

    if st.session_state["exam_submitted"]:
        res_info = st.session_state["last_result_data"]
        if res_info:
            if st.button("⬅️ নতুন পরীক্ষা / হোম", type="secondary"):
                st.session_state["exam_submitted"] = False
                st.session_state["confirmed_student_name"] = ""
                st.session_state["selected_exam_subject"] = ""
                st.session_state["selected_bio_chapter"] = ""
                st.session_state["exam_in_progress"] = False
                st.session_state["last_result_data"] = None
                st.rerun()

            st.markdown(
                f"""
                    <div class="result-box">
                        <h2>🎉 অভিনন্দন, {res_info['student_name']}!</h2>
                        <p style="font-size: 18px; margin: 5px 0;">বিষয়: {res_info['subject']}</p>
                        <h1 style="font-size: 32px; margin: 10px 0;">প্রাপ্ত নম্বর: {res_info['score']} / {res_info['total']}</h1>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("📊 বিস্তারিত উত্তরমালা")
            st.write("---")
            for i, row in res_info["active_df"].iterrows():
                ans = res_info["user_answers"].get(i)
                raw_correct = str(row["Correct_Answer"]).strip()
                opts = [
                    str(row["Option_A"]).strip(),
                    str(row["Option_B"]).strip(),
                    str(row["Option_C"]).strip(),
                    str(row["Option_D"]).strip(),
                ]
                correct_val = raw_correct
                for opt in opts:
                    if raw_correct.lower() in opt.lower():
                        correct_val = opt
                        break

                options_html = ""
                for opt in opts:
                    is_correct = opt == correct_val or raw_correct.lower() in opt.lower()
                    is_user = ans and str(ans).strip() == opt
                    if is_correct and is_user:
                        options_html += (
                            f"<div style='color: green; font-weight: bold;'>✅ {opt}"
                            " (আপনার সঠিক উত্তর)</div>"
                        )
                    elif is_correct:
                        options_html += (
                            f"<div style='color: green; font-weight: bold;'>✅ {opt}"
                            " (সঠিক উত্তর)</div>"
                        )
                    elif is_user:
                        options_html += (
                            f"<div style='color: red; font-weight: bold;'>❌ {opt}"
                            " (আপনার ভুল উত্তর)</div>"
                        )
                    else:
                        options_html += f"<div style='color: #555;'>• {opt}</div>"

                st.markdown(
                    f"""
                            <div class="question-card">
                                <strong>প্রশ্ন {i+1}: {str(row['Question'])}</strong><br><br>
                                {options_html}
                                <hr style="margin: 8px 0;">
                                <small>💡 ব্যাখ্যা: {row['Explanation']}</small>
                            </div>
                        """,
                    unsafe_allow_html=True,
                )
    else:
        if student_menu == "🏆 ক্লাসের মেধা তালিকা (Leaderboard)":
            st.subheader("🏆 ক্লাসের লাইভ মেধা তালিকা")
            st.write("---")
            if os.path.exists(RESULT_FILE):
                res_df = pd.read_csv(RESULT_FILE)
                if not res_df.empty:
                    if "Subject" in res_df.columns:
                        subjects_list = res_df["Subject"].unique().tolist()
                        leaderboard_sub = st.selectbox(
                            "বিষয় সিলেক্ট করুন:", subjects_list, key="lb_sub"
                        )
                        res_df = res_df[res_df["Subject"] == leaderboard_sub]
                    sorted_res = (
                        res_df.sort_values(by="Score", ascending=False)
                        .reset_index(drop=True)
                    )
                    sorted_res.index = sorted_res.index + 1
                    st.dataframe(sorted_res, use_container_width=True)
                else:
                    st.info("এখনো কোনো ফলাফল প্রকাশিত হয়নি।")
            else:
                st.info("এখনো কেউ পরীক্ষা দেয়নি।")
        else:
            if not st.session_state["exam_in_progress"]:
                st.subheader("✍️ পরীক্ষার্থীর তথ্য")
                with st.container(border=True):
                    col_input, col_btn = st.columns([8, 2])
                    with col_input:
                        student_name_input = st.text_input(
                            "আপনার পূর্ণ নাম লিখুন:",
                            placeholder="এখানে নাম লিখুন",
                            value=st.session_state.get("confirmed_student_name", ""),
                            key="input_student_name_single_page",
                        )
                    with col_btn:
                        st.write("")
                        st.write("")
                        if st.button(
                            "✅ সাবমিট করুন", use_container_width=True, type="secondary"
                        ):
                            if student_name_input.strip():
                                st.session_state["confirmed_student_name"] = (
                                    student_name_input.strip()
                                )
                                st.success("নাম সংরক্ষিত হয়েছে!")
                            else:
                                st.error("নাম লিখুন!")

                st.write("")
                st.subheader("📚 পরীক্ষার বিষয় নির্বাচন করুন")
                st.write("---")

                active_bio_sub_keys = [
                    s for s in active_subjects if s.startswith("জীববিজ্ঞান - ")
                ]
                other_active_subjects = [
                    s for s in active_subjects if not s.startswith("জীববিজ্ঞান - ")
                ]

                cols_per_row = 3
                subject_chunks = [
                    all_subjects_master[i : i + cols_per_row]
                    for i in range(0, len(all_subjects_master), cols_per_row)
                ]

                for chunk in subject_chunks:
                    row_cols = st.columns(len(chunk))
                    for idx, sub in enumerate(chunk):
                        with row_cols[idx]:
                            if sub != "জীববিজ্ঞান":
                                is_running = sub in other_active_subjects
                                with st.container(border=True):
                                    if is_running:
                                        st.markdown(
                                            f"<h4 style='margin: 0 0 4px 0; color: #1e3d59;"
                                            f" font-size: 16px; font-weight: bold; text-align:"
                                            f" center;'>{sub}</h4>",
                                            unsafe_allow_html=True,
                                        )
                                        st.markdown(
                                            "<p style='text-align: center; color: #137333;"
                                            " font-weight: bold; font-size: 13px; margin: 0 0 10px"
                                            " 0;'>🟢 পরীক্ষা আছে</p>",
                                            unsafe_allow_html=True,
                                        )
                                        if st.button(
                                            "শুরু করুন",
                                            key=f"btn_sub_{sub}",
                                            use_container_width=True,
                                            type="primary",
                                        ):
                                            current_typed_name = st.session_state.get(
                                                "confirmed_student_name", ""
                                            ).strip()
                                            if current_typed_name:
                                                st.session_state["selected_exam_subject"] = sub
                                                st.session_state["exam_start_time"] = time.time()
                                                st.session_state["exam_in_progress"] = True
                                                st.rerun()
                                            else:
                                                st.error(
                                                    "⚠️ পরীক্ষা শুরু করতে প্রথমে উপরে আপনার নাম লিখে"
                                                    " 'সাবমিট করুন' বাটনে চাপ দিন!"
                                                )
                                    else:
                                        st.markdown(
                                            f"<h4 style='margin: 0 0 4px 0; color: #5f6368;"
                                            f" font-size: 16px; font-weight: bold; text-align:"
                                            f" center;'>{sub}</h4>",
                                            unsafe_allow_html=True,
                                        )
                                        st.markdown(
                                            "<p style='text-align: center; color: #64748b;"
                                            " font-weight: bold; font-size: 13px; margin: 0 0 10px"
                                            " 0;'>⚪ পরীক্ষা নেই</p>",
                                            unsafe_allow_html=True,
                                        )
                                        st.button(
                                            "বন্ধ আছে",
                                            key=f"btn_sub_{sub}",
                                            use_container_width=True,
                                            disabled=True,
                                        )
                            else:
                                is_bio_running = len(active_bio_sub_keys) > 0
                                with st.container(border=True):
                                    st.markdown(
                                        "<h4 style='margin: 0 0 4px 0; color: #1e3d59;"
                                        " font-size: 16px; font-weight: bold; text-align:"
                                        " center;'>জীববিজ্ঞান</h4>",
                                        unsafe_allow_html=True,
                                    )
                                    if is_bio_running:
                                        st.markdown(
                                            "<p style='text-align: center; color: #137333;"
                                            " font-weight: bold; font-size: 13px; margin: 0 0 5px"
                                            " 0;'>🟢 অধ্যায়ভিত্তিক পরীক্ষা আছে</p>",
                                            unsafe_allow_html=True,
                                        )
                                        available_chapters = [
                                            s.replace("জীববিজ্ঞান - ", "")
                                            for s in active_bio_sub_keys
                                        ]
                                        chosen_ch = st.selectbox(
                                            "অধ্যায় বেছে নিন:",
                                            available_chapters,
                                            key="student_bio_ch_select",
                                        )
                                        if st.button(
                                            "জীববিজ্ঞানের পরীক্ষা শুরু করুন",
                                            key="btn_sub_biology_start",
                                            use_container_width=True,
                                            type="primary",
                                        ):
                                            current_typed_name = st.session_state.get(
                                                "confirmed_student_name", ""
                                            ).strip()
                                            if current_typed_name:
                                                st.session_state["selected_exam_subject"] = (
                                                    f"জীববিজ্ঞান - {chosen_ch}"
                                                )
                                                st.session_state["exam_start_time"] = time.time()
                                                st.session_state["exam_in_progress"] = True
                                                st.rerun()
                                            else:
                                                st.error(
                                                    "⚠️ পরীক্ষা শুরু করতে প্রথমে উপরে আপনার নাম লিখে"
                                                    " 'সাবমিট করুন' বাটনে চাপ দিন!"
                                                )
                                    else:
                                        st.markdown(
                                            "<p style='text-align: center; color: #64748b;"
                                            " font-weight: bold; font-size: 13px; margin: 0 0 10px"
                                            " 0;'>⚪ পরীক্ষা নেই</p>",
                                            unsafe_allow_html=True,
                                        )
                                        st.button(
                                            "বন্ধ আছে",
                                            key="btn_sub_biology_disabled",
                                            use_container_width=True,
                                            disabled=True,
                                        )
            else:
                selected_subject = st.session_state.get(
                    "selected_exam_subject", active_subjects[0]
                )
                df = all_q_df[all_q_df["Subject"] == selected_subject].reset_index(
                    drop=True
                )

                duration = 10
                if os.path.exists(CONFIG_FILE):
                    conf_df = pd.read_csv(CONFIG_FILE)
                    match_conf = conf_df[conf_df["Subject"] == selected_subject]
                    if not match_conf.empty:
                        duration = int(match_conf.iloc[0]["Duration"])

                current_student = st.session_state["confirmed_student_name"]
                active_df = df.copy()
                total_seconds = duration * 60

                if (
                    "exam_start_time" not in st.session_state
                    or st.session_state.get("current_sub") != selected_subject
                ):
                    st.session_state["exam_start_time"] = time.time()
                    st.session_state["current_sub"] = selected_subject

                elapsed_seconds = int(
                    time.time() - st.session_state["exam_start_time"]
                )
                remaining_seconds = max(0, total_seconds - elapsed_seconds)

                timer_html = f"""
                    <div style="background: linear-gradient(135deg, #ff4b4b, #ff9068); color: white; padding: 10px 15px; border-radius: 8px; text-align: center; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; font-size: 16px;">
                        ⏳ বাকি সময়: <span id="time-display">--:--</span>
                    </div>
                """
                st.markdown(timer_html, unsafe_allow_html=True)

                st.markdown(f"### বিষয়: {selected_subject}")
                st.markdown(f"**পরীক্ষার্থী:** {current_student}")
                st.write("---")

                user_answers = {}
                with st.form("exam_form"):
                    for i, row in active_df.iterrows():
                        opts = [
                            str(row["Option_A"]).strip(),
                            str(row["Option_B"]).strip(),
                            str(row["Option_C"]).strip(),
                            str(row["Option_D"]).strip(),
                        ]
                        user_answers[i] = st.radio(
                            f"প্রশ্ন {i+1}: {str(row['Question'])}",
                            options=opts,
                            key=f"q_{i}",
                            index=None,
                        )
                        st.write("")

                    submitted = st.form_submit_button(
                        "📤 খাতা জমা দিন (Submit)", use_container_width=True, type="primary"
                    )

                    if submitted:
                        score = 0
                        for i, row in active_df.iterrows():
                            ans = user_answers.get(i)
                            raw_correct = str(row["Correct_Answer"]).strip()
                            opts = [
                                str(row["Option_A"]).strip(),
                                str(row["Option_B"]).strip(),
                                str(row["Option_C"]).strip(),
                                str(row["Option_D"]).strip(),
                            ]
                            correct_val = raw_correct
                            for opt in opts:
                                if raw_correct.lower() in opt.lower():
                                    correct_val = opt
                                    break
                            if ans and (ans == correct_val or raw_correct.lower() in ans.lower()):
                                score += 1

                        total_q = len(active_df)
                        result_entry = pd.DataFrame([{
                            "Student_Name": current_student,
                            "Subject": selected_subject,
                            "Score": score,
                            "Total": total_q,
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }])

                        if os.path.exists(RESULT_FILE):
                            res_df_existing = pd.read_csv(RESULT_FILE)
                            final_res_df = pd.concat(
                                [res_df_existing, result_entry], ignore_index=True
                            )
                        else:
                            final_res_df = result_entry
                        final_res_df.to_csv(RESULT_FILE, index=False)

                        st.session_state["exam_submitted"] = True
                        st.session_state["exam_in_progress"] = False
                        st.session_state["last_result_data"] = {
                            "student_name": current_student,
                            "subject": selected_subject,
                            "score": score,
                            "total": total_q,
                            "active_df": active_df,
                            "user_answers": user_answers,
                        }
                        st.rerun()
