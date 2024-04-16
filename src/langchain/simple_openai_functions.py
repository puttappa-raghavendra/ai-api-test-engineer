import yfinance as yf

def get_stock_price(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    return stock.history(period='1d')['Close'].iloc[0]

print(get_stock_price('AAPL'))

# imports 
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from os import getenv
from dotenv import load_dotenv
from typing import List, Optional, Dict, Type

# load all the environment variables
load_dotenv(".env")

# initialize the llm
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

from pydantic import BaseModel, Field

class StockPriceTicker(BaseModel):
    """Input for stock price check"""
    stock_symbol: str = Field(..., description="The Ticker symbol for a company or index")
    
class StockPriceTool(BaseModel):
    
    name = "get_stock_price"
    # give more detailed description of the tool so that this tool is used when ever the user asks for stock price
    description = "This tool is used to get the stock price of a company or index. You should use stock symbol used on a yahoo finance API"
 
    def _run(self, stock_symbol: str) -> float:
        stock_price = get_stock_price(stock_symbol)
        return  stock_price
    
    def _arun(self, stock_symbol: str) -> float:
        return NotImplementedError("This method is not implemented yet")
    
    properties: Optional[Type[BaseModel]] = StockPriceTicker
    
    is_single_input = True
       
# define the tools
tools = [StockPriceTool()]

# define the agent with the tools
agent = initialize_agent(tools, llm=llm, type=AgentType.OPENAI_FUNCTIONS, verbose=True)

agent.invoke("What is the stock price of apple?")