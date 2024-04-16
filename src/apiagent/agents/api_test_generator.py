from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

# define the code generation format 
class Code(BaseModel):
    """Code Output"""
    filename: str = Field(..., description="The filename for the code")
    imports: str = Field(..., description="The imports for the code")
    code: str = Field(..., description="Generated code")

from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'), model="gpt-4-turbo")
tools = [ convert_to_openai_tool(Code) ]
pydantic_parser = PydanticToolsParser(tools=[Code])
llm_with_tools = llm.bind_tools(tools, tool_choice={ "type": "function", "function": { "name": "Code"}} )

template = '''You are a expert python software engineer. You are tasked to generate python test cases for the given openapi specification and acceptence criteria.
Openapi Specification: 
    {openapi_specification}
Acceptence Criteria:
    {acceptence_criteria}

Generate python test cases for acceptence criteria mentioned above.
For test cases use pytest framework and generate test cases covering all the acceptence criteria.
Structure your answer with the description of the code solution.
Then list the imports and the code block.
'''


from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    template,
    input_args=["openapi_specification", "acceptence_criteria"])

custom_prompt = prompt | llm_with_tools | pydantic_parser

class APITestingRequirements(BaseModel):
    """Input for openapi specification and acceptence criteria"""
    openapi_specification: str = Field(..., description="The openapi specification")
    acceptence_criteria: str = Field(..., description="The acceptence criteria")
    
@tool("api_test_case_generator", args_schema=APITestingRequirements)
def api_test_case_generator(openapi_specification: str, acceptence_criteria: str) -> Code:
    """This is used to generate the python test cases for the given openapi specification and acceptence criteria
    Pass the openapi specification and acceptence criteria as input to generate the test cases"""
    api_test_case = custom_prompt.invoke({"openapi_specification": openapi_specification, "acceptence_criteria": acceptence_criteria})
    return api_test_case

