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
    .stButton>button { width: 100%; border-radius: 8px; height: 2.8rem; font-weight: 600; background-color: #2563EB; color: white; }
    .stButton>button:hover { background-color: #1D4ED8; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📑 AI Productivity Workspace Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your All-in-One Intelligent Document Assistant & Productivity Suite</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar - License Verification, Lemon Squeezy & API Key Setup
# ---------------------------------------------------------
st.sidebar.title("⚙️ Workspace Settings")

# 1. Groq API Key Setup (Sidebar + Secrets Fallback)
api_key = st.sidebar.text_input("Enter Groq API Key (Optional):", type="password", help="Leave blank if system default key is configured in Secrets.")

if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

# 2. Lemon Squeezy License Key Verification System
st.sidebar.markdown("---")
st.sidebar.subheader("👑 Pro Subscription & License")

license_key = st.sidebar.text_input("Enter Lemon Squeezy License Key:", type="password", help="Enter the license key received after purchase.")

# Lemon Squeezy Product Checkout Button
st.sidebar.markdown(
    """
    <a href="https://lemonsqueezy.com" target="_blank">
        <button style="width:100%; background-color:#10B981; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:5px;">
            🛒 Buy Pro License ($9.99/mo)
        </button>
    </a>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by Llama 3.1 & Groq AI Engine")

# Verification Check
if not api_key:
    st.info("👈 Please enter your **Groq API Key** in the sidebar or configure `GROQ_API_KEY` in Streamlit Secrets to start.")
    st.stop()

# Initialize Client
client = Groq(api_key=api_key)

# Helper function to call Groq AI
def ask_groq(prompt_text, context_text):
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert AI document assistant. Answer accurately based on context. Natively support full Urdu and English responses based on the user question."
                },
                {"role": "user", "content": f"Context:\n{context_text[:12000]}\n\nTask/Question:\n{prompt_text}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error processing document: {str(e)}"

# ---------------------------------------------------------
# Main App Logic (7 Tools Suite)
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
        st.error("Could not extract readable text from this PDF. Please make sure it's not a scanned image-only PDF.")
        st.stop()

    st.success(f"✅ Document Successfully Loaded! ({len(pdf_reader.pages)} Pages Processed)")

    st.markdown("---")
    st.subheader("🛠️ Choose an AI Tool")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 Chat Q&A", 
        "📝 Summarizer", 
        "📌 Key Highlights", 
        "🌐 Translator", 
        "❓ Quiz Generator", 
        "📊 Executive Brief", 
        "🔍 Term Extractor"
    ])

    # Tool 1: Chat Q&A
    with tab1:
        st.markdown("### 💬 Ask Anything About Your Document")
        user_q = st.text_input("Type your question here (Supports Urdu & English):", placeholder="e.g. Is document ka main summary kya hai?")
        if st.button("Get Answer", key="btn1") and user_q:
            with st.spinner("Analyzing document..."):
                res = ask_groq(f"Answer accurately in the same language as asked: {user_q}", text)
                st.write(res)

    # Tool 2: Summarizer
    with tab2:
        st.markdown("### 📝 Instant Summary Generator")
        s_type = st.radio("Select Summary Detail Level:", ["Brief Overview", "Comprehensive Deep-Dive"])
        if st.button("Generate Summary", key="btn2"):
            with st.spinner("Summarizing..."):
                res = ask_groq(f"Provide a {s_type} of this document.", text)
                st.write(res)

    # Tool 3: Highlights
    with tab3:
        st.markdown("### 📌 Actionable Bullet Points")
        if st.button("Extract Key Highlights", key="btn3"):
            with st.spinner("Extracting insights..."):
                res = ask_groq("Extract top 5-10 key actionable takeaways as structured bullet points.", text)
                st.write(res)

    # Tool 4: Translator
    with tab4:
        st.markdown("### 🌐 Translate Document Insights")
        target_lang = st.selectbox("Select Target Language:", ["Urdu", "Spanish", "French", "German", "Arabic", "Hindi"])
        if st.button("Translate Summary", key="btn4"):
            with st.spinner(f"Translating into {target_lang}..."):
                res = ask_groq(f"Summarize the key document context and translate directly into {target_lang}.", text)
                st.write(res)

    # Tool 5: Quiz Generator
    with tab5:
        st.markdown("### ❓ AI Quiz & Test Generator")
        if st.button("Generate Multiple Choice Quiz", key="btn5"):
            with st.spinner("Generating Quiz..."):
                res = ask_groq("Create 5 multiple choice questions (MCQs) with 4 options each, and provide correct answers at the bottom.", text)
                st.write(res)

    # Tool 6: Executive Brief
    with tab6:
        st.markdown("### 📊 Executive Business Briefing")
        if st.button("Generate Executive Brief", key="btn6"):
            with st.spinner("Compiling executive brief..."):
                res = ask_groq("Write a formal Executive Brief containing: 1. Primary Objective/Problem, 2. Key Findings, 3. Strategic Recommendations.", text)
                st.write(res)

    # Tool 7: Term Extractor
    with tab7:
        st.markdown("### 🔍 Technical Keywords & Concepts")
        if st.button("Extract Key Terms", key="btn7"):
            with st.spinner("Extracting terminology..."):
                res = ask_groq("Extract top 10 important technical keywords/concepts from text along with 1-sentence concise definitions for each.", text)
                st.write(res)

else:
    st.info("👆 Please upload a PDF document above to activate the 7 AI Productivity Tools.")
    
