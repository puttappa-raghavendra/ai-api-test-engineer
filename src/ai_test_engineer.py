from api_spec_extractor import fetch_api_openapi_specification
from api_spec_search import search_apis
from api_test_generator import api_test_case_generator
from api_ac_generator import api_acceptence_criteria_generator

tools = [search_apis, fetch_api_openapi_specification, api_acceptence_criteria_generator, api_test_case_generator]

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

# load environment variables
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages

# init llm
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'), temperature=0)

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

input = '''Generate test case for the list virtual machines api'''

agent_executor.invoke({"input": input})


