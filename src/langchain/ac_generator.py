# How QA engineer write AC?
# Train the QA engineer on the product and techincal documents.
# QA engineer understand the new requirement and existing product functionality.
# QA engineer write the AC based on the understanding.

# import the required libraries
from os import getenv
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFDirectoryLoader

# load all the environment variables
load_dotenv(".env")

# Train AI Test Engineer by loading all product and technical documents.
# pdf directory loader can be used to load all pdf files from a directory
pdf_loader = PyPDFDirectoryLoader("data/product/")
docs = pdf_loader.load()

print("Documents:", len(docs))

# Embed the documents using HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# split the extracted data into text chunks using the text_splitter, which splits the text based on the specified number of characters and overlap
from langchain_text_splitters import RecursiveCharacterTextSplitter
pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
pdf_chunks = pdf_splitter.split_documents(docs)

print("Chunk documents length:", len(pdf_chunks))

# Index the pdf document using langchain_community.vectorstores.FAISS
from langchain_community.vectorstores import FAISS
vector = FAISS.from_documents(pdf_chunks, embeddings)
retriever = vector.as_retriever()

# create llm
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# stuff documents chain
# purpose of create_stuff_documents_chain is to create a chain that retrieves the document based on the input question
from langchain.chains.combine_documents import create_stuff_documents_chain

# import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template("""Your are AI Automation engineer & responsible to generate Acceptance criteria for a new product requriement.
Generate the API Acceptance Criteria for the following product requirement based on the context provided on current product and technical documents.

Acceptance Criteria must include below details:
1. Business Acceptance Criteria
2. Technical Acceptance Criteria
3. API Acceptance Criteria
    3.1 Must include all APIs to support the new requirement
    3.2 Must include API request and response details
    3.3 Must include API error handling details
    3.4 Must include API security details
4. Performance Acceptance Criteria
5. Security Acceptance Criteria
6. Error Handling Acceptance Criteria
7. Documentation Acceptance Criteria
8. Testing Acceptance Criteria
9. Deployment Acceptance Criteria
    9.1 Must include kubernetes deployment details
    9.2 Must include deployment monitoring details
    9.3 Must include deployment rollback details
10. Acceptance criteria on the existing product functionality for the new requirement
    10.1 List all the impacted functionalities
    10.2 List all the impacted APIs
    10.3 List all the impacted services


<context>
{context}
</context>

Product new requirement: {input}""")

# create the document chain
document_chain = create_stuff_documents_chain(llm, prompt)

# create retrieval chain
from langchain.chains.retrieval import create_retrieval_chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)

new_requirement = '''Real-time Chat Support:

Description: Introduce real-time chat support functionality, allowing users to communicate directly with customer support representatives for assistance during the ordering process.
Details:
Implement a chat interface accessible from within the application for users to initiate conversations with support agents.
Ensure real-time messaging capabilities to enable instant communication between users and support representatives.
Integrate chatbots to handle common inquiries and provide automated responses, improving response times and efficiency.
Enable file and image sharing functionalities within the chat interface for users to send relevant information or screenshots.
Implement message history and conversation logging for tracking and resolving user queries effectively.
Ensure cross-platform compatibility, allowing users to access chat support from web browsers and mobile applications seamlessly.'''
response = retrieval_chain.invoke({"input": new_requirement})

print(response["answer"])