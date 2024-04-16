from os import getenv
from dotenv import load_dotenv
# import langchain openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# load all the environment variables
load_dotenv(".env")

# summary of steps
# 1. create llm
# 2. create chat prompt template with system role as "QA Automation Engineer" and user role as "{input}
# 3. create chain with prompt, llm and output parser
# 4. invoke the chain with input as "what is the best way to automate testing?"
# 5. print the response


# create llm
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# create chat prompt template with system role as "QA Automation Engineer" and user role as "{input}
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are QA Automation Engineer."),
    ("user", "{input}")
])

# create chain with prompt, llm and output parser
chain = prompt | llm | StrOutputParser()

# invoke the chain with input as "what is the best way to automate testing?"
response = chain.invoke({"input": "what is the best way to automate testing?"})

# print the response
print(response)