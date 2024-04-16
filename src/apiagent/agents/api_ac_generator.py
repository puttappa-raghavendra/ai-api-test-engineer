from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

# define the code generation format 
class APIAcceptenceCriteria(BaseModel):
    """Acceptence Criteria Output"""
    filename: str = Field(..., description="The filename for the code")
    http_status_code: str = Field(..., description="The HTTP status code acceptence criteria")
    response_body: str = Field(..., description="The response body acceptence criteria")
    response_headers: str = Field(..., description="The response headers acceptence criteria")
    response_error_handling: str = Field(..., description="The response error handling acceptence criteria")
    response_content_type: str = Field(..., description="The response content type acceptence criteria")
    filtering: str = Field(..., description="The filtering acceptence criteria")
    pagination: str = Field(..., description="The pagination acceptence criteria")
    sorting: str = Field(..., description="The sorting acceptence criteria")
    search: str = Field(..., description="The search acceptence criteria")
    rate_limiting: str = Field(..., description="The rate limiting acceptence criteria")
    
    
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'), model="gpt-4-turbo")
tools = [ convert_to_openai_tool(APIAcceptenceCriteria) ]
pydantic_parser = PydanticToolsParser(tools=[APIAcceptenceCriteria])
llm_with_tools = llm.bind_tools(tools, tool_choice={ "type": "function", "function": { "name": "APIAcceptenceCriteria"}} )

template = '''You are a expert API Test Automation engineer. You are tasked to generate Acceptence Criteria for the given openapi specification.
Openapi Specification: 
    {openapi_specification}
    
Structure your answer with the description of the APIAcceptenceCriteria solution.
'''


from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    template,
    input_args=["openapi_specification"])

custom_prompt = prompt | llm_with_tools | pydantic_parser

class OpenAPISpecificationInput(BaseModel):
    """OpenAPI Specification Input"""
    openapi_specification: str = Field(..., description="The openapi specification")

@tool("api_acceptence_criteria_generator", args_schema=OpenAPISpecificationInput)
def api_acceptence_criteria_generator(openapi_specification: str) -> APIAcceptenceCriteria:
    """This is used to generate the Acceptence Criteria for the given openapi specification
    Pass the openapi specification input to generate the acceptence criterias"""
    ac_test_case = custom_prompt.invoke({"openapi_specification": openapi_specification})
    return ac_test_case

