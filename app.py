import streamlit as st
import os
from PyPDF2 import PdfReader
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Productivity Workspace Pro",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Professional Look
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📑 AI Productivity Workspace Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your All-in-One Intelligent Document Assistant & Productivity Suite</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar - Configuration & Monetization
# ---------------------------------------------------------
st.sidebar.title("⚙️ Workspace Settings")

api_key = st.sidebar.text_input("Enter Groq API Key:", type="password", help="Enter your Groq API key to unlock fast processing.")

# Fallback to Streamlit Secrets
if not api_key:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]

st.sidebar.markdown("---")
st.sidebar.subheader("👑 Upgrade to Pro Plan")
st.sidebar.info("Unlock unlimited processing, priority AI speed, and advanced export features.")
st.sidebar.markdown("[👉 Buy License Key via Lemon Squeezy](https://lemonsqueezy.com)", unsafe_allow_html=True)

if not api_key:
    st.info("👈 Please enter your **Groq API Key** in the sidebar to activate the AI Workspace.")
    st.stop()

# ---------------------------------------------------------
# Core AI Setup (Using Active Llama-3.1 Model)
# ---------------------------------------------------------
try:
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.3
    )
except Exception as e:
    st.error(f"Error initializing Groq API: {str(e)}")
    st.stop()

# ---------------------------------------------------------
# Main Application Logic
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

    st.success(f"✅ Document Loaded Successfully! ({len(pdf_reader.pages)} Pages Processed)")

    # Prepare chunks for processing
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    chunks = text_splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks[:12]]

    st.markdown("---")
    st.subheader("🛠️ Choose an AI Tool")

    # 7 Integrated Tools in Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬 Chat Q&A", 
        "📝 Summarizer", 
        "📌 Key Highlights", 
        "🌐 Translator", 
        "❓ Quiz Generator", 
        "📊 Executive Brief", 
        "🔍 Keyword Extractor"
    ])

    # Tool 1: Interactive Chat Q&A
    with tab1:
        st.markdown("### 💬 Ask Anything About Your Document")
        user_question = st.text_input("Type your question here (Supports English, Urdu, etc.):", key="q1")
        if st.button("Get Answer", key="btn1") and user_question:
            with st.spinner("Searching document for answers..."):
                prompt_template = """
                Answer the question accurately based on the provided context. 
                If the answer is not in the context, say "Answer not found in the document".
                Respond in the exact same language as the user's question (e.g. answer in Urdu if asked in Urdu).

                Context:\n{context}\n
                Question:\n{question}\n
                Answer:
                """
                prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question=user_question)
                st.markdown("#### **AI Response:**")
                st.write(response)

    # Tool 2: Document Summarizer
    with tab2:
        st.markdown("### 📝 Generate Complete Summary")
        summary_type = st.radio("Select Summary Length:", ["Brief (Short)", "Detailed (Comprehensive)"])
        if st.button("Generate Summary", key="btn2"):
            with st.spinner("Summarizing document..."):
                prompt_template = f"Provide a {summary_type} summary of the document context below:\nContext:\n{{context}}\nSummary:"
                prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question="Summarize document")
                st.markdown("#### **Summary Result:**")
                st.write(response)

    # Tool 3: Key Bullet Highlights
    with tab3:
        st.markdown("### 📌 Important Takeaways & Highlights")
        if st.button("Extract Key Points", key="btn3"):
            with st.spinner("Extracting top takeaways..."):
                prompt_template = "Extract 5 to 10 key actionable insights and bullet points from the text:\nContext:\n{context}\nHighlights:"
                prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question="Extract key points")
                st.markdown("#### **Key Bullet Points:**")
                st.write(response)

    # Tool 4: Multilingual Translator
    with tab4:
        st.markdown("### 🌐 Translate Document Insights")
        target_lang = st.selectbox("Select Target Language:", ["Urdu", "Spanish", "French", "German", "Arabic", "Hindi"])
        if st.button("Translate Summary", key="btn4"):
            with st.spinner(f"Translating into {target_lang}..."):
                prompt_template = f"Summarize and translate the following context directly into {target_lang}:\nContext:\n{{context}}\nTranslation:"
                prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question=f"Translate into {target_lang}")
                st.markdown(f"#### **Translation ({target_lang}):**")
                st.write(response)

    # Tool 5: Quiz & Test Generator
    with tab5:
        st.markdown("### ❓ Multiple Choice Quiz Generator")
        num_q = st.slider("Number of Questions:", 3, 10, 5)
        if st.button("Generate Quiz", key="btn5"):
            with st.spinner("Creating quiz questions..."):
                prompt_template = f"Create {num_q} multiple choice questions (MCQs) with 4 options each and include correct answers at the end:\nContext:\n{{context}}\nQuiz:"
                prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question="Generate quiz")
                st.markdown("#### **Generated Quiz:**")
                st.write(response)

    # Tool 6: Executive Briefing
    with tab6:
        st.markdown("### 📊 Executive Business Brief")
        if st.button("Generate Executive Brief", key="btn6"):
            with st.spinner("Compiling executive brief..."):
                prompt_template = "Write a formal Executive Brief containing: 1. Core Problem/Topic, 2. Key Findings, 3. Strategic Conclusion.\nContext:\n{context}\nExecutive Brief:"
                prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question="Generate executive brief")
                st.markdown("#### **Executive Briefing:**")
                st.write(response)

    # Tool 7: Keyword & Term Extractor
    with tab7:
        st.markdown("### 🔍 Extract Key Technical Terms & Concepts")
        if st.button("Extract Keywords", key="btn7"):
            with st.spinner("Extracting important terminology..."):
                prompt_template = "Identify top 10 core technical terms/keywords from the text and provide a 1-sentence definition for each:\nContext:\n{context}\nKeywords:"
                prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
                chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
                response = chain.run(input_documents=docs, question="Extract keywords")
                st.markdown("#### **Key Terms & Definitions:**")
                st.write(response)

else:
    st.info("👆 Please upload a PDF file above to unlock the 7 AI Productivity Tools.")
        
