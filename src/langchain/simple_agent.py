from langchain_openai import OpenAI
from langchain.agents import load_tools, initialize_agent
from os import getenv
from dotenv import load_dotenv
from langchain.agents import AgentType

# load all the environment variables
load_dotenv(".env")

llm = OpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# load the tools
tools_names = ["llm-math"]
tools = load_tools(tools_names, llm=llm)

# initialize the agent
agent = initialize_agent(tools=tools, llm=llm, type=AgentType.OPENAI_FUNCTIONS, verbose=True)

# run the agent
answer = agent.invoke("What is the square root of 4?")

# print the answer
print(answer)
