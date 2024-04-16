from os import getenv
from dotenv import load_dotenv
# import langchain openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# Load all the environment variables
load_dotenv(".env")

# Create a ChatOpenAI object
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# load Equinix metal OpenAPI specification using langchain_community.document_loaders.WebBaseLoader
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://deploy.equinix.com/developers/api/metal")
docs = loader.load()

# index the Equinix metal OpenAPI specification using langchain_openai.OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()

# index the Equinix metal OpenAPI specification using langchain_community.vectorstores.FAISS
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)

# create a chain to retrieve the document based on the input question
from langchain.chains.combine_documents import create_stuff_documents_chain

template = '''You are Equinix Metal domain and API expert. 

Answer the following question based only on the provided context: 

<context>
{context}
</context>

Question: {input}
'''
# create a ChatPromptTemplate object from the template
prompt = ChatPromptTemplate.from_template(template)

# create a document chain using the create_stuff_documents_chain function
document_chain = create_stuff_documents_chain(llm, prompt)

# create a retrieval chain using the create_retrieval_chain function
from langchain.chains import create_retrieval_chain

# create a retriever object from the vector object
retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

print(retriever)
response = retrieval_chain.invoke({"input": "Which API can be used to create a new device? give more details about the API with examples to create new device"})
print(response["answer"])

