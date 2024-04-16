# create two tools 
# 1. get_stock_price
# 2. get_percent_change

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

# Ticker symbol input
class StockTickerInput(BaseModel):
    """Input for the stock ticker symbol"""
    ticker: str = Field(..., description="The Ticker symbol for a company or index")

import yfinance as yf
    
@tool("get_stock_price", args_schema=StockTickerInput)
def get_stock_price(ticker: str) -> float:
    """Get the stock price of a company. Use the ticker as input to yahoo finance API."""
    stock = yf.Ticker(ticker)
    return stock.history(period='1d')['Close'].iloc[0]

# Percent change in stock price in the last month
class StockChangeQuery(BaseModel):
    """Input for stock ticker symbol and number of days"""
    ticker: str = Field(..., description="The Ticker symbol for a company or index")
    days: int = Field(30, description="Number of days to calculate percent change")
    
@tool("get_percent_change", args_schema=StockChangeQuery)
def get_percent_change(ticker: str, days: int) -> float:
    """Get the percent change in stock price for the given number of days. Use the ticker as input to yahoo finance API & use number of days to get historical data"""
    # Define the ticker symbol (e.g., 'AAPL' for Apple Inc.)
    ticker = yf.Ticker(ticker)
    # Get the stock price for the last month
    stock_data = ticker.history(period=f'{days}d')
    # Calculate the percent change
    percent_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0] * 100
    return percent_change

# define the tool to largest stock price movement in the given number of days
class StockLargestMovementQuery(BaseModel):
    """Input for stock ticker symbol and number of days"""
    ticker: str = Field(..., description="The Ticker symbol for a company or index")
    days: int = Field(30, description="Number of days to use to define the boundary to calculate largest stock price movement")
    
@tool("get_largest_stock_movement", args_schema=StockLargestMovementQuery)
def get_largest_stock_movement(ticker: str, days: int) -> float:
    """Get the largest stock price movement in the given number of days. Use the ticker as input to yahoo finance API & use number of days to get historical data"""
    # Define the ticker symbol (e.g., 'AAPL' for Apple Inc.)
    ticker = yf.Ticker(ticker)
    # Get the stock price for the last month
    stock_data = ticker.history(period=f'{days}d')
    # Calculate the percent change
    stock_data['movement'] = (stock_data['Close'] - stock_data['Open']) / stock_data['Open'] * 100
    # Get the largest movement
    largest_movement = stock_data['movement'].max()
    return largest_movement

from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
load_dotenv(".env")
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))


tools = [get_stock_price, get_percent_change, get_largest_stock_movement]

from langchain.agents import create_tool_calling_agent
from langchain import hub

prompt = hub.pull("hwchase17/openai-functions-agent")
agent = create_tool_calling_agent(llm, tools, prompt)

# use Agent Executor to invoke the agent
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# invoke the agent
agent_executor.invoke({"input": "What is the stock price of google?"})

# invoke the agent to calculate the percent change in stock price for the last 30 days
agent_executor.invoke({"input": "What is the percent change in stock price of google for the last week?"})

# invoke the agent to calculate the largest stock price movement in the last 30 days
agent_executor.invoke({"input": "What is the largest stock price movement of nvdia in the last week?"})