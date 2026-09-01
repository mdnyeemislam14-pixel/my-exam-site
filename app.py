import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

st.set_page_config(page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম", page_icon="📝", layout="centered")

st.title("📝 অনলাইন মডেল টেস্ট")

RESULT_FILE = "results.csv"
QUESTIONS_FILE = "saved_questions.csv"
ADMIN_PASSWORD = "1234"

# ==========================================
# 🔐 সেশন স্টেট ব্যবহার করে লগইন ম্যানেজমেন্ট
# ==========================================
if 'is_admin_logged_in' not in st.session_state:
    st.session_state['is_admin_logged_in'] = False

st.sidebar.header("⚙️ প্যানেল মেনু")

# যদি ইতিমধ্যে লগইন করা থাকে, তবে লগ আউট বাটন দেখাবে
if st.session_state['is_admin_logged_in']:
    st.sidebar.success("✅ অ্যাডমিন মোড সক্রিয়!")
    if st.sidebar.button("🚪 লগ আউট করুন (Log Out)"):
        st.session_state['is_admin_logged_in'] = False
        st.rerun()
        
    admin_menu = st.sidebar.radio("অ্যাডমিন কন্ট্রোল প্যানেল:", [
        "📝 প্রশ্ন আপলোড ও সেটআপ",
        "📊 সকল শিক্ষার্থীর মেধা তালিকা ও রিপোর্ট"
    ])
    is_admin = True
else:
    entered_password = st.sidebar.text_input("অ্যাডমিন পাসওয়ার্ড দিন (শিক্ষকদের জন্য):", type="password")
    
    if entered_password == ADMIN_PASSWORD:
        st.session_state['is_admin_logged_in'] = True
        st.rerun()
    elif entered_password != "":
        st.sidebar.error("❌ ভুল পাসওয়ার্ড!")
    
    st.sidebar.divider()
    student_menu = st.sidebar.radio("শিক্ষার্থী মেনু:", [
        "📝 পরীক্ষা দিন",
        "🏆 ক্লাসের মেধা তালিকা (Leaderboard)"
    ])
    is_admin = False

# ==========================================
# 📊 ১. অ্যাডমিন: মেধা তালিকা ও রিপোর্ট সেক্টর
# ==========================================
if is_admin and admin_menu == "📊 শিক্ষার্থীদের মেধা তালিকা ও রিপোর্ট":
    st.subheader("🏆 সকল শিক্ষার্থীর মেধা তালিকা ও রিপোর্ট (অ্যাডমিন ভিউ)")
    st.write("---")
    
    if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
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
    st.write("এখানে সকল শিক্ষার্থীর প্রাপ্ত নম্বরের মেধা তালিকা দেখতে পাবেন।")
    st.write("---")
    
    if os.path.exists(RESULT_FILE):
        res_df = pd.read_csv(RESULT_FILE)
        if not res_df.empty:
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
        st.sidebar.subheader("📋 প্রশ্ন দেওয়ার মাধ্যম:")
        input_mode = st.sidebar.radio("মাধ্যম বেছে নিন:", [
            "এক ক্লিকের টেক্সট পেস্ট (Easy Paste)",
            "এক্সেল/সিএসভি ফাইল আপলোড"
        ], key="admin_input_mode")

        if input_mode == "এক ক্লিকের টেক্সট পেস্ট (Easy Paste)":
            st.sidebar.subheader("📋 সব প্রশ্ন একসাথে পেস্ট করুন")
            pasted_text = st.sidebar.text_area("এখানে আপনার প্রশ্ন পেস্ট করুন:", height=250)
            
            if pasted_text:
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
                            "Question": q_text,
                            "Option_A": opt_a,
                            "Option_B": opt_b,
                            "Option_C": opt_c,
                            "Option_D": opt_d,
                            "Correct_Answer": correct_ans,
                            "Explanation": explanation
                        })
                
                if parsed_questions:
                    temp_df = pd.DataFrame(parsed_questions)
                    temp_df.to_csv(QUESTIONS_FILE, index=False)
                    st.sidebar.success("✅ টেক্সট থেকে প্রশ্ন সফলভাবে ফাইলে সেভ হয়েছে!")

        else:
            uploaded_file = st.sidebar.file_uploader("questions.xlsx বা csv ফাইল আপলোড করুন:", type=["xlsx", "csv"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        raw_df = pd.read_csv(uploaded_file)
                    else:
                        raw_df = pd.read_excel(uploaded_file)
                    
                    st.sidebar.subheader("📚 সাবজেক্টের কলাম রেঞ্জ সিলেক্ট করুন")
                    
                    def get_column_letter(n):
                        string = ""
                        while n >= 0:
                            string = chr(n % 26 + 65) + string
                            n = n // 26 - 1
                        return string

                    total_cols = len(raw_df.columns)
                    col_choices = {}
                    
                    for idx in range(0, total_cols, 6):
                        start_letter = get_column_letter(idx)
                        end_letter = get_column_letter(min(idx + 5, total_cols - 1))
                        col_choices[idx] = f"কলাম {start_letter} থেকে {end_letter} (প্রশ্ন, অপশন ৪টি ও উত্তর)"

                    selected_start_idx = st.sidebar.selectbox(
                        "কোন সাবজেক্টের কলাম থেকে প্রশ্ন নিতে চান?",
                        options=list(col_choices.keys()),
                        format_func=lambda x: col_choices[x]
                    )
                    
                    start_idx = selected_start_idx
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

                        if st.sidebar.button("📌 এই প্রশ্নগুলো দিয়ে পরীক্ষা সেট করুন"):
                            if filter_type == "র‍্যান্ডম (Random) নির্দিষ্ট সংখ্যক প্রশ্ন":
                                final_filtered_df = sub_df.sample(n=num_q).reset_index(drop=True)
                            
                            final_filtered_df.to_csv(QUESTIONS_FILE, index=False)
                            st.sidebar.success("✅ প্রশ্ন সফলভাবে লক ও ফাইলে সেভ করা হয়েছে!")
                    else:
                        st.sidebar.error("⚠️ সঠিক কলাম রেঞ্জ পাওয়া যায়নি।")
                except Exception as e:
                    st.sidebar.error(f"ফাইল পড়তে সমস্যা হয়েছে: {e}")

    # পরীক্ষার্থীদের মূল পরীক্ষার পেজ
    df = None
    if os.path.exists(QUESTIONS_FILE):
        df = pd.read_csv(QUESTIONS_FILE)

    if df is not None and not df.empty:
        st.info(f"🎉 **পরীক্ষার জন্য প্রশ্ন প্রস্তুত আছে!**")
        
        student_name = st.text_input("পরীক্ষার্থীর নাম লিখুন:", placeholder="আপনার নাম")
        
        if student_name:
            active_df = df.copy()
            
            st.success(f"স্বাগতম, **{student_name}**! পরীক্ষা শুরু করুন।")
            st.divider()
            
            user_answers = {}
            
            for i, row in active_df.iterrows():
                st.markdown(f"##### **{i+1}. {str(row['Question'])}**")
                options_list = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
                
                user_answers[i] = st.radio(
                    f"উত্তর বেছে নিন:", 
                    options_list, 
                    index=None, 
                    key=f"q_{i}"
                )
                st.write("---")
                
            if st.button("পরীক্ষা জমা দিন", type="primary"):
                score = 0
                total = len(active_df)
                
                st.subheader("📊 আপনার পরীক্ষার ফলাফল ও মূল্যায়ন")
                st.write("---")
                
                for i, row in active_df.iterrows():
                    ans = user_answers[i]
                    correct = str(row['Correct_Answer'])
                    
                    st.markdown(f"##### **প্রশ্ন {i+1}: {str(row['Question'])}**")
                    
                    if ans and ans.strip() == correct.strip():
                        score += 1
                        st.success(f"✅ সঠিক উত্তর! (আপনার উত্তর: {ans})")
                    else:
                        st.error(f"❌ ভুল উত্তর! (আপনার উত্তর ছিল: {ans if ans else 'দেওয়া হয়নি'})")
                        st.info(f"👉 **সঠিক উত্তর:** {correct}")
                    
                    st.markdown(f"💡 **ব্যাখ্যা:** {row['Explanation']}")
                    st.write("---")
                
                st.metric(label=f"{student_name}-এর মোট ফলাফল", value=f"{score} / {total}")
                st.balloons()
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_result = pd.DataFrame([{
                    "Student Name": student_name,
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
    else:
        st.warning("⚠️ বর্তমানে কোনো প্রশ্ন সেট করা নেই। শিক্ষক মহোদয় পাসওয়ার্ড দিয়ে ফাইল আপলোড বা টেক্সট পেস্ট করে প্রশ্ন সেট করলে এখানে পরীক্ষা দেখা যাবে।")
