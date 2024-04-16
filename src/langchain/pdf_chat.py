# Idea is to load the product or technical document about the product.
# This is first phase of training the QA engineer in real world scenario.
# Once the QA engineer is trained, the next phase is to ask QA engineer to write the test cases based on the document.

# ask questions on those documents
# import required libraries
from os import getenv
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFDirectoryLoader

# Load all the environment variables
load_dotenv(".env")

# pdf directory loader can be used to load all pdf files from a directory
# pdf_loader = PyPDFDirectoryLoader("path/to/pdf/directory")
# docs = pdf_loader.load()

# Load the PdF document using langchain_community.document_loaders import PyPDFLoader
loader = PyMuPDFLoader("https://www.first.org/resources/guides/Establishing-a-Certification-Authority-CA.pdf")
docs = loader.load()

# print(len(docs))

# used embedding from langchain_community.embeddings.HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# split the extracted data into text chunks using the text_splitter, which splits the text based on the specified number of characters and overlap
# import text spitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
pdf_chunks = pdf_splitter.split_documents(docs)

# print the number of chunks obtained
# print(len(pdf_chunks))
# Index the pdf document using langchain_community.vectorstores.FAISS
from langchain_community.vectorstores import FAISS
vector = FAISS.from_documents(pdf_chunks, embeddings)
retriever = vector.as_retriever()
# Query vector store to verify the similarity of the question with the document
# print(vector.index.ntotal)
# response = vector.similarity_search("What is the purpose of a Certification Authority (CA)?")
# print(response[0].page_content)

# create llm
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# stuff documents chain 
# purpose of create_stuff_documents_chain is to create a chain that retrieves the document based on the input question
from langchain.chains.combine_documents import create_stuff_documents_chain

# import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

document_chain = create_stuff_documents_chain(llm, prompt)
# create retrieval chain
# purpose of retriever is to retrieve the document based on the input question
from langchain.chains import create_retrieval_chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)

response = retrieval_chain.invoke({"input": "explain the flow of issuing client certificates in a Certification Authority (CA) system"})
print(response["answer"])