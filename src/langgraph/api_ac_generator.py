# import langchain openai
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# import dotenv, os
from dotenv import load_dotenv
from os import getenv

# load all the environment variables
load_dotenv(".env")

# initialize the ChatOpenAI class
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

# import langgraph
from langgraph.graph import StateGraph, END
from typing import Dict, TypedDict, Optional

# Define the state of the graph
# Given API specifications, we need to generate a acceptence criteria for the API
class AcceptenceCriteria(TypedDict):
    # Open API specification or requirement
    requirement: Optional[str] = None
    # Expected response
    acceptence_criteria: Optional[list[str]] = None
    
# Create a new workflow
workflow = StateGraph(AcceptenceCriteria)

# Define the ndoes - classify request is for API AC or Requirement AC 

# define the prompt template for the requirement classification
requirement_classification_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a QA Automation Engineer. Based on the input, classify the requirement as API requirement or Product Requirement. If it's API, return 'api' else 'requirement'"),
    ("user", "{input}")
])

def classify_request_node(state):
    requirement = state.get('requirement', '').strip()
    chain = requirement_classification_prompt | llm | StrOutputParser()
    classification = chain.invoke({"input": requirement})
    # returning new state with classification
    return {"classification": classification}

api_ac_template = '''You are a QA Automation Engineer. Based on the context, write the acceptance criteria for the API.
API Open API Specification: {input}

return the acceptance criteria for the API in array of acceptance criteria. 

Include below topics in the acceptance criteria:
1. Error handling
2. Http status codes for different scenarios
3. Response format
4. Request format
5. Security

'''

# define the prompt template for the API AC
api_ac_prompt = ChatPromptTemplate.from_template(api_ac_template)

# handle API AC flow
def handle_api_ac_node(state):
    requirement = state.get('requirement', '').strip()
    chain = api_ac_prompt | llm | StrOutputParser()
    acceptence_criteria = chain.invoke({"input": requirement})
    # append response to the state
    return {"acceptence_criteria": acceptence_criteria}

# define the prompt template for the Requirement AC
requirement_ac_prompt = ChatPromptTemplate.from_template("""Your are AI Automation engineer & responsible to generate Acceptance criteria for a new product requriement.
Generate the API Acceptance Criteria for the following product requirement based on the context provided on current product and technical documents.

Acceptance Criteria must include below details:
1. Business Acceptance Criteria
2. Technical Acceptance Criteria
3. API Acceptance Criteria
    3.1 Must include all APIs to support the new requirement
    3.2 Must include API request and response details
    3.3 Must include API error handling details
    3.4 Must include API security details
4. Performance Acceptance Criteria
5. Security Acceptance Criteria
6. Error Handling Acceptance Criteria
7. Documentation Acceptance Criteria
8. Testing Acceptance Criteria
9. Deployment Acceptance Criteria
    9.1 Must include kubernetes deployment details
    9.2 Must include deployment monitoring details
    9.3 Must include deployment rollback details
10. Acceptance criteria on the existing product functionality for the new requirement
    10.1 List all the impacted functionalities
    10.2 List all the impacted APIs
    10.3 List all the impacted services


<context>
{context}
</context>

Product new requirement: {input}""")

# handle Requirement AC flow
def handle_requirement_ac_node(state):
    requirement = state.get('requirement', '').strip()
    chain = requirement_ac_prompt | llm | StrOutputParser()
    acceptence_criteria = chain.invoke({"input": requirement})
    # append response to the state
    return {"acceptence_criteria": acceptence_criteria}

# define all nodes

workflow.add_node("classify_request", classify_request_node)
workflow.add_node("handle_api_ac", handle_api_ac_node)
workflow.add_node("handle_requirement_ac", handle_requirement_ac_node)

def decide_next_node(state):
    return "handle_api_ac" if state.get('classification') == "api" else "handle_requirement_ac"

# make "classify_request" node as entry point and add conditional edges based on "classification"
workflow.add_conditional_edges(
    "classify_request",
    # based on the classification, decide the next node
    decide_next_node,
    # mapping return value of decide next node to classification to the next node
    {
        "handle_api_ac": "handle_api_ac",
        "handle_requirement_ac": "handle_requirement_ac"
    }
)

# add entry point
workflow.set_entry_point("classify_request")
# add edges to other nodes
workflow.add_edge('handle_api_ac', END)
workflow.add_edge('handle_requirement_ac', END)

# compile the workflow
app = workflow.compile()

api_spec = '''
openapi: 3.0.0
info:
  title: Cloud Management API
  version: 1.0.0
  description: |
    This API allows you to manage virtual machines and containers in your cloud environment.

servers:
  - url: https://api.example.com/v1

paths:
  /virtual-machines:
    get:
      summary: Retrieve a list of virtual machines
      description: |
        Get a list of all virtual machines in the cloud.
      responses:
        '200':
          description: A list of virtual machines
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/VirtualMachine'

  /virtual-machines/{vmId}:
    parameters:
      - name: vmId
        in: path
        required: true
        description: ID of the virtual machine
        schema:
          type: string
    get:
      summary: Get details of a specific virtual machine
      description: |
        Get details of a specific virtual machine by providing its ID.
      responses:
        '200':
          description: Virtual machine details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VirtualMachine'
    delete:
      summary: Delete a virtual machine
      description: |
        Delete a virtual machine by providing its ID.
      responses:
        '204':
          description: Virtual machine deleted successfully

  /virtual-machines/{vmId}/start:
    parameters:
      - name: vmId
        in: path
        required: true
        description: ID of the virtual machine
        schema:
          type: string
    post:
      summary: Start a virtual machine
      description: |
        Start a virtual machine by providing its ID.
      responses:
        '200':
          description: Virtual machine started successfully

  /virtual-machines/{vmId}/stop:
    parameters:
      - name: vmId
        in: path
        required: true
        description: ID of the virtual machine
        schema:
          type: string
    post:
      summary: Stop a virtual machine
      description: |
        Stop a virtual machine by providing its ID.
      responses:
        '200':
          description: Virtual machine stopped successfully
components:
  schemas:
    VirtualMachine:
      type: object
      properties:
        id:
          type: string
          description: The unique identifier of the virtual machine.
        name:
          type: string
          description: The name of the virtual machine.
        status:
          type: string
          description: The current status of the virtual machine.
          enum: [running, stopped, suspended]
        cpu:
          type: integer
          description: The number of CPU cores allocated to the virtual machine.
        memory:
          type: string
          description: The amount of memory allocated to the virtual machine (e.g., "4GB").
        disk:
          type: string
          description: The size of the disk allocated to the virtual machine (e.g., "100GB").
        os:
          type: string
          description: The operating system installed on the virtual machine.
'''

# invoke the workflow
inputs = {"requirement": api_spec}
result = app.invoke(inputs)
print(result['acceptence_criteria'])