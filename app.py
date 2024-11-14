import os
import io
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Set up Google Drive API using environment variables from .env
credentials_info = {
    "type": "service_account",
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
}

credentials = service_account.Credentials.from_service_account_info(credentials_info)
drive_service = build('drive', 'v3', credentials=credentials)

# Function to download and combine CSV files from Google Drive folder as text
def get_combined_csv_text_from_drive(folder_id):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    
    all_text = []
    for file in files:
        print(f"Processing file: {file['name']} (ID: {file['id']})")
        fh = io.BytesIO()
        
        try:
            request = drive_service.files().get_media(fileId=file['id'])
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        except Exception as e:
            print(f"Download failed for {file['name']}, attempting export as CSV. Error: {e}")
            request = drive_service.files().export_media(fileId=file['id'], mimeType='text/csv')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        fh.seek(0)
        content = fh.read().decode("utf-8")
        try:
            df = pd.read_csv(io.StringIO(content))
            all_text.append(df.to_string(index=False))
        except pd.errors.EmptyDataError:
            print(f"{file['name']} is empty or not a valid CSV.")
    
    return "\n".join(all_text)

# Split text into manageable chunks for embedding
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    return [Document(page_content=chunk, metadata={"id": str(i)}) for i, chunk in enumerate(text_splitter.split_text(text))]

# Set up FAISS vector store with embeddings
def setup_vectorstore(docs):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = FAISS.from_documents(docs, embedding=embeddings)
    vectorstore.save_local("faiss_index")
    return vectorstore

# Configure RAG chain with Google Gemini API
def setup_rag_chain(vectorstore, model_name="gemini-1.5-flash"):
    template = """Answer the question in a single sentence with the correct answer.
                  Context: {context}
                  Question: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0.01)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    return RunnableParallel({"context": retriever, "question": RunnablePassthrough()}) | prompt | model | StrOutputParser()

# Handle queries and display answers
def answer_question(chain, query):
    return chain.invoke(query)

# Streamlit interface for querying CSV data
def main():
    st.title("CSV Data Query Chatbot")

    # Google Drive Folder ID
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    
    if "text_chunks" not in st.session_state:
        with st.spinner("Processing CSV files from Google Drive..."):
            raw_text = get_combined_csv_text_from_drive(folder_id)
            docs = get_text_chunks(raw_text)
            vectorstore = setup_vectorstore(docs)
            chain = setup_rag_chain(vectorstore)
            st.session_state['chain'] = chain
            st.session_state["text_chunks"] = docs

    # Query input
    query = st.text_input("Ask a question about the CSV data:")
    if query and 'chain' in st.session_state:
        answer = answer_question(st.session_state['chain'], query)
        st.write(f"Answer: {answer}")

# Run the Streamlit app
if __name__ == "__main__":
    main()
