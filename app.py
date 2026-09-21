import time
from datetime import datetime
import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# File paths and configuration constants placeholder
RESULT_FILE = "exam_results.csv"
CONFIG_FILE = "exam_config.csv"
all_subjects_master = ["বাংলা", "ইংরেজি", "গণিত", "বিজ্ঞান", "বাংলাদেশ ও বিশ্বপরিচয়", "জীববিজ্ঞান"]
active_subjects = ["বাংলা", "ইংরেজি", "জীববিজ্ঞান - উদ্ভিদবিজ্ঞান", "জীববিজ্ঞান - প্রাণীবিজ্ঞান"]

# Ensure session states are initialized
if "exam_in_progress" not in st.session_state:
    st.session_state["exam_in_progress"] = False
if "exam_submitted" not in st.session_state:
    st.session_state["exam_submitted"] = False
if "confirmed_student_name" not in st.session_state:
    st.session_state["confirmed_student_name"] = ""

# Example dummy dataframe for testing if all_q_df is not defined
if 'all_q_df' not in locals():
    all_q_df = pd.DataFrame(columns=["Subject", "Question", "Option_A", "Option_B", "Option_C", "Option_D", "Correct_Answer", "Explanation"])

student_menu = st.sidebar.radio("মেনু", ["পরীক্ষায় অংশগ্রহণ", "🏆 ক্লাসের মেধা তালিকা (Leaderboard)"])

if st.session_state.get("exam_submitted", False):
    res_info = st.session_state.get("last_result_data", {})
    if res_info:
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
        if st.button("🔄 নতুন পরীক্ষায় অংশ নিন"):
            st.session_state["exam_submitted"] = False
            st.rerun()
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
            total_marks = len(active_df)

            if (
                "exam_start_time" not in st.session_state
                or st.session_state.get("current_sub") != selected_subject
            ):
                st.session_state["exam_start_time"] = time.time()
                st.session_state["current_sub"] = selected_subject

            # অটো-রিফ্রেশ ট্রিগার (প্রতি ১ সেকেন্ড পর পর পেজ রিফ্রেশ করে টাইমার আপডেট করবে)
            count = st_autorefresh(interval=1000, limit=total_seconds, key="exam_live_timer")
            elapsed_seconds = int(time.time() - st.session_state["exam_start_time"])
            remaining_seconds = max(0, total_seconds - elapsed_seconds)

            mins, secs = divmod(remaining_seconds, 60)

            # সুন্দর ডিজাইনযুক্ত স্টিকি ইনফো বার (মোট নম্বর, মোট সময় ও লাইভ টাইমার প্রদর্শনের জন্য)
            st.markdown(
                f"""
                <style>
                    .exam-header-card {{
                        display: flex;
                        justify-content: space-around;
                        background: linear-gradient(135deg, #1e3d59, #17b978);
                        color: white;
                        padding: 15px;
                        border-radius: 10px;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                        margin-bottom: 20px;
                        font-family: sans-serif;
                        text-align: center;
                    }}
                    .exam-header-item {{
                        flex: 1;
                        border-right: 1px solid rgba(255,255,255,0.3);
                    }}
                    .exam-header-item:last-child {{
                        border-right: none;
                    }}
                    .exam-header-title {{
                        font-size: 13px;
                        opacity: 0.9;
                        margin-bottom: 3px;
                    }}
                    .exam-header-value {{
                        font-size: 18px;
                        font-weight: bold;
                    }}
                </style>

                <div class="exam-header-card">
                    <div class="exam-header-item">
                        <div class="exam-header-title">📚 বিষয়</div>
                        <div class="exam-header-value">{selected_subject}</div>
                    </div>
                    <div class="exam-header-item">
                        <div class="exam-header-title">🎯 মোট নম্বর</div>
                        <div class="exam-header-value">{total_marks} নম্বর</div>
                    </div>
                    <div class="exam-header-item">
                        <div class="exam-header-title">⏱️ মোট সময়</div>
                        <div class="exam-header-value">{duration} মিনিট</div>
                    </div>
                    <div class="exam-header-item" style="background: rgba(255, 75, 75, 0.4); border-radius: 6px;">
                        <div class="exam-header-title">⏳ বাকি সময়</div>
                        <div class="exam-header-value" style="color: #ffeb3b;">{mins:02d}:{secs:02d} মিনিট</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(f"**পরীক্ষার্থী:** {current_student}")
            st.write("---")

            # সময় শেষ হয়ে গেলে স্বয়ংক্রিয়ভাবে খাতা সাবমিট করার লজিক
            if remaining_seconds == 0 and not st.session_state.get("exam_submitted", False):
                st.warning("⏰ আপনার পরীক্ষার নির্ধারিত সময় শেষ! আপনার খাতাটি স্বয়ংক্রিয়ভাবে জমা হয়ে গেছে।")
                time.sleep(1.5)
                # স্বয়ংক্রিয় জমার জন্য ডিফল্ট স্কোর বা সাবমিশন প্রসেস ট্রিগার করা হচ্ছে
                st.session_state["exam_submitted"] = True
                st.session_state["exam_in_progress"] = False
                st.rerun()

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
