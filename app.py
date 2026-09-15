import streamlit as st
import tempfile
import os
import datetime
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from groq import Groq

# Page Config
st.set_page_config(page_title="AI Productivity Workspace Pro", layout="wide", initial_sidebar_state="expanded")

# --- SUBSCRIPTION & TRIAL SYSTEM ---
TRIAL_DAYS = 30
PAYMENT_LINK = "https://www.lemonsqueezy.com" 

if "install_date" not in st.session_state:
    st.session_state.install_date = datetime.date.today()

if "is_subscribed" not in st.session_state:
    st.session_state.is_subscribed = False

days_used = (datetime.date.today() - st.session_state.install_date).days
days_left = max(0, TRIAL_DAYS - days_used)

st.title("🚀 Ultimate AI Productivity Workspace Pro")
st.caption("All-in-One Assistant for Docs, Voice Notes, Legal Reviews, Data Analysis & Quizzes")

# --- SIDEBAR SUBSCRIPTION ---
with st.sidebar:
    st.header("👑 VIP Membership")
    
    if st.session_state.is_subscribed:
        st.success("STATUS: Pro Member Active 💎")
    elif days_left > 0:
        st.info(f"STATUS: Free Trial ({days_left} Days Left)")
    else:
        st.error("STATUS: Trial Expired ❌")

    st.divider()

    if not st.session_state.is_subscribed:
        st.subheader("🔥 Unlock All 7 Pro AI Tools")
        st.markdown(
            "- 📑 1000+ Page Document Assistant\n"
            "- 🎤 Voice & Audio Transcriber (Whisper AI)\n"
            "- 📊 CSV & Excel Data Analyst\n"
            "- ⚖️ Legal Contract & Risk Auditor\n"
            "- ✍️ AI Text Humanizer & Paraphraser\n"
            "- 📝 Auto Quiz & Flashcard Generator\n"
            "- 🇵🇰 Urdu & English Dual Engine"
        )
        st.markdown(f"[👉 **Subscribe Now ($5/Month)**]({PAYMENT_LINK})")
        
        st.divider()
        st.write("🔑 **Activation Key:**")
        activation_code = st.text_input("Enter Activation Key:", type="password", key="pass_input")
        if st.button("Activate Pro Access"):
            if activation_code == "PDF555": 
                st.session_state.is_subscribed = True
                st.success("Pro Workspace Unlocked!")
                st.rerun()
            else:
                st.error("Invalid Code!")

# --- CORE APP LOGIC ---
api_key = st.secrets.get("GROQ_API_KEY")

if days_left <= 0 and not st.session_state.is_subscribed:
    st.error("🚨 Free Trial Expired! Subscribe to $5/Month to access the workspace.")
else:
    if not api_key:
        st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    else:
        client = Groq(api_key=api_key)
        
        models_list = client.models.list().data
        active_models = [m.id for m in models_list if getattr(m, 'active', True)]
        target_model = active_models[0] if active_models else "llama-3.1-8b-instant"

        # Tabs Navigation
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📄 Document Assistant", 
            "🎤 Voice Summarizer", 
            "📊 Data & Excel Analyst",
            "⚖️ Legal & Contract Auditor",
            "✍️ AI Humanizer",
            "📝 Auto Quiz Generator"
        ])

        # TAB 1: DOC ASSISTANT
        with tab1:
            st.subheader("Smart Document Analysis (PDF / Word / TXT)")
            uploaded_file = st.file_uploader("Upload Document:", type=["pdf", "docx", "txt"])

            if uploaded_file:
                file_ext = uploaded_file.name.split(".")[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                try:
                    if file_ext == "pdf":
                        loader = PyPDFLoader(tmp_path)
                        docs = loader.load()
                        full_text = "\n".join([doc.page_content for doc in docs])
                    elif file_ext == "docx":
                        loader = Docx2txtLoader(tmp_path)
                        docs = loader.load()
                        full_text = docs[0].page_content
                    else:
                        loader = TextLoader(tmp_path)
                        docs = loader.load()
                        full_text = docs[0].page_content

                    st.success(f"✅ Document Loaded ({len(full_text.split())} words)")

                    col1, col2 = st.columns(2)
                    with col1:
                        gen_summary = st.button("⚡ Executive Summary (English)")
                    with col2:
                        gen_urdu = st.button("🇵🇰 Executive Summary (اردو خلاصہ)")

                    if gen_summary or gen_urdu:
                        lang = "Urdu" if gen_urdu else "English"
                        prompt = f"Provide a structured Executive Summary with Key Takeaways in {lang}:\n\n{full_text[:12000]}"
                        res = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": prompt}])
                        st.markdown(f"### Summary ({lang}):\n" + res.choices[0].message.content)

                    st.divider()
                    user_q = st.text_input("Ask anything about the document:")
                    if user_q:
                        prompt = f"Answer in the same language as question (Urdu or English) based on context.\nContext:\n{full_text[:12000]}\nQuestion: {user_q}"
                        resp_container = st.empty()
                        stream = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": prompt}], stream=True)
                        ans_text = ""
                        for chunk in stream:
                            if chunk.choices[0].delta.content:
                                ans_text += chunk.choices[0].delta.content
                                resp_container.markdown(f"### Answer:\n{ans_text}")

                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    if os.path.exists(tmp_path): os.remove(tmp_path)

        # TAB 2: VOICE SUMMARIZER
        with tab2:
            st.subheader("Voice Notes & Meeting Audio Transcriber")
            audio_file = st.file_uploader("Upload Audio (.mp3, .wav, .m4a):", type=["mp3", "wav", "m4a"])

            if audio_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_audio:
                    tmp_audio.write(audio_file.read())
                    audio_path = tmp_audio.name

                st.audio(audio_file)
                if st.button("🎙️ Process Audio"):
                    try:
                        with st.spinner("Transcribing..."):
                            with open(audio_path, "rb") as f:
                                transcription = client.audio.transcriptions.create(file=(audio_path, f.read()), model="whisper-large-v3-turbo", response_format="text")
                            st.success("Transcription Complete!")
                            st.text_area("Full Transcript:", transcription, height=150)

                            sum_res = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": f"Summarize key meeting takeaways:\n\n{transcription}"}])
                            st.markdown("### Audio Summary:\n" + sum_res.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Audio Error: {e}")
                    finally:
                        if os.path.exists(audio_path): os.remove(audio_path)

        # TAB 3: DATA & EXCEL ANALYST
        with tab3:
            st.subheader("CSV & Data Sheet Insights")
            csv_file = st.file_uploader("Upload CSV File:", type=["csv"])
            if csv_file:
                df = pd.read_csv(csv_file)
                st.dataframe(df.head(10))
                if st.button("📊 Analyze Data Trends"):
                    prompt = f"Analyze this dataset preview and provide key statistical insights, trends, and summary:\n\n{df.head(20).to_string()}"
                    res = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": prompt}])
                    st.markdown("### Data Insights:\n" + res.choices[0].message.content)

        # TAB 4: LEGAL & CONTRACT AUDITOR
        with tab4:
            st.subheader("Contract & Legal Document Risk Auditor")
            contract_text = st.text_area("Paste Legal Contract / Agreement Text:", height=200)
            if st.button("⚖️ Audit Contract Risks") and contract_text:
                prompt = f"Audit this legal agreement. List: 1. High Risks/Penalties 2. Key Obligations 3. Missing Clauses\n\nText:\n{contract_text}"
                res = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": prompt}])
                st.markdown("### Legal Audit Report:\n" + res.choices[0].message.content)

        # TAB 5: AI HUMANIZER
        with tab5:
            st.subheader("AI Content Humanizer & Paraphraser")
            raw_text = st.text_area("Paste AI Generated / Rough Text:", height=150)
            if st.button("✍️ Make Human-Like & Natural") and raw_text:
                prompt = f"Rewrite this text in a natural, highly engaging human tone while maintaining original facts:\n\n{raw_text}"
                res = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": prompt}])
                st.markdown("### Humanized Output:\n" + res.choices[0].message.content)

        # TAB 6: AUTO QUIZ GENERATOR
        with tab6:
            st.subheader("AI Quiz & Flashcard Generator")
            study_text = st.text_area("Paste Study Material / Notes:", height=150)
            num_q = st.slider("Questions:", 3, 10, 5)
            if st.button("🧠 Generate Test") and study_text:
                prompt = f"Create {num_q} MCQs with answer keys and 3 Flashcards from this text:\n\n{study_text}"
                res = client.chat.completions.create(model=target_model, messages=[{"role": "user", "content": prompt}])
                st.markdown("### Quiz & Study Prep:\n" + res.choices[0].message.content)
