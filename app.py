import os
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from langchain_core.documents import Document
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Helper function to retrieve environment variables with error handling
def get_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

# Setting Google service account credentials using environment variables
credentials_dict = {
    "type": "service_account",
    "project_id": get_env_var("GOOGLE_PROJECT_ID"),
    "private_key_id": get_env_var("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": get_env_var("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": get_env_var("GOOGLE_CLIENT_EMAIL"),
    "client_id": get_env_var("GOOGLE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": get_env_var("GOOGLE_CLIENT_CERT_URL"),
}

# Google Drive API setup
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
drive_service = build('drive', 'v3', credentials=credentials)

# Function to download CSV files from Google Drive folder and combine as text
def get_combined_csv_text_from_drive(folder_id):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    
    if not files:
        print("No files found in the specified Google Drive folder.")
        return ""
    
    all_text = []
    for file in files:
        print(f"Processing file: {file['name']} (ID: {file['id']}, MIME type: {file['mimeType']})")
        fh = io.BytesIO()

        try:
            request = drive_service.files().get_media(fileId=file['id'])
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        except Exception as e:
            print(f"Direct download failed for {file['name']}, attempting export as CSV. Error: {e}")
            request = drive_service.files().export_media(fileId=file['id'], mimeType='text/csv')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        fh.seek(0)
        content = fh.read().decode("utf-8")
        print(f"Downloaded content for {file['name']} (first 500 characters):\n{content[:500]}")

        try:
            df = pd.read_csv(io.StringIO(content))
            print(f"Successfully read {len(df)} rows from {file['name']}")
            text = df.to_string(index=False)
            all_text.append(text)
        except pd.errors.EmptyDataError:
            print(f"Warning: {file['name']} is empty or not a valid CSV.")
        except Exception as e:
            print(f"Error reading {file['name']}: {e}")

    combined_text = "\n".join(all_text)
    print("Combined text length after processing all files:", len(combined_text))
    return combined_text

# Split text into manageable chunks and create Document objects
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    chunks = text_splitter.split_text(text)
    return [Document(page_content=chunk, metadata={"id": str(i)}) for i, chunk in enumerate(chunks)]

# Set up the FAISS vector store with embeddings
def setup_vectorstore(docs):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    embedding_values = embeddings.embed_documents([document.page_content for document in docs])

    if len(embedding_values) == 0 or len(embedding_values[0]) == 0:
        raise ValueError("Embedding generation failed. Check the embeddings model and API configuration.")
    
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore.save_local("faiss_index")
    return vectorstore

# Set up the RAG chain with Google Gemini API
def setup_rag_chain(vectorstore, model_name="gemini-1.5-flash"):
    template = """Answer the question in a single sentence. If the answer is not in the context, just say, "answer is not available in the context".
    Context: {context}
    Question: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0.01)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    chain = (
        RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
        | prompt
        | model
        | StrOutputParser()
    )
    return chain

# Handle the query and return an answer
def answer_question(chain, query):
    answer = chain.invoke(query)
    return answer

# Streamlit interface for chatting with CSV data
def main():
    st.title("Chat - BOT")
    folder_id = '1Oi7MC9FrSHjhw0r5x_H8tuDMR5gyb_UX'
    
    if "text_chunks" not in st.session_state:
        with st.spinner("Processing CSV files from Google Drive..."):
            raw_text = get_combined_csv_text_from_drive(folder_id)
            docs = get_text_chunks(raw_text)
            if len(docs) == 0:
                st.error("No text chunks were created from the CSV files.")
                return
            vectorstore = setup_vectorstore(docs)
            chain = setup_rag_chain(vectorstore)
            st.session_state['chain'] = chain
            st.session_state["text_chunks"] = docs

    if 'chain' in st.session_state:
        query = st.text_input("Ask a question about the CSV data:")
        
        if query:
            answer = answer_question(st.session_state['chain'], query)
            st.write(f"Answer: {answer}")

if __name__ == "__main__":
    main()
