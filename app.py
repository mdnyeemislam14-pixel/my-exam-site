import streamlit as st
import pandas as pd
import random
import os
import json
import re
import time
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম", page_icon="📝", layout="wide")

# ল্যাপটপ ও বড় স্ক্রিন কেন্দ্রিক প্রফেশনাল ডিজাইন এবং সাইডবার সিএসএস
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppToolbar {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}

    /* ফন্ট সাইজ এবং লেআউট */
    html, body, [class*="css"] {
        font-size: 16px !important;
    }

    /* মূল কন্টেইনার ল্যাপটপের জন্য প্রশস্ত ও সুন্দর করা */
    .block-container {
        max-width: 950px;
        padding-top: 1.5rem !important;
        margin: 0 auto;
    }

    /* প্রশ্নগুলোর জন্য সুন্দর বক্স বা কার্ড স্টাইল */
    .question-card {
        background-color: #fcfcfc;
        border: 1px solid #e0e0e0;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* ফলাফল প্রদর্শনের জন্য প্রিমিয়াম বক্স */
    .result-box {
        background: linear-gradient(135deg, #f6d365, #fda085);
        color: #2c3e50;
        padding: 24px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* রেডিও অপশনগুলোর ডিজাইন */
    div[role="radiogroup"] label {
        padding: 10px 12px;
        border-radius: 6px;
        min-height: 42px;
        display: flex;
        align-items: center;
        margin-bottom: 6px;
        border: 1px solid #eaeaea;
    }
    div[role="radiogroup"] label:hover {
        background-color: #f7f9fa;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ব্যানার
st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #654ea3, #eaafc8); border-radius: 10px; margin-bottom: 20px; color: white;">
        <h1 style="margin: 0; font-size: 26px; font-weight: bold;">📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম</h1>
        <p style="margin: 5px 0 5px 0; font-size: 15px; opacity: 0.95;">বিসিএস, ব্যাংক, প্রাথমিক সহকারী শিক্ষক নিয়োগ এবং NTRCA সহ সকল চাকরির প্রস্তুতির বিশ্বস্ত মাধ্যম</p>
        <h4 style="margin: 0; font-size: 14px; letter-spacing: 1px;">✨ Powered by <span style="background-color: #ffcc00; color: #000; padding: 2px 8px; border-radius: 4px;">Job Efforts</span></h4>
    </div>
""", unsafe_allow_html=True)

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"
ADMIN_PASSWORD = "1234"

# সেশন ফোল্ডার তৈরি
SESSIONS_DIR = "exam_sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

def _safe_key(text):
    return re.sub(r'[^\w\u0980-\u09FF]+', '_', str(text).strip())

def get_session_path(student_name, subject):
    return os.path.join(SESSIONS_DIR, f"{_safe_key(student_name)}__{_safe_key(subject)}.json")

def save_session_progress(student_name, subject, start_time, duration_minutes, answers_dict):
    session_path = get_session_path(student_name, subject)
    data = {
        "student_name": student_name, "subject": subject,
        "start_time": start_time, "duration_minutes": duration_minutes,
        "answers": {str(k): v for k, v in answers_dict.items()}
    }
    try:
        with open(session_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass

def load_session_progress(student_name, subject):
    session_path = get_session_path(student_name, subject)
    if os.path.exists(session_path):
        try:
            with open(session_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def clear_session_progress(student_name, subject):
    session_path = get_session_path(student_name, subject)
    if os.path.exists(session_path):
        try:
            os.remove(session_path)
        except Exception:
            pass

# সেশন স্টেট ইনিশিয়ালাইজেশন
if 'is_admin_logged_in' not in st.session_state:
    st.session_state['is_admin_logged_in'] = False
if 'confirmed_student_name' not in st.session_state:
    st.session_state['confirmed_student_name'] = ""
if 'exam_submitted' not in st.session_state:
    st.session_state['exam_submitted'] = False
if 'last_result_data' not in st.session_state:
    st.session_state['last_result_data'] = None
if 'selected_exam_subject' not in st.session_state:
    st.session_state['selected_exam_subject'] = ""
if 'exam_in_progress' not in st.session_state:
    st.session_state['exam_in_progress'] = False

# ==========================================
# 🧭 সাইডবার (ল্যাপটপের জন্য উপরের বাম পাশে ফিক্সড কন্ট্রোল ও অ্যাডমিন লগইন)
# ==========================================
with st.sidebar:
    st.header("📌 মেনু ও কন্ট্রোল প্যানেল")
    st.write("---")
    
    admin_menu = None
    is_admin = False

    if st.session_state['is_admin_logged_in']:
        st.success("✅ অ্যাডমিন মোড সক্রিয়!")
        if st.button("🚪 লগ আউট করুন", key="logout_btn"):
            st.session_state['is_admin_logged_in'] = False
            st.session_state['confirmed_student_name'] = ""
            st.session_state['exam_submitted'] = False
            st.session_state['selected_exam_subject'] = ""
            st.session_state['exam_in_progress'] = False
            st.rerun()
            
        admin_menu = st.radio("অ্যাডমিন অপশন:", [
            "📝 প্রশ্ন আপলোড ও সেটআপ",
            "📊 সকল শিক্ষার্থীর ফলাফল"
        ], key="admin_radio_menu")
        is_admin = True
    else:
        if not st.session_state['exam_in_progress']:
            student_menu = st.radio(
                "নেভিগেশন নির্বাচন:",
                ["📝 পরীক্ষা দিন", "🏆 ক্লাসের মেধা তালিকা দেখুন"],
                key="student_radio_menu"
            )
        else:
            st.info("⚠️ পরীক্ষা চলমান রয়েছে।")
            student_menu = "📝 পরীক্ষা দিন"

        st.write("---")
        with st.expander("🔐 শিক্ষক / অ্যাডমিন লগইন"):
            with st.form("admin_login_form"):
                entered_password = st.text_input("পাসওয়ার্ড দিন:", type="password", key="admin_pwd_box")
                submitted = st.form_submit_button("লগইন করুন")
                if submitted:
                    if entered_password == ADMIN_PASSWORD:
                        st.session_state['is_admin_logged_in'] = True
                        st.rerun()
                    else:
                        st.error("❌ ভুল পাসওয়ার্ড!")

# ==========================================
# মূল কাজের অংশ (অ্যাডমিন বা শিক্ষার্থী ইন্টারফেস)
# ==========================================
if is_admin and admin_menu == "📊 সকল শিক্ষার্থীর ফলাফল":
    st.subheader("🏆 সকল শিক্ষার্থীর ফলাফল তালিকা")
    st.write("---")
    
    if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
            if 'Subject' in res_df.columns:
                subjects_list = ["সকল বিষয়"] + res_df['Subject'].unique().tolist()
                selected_filter_sub = st.selectbox("বিষয় সিলেক্ট করুন:", subjects_list, key="filter_sub_box")
                if selected_filter_sub != "সকল বিষয়":
                    res_df = res_df[res_df['Subject'] == selected_filter_sub]

            st.info(f"মোট খাতা জমা পড়েছে: {len(res_df)} টি")
            
            sorted_res = res_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            sorted_res.index = sorted_res.index + 1
            st.dataframe(sorted_res, use_container_width=True)
            
            csv_data = sorted_res.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 মেধা তালিকা ডাউনলোড (CSV)",
                data=csv_data,
                file_name="merit_list.csv",
                mime="text/csv",
            )
            
            st.write("---")
            if st.button("🗑️ সব ফলাফল রিসেট করুন", type="secondary", key="reset_results_btn"):
                if os.path.exists(RESULT_FILE):
                    os.remove(RESULT_FILE)
                    st.success("সব ফলাফল মুছে ফেলা হয়েছে!")
                    st.rerun()
        else:
            st.warning("এখনো কেউ পরীক্ষা দেয়নি।")
    else:
        st.warning("কোনো ফলাফল জমা হয়নি।")

elif not is_admin and student_menu == "🏆 ক্লাসের মেধা তালিকা দেখুন":
    st.subheader("🏆 ক্লাসের লাইভ মেধা তালিকা")
    st.write("---")
    
    if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
            if 'Subject' in res_df.columns:
                subjects_list = res_df['Subject'].unique().tolist()
                leaderboard_sub = st.selectbox("বিষয় সিলেক্ট করুন:", subjects_list, key="lb_subject_select")
                res_df = res_df[res_df['Subject'] == leaderboard_sub]
            
            sorted_res = res_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            sorted_res.index = sorted_res.index + 1
            st.dataframe(sorted_res, use_container_width=True)
        else:
            st.info("এখনো কোনো ফলাফল প্রকাশিত হয়নি।")
    else:
        st.info("এখনো কেউ পরীক্ষা দেয়নি।")

else:
    if is_admin:
        st.subheader("📚 নতুন প্রশ্ন সংযোজন ও সেটআপ")
        
        subject_options = ["বাংলা", "English", "গণিত", "বিজ্ঞান", "বাংলাদেশের বিষয়াবলি", "আন্তর্জাতিক বিষয়াবলি", "ICT"]
        subject_name = st.selectbox("বিষয়ের নাম:", subject_options, key="admin_subject_sel")
        exam_duration = st.number_input("⏱️ সময় (মিনিট):", min_value=1, max_value=300, value=10, key="admin_dur_num")
        
        st.write("---")
        input_mode = st.radio("প্রশ্ন যুক্ত করার পদ্ধতি:", ["টেক্সট পেস্ট (Easy Paste)", "ফাইল আপলোড"], key="admin_mode_radio")

        if input_mode == "টেক্সট পেস্ট (Easy Paste)":
            pasted_text = st.text_area("প্রশ্ন পেস্ট করুন:", height=200, placeholder="১. প্রশ্ন...\nক) ...\nখ) ...\nগ) ...\nঘ) ...\nউত্তর: ক", key="admin_paste_box")
            
            if st.button("📌 সেভ করুন", key="admin_save_paste_btn"):
                if not pasted_text:
                    st.error("⚠️ প্রশ্ন দিন।")
                else:
                    parsed_questions = []
                    blocks = pasted_text.strip().split('\n\n')
                    
                    for block in blocks:
                        lines = [line.strip() for line in block.split('\n') if line.strip()]
                        if len(lines) >= 5:
                            q_text, opt_a, opt_b, opt_c, opt_d = lines[0], lines[1], lines[2], lines[3], lines[4]
                            correct_ans, explanation = opt_a, "ব্যাখ্যা নেই।"
                            
                            for l in lines[5:]:
                                if l.startswith("উত্তর:") or l.startswith("Answer:"):
                                    ans_key = l.replace("উত্তর:", "").replace("Answer:", "").strip().lower()
                                    if ans_key in ['ক', 'a']: correct_ans = opt_a
                                    elif ans_key in ['খ', 'b']: correct_ans = opt_b
                                    elif ans_key in ['গ', 'c']: correct_ans = opt_c
                                    elif ans_key in ['ঘ', 'd']: correct_ans = opt_d
                                    else: correct_ans = ans_key
                                elif l.startswith("ব্যাখ্যা:") or l.startswith("Explanation:"):
                                    explanation = l.replace("ব্যাখ্যা:", "").replace("Explanation:", "").strip()
                            
                            parsed_questions.append({
                                "Subject": subject_name, "Question": q_text,
                                "Option_A": opt_a, "Option_B": opt_b, "Option_C": opt_c, "Option_D": opt_d,
                                "Correct_Answer": correct_ans, "Explanation": explanation
                            })
                    
                    if parsed_questions:
                        new_df = pd.DataFrame(parsed_questions)
                        if os.path.exists(QUESTIONS_FILE):
                            existing_q_df = pd.read_csv(QUESTIONS_FILE)
                            existing_q_df = existing_q_df[existing_q_df['Subject'] != subject_name]
                            final_q_df = pd.concat([existing_q_df, new_df], ignore_index=True)
                        else:
                            final_q_df = new_df
                        
                        final_q_df.to_csv(QUESTIONS_FILE, index=False)
                        config_df = pd.DataFrame([{"Subject": subject_name, "Duration": exam_duration}])
                        
                        if os.path.exists(CONFIG_FILE):
                            existing_conf = pd.read_csv(CONFIG_FILE)
                            existing_conf = existing_conf[existing_conf['Subject'] != subject_name]
                            final_conf = pd.concat([existing_conf, config_df], ignore_index=True)
                        else:
                            final_conf = config_df
                        final_conf.to_csv(CONFIG_FILE, index=False)
                        st.success("✅ সফলভাবে সেভ হয়েছে!")

        else:
            uploaded_file = st.file_uploader("ফাইল আপলোড (xlsx/csv):", type=["xlsx", "csv"], key="admin_file_up")
            if uploaded_file is not None:
                try:
                    raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                    
                    column_ranges = {
                        "বাংলা (A-F)": (0, 6),
                        "English (G-L)": (6, 12),
                        "গণিত (M-R)": (12, 18),
                        "বিজ্ঞান (S-X)": (18, 24),
                        "বাংলাদেশ (Y-AD)": (24, 30),
                        "আন্তর্জাতিক (AE-AJ)": (30, 36),
                        "ICT (AK-AP)": (36, 42)
                    }
                    
                    selected_range_name = st.selectbox("কলাম রেঞ্জ সিলেক্ট করুন:", options=list(column_ranges.keys()), key="admin_col_rng")
                    start_idx, end_idx = column_ranges[selected_range_name]
                    
                    if end_idx <= len(raw_df.columns):
                        sub_df = raw_df.iloc[:, start_idx:end_idx].copy()
                        sub_df.columns = ['Question', 'Option_A', 'Option_B', 'Option_C', 'Option_D', 'Correct_Answer']
                        sub_df = sub_df.dropna(subset=['Question']).reset_index(drop=True)
                        if 'Explanation' not in sub_df.columns: 
                            sub_df['Explanation'] = 'ব্যাখ্যা নেই।'
                        else:
                            sub_df['Explanation'] = sub_df['Explanation'].fillna('ব্যাখ্যা নেই।')
                        
                        st.write(f"🔍 ফাইল থেকে মোট প্রশ্ন পাওয়া গেছে: {len(sub_df)}টি")
                        
                        upload_sub_mode = st.radio(
                            "আপলোড করার পদ্ধতি বেছে নিন:",
                            ["সব প্রশ্ন একসাথে (Bulk Import)", "রেন্ডমলি এলোমেলোভাবে প্রশ্ন বাছাই", "একটি একটি করে দেখে সিলেক্ট করুন (Manual)"],
                            key="admin_sub_upload_choice"
                        )
                        
                        questions_to_save = pd.DataFrame()
                        
                        if upload_sub_mode == "সব প্রশ্ন একসাথে (Bulk Import)":
                            questions_to_save = sub_df
                        elif upload_sub_mode == "রেন্ডমলি এলোমেলোভাবে প্রশ্ন বাছাই":
                            sample_size = st.number_input("কতটি প্রশ্ন রেন্ডমলি নিতে চান?", min_value=1, max_value=len(sub_df), value=min(10, len(sub_df)), key="admin_sample_num")
                            questions_to_save = sub_df.sample(n=sample_size).reset_index(drop=True)
                            st.success(f"✨ স্বয়ংক্রিয়ভাবে {sample_size}টি প্রশ্ন বাছাই করা হয়েছে!")
                        else:
                            st.write("---")
                            st.subheader("🔍 ম্যানুয়াল প্রশ্ন সিলেকশন প্রিভিউ")
                            selected_indices = []
                            for idx, row in sub_df.iterrows():
                                if st.checkbox(f"প্রশ্ন {idx+1}: {str(row['Question'])[:50]}...", value=True, key=f"chk_file_q_{idx}"):
                                    selected_indices.append(idx)
                            questions_to_save = sub_df.loc[selected_indices].reset_index(drop=True)

                        if st.button("📌 ফাইল থেকে সেভ করুন", key="admin_save_file_action"):
                            if not questions_to_save.empty:
                                questions_to_save['Subject'] = subject_name
                                if os.path.exists(QUESTIONS_FILE):
                                    existing_q_df = pd.read_csv(QUESTIONS_FILE)
                                    existing_q_df = existing_q_df[existing_q_df['Subject'] != subject_name]
                                    final_q_df = pd.concat([existing_q_df, questions_to_save], ignore_index=True)
                                else:
                                    final_q_df = questions_to_save
                                
                                final_q_df.to_csv(QUESTIONS_FILE, index=False)
                                
                                config_df = pd.DataFrame([{"Subject": subject_name, "Duration": exam_duration}])
                                if os.path.exists(CONFIG_FILE):
                                    existing_conf = pd.read_csv(CONFIG_FILE)
                                    existing_conf = existing_conf[existing_conf['Subject'] != subject_name]
                                    final_conf = pd.concat([existing_conf, config_df], ignore_index=True)
                                else:
                                    final_conf = config_df
                                final_conf.to_csv(CONFIG_FILE, index=False)
                                
                                st.success("✅ ফাইল থেকে সফলভাবে সেভ হয়েছে!")
                            else:
                                st.error("⚠️ কোনো প্রশ্ন সিলেক্ট করা হয়নি।")
                    else:
                        st.error("⚠️ আপনার ফাইলের কলাম সংখ্যা নির্ধারিত রেঞ্জের চেয়ে কম।")
                except Exception as e:
                    st.error(f"ত্রুটি: {e}")

        st.write("---")
        st.subheader("📂 সংরক্ষিত বিষয়সমূহ (প্রশ্ন প্রিভিউ সহ)")
        if os.path.exists(QUESTIONS_FILE):
            q_check_df = pd.read_csv(QUESTIONS_FILE)
            if not q_check_df.empty and 'Subject' in q_check_df.columns:
                for sub in q_check_df['Subject'].unique().tolist():
                    sub_q_df = q_check_df[q_check_df['Subject'] == sub].reset_index(drop=True)
                    count = len(sub_q_df)
                    with st.expander(f"📁 {sub} (প্রশ্ন: {count}টি)"):
                        for i, q_row in sub_q_df.iterrows():
                            st.markdown(f"""
                                <div style="background-color: #fcfcfc; border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                                    <strong>প্রশ্ন {i+1}: {q_row['Question']}</strong><br>
                                    • {q_row['Option_A']}<br>
                                    • {q_row['Option_B']}<br>
                                    • {q_row['Option_C']}<br>
                                    • {q_row['Option_D']}<br>
                                    <span style="color: green; font-weight: bold;">সঠিক উত্তর: {q_row['Correct_Answer']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        if st.button(f"❌ '{sub}' এর সব প্রশ্ন মুছুন", key=f"del_sub_btn_{sub}"):
                            q_check_df[q_check_df['Subject'] != sub].to_csv(QUESTIONS_FILE, index=False)
                            st.rerun()

    else:
        all_q_df = pd.read_csv(QUESTIONS_FILE) if os.path.exists(QUESTIONS_FILE) else pd.DataFrame()

        if not all_q_df.empty and 'Subject' in all_q_df.columns:
            available_subjects = all_q_df['Subject'].unique().tolist()
            
            if st.session_state['exam_submitted']:
                res_info = st.session_state['last_result_data']
                if res_info:
                    if st.button("⬅️ নতুন পরীক্ষা / হোম", type="secondary", key="home_page_btn"):
                        st.session_state['exam_submitted'] = False
                        st.session_state['confirmed_student_name'] = ""
                        st.session_state['selected_exam_subject'] = ""
                        st.session_state['exam_in_progress'] = False
                        st.session_state['last_result_data'] = None
                        st.rerun()

                    st.markdown(f"""
                        <div class="result-box">
                            <h2>🎉 অভিনন্দন, {res_info['student_name']}!</h2>
                            <p style="font-size: 18px; margin: 5px 0;">বিষয়: {res_info['subject']}</p>
                            <h1 style="font-size: 32px; margin: 10px 0;">প্রাপ্ত নম্বর: {res_info['score']} / {res_info['total']}</h1>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.subheader("📊 বিস্তারিত উত্তরমালা (৪ অপশনসহ সঠিক ও ভুল মার্কিং)")
                    st.write("---")
                    
                    for i, row in res_info['active_df'].iterrows():
                        ans = res_info['user_answers'].get(i)
                        raw_correct = str(row['Correct_Answer']).strip()
                        raw_correct_lower = raw_correct.lower()
                        
                        opts = [str(row['Option_A']).strip(), str(row['Option_B']).strip(), str(row['Option_C']).strip(), str(row['Option_D']).strip()]
                        
                        correct_val = ""
                        for opt in opts:
                            opt_lower = opt.lower()
                            if raw_correct_lower in ['ক', 'a'] and (opt.startswith('ক') or opt_lower.startswith('a.')):
                                correct_val = opt
                            elif raw_correct_lower in ['খ', 'b'] and (opt.startswith('খ') or opt_lower.startswith('b.')):
                                correct_val = opt
                            elif raw_correct_lower in ['গ', 'c'] and (opt.startswith('গ') or opt_lower.startswith('c.')):
                                correct_val = opt
                            elif raw_correct_lower in ['ঘ', 'd'] and (opt.startswith('ঘ') or opt_lower.startswith('d.')):
                                correct_val = opt
                            elif raw_correct_lower == opt_lower or raw_correct_lower in opt_lower or opt_lower in raw_correct_lower:
                                correct_val = opt
                        
                        if not correct_val:
                            correct_val = raw_correct

                        options_html = ""
                        for opt in opts:
                            opt_lower = opt.lower()
                            c_val_lower = correct_val.lower()
                            
                            is_correct_option = (
                                opt == correct_val or 
                                opt_lower == c_val_lower or 
                                c_val_lower in opt_lower or 
                                opt_lower in c_val_lower or
                                (raw_correct_lower in ['ক', 'a'] and (opt.startswith('ক') or opt_lower.startswith('a.'))) or
                                (raw_correct_lower in ['খ', 'b'] and (opt.startswith('খ') or opt_lower.startswith('b.'))) or
                                (raw_correct_lower in ['গ', 'c'] and (opt.startswith('গ') or opt_lower.startswith('c.'))) or
                                (raw_correct_lower in ['ঘ', 'd'] and (opt.startswith('ঘ') or opt_lower.startswith('d.')))
                            )
                            
                            is_user_choice = (ans and str(ans).strip() == opt)
                            
                            if is_correct_option and is_user_choice:
                                options_html += f"<div style='color: green; font-weight: bold; margin: 4px 0;'>✅ {opt} (আপনার সঠিক উত্তর)</div>"
                            elif is_correct_option:
                                options_html += f"<div style='color: green; font-weight: bold; margin: 4px 0;'>✅ {opt} (সঠিক উত্তর)</div>"
                            elif is_user_choice and not is_correct_option:
                                options_html += f"<div style='color: red; font-weight: bold; margin: 4px 0;'>❌ {opt} (আপনার ভুল উত্তর)</div>"
                            else:
                                options_html += f"<div style='color: #555; margin: 4px 0;'>• {opt}</div>"
                        
                        st.markdown(f"""
                            <div class="question-card">
                                <strong>প্রশ্ন {i+1}: {str(row['Question'])}</strong><br><br>
                                {options_html}
                                <hr style="margin: 8px 0;">
                                <small>💡 ব্যাখ্যা: {row['Explanation']}</small>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                if not st.session_state['exam_in_progress']:
                    st.subheader("📚 পরীক্ষার বিষয় নির্বাচন করুন")
                    selected_subject = st.selectbox("বিষয়:", available_subjects, key="student_subject_select")
                    st.write("---")
                    
                    df = all_q_df[all_q_df['Subject'] == selected_subject].reset_index(drop=True)
                    duration = 10
                    if os.path.exists(CONFIG_FILE):
                        conf_df = pd.read_csv(CONFIG_FILE)
                        match_conf = conf_df[conf_df['Subject'] == selected_subject]
                        if not match_conf.empty: duration = int(match_conf.iloc[0]['Duration'])

                    if not df.empty:
                        st.info(f"📌 বিষয়: {selected_subject} | ⏱️ সময়: {duration} মিনিট | 🎯 প্রশ্ন: {len(df)}টি")
                        
                        with st.container(border=True):
                            st.markdown("#### ✍️ পরীক্ষার্থীর তথ্য")
                            student_name = st.text_input("আপনার পূর্ণ নাম লিখুন:", placeholder="এখানে নাম লিখুন", key="student_name_input_field")

                            if student_name.strip():
                                existing_session = load_session_progress(student_name.strip(), selected_subject)
                                if existing_session:
                                    st.info("🔄 আপনার এই বিষয়ে একটি অসম্পূর্ণ পরীক্ষা পাওয়া গেছে। 'পরীক্ষা শুরু করুন' চাপলে সেটি আগের জায়গা থেকেই চালু হবে।")

                            if st.button("➔ পরীক্ষা শুরু করুন", type="primary", key="start_exam_action_btn"):
                                if student_name.strip():
                                    clean_name = student_name.strip()
                                    st.session_state['confirmed_student_name'] = clean_name
                                    st.session_state['selected_exam_subject'] = selected_subject

                                    existing_session = load_session_progress(clean_name, selected_subject)
                                    if existing_session:
                                        st.session_state['exam_start_time'] = existing_session.get("start_time", time.time())
                                        saved_answers = existing_session.get("answers", {})
                                        for q_idx_str, ans_val in saved_answers.items():
                                            widget_key = f"q_{q_idx_str}_{selected_subject}"
                                            if ans_val is not None:
                                                st.session_state[widget_key] = ans_val
                                    else:
                                        st.session_state['exam_start_time'] = time.time()
                                        save_session_progress(clean_name, selected_subject, st.session_state['exam_start_time'], duration, {})

                                    st.session_state['exam_in_progress'] = True
                                    st.rerun()
                                else:
                                    st.error("⚠️ নাম লিখুন।")
                else:
                    selected_subject = st.session_state.get('selected_exam_subject', available_subjects[0])
                    df = all_q_df[all_q_df['Subject'] == selected_subject].reset_index(drop=True)
                    
                    duration = 10
                    if os.path.exists(CONFIG_FILE):
                        conf_df = pd.read_csv(CONFIG_FILE)
                        match_conf = conf_df[conf_df['Subject'] == selected_subject]
                        if not match_conf.empty: duration = int(match_conf.iloc[0]['Duration'])
                    
                    current_student = st.session_state['confirmed_student_name']
                    active_df = df.copy()
                    total_seconds = duration * 60
                    
                    if 'exam_start_time' not in st.session_state or st.session_state.get('current_sub') != selected_subject:
                        st.session_state['exam_start_time'] = time.time()
                        st.session_state['current_sub'] = selected_subject

                    elapsed_seconds = int(time.time() - st.session_state['exam_start_time'])
                    remaining_seconds = max(0, total_seconds - elapsed_seconds)

                    end_timestamp_ms = int((st.session_state['exam_start_time'] + total_seconds) * 1000)
                    timer_html = f"""
                        <div id="examTimerBox" style="
                            position: sticky; top: 0; z-index: 99999;
                            background: linear-gradient(135deg, #ff4b4b, #ff9068);
                            color: white; padding: 12px 15px; border-radius: 6px;
                            text-align: center; font-weight: bold;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            margin-bottom: 15px; font-size: 16px; font-family: sans-serif;">
                            ⏳ বাকি সময়: <span id="examTimerText">--:--</span>
                        </div>
                        <script>
                        (function() {{
                            var endTime = {end_timestamp_ms};
                            function tick() {{
                                var now = new Date().getTime();
                                var remaining = Math.max(0, Math.floor((endTime - now) / 1000));
                                var m = Math.floor(remaining / 60);
                                var s = remaining % 60;
                                var el = document.getElementById("examTimerText");
                                if (el) {{
                                    el.innerHTML = (m < 10 ? "0" : "") + m + " মিনিট " + (s < 10 ? "0" : "") + s + " সেকেন্ড";
                                }}
                                var box = document.getElementById("examTimerBox");
                                if (box && remaining <= 60) {{
                                    box.style.background = "linear-gradient(135deg, #b30000, #ff0000)";
                                }}
                                if (remaining <= 0) {{
                                    clearInterval(timerInterval);
                                    try {{ window.parent.location.reload(); }} catch (e) {{ window.location.reload(); }}
                                }}
                            }}
                            var timerInterval = setInterval(tick, 1000);
                            tick();
                        }})();
                        </script>
                    """
                    components.html(timer_html, height=70)

                    auto_submit_triggered = remaining_seconds <= 0

                    st.success(f"পরীক্ষার্থী: **{current_student}** ({selected_subject})")
                    st.write("---")
                    
                    user_answers = {}
                    
                    for i, row in active_df.iterrows():
                        options_list = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
                        
                        with st.container():
                            st.markdown(f"""
                                <div class="question-card">
                                    <strong>প্রশ্ন {i+1}: {str(row['Question'])}</strong>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            user_answers[i] = st.radio(
                                f"উত্তর নির্বাচন করুন (প্রশ্ন {i+1}):", 
                                options_list, 
                                index=None, 
                                key=f"q_{i}_{selected_subject}",
                                label_visibility="collapsed"
                            )

                    save_session_progress(current_student, selected_subject, st.session_state['exam_start_time'], duration, user_answers)

                    def _grade_and_submit(final_answers, note_auto=False):
                        score = 0
                        for i, row in active_df.iterrows():
                            ans = final_answers.get(i)
                            raw_c = str(row['Correct_Answer']).strip().lower()
                            opt_a_str = str(row['Option_A']).strip()
                            opt_b_str = str(row['Option_B']).strip()
                            opt_c_str = str(row['Option_C']).strip()
                            opt_d_str = str(row['Option_D']).strip()
                            
                            correct_v = opt_a_str
                            for o in [opt_a_str, opt_b_str, opt_c_str, opt_d_str]:
                                o_low = o.lower()
                                if raw_c in ['ক', 'a'] and (o.startswith('ক') or o_low.startswith('a.')): correct_v = o
                                elif raw_c in ['খ', 'b'] and (o.startswith('খ') or o_low.startswith('b.')): correct_v = o
                                elif raw_c in ['গ', 'c'] and (o.startswith('গ') or o_low.startswith('c.')): correct_v = o
                                elif raw_c in ['ঘ', 'd'] and (o.startswith('ঘ') or o_low.startswith('d.')): correct_v = o
                                elif raw_c == o_low or raw_c in o_low or o_low in raw_c: correct_v = o

                            if ans and (str(ans).strip() == correct_v or str(ans).strip().lower() == correct_v.lower()):
                                score += 1

                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_result = pd.DataFrame([{
                            "Student Name": current_student, "Subject": selected_subject,
                            "Score": score, "Total Marks": len(active_df), "Submission Time": current_time,
                            "Note": "সময় শেষে অটো-সাবমিট" if note_auto else ""
                        }])
                        
                        if os.path.exists(RESULT_FILE):
                            updated_res = pd.concat([pd.read_csv(RESULT_FILE), new_result], ignore_index=True)
                        else:
                            updated_res = new_result
                        updated_res.to_csv(RESULT_FILE, index=False)

                        clear_session_progress(current_student, selected_subject)
                        
                        st.session_state['exam_submitted'] = True
                        st.session_state['exam_in_progress'] = False
                        st.session_state['last_result_data'] = {
                            "student_name": current_student, "subject": selected_subject,
                            "score": score, "total": len(active_df), "active_df": active_df, "user_answers": final_answers
                        }
                        if not note_auto:
                            st.balloons()
                        st.rerun()

                    if auto_submit_triggered:
                        st.warning("⏰ সময় শেষ! আপনার উত্তরগুলো স্বয়ংক্রিয়ভাবে জমা দেওয়া হচ্ছে...")
                        _grade_and_submit(user_answers, note_auto=True)

                    if st.button("পরীক্ষা জমা দিন", type="primary", key="final_submit_exam_btn"):
                        _grade_and_submit(user_answers, note_auto=False)
        else:
            st.warning("⚠️ বর্তমানে কোনো প্রশ্ন সেট করা নেই।")
