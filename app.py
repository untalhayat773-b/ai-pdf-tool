import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from groq import Groq

st.set_page_config(page_title="AI PDF Assistant")
st.title("📄 AI PDF Research Assistant")

# Fetch API Key from Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    if not api_key:
        st.error("API Key Secrets mein nahi mili! Streamlit Secrets check karein.")
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
                client = Groq(api_key=api_key)

                # Fetch available active models dynamically from Groq
                models_list = client.models.list().data
                active_models = [m.id for m in models_list if getattr(m, 'active', True)]
                
                # Pick the first available active model
                target_model = active_models[0] if active_models else "llama-3.1-8b-instant"

                prompt = f"Context from document:\n{pdf_text[:6000]}\n\nQuestion: {user_question}"
                
                completion = client.chat.completions.create(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.write("### Answer:")
                st.write(completion.choices[0].message.content)

            except Exception as e:
                st.error(f"Error detail: {e}")

        os.remove(tmp_path)


        
