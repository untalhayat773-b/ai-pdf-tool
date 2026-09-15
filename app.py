import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq

st.set_page_config(page_title="AI PDF Assistant")
st.title("📄 AI PDF Research Assistant")

# Fetch API Key from Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    if not api_key:
        st.error("API Key Secrets mein nahi mili. Kripya Streamlit Secrets check karein.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        # Load PDF Text
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        pdf_text = "\n".join([doc.page_content for doc in docs])

        st.success("PDF Uploaded Successfully!")

        user_question = st.text_input("Ask anything about the PDF:")

        if user_question:
            try:
                # Active production model on Groq
                llm = ChatGroq(
                    model="llama-3.1-8b-instant",
                    groq_api_key=api_key
                )
                prompt = f"Context from document:\n{pdf_text[:6000]}\n\nQuestion: {user_question}"
                
                response = llm.invoke(prompt)
                st.write("### Answer:")
                st.write(response.content)
            except Exception as e:
                st.error(f"Error detail: {e}")

        os.remove(tmp_path)
        
        
        
            
    
    
