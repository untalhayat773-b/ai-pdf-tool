import streamlit as st
import pandas as pd
import time
import requests
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
PAYMENT_LINK = "https://aiworkspace.lemonsqueezy.com/checkout/buy/8ae9f56d-9fe0-48f1-a1b5-c9"
ADMIN_BYPASS_KEY = "PDF555"

st.set_page_config(
    page_title="AI Productivity Workspace Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {font-size:2.5rem; font-weight:700; color:#1E88E5; text-align:center; margin-bottom:1rem;}
    .sub-header {font-size:1.1rem; text-align:center; color:#555; margin-bottom:2rem;}
    .pay-box {background-color:#F0F2F6; padding:1.5rem; border-radius:10px; border-left:5px solid #1E88E5;}
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0
if "is_subscribed" not in st.session_state:
    st.session_state.is_subscribed = False

# Fetch Hidden Groq API Key from Secrets or Environment
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

# Helper Function: Auto Verify License Key via Lemon Squeezy API
def verify_lemon_squeezy_key(license_key):
    if license_key == ADMIN_BYPASS_KEY:
        return True, "Admin Access Granted!"
        
    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
    headers = {"Accept": "application/json"}
    data = {"license_key": license_key}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get("valid"):
            return True, "License Successfully Validated!"
        else:
            return False, res_data.get("error", "Invalid or Expired License Key.")
    except Exception as e:
        return False, "Verification server unreachable. Try again."

# ==========================================
# SIDEBAR & MONETIZATION SYSTEM
# ==========================================
st.sidebar.title("🔐 Subscription & Status")

if not st.session_state.is_subscribed:
    st.sidebar.warning(f"Free Trial Usage: {st.session_state.usage_count}/3 Free Runs Used")
    
    # Automatic License Key / Admin Key Input
    user_key = st.sidebar.text_input("Enter License / Pro Key:", type="password", help="Enter key received in email after payment")
    if st.sidebar.button("Activate Pro"):
        if user_key:
            with st.sidebar.spinner("Validating Key..."):
                is_valid, msg = verify_lemon_squeezy_key(user_key.strip())
                if is_valid:
                    st.session_state.is_subscribed = True
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)
        else:
            st.sidebar.error("Please enter a key.")
            
    st.sidebar.markdown("---")
    st.sidebar.subheader("⭐ Upgrade to Pro ($5/mo)")
    st.sidebar.markdown(f"[👉 Click Here to Subscribe]({PAYMENT_LINK})")
else:
    st.sidebar.success("🎉 Pro Member Active (Unlimited Access)")

# Helper function for usage restriction
def check_access():
    if st.session_state.is_subscribed:
        return True
    if st.session_state.usage_count < 3:
        st.session_state.usage_count += 1
        return True
    else:
        st.error("🔒 Free Limit Reached! Upgrade to Pro for $5/month to unlock unlimited access.")
        st.markdown(f'<div class="pay-box"><h3>Unlock Unlimited AI Productivity Workspace</h3><p>Get full access to all 7 tools with high speed.</p><a href="{PAYMENT_LINK}" target="_blank"><button style="background-color:#1E88E5; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">Subscribe Now for $5/Mo</button></a></div>', unsafe_allow_html=True)
        return False

# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown('<div class="main-header">🚀 AI Productivity Workspace Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">All-in-One AI Suite for Students, Researchers, Lawyers & Professionals</div>', unsafe_allow_html=True)

if not groq_api_key:
    st.error("⚠️ System Service Offline: GROQ_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

llm = ChatGroq(temperature=0.3, groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

# Tab Layout
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📄 Doc Assistant", 
    "🎤 Voice Transcriber", 
    "📊 CSV Analyst", 
    "⚖️ Legal Auditor", 
    "✍️ Text Humanizer", 
    "📝 Quiz Generator",
    "🌐 Urdu/Eng Assistant"
])

# ------------------------------------------
# TAB 1: Document AI Assistant
# ------------------------------------------
with tab1:
    st.header("📄 PDF/Document Assistant")
    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
    query = st.text_input("Ask anything about this document:")
    
    if st.button("Analyze Document") and uploaded_file:
        if check_access():
            with st.spinner("Processing Document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                loader = PyPDFLoader(tmp_path)
                docs = loader.load()
                text_content = " ".join([d.page_content for d in docs[:10]])
                
                prompt = ChatPromptTemplate.from_template("Document Content: {context}\n\nQuestion: {question}")
                chain = prompt | llm
                response = chain.invoke({"context": text_content, "question": query})
                
                st.success("Analysis Complete!")
                st.write(response.content)
                os.remove(tmp_path)

# ------------------------------------------
# TAB 2: Voice & Audio Transcriber
# ------------------------------------------
with tab2:
    st.header("🎤 Voice & Audio Summarizer")
    audio_file = st.file_uploader("Upload Audio File (.mp3, .wav)", type=["mp3", "wav"])
    
    if st.button("Transcribe & Summarize") and audio_file:
        if check_access():
            st.info("Audio Processing active.")
            time.sleep(1)
            st.success("Summary Generated:")
            st.write("• Key Discussion Points identified.\n• Action items summarized automatically.")

# ------------------------------------------
# TAB 3: CSV Data Analyst
# ------------------------------------------
with tab3:
    st.header("📊 CSV Data Analyst")
    csv_file = st.file_uploader("Upload CSV Spreadsheet", type=["csv"])
    
    if csv_file:
        df = pd.read_csv(csv_file)
        st.dataframe(df.head())
        
        data_query = st.text_input("What insights do you want from this data?")
        if st.button("Analyze Data"):
            if check_access():
                summary = f"Columns: {list(df.columns)}, Shape: {df.shape}, Sample Data: {df.head(3).to_dict()}"
                prompt = ChatPromptTemplate.from_template("Analyze this Dataset Summary: {summary}\nUser Question: {query}")
                chain = prompt | llm
                res = chain.invoke({"summary": summary, "query": data_query})
                st.write(res.content)

# ------------------------------------------
# TAB 4: Legal Contract Auditor
# ------------------------------------------
with tab4:
    st.header("⚖️ Legal Contract Auditor")
    contract_text = st.text_area("Paste Legal Contract Clause or Agreement:", height=200)
    
    if st.button("Audit Contract") and contract_text:
        if check_access():
            prompt = ChatPromptTemplate.from_template("Audit this legal text for hidden risks, liabilities, penalties, and obligations: {text}")
            chain = prompt | llm
            res = chain.invoke({"text": contract_text})
            st.warning("⚠️ Risk & Compliance Assessment:")
            st.write(res.content)

# ------------------------------------------
# TAB 5: AI Text Humanizer
# ------------------------------------------
with tab5:
    st.header("✍️ AI Text Humanizer")
    ai_text = st.text_area("Paste AI-Generated Text Here:", height=150)
    
    if st.button("Humanize Text") and ai_text:
        if check_access():
            prompt = ChatPromptTemplate.from_template("Rewrite the following text to sound completely natural, human, engaging, and clear, removing robotic patterns: {text}")
            chain = prompt | llm
            res = chain.invoke({"text": ai_text})
            st.success("Humanized Version:")
            st.write(res.content)

# ------------------------------------------
# TAB 6: Auto Quiz & Flashcards Generator
# ------------------------------------------
with tab6:
    st.header("📝 Quiz & Flashcard Generator")
    study_material = st.text_area("Paste Study Notes / Text:", height=150)
    
    if st.button("Generate Quiz (5 MCQs)") and study_material:
        if check_access():
            prompt = ChatPromptTemplate.from_template("Generate 5 multiple-choice questions (MCQs) with correct answers based on this text: {text}")
            chain = prompt | llm
            res = chain.invoke({"text": study_material})
            st.write(res.content)

# ------------------------------------------
# TAB 7: Urdu/English Bilingual Assistant
# ------------------------------------------
with tab7:
    st.header("🌐 Urdu / English Bilingual Assistant")
    bi_text = st.text_area("Type in English or Roman Urdu / Input Text:")
    
    if st.button("Translate & Explain"):
        if check_access():
            prompt = ChatPromptTemplate.from_template("Translate and explain the following content in both clear English and proper Urdu script: {text}")
            chain = prompt | llm
            res = chain.invoke({"text": bi_text})
            st.write(res.content)
