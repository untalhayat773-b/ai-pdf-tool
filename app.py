import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from groq import Groq

st.set_page_config(page_title="AI PDF Assistant", layout="wide")
st.title("📄 AI PDF Research Assistant")

api_key = st.secrets.get("GROQ_API_KEY")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file:
    if not api_key:
        st.error("API Key Secrets mein nahi mili! Streamlit Secrets check karein.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        # Large document support: Memory optimization
        full_text = "\n".join([doc.page_content for doc in docs])
        
        st.success(f"PDF Uploaded Successfully! Total Pages: {len(docs)}")

        user_question = st.text_input("Sawaal poochen / Ask anything about the PDF (Urdu or English):")

        if user_question:
            try:
                client = Groq(api_key=api_key)

                models_list = client.models.list().data
                active_models = [m.id for m in models_list if getattr(m, 'active', True)]
                target_model = active_models[0] if active_models else "llama-3.1-8b-instant"

                # Prompt update for bilingual support & heavy context management
                prompt = (
                    f"You are a helpful assistant. Answer the user question based on the document context below.\n"
                    f"Respond in the same language as the user's question (Urdu or English).\n\n"
                    f"Context:\n{full_text[:12000]}\n\n"
                    f"Question: {user_question}"
                )

                response_container = st.empty()
                
                # Streaming output to prevent UI lag
                stream = client.chat.completions.create(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )
                
                collected_text = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        collected_text += chunk.choices[0].delta.content
                        response_container.markdown(f"### Answer:\n{collected_text}")

            except Exception as e:
                st.error(f"Error detail: {e}")

        os.remove(tmp_path)



        
