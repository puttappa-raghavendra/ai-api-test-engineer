from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

class StockTickerInput(BaseModel):
    """Input for the stock ticker symbol"""
    ticker: str = Field(..., description="The Ticker symbol for a company or index")
    
import yfinance as yf
@tool("get_stock_price", args_schema=StockTickerInput)
def get_stock_price(ticker: str) -> float:
    """Get the stock price of a company. Use the ticker as input to yahoo finance API."""
    stock = yf.Ticker(ticker)
    return stock.history(period='1d')['Close'].iloc[0]

tools = [get_stock_price]

from langchain import hub 
# load environment variables
from os import getenv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(".env")

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages


# init llm
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({"input": "What is the stock price of google?"})