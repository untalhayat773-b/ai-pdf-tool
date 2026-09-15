import streamlit as st
from PyPDF2 import PdfReader
from groq import Groq

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Productivity Workspace Pro",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #64748B; text-align: center; margin-bottom: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 2.8rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📑 AI Productivity Workspace Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your All-in-One Intelligent Document Assistant & Productivity Suite</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------
st.sidebar.title("⚙️ Workspace Settings")
api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

st.sidebar.markdown("---")
st.sidebar.subheader("👑 Upgrade to Pro Plan")
st.sidebar.info("Unlock unlimited processing and priority AI speed.")
st.sidebar.markdown("[👉 Buy License Key via Lemon Squeezy](https://lemonsqueezy.com)", unsafe_allow_html=True)

if not api_key:
    st.info("👈 Please enter your **Groq API Key** in the sidebar to activate the AI Workspace.")
    st.stop()

# Initialize Direct Groq Client
client = Groq(api_key=api_key)

def ask_groq(prompt_text, context_text):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert AI assistant. Answer accurately based on context. Support Urdu and English natively."},
                {"role": "user", "content": f"Context:\n{context_text[:12000]}\n\nTask/Question:\n{prompt_text}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------------------------------------
# Main Logic
# ---------------------------------------------------------
uploaded_file = st.file_uploader("📂 Upload your PDF Document to get started", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

    if not text.strip():
        st.error("Could not extract text. Make sure it is not a scanned image PDF.")
        st.stop()

    st.success(f"✅ Document Loaded Successfully! ({len(pdf_reader.pages)} Pages Processed)")

    st.markdown("---")
    st.subheader("🛠️ Choose an AI Tool")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 Chat Q&A", "📝 Summarizer", "📌 Key Highlights", 
        "🌐 Translator", "❓ Quiz Generator", "📊 Executive Brief", "🔍 Keyword Extractor"
    ])

    # 1. Chat
    with tab1:
        st.markdown("### 💬 Ask Anything About Your Document")
        user_q = st.text_input("Type your question here (Supports Urdu & English):")
        if st.button("Get Answer", key="btn1") and user_q:
            with st.spinner("Analyzing..."):
                res = ask_groq(f"Answer this in the same language as asked: {user_q}", text)
                st.write(res)

    # 2. Summarizer
    with tab2:
        st.markdown("### 📝 Summary Generator")
        s_type = st.radio("Select Summary Type:", ["Short Brief", "Detailed Summary"])
        if st.button("Generate Summary", key="btn2"):
            with st.spinner("Summarizing..."):
                res = ask_groq(f"Provide a {s_type} of this document.", text)
                st.write(res)

    # 3. Highlights
    with tab3:
        st.markdown("### 📌 Important Takeaways")
        if st.button("Extract Highlights", key="btn3"):
            with st.spinner("Extracting..."):
                res = ask_groq("Extract top 5-10 bullet key takeaways.", text)
                st.write(res)

    # 4. Translator
    with tab4:
        st.markdown("### 🌐 Translate Document Insights")
        target_lang = st.selectbox("Target Language:", ["Urdu", "Spanish", "French", "German", "Arabic", "Hindi"])
        if st.button("Translate Summary", key="btn4"):
            with st.spinner("Translating..."):
                res = ask_groq(f"Summarize and translate directly into {target_lang}.", text)
                st.write(res)

    # 5. Quiz
    with tab5:
        st.markdown("### ❓ Multiple Choice Quiz")
        if st.button("Generate Quiz", key="btn5"):
            with st.spinner("Creating Quiz..."):
                res = ask_groq("Create 5 MCQs with 4 options and answers at the end.", text)
                st.write(res)

    # 6. Brief
    with tab6:
        st.markdown("### 📊 Executive Business Brief")
        if st.button("Generate Executive Brief", key="btn6"):
            with st.spinner("Generating..."):
                res = ask_groq("Write an Executive Brief: 1. Main Problem, 2. Key Findings, 3. Conclusion.", text)
                st.write(res)

    # 7. Keywords
    with tab7:
        st.markdown("### 🔍 Terminology Extractor")
        if st.button("Extract Keywords", key="btn7"):
            with st.spinner("Extracting..."):
                res = ask_groq("Extract top 10 technical keywords with 1-line definitions.", text)
                st.write(res)
else:
    st.info("👆 Please upload a PDF file above to unlock the tools.")
    
