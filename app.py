import streamlit as st
import pandas as pd
import random
import os
import time
from datetime import datetime

st.set_page_config(page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম", page_icon="📝", layout="centered")

# Streamlit এর ডিফল্ট হেডার, ফর্ক বাটন, ফুটার এবং ব্র্যান্ডিং হাইড করার জন্য CSS
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("📝 অনলাইন মডেল টেস্ট প্ল্যাটফর্ম")
st.caption("✨ Powered by **Job Efforts**")

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
CONFIG_FILE = "exam_configs.csv"
ADMIN_PASSWORD = "1234"

# ==========================================
# 🔐 সেশন স্টেট ম্যানেজমেন্ট
# ==========================================
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

st.sidebar.header("⚙️ মেনু")

admin_menu = None
student_menu = None

# যদি অ্যাডমিন লগইন করা থাকে
if st.session_state['is_admin_logged_in']:
    st.sidebar.success("✅ অ্যাডমিন মোড সক্রিয়!")
    
    if st.sidebar.button("🚪 লগ আউট করুন (Log Out)"):
        st.session_state['is_admin_logged_in'] = False
        st.session_state['confirmed_student_name'] = ""
        st.session_state['exam_submitted'] = False
        st.session_state['selected_exam_subject'] = ""
        st.rerun()
        
    admin_menu = st.sidebar.radio("অ্যাডমিন কন্ট্রোল প্যানেল:", [
        "📝 প্রশ্ন আপলোড ও সেটআপ (একাধিক বিষয়)",
        "📊 সকল শিক্ষার্থীর মেধা তালিকা ও রিপোর্ট"
    ])
    is_admin = True
else:
    # শিক্ষার্থীরা শুধু তাদের নির্দিষ্ট মেনুটাই দেখতে পাবে
    student_menu = st.sidebar.radio("শিক্ষার্থী মেনু:", [
        "📝 পরীক্ষা দিন",
        "🏆 ক্লাসের মেধা তালিকা (Leaderboard)"
    ])
    is_admin = False
    
    # সাধারণ শিক্ষার্থীদের চোখের আড়ালে রাখার জন্য অ্যাডমিন লগইন অপশনটি নিচের দিকে একটি ড্রপডাউনে রাখা হয়েছে
    with st.sidebar.expander("🔐 শিক্ষক/অ্যাডমিন লগইন"):
        entered_password = st.text_input("পাসওয়ার্ড দিন:", type="password", key="admin_pwd_input")
        if st.button("🔑 লগইন করুন"):
            if entered_password == ADMIN_PASSWORD:
                st.session_state['is_admin_logged_in'] = True
                st.rerun()
            else:
                st.error("❌ ভুল পাসওয়ার্ড!")

# ==========================================
# 📊 ১. অ্যাডমিন: মেধা তালিকা ও রিপোর্ট সেক্টর
# ==========================================
if is_admin and admin_menu == "📊 সকল শিক্ষার্থীর মেধা তালিকা ও রিপোর্ট":
    st.subheader("🏆 সকল শিক্ষার্থীর মেধা তালিকা ও রিপোর্ট (অ্যাডমিন ভিউ)")
    st.write("---")
    
    if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
            if 'Subject' in res_df.columns:
                subjects_list = ["সকল বিষয়"] + res_df['Subject'].unique().tolist()
                selected_filter_sub = st.selectbox("বিষয় অনুযায়ী ফলাফল দেখুন:", subjects_list)
                if selected_filter_sub != "সকল বিষয়":
                    res_df = res_df[res_df['Subject'] == selected_filter_sub]

            st.info(f"মোট জমা পড়া খাতা: {len(res_df)} টি")
            
            sorted_res = res_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            sorted_res.index = sorted_res.index + 1
            st.dataframe(sorted_res, use_container_width=True)
            
            csv_data = sorted_res.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 মেধা তালিকা ডাউনলোড করুন (CSV)",
                data=csv_data,
                file_name="merit_list.csv",
                mime="text/csv",
            )
            
            st.write("---")
            if st.button("🗑️ সকল ফলাফল মুছে ফেলুন (Reset Results)", type="secondary"):
                if os.path.exists(RESULT_FILE):
                    os.remove(RESULT_FILE)
                    st.success("সকল ফলাফল সফলভাবে মুছে ফেলা হয়েছে!")
                    st.rerun()
        else:
            st.warning("এখনো কেউ পরীক্ষা জমা দেয়নি।")
    else:
        st.warning("এখনো কোনো ফলাফল জমা হয়নি।")

# ==========================================
# 🏆 ২. শিক্ষার্থী: ক্লাসের মেধা তালিকা দেখার পেজ
# ==========================================
elif not is_admin and student_menu == "🏆 ক্লাসের মেধা তালিকা (Leaderboard)":
    st.subheader("🏆 ক্লাসের লাইভ মেধা তালিকা")
    st.write("এখানে বিভিন্ন বিষয়ের প্রাপ্ত নম্বরের মেধা তালিকা দেখতে পাবেন।")
    st.write("---")
    
    if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
            if 'Subject' in res_df.columns:
                subjects_list = res_df['Subject'].unique().tolist()
                leaderboard_sub = st.selectbox("কোন বিষয়ের মেধা তালিকা দেখতে চান?", subjects_list, key="lb_sub")
                res_df = res_df[res_df['Subject'] == leaderboard_sub]
            
            sorted_res = res_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            sorted_res.index = sorted_res.index + 1
            st.dataframe(sorted_res, use_container_width=True)
        else:
            st.info("এখনো কোনো ফলাফল প্রকাশিত হয়নি।")
    else:
        st.info("এখনো কেউ পরীক্ষা জমা দেয়নি।")

# ==========================================
# 📝 ৩. প্রশ্ন আপলোড বা পরীক্ষার্থীদের মূল পরীক্ষার পেজ
# ==========================================
else:
    if is_admin:
        st.sidebar.markdown("### 📚 নতুন বিষয় ও প্রশ্ন সংযোজন")
        
        subject_options = [
            "বাংলা", 
            "English", 
            "গণিত", 
            "বিজ্ঞান", 
            "বাংলাদেশের বিষয়াবলি", 
            "আন্তর্জাতিক বিষয়াবলি", 
            "ICT"
        ]
        subject_name = st.sidebar.selectbox("বিষয়ের নাম সিলেক্ট করুন:", subject_options)
        
        exam_duration = st.sidebar.number_input("⏱️ পরীক্ষার সময় (মিনিটে):", min_value=1, max_value=300, value=10)
        
        st.sidebar.markdown("---")
        input_mode = st.sidebar.radio("প্রশ্ন দেওয়ার মাধ্যম বেছে নিন:", [
            "এক ক্লিকের টেক্সট পেস্ট (Easy Paste)",
            "এক্সেল/সিএসভি ফাইল আপলোড"
        ], key="admin_input_mode")

        if input_mode == "এক ক্লিকের টেক্সট পেস্ট (Easy Paste)":
            st.sidebar.subheader("📋 সব প্রশ্ন একসাথে পেস্ট করুন")
            pasted_text = st.sidebar.text_area("এখানে আপনার প্রশ্ন পেস্ট করুন:", height=250, placeholder="১. প্রশ্ন...\nক) অপশন...\nখ) অপশন...\nগ) অপশন...\nঘ) অপশন...\nউত্তর: ক\nব্যাখ্যা: ...")
            
            if st.sidebar.button("📌 টেক্সট থেকে প্রশ্ন সেভ করুন"):
                if not pasted_text:
                    st.sidebar.error("⚠️ অনুগ্রহ করে প্রশ্ন পেস্ট করুন।")
                else:
                    parsed_questions = []
                    blocks = pasted_text.strip().split('\n\n')
                    
                    for block in blocks:
                        lines = [line.strip() for line in block.split('\n') if line.strip()]
                        if len(lines) >= 5:
                            q_text = lines[0]
                            opt_a = lines[1]
                            opt_b = lines[2]
                            opt_c = lines[3]
                            opt_d = lines[4]
                            
                            correct_ans = opt_a
                            explanation = "কোন ব্যাখ্যা নেই।"
                            
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
                        
                        st.sidebar.success(f"✅ '{subject_name}' বিষয়ের প্রশ্ন ও সময় সফলভাবে স্থায়ীভাবে সেভ হয়েছে!")

        else:
            uploaded_file = st.sidebar.file_uploader("questions.xlsx বা csv ফাইল আপলোড করুন:", type=["xlsx", "csv"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        raw_df = pd.read_csv(uploaded_file)
                    else:
                        raw_df = pd.read_excel(uploaded_file)
                    
                    st.sidebar.subheader("📚 কলাম সেটআপ (আপনার ফাইল অনুযায়ী)")
                    
                    predefined_columns = {
                        "বাংলা (A - F)": 0,
                        "English (G - L)": 6,
                        "গণিত (M - R)": 12,
                        "বিজ্ঞান (S - X)": 18,
                        "বাংলাদেশের বিষয়াবলি (Y - AD)": 24,
                        "আন্তর্জাতিক বিষয়াবলি (AE - AJ)": 30,
                        "ICT (AK - AP)": 36
                    }

                    selected_col_range = st.sidebar.selectbox(
                        "কোন বিষয়ের কলাম রেঞ্জ থেকে প্রশ্ন নিতে চান?",
                        options=list(predefined_columns.keys())
                    )
                    
                    start_idx = predefined_columns[selected_col_range]
                    total_cols = len(raw_df.columns)
                    
                    if start_idx + 5 < total_cols:
                        sub_df = raw_df.iloc[:, start_idx:start_idx+6].copy()
                        sub_df.columns = ['Question', 'Option_A', 'Option_B', 'Option_C', 'Option_D', 'Correct_Answer']
                        
                        sub_df = sub_df.dropna(subset=['Question']).reset_index(drop=True)
                        
                        if 'Explanation' not in sub_df.columns:
                            sub_df['Explanation'] = 'কোন ব্যাখ্যা দেওয়া হয়নি।'
                        
                        st.sidebar.subheader("🎯 প্রশ্ন ফিল্টার অপশন")
                        filter_type = st.sidebar.radio("কীভাবে প্রশ্ন সিলেক্ট করতে চান?", [
                            "সব প্রশ্ন দিয়ে পরীক্ষা",
                            "র‍্যান্ডম (Random) নির্দিষ্ট সংখ্যক প্রশ্ন",
                            "ম্যানুয়ালি বেছে বেছে প্রশ্ন সিলেক্ট"
                        ], key="filter_radio")
                        
                        final_filtered_df = sub_df
                        
                        if filter_type == "র‍্যান্ডম (Random) নির্দিষ্ট সংখ্যক প্রশ্ন":
                            max_q = len(sub_df)
                            num_q = st.sidebar.number_input(f"কতটি প্রশ্ন রাখতে চান? (সর্বোচ্চ {max_q})", min_value=1, max_value=max_q, value=min(10, max_q))
                        elif filter_type == "ম্যানুয়ালি বেছে বেছে প্রশ্ন সিলেক্ট":
                            selected_indices = st.sidebar.multiselect(
                                "তালিকা থেকে প্রশ্নগুলো নির্বাচন করুন:",
                                options=list(sub_df.index),
                                format_func=lambda x: f"প্রশ্ন {x+1}: {str(sub_df.loc[x, 'Question'])[:30]}..."
                            )
                            if selected_indices:
                                final_filtered_df = sub_df.loc[selected_indices].reset_index(drop=True)

                        if st.sidebar.button("📌 ফাইল থেকে প্রশ্ন সেট করুন"):
                            if filter_type == "র‍্যান্ডম (Random) নির্দিষ্ট সংখ্যক প্রশ্ন":
                                final_filtered_df = sub_df.sample(n=num_q).reset_index(drop=True)
                            
                            final_filtered_df['Subject'] = subject_name
                            
                            if os.path.exists(QUESTIONS_FILE):
                                existing_q_df = pd.read_csv(QUESTIONS_FILE)
                                existing_q_df = existing_q_df[existing_q_df['Subject'] != subject_name]
                                final_q_df = pd.concat([existing_q_df, final_filtered_df], ignore_index=True)
                            else:
                                final_q_df = final_filtered_df
                            
                            final_q_df.to_csv(QUESTIONS_FILE, index=False)
                            
                            config_df = pd.DataFrame([{"Subject": subject_name, "Duration": exam_duration}])
                            if os.path.exists(CONFIG_FILE):
                                existing_conf = pd.read_csv(CONFIG_FILE)
                                existing_conf = existing_conf[existing_conf['Subject'] != subject_name]
                                final_conf = pd.concat([existing_conf, config_df], ignore_index=True)
                            else:
                                final_conf = config_df
                            final_conf.to_csv(CONFIG_FILE, index=False)
                            
                            st.sidebar.success(f"✅ '{subject_name}' বিষয়ের ফাইল থেকে প্রশ্ন ও সময় সফলভাবে স্থায়ীভাবে সেভ হয়েছে!")
                    else:
                        st.sidebar.error("⚠️ আপনার এক্সেল ফাইলে এই কলাম রেঞ্জ পর্যন্ত ডেটা নেই বা কলাম সংখ্যা কম আছে।")
                except Exception as e:
                    st.sidebar.error(f"ফাইল পড়তে সমস্যা হয়েছে: {e}")

        st.write("---")
        st.subheader("📂 স্থায়ীভাবে সংরক্ষিত বিষয়সমূহ ও প্রশ্ন ব্যবস্থাপনা")
        st.info("💡 এখানে সেভ করা প্রশ্নগুলো সার্ভারে নিরাপদভাবে সংরক্ষিত থাকে। আপনি নিজে 'মুছুন' বাটন ক্লিক না করা পর্যন্ত এগুলো মুছে যাবে না।")
        
        if os.path.exists(QUESTIONS_FILE):
            q_check_df = pd.read_csv(QUESTIONS_FILE)
            if not q_check_df.empty and 'Subject' in q_check_df.columns:
                saved_subs = q_check_df['Subject'].unique().tolist()
                for sub in saved_subs:
                    count = len(q_check_df[q_check_df['Subject'] == sub])
                    
                    with st.expander(f"📁 বিষয়: {sub} (প্রশ্ন সংখ্যা: {count}টি)"):
                        sub_questions = q_check_df[q_check_df['Subject'] == sub].reset_index(drop=True)
                        
                        for idx, q_row in sub_questions.iterrows():
                            st.markdown(f"**প্রশ্ন {idx+1}:** {q_row['Question']}")
                            st.markdown(f"- (ক) {q_row['Option_A']}")
                            st.markdown(f"- (খ) {q_row['Option_B']}")
                            st.markdown(f"- (গ) {q_row['Option_C']}")
                            st.markdown(f"- (ঘ) {q_row['Option_D']}")
                            st.success(f"✔️ সঠিক উত্তর: {q_row['Correct_Answer']}")
                            st.info(f"💡 ব্যাখ্যা: {q_row['Explanation']}")
                            st.write("---")
                        
                        if st.button(f"❌ 🗑️ '{sub}' বিষয়ের সকল প্রশ্ন চিরতরে মুছুন", key=f"del_sub_{sub}"):
                            new_q_df = q_check_df[q_check_df['Subject'] != sub]
                            new_q_df.to_csv(QUESTIONS_FILE, index=False)
                            
                            if os.path.exists(CONFIG_FILE):
                                conf_df = pd.read_csv(CONFIG_FILE)
                                conf_df = conf_df[conf_df['Subject'] != sub]
                                conf_df.to_csv(CONFIG_FILE, index=False)
                            st.success(f"'{sub}' বিষয়টি সফলভাবে মুছে ফেলা হয়েছে!")
                            st.rerun()
            else:
                st.info("কোনো বিষয় সেভ করা নেই।")
        else:
            st.info("কোনো বিষয় সেভ করা নেই।")

    # পরীক্ষার্থীদের মূল পরীক্ষার পেজ
    else:
        if os.path.exists(QUESTIONS_FILE):
            all_q_df = pd.read_csv(QUESTIONS_FILE)
        else:
            all_q_df = pd.DataFrame()

        if not all_q_df.empty and 'Subject' in all_q_df.columns:
            available_subjects = all_q_df['Subject'].unique().tolist()
            
            # যদি পরীক্ষা ইতিমধ্যেই জমা হয়ে গিয়ে থাকে, তবে ফলাফল স্ক্রিন স্থিরভাবে দেখাবে
            if st.session_state['exam_submitted']:
                res_info = st.session_state['last_result_data']
                if res_info:
                    if st.button("⬅️ হোমে ফিরে যান / নতুন পরীক্ষা", type="secondary"):
                        st.session_state['exam_submitted'] = False
                        st.session_state['confirmed_student_name'] = ""
                        st.session_state['selected_exam_subject'] = ""
                        st.session_state['last_result_data'] = None
                        st.rerun()

                    st.subheader(f"🎉 অভিনন্দন, **{res_info['student_name']}**! আপনার পরীক্ষা সফলভাবে জমা হয়েছে।")
                    st.markdown(f"### 🏆 আপনার প্রাপ্ত ফলাফল: **{res_info['score']} / {res_info['total']}** (বিষয়: {res_info['subject']})")
                    st.write("---")
                    
                    st.subheader("📊 বিস্তারিত উত্তরমালা ও মূল্যায়ন")
                    st.write("---")
                    
                    for i, row in res_info['active_df'].iterrows():
                        ans = res_info['user_answers'].get(i)
                        correct = str(row['Correct_Answer'])
                        
                        st.markdown(f"##### **প্রশ্ন {i+1}: {str(row['Question'])}**")
                        
                        if ans and ans.strip() == correct.strip():
                            st.success(f"✅ সঠিক উত্তর! (আপনার উত্তর: {ans})")
                        else:
                            st.error(f"❌ ভুল উত্তর! (আপনার উত্তর ছিল: {ans if ans else 'দেওয়া হয়নি'})")
                            st.info(f"👉 **সঠিক উত্তর:** {correct}")
                        
                        st.markdown(f"💡 **ব্যাখ্যা:** {row['Explanation']}")
                        st.write("---")
                    
                    if st.button("🔄 নতুন পরীক্ষা শুরু করুন / হোমে ফিরে যান", type="primary", key="bottom_home_btn"):
                        st.session_state['exam_submitted'] = False
                        st.session_state['confirmed_student_name'] = ""
                        st.session_state['selected_exam_subject'] = ""
                        st.session_state['last_result_data'] = None
                        st.rerun()
            else:
                # স্বাভাবিক পরীক্ষার ফ্লো
                if not st.session_state['confirmed_student_name']:
                    st.subheader("📚 পরীক্ষার বিষয় নির্বাচন করুন")
                    selected_subject = st.selectbox("কোন বিষয়ের পরীক্ষা দিতে চান তা সিলেক্ট করুন:", available_subjects)
                    st.write("---")
                    
                    # সুনির্দিষ্ট বিষয়ের প্রশ্ন ফিল্টার করা
                    df = all_q_df[all_q_df['Subject'] == selected_subject].reset_index(drop=True)
                    
                    duration = 10
                    if os.path.exists(CONFIG_FILE):
                        conf_df = pd.read_csv(CONFIG_FILE)
                        match_conf = conf_df[conf_df['Subject'] == selected_subject]
                        if not match_conf.empty:
                            duration = int(match_conf.iloc[0]['Duration'])

                    if df is not None and not df.empty:
                        total_marks = len(df)
                        st.info(f"📌 **বিষয়:** {selected_subject} | ⏱️ **নির্ধারিত সময়:** {duration} মিনিট | 🎯 **মোট মার্ক:** {total_marks}")
                        
                        with st.container(border=True):
                            st.markdown("#### ✍️ পরীক্ষার্থীর তথ্য ও সূচনা")
                            student_name = st.text_input("আপনার পূর্ণ নাম লিখুন:", placeholder="এখানে নাম টাইপ করুন", key="input_student_name")
                            st.caption("ℹ️ নাম লেখার পর নিচের বাটনে ক্লিক করুন।")
                            
                            if st.button("এগিয়ে যান ➔ পরীক্ষা শুরু করুন", type="primary"):
                                if student_name.strip():
                                    st.session_state['confirmed_student_name'] = student_name.strip()
                                    st.session_state['selected_exam_subject'] = selected_subject
                                    st.session_state['exam_start_time'] = time.time()
                                    st.rerun()
                                else:
                                    st.error("⚠️ অনুগ্রহ করে আপনার নাম লিখুন।")
                else:
                    selected_subject = st.session_state.get('selected_exam_subject', available_subjects[0])
                    df = all_q_df[all_q_df['Subject'] == selected_subject].reset_index(drop=True)
                    
                    duration = 10
                    if os.path.exists(CONFIG_FILE):
                        conf_df = pd.read_csv(CONFIG_FILE)
                        match_conf = conf_df[conf_df['Subject'] == selected_subject]
                        if not match_conf.empty:
                            duration = int(match_conf.iloc[0]['Duration'])
                    
                    total_marks = len(df)
                    current_student = st.session_state['confirmed_student_name']
                    active_df = df.copy()
                    
                    total_seconds = duration * 60
                    
                    if 'exam_start_time' not in st.session_state or st.session_state.get('current_sub') != selected_subject:
                        st.session_state['exam_start_time'] = time.time()
                        st.session_state['current_sub'] = selected_subject

                    elapsed_seconds = int(time.time() - st.session_state['exam_start_time'])
                    remaining_seconds = max(0, total_seconds - elapsed_seconds)
                    
                    mins = remaining_seconds // 60
                    secs = remaining_seconds % 60
                    
                    st.sidebar.markdown("---")
                    st.sidebar.subheader("⏱️ পরীক্ষার লাইভ টাইমার")
                    st.sidebar.markdown(f"⏳ **বাকি সময়:**\n### `{mins:02d} মিনিট {secs:02d} সেকেন্ড`")
                    st.sidebar.caption(f"পরীক্ষার্থী: {current_student} ({selected_subject})")
                    
                    st.success(f"স্বাগতম, **{current_student}**! **{selected_subject}** বিষয়ের পরীক্ষা শুরু করুন।")
                    st.divider()
                    
                    user_answers = {}
                    
                    for i, row in active_df.iterrows():
                        st.markdown(f"##### **{i+1}. {str(row['Question'])}**")
                        options_list = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
                        
                        user_answers[i] = st.radio(
                            f"উত্তর বেছে নিন:", 
                            options_list, 
                            index=None, 
                            key=f"q_{i}_{selected_subject}"
                        )
                        st.write("---")
                        
                    if st.button("পরীক্ষা জমা দিন", type="primary"):
                        score = 0
                        total = total_marks
                        
                        for i, row in active_df.iterrows():
                            ans = user_answers.get(i)
                            correct = str(row['Correct_Answer'])
                            if ans and ans.strip() == correct.strip():
                                score += 1

                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_result = pd.DataFrame([{
                            "Student Name": current_student,
                            "Subject": selected_subject,
                            "Score": score,
                            "Total Marks": total,
                            "Submission Time": current_time
                        }])
                        
                        if os.path.exists(RESULT_FILE):
                            existing_res = pd.read_csv(RESULT_FILE)
                            updated_res = pd.concat([existing_res, new_result], ignore_index=True)
                        else:
                            updated_res = new_result
                            
                        updated_res.to_csv(RESULT_FILE, index=False)
                        
                        st.session_state['exam_submitted'] = True
                        st.session_state['last_result_data'] = {
                            "student_name": current_student,
                            "subject": selected_subject,
                            "score": score,
                            "total": total,
                            "active_df": active_df,
                            "user_answers": user_answers
                        }
                        st.balloons()
                        st.rerun()
                    
                    if remaining_seconds > 0:
                        time.sleep(1)
                        st.rerun()
        else:
            st.warning("⚠️ বর্তমানে কোনো বিষয়ের পরীক্ষা সেট করা নেই। শিক্ষক মহোদয় পাসওয়ার্ড দিয়ে একাধিক বিষয়ের প্রশ্ন ও সময় সেট করলে শিক্ষার্থীরা এখানে পরীক্ষা দিতে পারবে।")
