from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool

# define the code generation format 
class Code(BaseModel):
    """Code Output"""
    filename: str = Field(..., description="The filename for the code")
    imports: str = Field(..., description="The imports for the code")
    code: str = Field(..., description="Generated code")
    

from langchain_core.utils.function_calling import convert_to_openai_tool
    
# convert Code to Tool
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv(".env")

llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))
tools = [ convert_to_openai_tool(Code) ]


from langchain_core.output_parsers.openai_tools import PydanticToolsParser

llm_with_tools = llm.bind_tools(tools, tool_choice={ "type": "function", "function": { "name": "Code"}} ) 
pydantic_parser = PydanticToolsParser(tools=[Code])


template = '''You are a expert software engineer. You are tasked to generate API Test code for the given openapi specification and acceptence criteria.

API Specificiation: {openapi_specification}

Acceptence Criteria: {acceptence_criteria}

Generate python test code all the acceptence criteria mentioned above. 
For test use pytest framework and generate new test functions for each acceptence criteria.
Structure your answer with the description of the code solution.
Then list the imports and the code block.
'''

from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    template,
    input_args=["openapi_specification", "acceptence_criteria"])

custom_prompt = prompt | llm_with_tools | pydantic_parser

openapi_specification = '''
summary: Create a new virtual machine
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/VirtualMachineInput'
responses:
  201:
    description: The created virtual machine
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/VirtualMachine'
        examples:
          createdVM:
            value:
              id: 2
              name: NewVM
              os: CentOS
              memory: 2048
              storage: 100
              status: stopped
  400:
    description: Bad request, check your input data
  401:
    description: Unauthorized, authentication required
  403:
    description: Forbidden, you are not authorized to perform this action
  500:
    description: Internal server error
'''
acceptence_criteria = '''
1. Different error handling scenarios
2. Http status codes for different scenarios
3. Security testing
'''

ans = custom_prompt.invoke({"openapi_specification": openapi_specification, "acceptence_criteria": acceptence_criteria})

print(ans[0].filename)
print(ans[0].imports)
print(ans[0].code)