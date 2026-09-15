import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
import tempfile
import os

st.set_page_config(page_title="AI PDF Assistant")
st.title("📄 AI PDF Research Assistant")

# Sidebar for API Key
api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file and api_key:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Load PDF text
    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    pdf_text = "\n".join([doc.page_content for doc in docs])

    st.success("PDF Uploaded Successfully!")

    user_question = st.text_input("Ask anything about the PDF:")

    if user_question:
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=api_key)
        prompt = f"Context from document:\n{pdf_text[:6000]}\n\nQuestion: {user_question}"
        
        response = llm.invoke(prompt)
        st.write("### Answer:")
        st.write(response.content)

    os.remove(tmp_path)
    
