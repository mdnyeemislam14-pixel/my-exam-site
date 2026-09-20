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

# প্রিমিয়াম থ্রি-ডি (3D) বক্স এবং পরিপাটি CSS ডিজাইন
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
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

    /* থ্রি-ডি (3D) বক্স বা কার্ড স্টাইল */
    [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.3s ease-in-out !important;
        margin-bottom: 15px;
    }
    
    [data-testid="stVerticalBlock"] > [data-testid="stContainer"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 30px -10px rgba(59, 130, 246, 0.15), 0 10px 15px -5px rgba(0, 0, 0, 0.05) !important;
        border-color: #3B82F6 !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# শীর্ষ ব্যানার
st.markdown(
    """
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #3B82F6, #1d4ed8); border-radius: 16px; margin-bottom: 25px; color: white; box-shadow: 0 10px 25px -5px rgba(59,130,246,0.3);">
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
  st.write("এখানে পরীক্ষার প্রশ্ন এবং সেটিংস পরিচালনা করুন।")
  # (অ্যাডমিন প্যানেলের বাকি অংশ এখানে থাকবে)
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
    # পরীক্ষার ফলাফল স্ক্রিন
    pass
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

        # থ্রি-ডি বক্স কার্ড লেআউট লুপ
        for chunk in subject_chunks:
          row_cols = st.columns(len(chunk))
          for idx, sub in enumerate(chunk):
            with row_cols[idx]:
              with st.container(border=True):
                if sub != "জীববিজ্ঞান":
                  is_running = sub in other_active_subjects
                  st.markdown(
                      f"<h4 style='margin: 0 0 8px 0; color: #1e3d59; font-size:"
                      f" 17px; font-weight: 700; text-align:"
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
                  st.markdown(
                      "<h4 style='margin: 0 0 8px 0; color: #1e3d59; font-size:"
                      " 17px; font-weight: 700; text-align:"
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
        pass
