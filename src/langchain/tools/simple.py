# simple tool which will be used in Agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

# simple tool using @tools
@tool
def search(query: str) -> str:
    """Search the web for the query""" # this is description
    return f"Search results for {query}"

print(search.name)
print(search.description) 
print(search.schema)

@tool
def multiple(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

print(multiple.name)
print(multiple.description)
print(multiple.schema)
print(multiple.args)

class QueryInput(BaseModel):
    query: str = Field(..., description="The search query")
    
@tool("search", args_schema=QueryInput, return_direct=True)
def search_tool(query: str) -> str:
    """Search the web for the query"""
    return f"Search results for {query}"

print(search_tool.name)
print(search_tool.description)
print(search_tool.schema)

# lets define a tool get ticker
class StockTickerInput(BaseModel):
    stock_symbol: str = Field(..., description="The Ticker symbol for a company or index")

import yfinance as yf

@tool("get_stock_price", args_schema=StockTickerInput, return_direct=True)
def get_stock_price(stock_symbol: str) -> float:
    """Get the stock price of a company"""
    stock = yf.Ticker(stock_symbol)
    return stock.history(period='1d')['Close'].iloc[0]

import yfinance as yf
from datetime import datetime, timedelta

class StockChangeQuery(BaseModel):
    """Input for stock ticker symbol"""
    stock_symbol: str = Field(..., description="The Ticker symbol for a company or index")
     

@tool("get_percent_change", args_schema=StockChangeQuery, return_direct=True)
def get_percent_change(stock_symbol: str) -> float:
    """Get the percent change in stock price for the last month"""
    # Define the ticker symbol (e.g., 'AAPL' for Apple Inc.)
    ticker = yf.Ticker(stock_symbol)

    # Get historical data for the last month
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)  # 30 days ago

    # Fetch historical data
    historical_data = ticker.history(start=start_date, end=end_date)

    if historical_data.empty:
        return None  # Return None if no data is available

    # Calculate percent change in closing price
    last_close = historical_data['Close'].iloc[0]
    current_close = historical_data['Close'].iloc[-1]

    percent_change = ((current_close - last_close) / last_close) * 100

    return percent_change

print(get_stock_price.name) 
print(get_stock_price.description)
print(get_stock_price.schema)
print(get_stock_price.args)
print(get_stock_price("AAPL"))

tools = [get_stock_price, get_percent_change]

from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from os import getenv
from dotenv import load_dotenv
from typing import List, Optional, Dict, Type

# load all the environment variables
load_dotenv(".env")

# initialize the llm
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# define the agent with the tools
agent = initialize_agent(tools, llm=llm, type=AgentType.OPENAI_FUNCTIONS, verbose=True)

agent.invoke("What is the stock price of Equinix?")

agent.invoke("What is the percent change in stock price of Apple?")