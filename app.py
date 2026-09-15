import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from groq import Groq

st.set_page_config(page_title="AI PDF Assistant")
st.title("📄 AI PDF Research Assistant")

# Fetch API key from Streamlit Secrets
groq_api_key = st.secrets.get("GROQ_API_KEY")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    if not groq_api_key:
        st.error("API Key Secrets mein nahi mili! Streamlit Secrets check karein.")
    else:
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
            client = Groq(api_key=groq_api_key)
            prompt = f"Context from document:\n{pdf_text[:6000]}\n\nQuestion: {user_question}"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.write("### Answer:")
            st.write(completion.choices[0].message.content)

        os.remove(tmp_path)
            
    
    
