from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
# import langchain openai
from langchain_openai import ChatOpenAI
from os import getenv

# load all the environment variables
load_dotenv(".env")

llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

print(llm.invoke("Hello, how are you?").content)