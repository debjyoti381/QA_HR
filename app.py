import os
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import pandas as pd
from langchain_core.documents import Document
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Load environment variables
load_dotenv()

# Set environment variable for Google API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyARxm0Lk5SXSHRMt_Rw3iklQrVQcGRgVCA"

# Google Drive API Setup
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'client_secret.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
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
        fh = io.BytesIO()  # Use BytesIO for binary content

        try:
            # Attempt to download as binary content first
            request = drive_service.files().get_media(fileId=file['id'])
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        except Exception as e:
            print(f"Direct download failed for {file['name']}, attempting export as CSV. Error: {e}")
            # If direct download fails, fallback to exporting as Google Sheets
            request = drive_service.files().export_media(fileId=file['id'], mimeType='text/csv')
            fh = io.BytesIO()  # Reset file handler as BytesIO for export
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        # Check if the file content was downloaded
        fh.seek(0)
        content = fh.read().decode("utf-8")  # Decode bytes to string
        print(f"Downloaded content for {file['name']} (first 500 characters):\n{content[:500]}")  # Check content

        # Attempt to read the CSV content
        try:
            df = pd.read_csv(io.StringIO(content))  # Read content as CSV
            print(f"Successfully read {len(df)} rows from {file['name']}")  # Confirm rows read
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

    print("Embedding values:", embedding_values)  # Debugging statement
    if len(embedding_values) == 0 or len(embedding_values[0]) == 0:
        raise ValueError("Embedding generation failed. Check the embeddings model and API configuration.")
    
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore.save_local("faiss_index")
    return vectorstore

# Set up the RAG chain with Google Gemini API
def setup_rag_chain(vectorstore, model_name="gemini-1.5-flash"):
    template = """Answer the question in a single sentence with correct answer . Do not require extra explanation from the provided context. Make sure to provide all the details.
    If the answer is not in the provided context, just say, "answer is not available in the context.
    If user asks you like 1. who build you then give the answer as Utkarsh and 2. what is your name then give the answer as FlivoAI chatbot or 3. who are you just say FlivoAI Chatbot to solve your queries".
    
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

    # Google Drive Folder ID
    folder_id = '1Oi7MC9FrSHjhw0r5x_H8tuDMR5gyb_UX'  # Replace with the actual Google Drive folder ID containing the CSV files
    
    if "text_chunks" not in st.session_state:
        with st.spinner("Processing CSV files from Google Drive..."):
            raw_text = get_combined_csv_text_from_drive(folder_id)
            docs = get_text_chunks(raw_text)
            print("Number of documents:", len(docs))  # Debugging statement
            if len(docs) == 0:
                st.error("No text chunks were created from the CSV files.")
                return
            vectorstore = setup_vectorstore(docs)
            chain = setup_rag_chain(vectorstore)
            st.session_state['chain'] = chain
            st.session_state["text_chunks"] = docs

    # Query input
    if 'chain' in st.session_state:
        query = st.text_input("Ask a question about the CSV data:")
        
        if query:
            answer = answer_question(st.session_state['chain'], query)
            st.write(f"Answer: {answer}")

# Run the Streamlit app
if __name__ == "__main__":
    main()
