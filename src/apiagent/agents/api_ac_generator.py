from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

class AcceptenceCriteriaFormat(BaseModel):
    """Acceptence Criteria Output"""
    scenario: str = Field(..., description="The acceptence criteria scenario")
    given: str = Field(..., description="Initial context or state of the system or api resource")
    when: str = Field(..., description="Action that is performed")
    then: str = Field(..., description="Expected outcome of the action")

class ListAcceptenceCriteriaFormat(BaseModel):
    """List of Acceptence Criteria Output"""
    acceptence_criteria: list[AcceptenceCriteriaFormat] = Field(..., description="List of acceptence criterias")
   
    
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")

llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'), model="gpt-4-turbo")
tools = [ convert_to_openai_tool(ListAcceptenceCriteriaFormat) ]

pydantic_parser = PydanticToolsParser(tools=[ListAcceptenceCriteriaFormat])

llm_with_tools = llm.bind_tools(tools, tool_choice={ "type": "function", "function": { "name": "ListAcceptenceCriteriaFormat"}} )

template = '''You are a expert API Test Automation engineer. You are tasked to generate Acceptence Criteria for the given openapi specification.

Openapi Specification: 
    {openapi_specification}

Acceptence Criteria must cover basics scenarios followed by many more based on API specification.

1. Acceptence criteria which covers all the HTTP status codes.
2. Acceptence criteria covering filtering, sorting, pagination, and searching based on API.
3. Acceptence criteria covering all the request and response parameters which validate the correctness of the API.
4. Acceptence criteria covering all the error scenarios and edge cases.
5. Cover all success scenarios with the response validation.
6. Cover all the security and authorization scenarios.
7. Cover all the performance scenarios.
8. Cover all the negative scenarios.

+ more acceptence criterias based on the API specification.
    
* Structure your answer with the description of the APIAcceptenceCriteria solution.
* Make sure you cover all the above mentioned acceptence criterias while generating the acceptence criterias.


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
def api_acceptence_criteria_generator(openapi_specification: str) -> ListAcceptenceCriteriaFormat:
    """This is used to generate the Acceptence Criteria for the given openapi specification
    Pass the openapi specification input to generate the acceptence criterias"""
    return custom_prompt.invoke({"openapi_specification": openapi_specification})

