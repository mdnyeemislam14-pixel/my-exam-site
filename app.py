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

# প্রিমিয়াম এবং পরিপাটি CSS ডিজাইন
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {visibility: hidden;}
    
    html, body, [class*="css"] {
        font-size: 14px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stApp {
        background-color: #f4f6f9 !important;
    }
    
    .question-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    
    .result-box {
        background: linear-gradient(135deg, #3B82F6, #1d4ed8) !important;
        color: #ffffff !important;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
        margin-bottom: 25px;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# শীর্ষ ব্যানার
st.markdown(
    """
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #3B82F6, #1d4ed8); border-radius: 12px; margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(59,130,246,0.2);">
        <h2 style="margin: 0; font-size: 26px; font-weight: bold;">📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম</h2>
        <p style="margin: 8px 0 10px 0; font-size: 14px; opacity: 0.95;">বিসিএস, ব্যাংক, প্রাথমিক সহকারী শিক্ষক নিয়োগ এবং NTRCA সহ সকল সরকারি চাকরির প্রস্তুতির বিশ্বস্ত মাধ্যম</p>
        <h4 style="margin: 0; font-size: 15px; letter-spacing: 1px;">✨ Powered by <span style="background-color: #ffcc00; color: #000; padding: 2px 10px; border-radius: 4px;">Job Efforts</span></h4>
    </div>
""",
    unsafe_allow_html=True,
)

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"
ADMIN_PASSWORD = "1234"

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
if "exam_in_progress" not in st.session_state:
  st.session_state["exam_in_progress"] = False

# টপ নেভিগেশন ও অ্যাডমিন পপওভার
col_nav1, col_nav2, col_nav3 = st.columns([6, 3, 3])
with col_nav3:
  if not st.session_state["exam_in_progress"]:
    if st.session_state["is_admin_logged_in"]:
      if st.button("🚪 অ্যাডমিন লগ আউট", use_container_width=True):
        st.session_state["is_admin_logged_in"] = False
        st.session_state["confirmed_student_name"] = ""
        st.session_state["exam_submitted"] = False
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
  st.subheader("🛠️ অ্যাডমিন কন্ট্রোল প্যানেল")
  st.write("---")

  admin_menu = st.radio(
      "অ্যাডমিন মেনু নির্বাচন করুন:",
      [
          "📝 প্রশ্ন তৈরি ও ম্যানেজ",
          "🟢 পরীক্ষা চালু/বন্ধ করুন",
          "🏆 শিক্ষার্থীদের ফলাফল",
      ],
      horizontal=True,
  )
  st.write("")

  if admin_menu == "📝 প্রশ্ন তৈরি ও ম্যানেজ":
    st.markdown("#### নতুন প্রশ্ন যুক্ত করুন")
    with st.form("admin_question_form"):
      sub_list_full = all_subjects_master + [
          f"জীববিজ্ঞান - {ch}" for ch in bio_chapters_master
      ]
      q_subject = st.selectbox("বিষয় বা অধ্যায় নির্বাচন করুন:", sub_list_full)
      q_text = st.text_area("প্রশ্ন লিখুন:")

      col_op1, col_op2 = st.columns(2)
      with col_op1:
        opt_a = st.text_input("অপশন ক:")
        opt_c = st.text_input("অপশন গ:")
      with col_op2:
        opt_b = st.text_input("অপশন খ:")
        opt_d = st.text_input("অপশন ঘ:")

      correct_ans = st.selectbox(
          "সঠিক উত্তর নির্বাচন করুন:", [opt_a, opt_b, opt_c, opt_d]
      )

      submitted_q = st.form_submit_button(
          "➕ প্রশ্ন সেভ করুন", type="primary"
      )
      if submitted_q:
        if q_text.strip() and correct_ans.strip():
          new_row = pd.DataFrame(
              [{
                  "Subject": q_subject,
                  "Question": q_text,
                  "OptionA": opt_a,
                  "OptionB": opt_b,
                  "OptionC": opt_c,
                  "OptionD": opt_d,
                  "Correct": correct_ans,
              }]
          )
          if os.path.exists(QUESTIONS_FILE):
            old_q_df = pd.read_csv(QUESTIONS_FILE)
            new_row = pd.concat([old_q_df, new_row], ignore_index=True)
          new_row.to_csv(QUESTIONS_FILE, index=False)
          st.success("✅ সফলভাবে প্রশ্ন যুক্ত হয়েছে!")
        else:
          st.error("⚠️ অনুগ্রহ করে প্রশ্ন এবং সঠিক উত্তর পূরণ করুন!")

    if os.path.exists(QUESTIONS_FILE):
      st.write("---")
      st.markdown("#### বিদ্যমান প্রশ্নসমূহ")
      q_display_df = pd.read_csv(QUESTIONS_FILE)
      st.dataframe(q_display_df, use_container_width=True)

  elif admin_menu == "🟢 পরীক্ষা চালু/বন্ধ করুন":
    st.markdown("#### কোন বিষয়গুলোর পরীক্ষা চালু রাখবেন তা টিক দিন")
    all_q_df = (
        pd.read_csv(QUESTIONS_FILE)
        if os.path.exists(QUESTIONS_FILE)
        else pd.DataFrame()
    )
    existing_q_subjects = (
        all_q_df["Subject"].unique().tolist()
        if not all_q_df.empty and "Subject" in all_q_df.columns
        else []
    )

    if existing_q_subjects:
      st.info(
          "যে বিষয়গুলোতে ডাটাবেজে প্রশ্ন আছে, সেগুলোর তালিকা নিচে দেখানো হলো:"
      )
      for sub_item in existing_q_subjects:
        st.write(f"✔️ **{sub_item}** - প্রশ্ন উপলব্ধ রয়েছে।")
    else:
      st.warning(
          "⚠️ এখনো কোনো প্রশ্ন ডাটাবেজে নেই। আগে 'প্রশ্ন তৈরি ও ম্যানেজ' থেকে"
          " প্রশ্ন যোগ করুন।"
      )

  elif admin_menu == "🏆 শিক্ষার্থীদের ফলাফল":
    st.markdown("#### শিক্ষার্থীদের পরীক্ষার ফলাফল তালিকা")
    if os.path.exists(RESULT_FILE):
      res_df = pd.read_csv(RESULT_FILE)
      if not res_df.empty:
        st.dataframe(res_df, use_container_width=True)
        if st.button("🗑️ সকল ফলাফল মুছে ফেলুন", type="primary"):
          os.remove(RESULT_FILE)
          st.success("ফলাফল রিসেট করা হয়েছে!")
          st.rerun()
      else:
        st.info("এখনো কোনো ফলাফল জমা হয়নি।")
    else:
      st.info("এখনো কোনো ফলাফল জমা হয়নি।")

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
    st.subheader("🎉 পরীক্ষার ফলাফল")
    res = st.session_state["last_result_data"]
    if res:
      st.markdown(
          f"""
            <div class='result-box'>
                <h3>অভিনন্দন, {res['name']}!</h3>
                <p>বিষয়: {res['subject']}</p>
                <p>মোট প্রশ্ন: {res['total']} | সঠিক উত্তর: {res['score']} | ভুল উত্তর: {res['wrong']}</p>
                <h2>প্রাপ্ত নম্বর: {res['percentage']:.2f}%</h2>
            </div>
            """,
          unsafe_allow_html=True,
      )
    if st.button("🔄 হোম পেজে ফিরে যান", type="primary"):
      st.session_state["exam_submitted"] = False
      st.session_state["last_result_data"] = None
      st.rerun()

  else:
    if student_menu == "🏆 ক্লাসের মেধা তালিকা (Leaderboard)":
      st.subheader("🏆 ক্লাসের লাইভ মেধা তালিকা")
      st.write("---")
      if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
          st.dataframe(res_df, use_container_width=True)
        else:
          st.info("এখনো কোনো ফলাফল জমা হয়নি।")
      else:
        st.info("এখনো কোনো ফলাফল জমা হয়নি।")

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

        # সুন্দর বক্স কার্ড ও নীল রঙের শিরোনাম সহ সাবজেক্ট লুপ
        for chunk in subject_chunks:
          row_cols = st.columns(len(chunk))
          for idx, sub in enumerate(chunk):
            with row_cols[idx]:
              with st.container(border=True):
                if sub != "জীববিজ্ঞান":
                  is_running = sub in other_active_subjects

                  # প্রিমিয়াম নীল রঙের বিষয়ের নাম (#2563eb)
                  st.markdown(
                      f"<h4 style='margin: 0 0 8px 0; color: #2563eb; font-size:"
                      f" 18px; font-weight: 700; text-align:"
                      f" center;'>{sub}</h4>",
                      unsafe_allow_html=True,
                  )

                  if is_running:
                    st.markdown(
                        "<p style='text-align: center; color: #16a34a; font-weight:"
                        " 600; font-size: 13px; margin: 0 0 15px 0;'>🟢 পরীক্ষা"
                        " আছে</p>",
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
                        st.error("⚠️ প্রথমে উপরে নাম লিখে সাবমিট করুন!")
                  else:
                    st.markdown(
                        "<p style='text-align: center; color: #94a3b8; font-weight:"
                        " 600; font-size: 13px; margin: 0 0 15px 0;'>⚪ পরীক্ষা"
                        " নেই</p>",
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

                  # জীববিজ্ঞান নীল রঙের শিরোনাম
                  st.markdown(
                      "<h4 style='margin: 0 0 8px 0; color: #2563eb; font-size:"
                      " 18px; font-weight: 700; text-align:"
                      " center;'>জীববিজ্ঞান</h4>",
                      unsafe_allow_html=True,
                  )

                  if is_bio_running:
                    st.markdown(
                        "<p style='text-align: center; color: #16a34a; font-weight:"
                        " 600; font-size: 13px; margin: 0 0 10px 0;'>🟢"
                        " অধ্যায়ভিত্তিক পরীক্ষা আছে</p>",
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
                        label_visibility="collapsed",
                    )
                    if st.button(
                        "পরীক্ষা শুরু করুন",
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
                        st.error("⚠️ প্রথমে উপরে নাম লিখে সাবমিট করুন!")
                  else:
                    st.markdown(
                        "<p style='text-align: center; color: #94a3b8; font-weight:"
                        " 600; font-size: 13px; margin: 0 0 15px 0;'>⚪ পরীক্ষা"
                        " নেই</p>",
                        unsafe_allow_html=True,
                    )
                    st.button(
                        "বন্ধ আছে",
                        key="btn_sub_biology_disabled",
                        use_container_width=True,
                        disabled=True,
                    )
      else:
        # পরীক্ষা চলাকালীন স্ক্রিন
        sub_name = st.session_state["selected_exam_subject"]
        st.subheader(f"📝 পরীক্ষা চলছে: {sub_name}")
        st.write("---")

        q_df = (
            pd.read_csv(QUESTIONS_FILE)
            if os.path.exists(QUESTIONS_FILE)
            else pd.DataFrame()
        )
        if not q_df.empty and "Subject" in q_df.columns:
          exam_questions = q_df[q_df["Subject"] == sub_name]

          if not exam_questions.empty:
            with st.form("exam_questions_form"):
              user_answers = {}
              for q_idx, row in exam_questions.iterrows():
                st.markdown(f"**প্রশ্ন {q_idx+1}: {row['Question']}**")
                opts = [row["OptionA"], row["OptionB"], row["OptionC"], row["OptionD"]]
                opts = [o for o in opts if pd.notna(o) and str(o).strip() != ""]
                user_answers[q_idx] = st.radio(
                    "উত্তর নির্বাচন করুন:",
                    opts,
                    key=f"q_{q_idx}",
                    index=None,
                    label_visibility="collapsed",
                )
                st.write("")

              submitted_exam = st.form_submit_button(
                  "পরীক্ষা জমা দিন", type="primary"
              )
              if submitted_exam:
                score = 0
                wrong = 0
                total = len(exam_questions)

                for q_idx, row in exam_questions.iterrows():
                  ans = user_answers.get(q_idx)
                  if ans == row["Correct"]:
                    score += 1
                  else:
                    wrong += 1

                percentage = (score / total) * 100 if total > 0 else 0
                student_name = st.session_state["confirmed_student_name"]

                result_dict = {
                    "name": student_name,
                    "subject": sub_name,
                    "total": total,
                    "score": score,
                    "wrong": wrong,
                    "percentage": percentage,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                res_df = (
                    pd.read_csv(RESULT_FILE)
                    if os.path.exists(RESULT_FILE)
                    else pd.DataFrame()
                )
                res_df = pd.concat(
                    [res_df, pd.DataFrame([result_dict])], ignore_index=True
                )
                res_df.to_csv(RESULT_FILE, index=False)

                st.session_state["last_result_data"] = result_dict
                st.session_state["exam_submitted"] = True
                st.session_state["exam_in_progress"] = False
                st.rerun()
          else:
            st.warning("এই বিষয়ে কোনো প্রশ্ন পাওয়া যায়নি।")
            if st.button("ফিরে যান"):
              st.session_state["exam_in_progress"] = False
              st.rerun()
