import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="অনলাইন পরীক্ষা প্ল্যাটফর্ম", page_icon="📝", layout="centered")

st.title("📝 অনলাইন মডেল টেস্ট")

# ==========================================
# 🔐 অ্যাডমিন সিকিউরিটি পাসওয়ার্ড সেটআপ
# ==========================================
ADMIN_PASSWORD = "1234"  # আপনি চাইলে এই পাসওয়ার্ডটি পরে পরিবর্তন করে নিতে পারেন

# সাইডবার শুধু অ্যাডমিনদের জন্য
st.sidebar.header("⚙️ শিক্ষক / অ্যাডমিন প্যানেল")
entered_password = st.sidebar.text_input("অ্যাডমিন পাসওয়ার্ড দিন:", type="password")

df = None

# পাসওয়ার্ড মিললেই কেবল প্রশ্ন সেটআপ বা আপলোড করার অপশন দেখা যাবে
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
                    
                    correct_ans = ""
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
                df = pd.DataFrame(parsed_questions)
                # সেশনে প্রশ্নগুলো সেভ করে রাখা যাতে পাসওয়ার্ড ছদ্মবেশে হারিয়ে না যায়
                st.session_state['saved_df'] = df

    else:
        uploaded_file = st.sidebar.file_uploader("questions.xlsx বা csv ফাইল আপলোড করুন:", type=["xlsx", "csv"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_excel(uploaded_file)
                
            st.sidebar.subheader("🎯 প্রশ্ন ফিল্টার অপশন")
            filter_type = st.sidebar.radio("কীভাবে প্রশ্ন সিলেক্ট করতে চান?", [
                "সব প্রশ্ন দিয়ে পরীক্ষা",
                "র‍্যান্ডম (Random) নির্দিষ্ট সংখ্যক প্রশ্ন",
                "ম্যানুয়ালি বেছে বেছে প্রশ্ন সিলেক্ট"
            ])
            
            if filter_type == "সব প্রশ্ন দিয়ে পরীক্ষা":
                df = raw_df
            elif filter_type == "র‍্যান্ডম (Random) নির্দিষ্ট সংখ্যক প্রশ্ন":
                max_q = len(raw_df)
                num_q = st.sidebar.number_input(f"কতটি প্রশ্ন রাখতে চান? (সর্বোচ্চ {max_q})", min_value=1, max_value=max_q, value=min(10, max_q))
                df = raw_df.sample(n=num_q).reset_index(drop=True)
            elif filter_type == "ম্যানুয়ালি বেছে বেছে প্রশ্ন সিলেক্ট":
                selected_indices = st.sidebar.multiselect(
                    "তালিকা থেকে প্রশ্নগুলো নির্বাচন করুন:",
                    options=list(raw_df.index),
                    format_func=lambda x: f"প্রশ্ন {x+1}: {raw_df.loc[x, 'Question'][:30]}..."
                )
                if selected_indices:
                    df = raw_df.loc[selected_indices].reset_index(drop=True)
            
            if df is not None:
                st.session_state['saved_df'] = df

    # অ্যাডমিন যদি আগে প্রশ্ন সেট করে থাকেন, সেটি মেমোরিতে রাখা
    if 'saved_df' in st.session_state and df is None:
        df = st.session_state['saved_df']

elif entered_password != "":
    st.sidebar.error("❌ ভুল পাসওয়ার্ড! সঠিক পাসওয়ার্ড দিন।")
    # সাধারণ পরীক্ষার্থীরা যদি আগে প্রশ্ন সেট করা থাকে সেটি দেখতে পাবে, নতুন করে এডিট করতে পারবে না
    if 'saved_df' in st.session_state:
        df = st.session_state['saved_df']
else:
    # কেউ যদি পাসওয়ার্ড না দেয়, তবে আগের সেভ করা প্রশ্নগুলো লোড করে পরীক্ষা নেওয়ার জন্য প্রস্তুত রাখা
    if 'saved_df' in st.session_state:
        df = st.session_state['saved_df']

# ==========================================
# 📝 পরীক্ষার্থীদের জন্য মূল পরীক্ষার পেজ
# ==========================================
if df is not None and not df.empty:
    st.info(f"🎉 **পরীক্ষার জন্য মোট {len(df)} টি প্রশ্ন প্রস্তুত আছে!**")
    
    student_name = st.text_input("পরীক্ষার্থীর নাম লিখুন:", placeholder="আপনার নাম")
    
    if student_name:
        st.success(f"স্বাগতম, **{student_name}**! পরীক্ষা শুরু করুন।")
        st.divider()
        
        user_answers = {}
        
        for i, row in df.iterrows():
            st.markdown(f"##### **{i+1}. {row['Question']}**")
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
                    st.info(f"👉 **সঠিক উত্তর:** {correct}\n\n💡 **ব্যাখ্যা:** {row['Explanation']}")
            
            st.divider()
            st.metric(label=f"{student_name}-এর মোট ফলাফল", value=f"{score} / {total}")
            st.balloons()
else:
    st.warning("⚠️ বর্তমানে কোনো প্রশ্ন সেট করা নেই। শিক্ষক মহোদয় পাসওয়ার্ড দিয়ে প্রশ্ন যুক্ত করলে পরীক্ষা শুরু হবে।")
