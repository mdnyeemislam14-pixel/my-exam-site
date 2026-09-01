import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম", page_icon="📝", layout="centered")

st.title("📝 অনলাইন মডেল টেস্ট")

# ==========================================
# 🔐 অ্যাডমিন সিকিউরিটি পাসওয়ার্ড সেটআপ
# ==========================================
ADMIN_PASSWORD = "1234"

st.sidebar.header("⚙️ শিক্ষক / অ্যাডমিন প্যানেল")
entered_password = st.sidebar.text_input("অ্যাডমিন পাসওয়ার্ড দিন:", type="password")

if entered_password == ADMIN_PASSWORD:
    st.sidebar.success("✅ অ্যাডমিন মোড সক্রিয়!")
    
    input_mode = st.sidebar.radio("প্রশ্ন দেওয়ার মাধ্যম বেছে নিন:", [
        "এক ক্লিকের টেক্সট পেস্ট (Easy Paste)",
        "এক্সেল/সিএসভি ফাইল আপলোড"
    ])

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
                st.session_state['saved_df'] = temp_df
                st.sidebar.success("✅ টেক্সট থেকে প্রশ্ন সফলভাবে সেভ হয়েছে!")

    else:
        uploaded_file = st.sidebar.file_uploader("questions.xlsx বা csv ফাইল আপলোড করুন:", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    raw_df = pd.read_excel(uploaded_file)
                
                st.sidebar.subheader("📚 সাবজেক্ট / কলাম রেঞ্জ সিলেক্ট করুন")
                
                # আপনার প্রতি ৫ কলামের প্যাটার্ন অনুযায়ী অপশন তৈরি
                # যেমন: প্রথম সাবজেক্ট (0-4 ইনডেক্স), দ্বিতীয় সাবজেক্ট (6-10 ইনডেক্স) ইত্যাদি
                total_cols = len(raw_df.columns)
                subject_options = {}
                
                # স্বয়ংক্রিয়ভাবে প্রতি ৫ কলাম পরপর সাবজেক্ট ব্লক খুঁজে বের করা
                i = 0
                sub_count = 1
                while i < total_cols:
                    q_col_name = str(raw_df.columns[i]).strip()
                    if q_col_name and not q_col_name.startswith("Unnamed"):
                        subject_options[f"সাবজেক্ট {sub_count} (কলাম {i+1} থেকে শুরু)"] = i
                        sub_count += 1
                    i += 6 # প্রতি সাবজেক্টের কলাম গ্যাপ হিসাব করে (যেমন A-F বা এর কাছাকাছি)
                
                # যদি সরাসরি ড্রপডাউন দিতে চান অথবা ইনডেক্স সিলেক্ট করতে চান:
                selected_sub_key = st.sidebar.selectbox(
                    "কোন সাবজেক্টের প্রশ্ন নিয়ে পরীক্ষা নিতে চান?", 
                    options=list(range(0, total_cols, 6)),
                    format_func=lambda x: f"কলাম {x+1} থেকে পরবর্তী অংশ (যেমন: প্রশ্ন ও অপশন ক, খ, গ, ঘ)"
                )
                
                start_idx = selected_sub_key
                # সাবজেক্টের ডেটা কাট করে নেওয়া (প্রশ্ন + ৪টি অপশন = ৫টি কলাম)
                if start_idx + 4 < total_cols:
                    sub_df = raw_df.iloc[:, start_idx:start_idx+5].copy()
                    sub_df.columns = ['Question', 'Option_A', 'Option_B', 'Option_C', 'Option_D']
                    
                    # খালি সারিগুলো বাদ দেওয়া
                    sub_df = sub_df.dropna(subset=['Question']).reset_index(drop=True)
                    
                    if 'Correct_Answer' not in sub_df.columns:
                        sub_df['Correct_Answer'] = sub_df['Option_A']
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
                        final_filtered_df = sub_df.sample(n=num_q).reset_index(drop=True)
                        
                    elif filter_type == "ম্যানুয়ালি বেছে বেছে প্রশ্ন সিলেক্ট":
                        selected_indices = st.sidebar.multiselect(
                            "তালিকা থেকে প্রশ্নগুলো নির্বাচন করুন:",
                            options=list(sub_df.index),
                            format_func=lambda x: f"প্রশ্ন {x+1}: {str(sub_df.loc[x, 'Question'])[:30]}..."
                        )
                        if selected_indices:
                            final_filtered_df = sub_df.loc[selected_indices].reset_index(drop=True)
                    
                    if final_filtered_df is not None and not final_filtered_df.empty:
                        st.session_state['saved_df'] = final_filtered_df
                        st.sidebar.success("✅ সাবজেক্টের প্রশ্ন সফলভাবে সিলেক্ট ও সেভ হয়েছে!")
                else:
                    st.sidebar.error("⚠️ সঠিক কলাম রেঞ্জ পাওয়া যায়নি।")
            except Exception as e:
                st.sidebar.error(f"ফাইল পড়তে সমস্যা হয়েছে: {e}")

elif entered_password != "":
    st.sidebar.error("❌ ভুল পাসওয়ার্ড!")

# ==========================================
# 📝 পরীক্ষার্থীদের জন্য মূল পরীক্ষার পেজ
# ==========================================
df = st.session_state.get('saved_df', None)

if df is not None and not df.empty:
    st.info(f"🎉 **পরীক্ষার জন্য মোট {len(df)} টি প্রশ্ন প্রস্তুত আছে!**")
    
    student_name = st.text_input("পরীক্ষার্থীর নাম লিখুন:", placeholder="আপনার নাম")
    
    if student_name:
        st.success(f"স্বাগতম, **{student_name}**! পরীক্ষা শুরু করুন।")
        st.divider()
        
        user_answers = {}
        
        for i, row in df.iterrows():
            st.markdown(f"##### **{i+1}. {str(row['Question'])}**")
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            user_answers[i] = st.radio(
                f"উত্তর বেছে নিন:", 
                options, 
                index=None, 
                key=f"q_{i}"
            )
            st.write("---")
            
        if st.button("পরীক্ষা জমা দিন", type="primary"):
            score = 0
            total = len(df)
            
            st.subheader("📊 আপনার পরীক্ষার ফলাফল")
            
            for i, row in df.iterrows():
                ans = user_answers[i]
                correct = str(row['Correct_Answer'])
                
                if ans and ans.strip() == correct.strip():
                    score += 1
                    st.success(f"✅ **প্রশ্ন {i+1}: সঠিক উত্তর!**")
                else:
                    st.error(f"❌ **প্রশ্ন {i+1}: ভুল উত্তর!** (আপনার উত্তর: {ans if ans else 'দেওয়া হয়নি'})")
                    st.info(f"👉 **সঠিক উত্তর:** প্রিন্ট হবে: {correct}\n\n💡 **ব্যাখ্যা:** {row['Explanation']}")
            
            st.divider()
            st.metric(label=f"{student_name}-এর মোট ফলাফল", value=f"{score} / {total}")
            st.balloons()
else:
    st.warning("⚠️ বর্তমানে কোনো প্রশ্ন সেট করা নেই। শিক্ষক মহোদয় পাসওয়ার্ড দিয়ে ফাইল আপলোড বা সাবজেক্ট সিলেক্ট করলে এখানে পরীক্ষা দেখা যাবে।")
