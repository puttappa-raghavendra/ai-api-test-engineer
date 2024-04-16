from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import getenv

# load all the environment variables
load_dotenv(".env")

# initialize the ChatOpenAI class
llm = ChatOpenAI(openai_api_key=getenv('OPENAI_API_KEY'))

from typing import Dict, TypedDict, Optional
 
# Define the state of the graph
class GraphState(TypedDict):
    # First Question
    question: Optional[str] = None
    # Classification of the question. Based on this, we will decide the next node
    classification: Optional[str] = None
    # Response to the user
    response: Optional[str] = None
    
from langgraph.graph import StateGraph, END

# Create a new workflow
workflow = StateGraph(GraphState)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()

question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are english language expert and have expertise in computer programming and architecture. Based on the input, classify the question on software development or its generic query. if it's software question return 'software' else 'generic'"),
    ("user", "{input}")
])

# define the nodes - classify the input type. It can be a greeting or a search query
def question_classification_node(state):
    question = state.get('question', '').strip()
    chain = question_prompt | llm | output_parser
    response = chain.invoke({"input": question})
    print("quesiton_classification", response)
    # returning new state with classification
    return {"classification": response}

software_question_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a world class software engineer. Based on the input, answer the software question."),
    ("user", "{input}")
])

# handle software question flow
def handle_software_question_node(state):
    question = state.get('question', '').strip()
    chain = software_question_prompt | llm | output_parser
    response = chain.invoke({"input": question})
    # append response to the state
    return {"response": response}

generic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are very good in general knowledge. Based on the input, answer the generic question."),
    ("user", "{input}")
])


# handle generic question flow
def handle_generic_question_node(state):
    question = state.get('question', '').strip()
    response = f"Search result for '{question}'"
    chain = generic_prompt | llm | output_parser
    
    response = chain.invoke({"input": response})
    # append response to the state
    return {"response": response}

# define all nodes

workflow.add_node("question_classification", question_classification_node)
workflow.add_node("handle_software_question", handle_software_question_node)
workflow.add_node("handle_generic_question", handle_generic_question_node)

# decide the next node based on classification
def decide_next_node(state):
    return "handle_software_question" if state.get('classification') == "software" else "handle_generic_question"

# make "question_classification" node as entry point and add conditional edges based on "classification"
workflow.add_conditional_edges(
    "question_classification",
    # based on the classification, decide the next node
    decide_next_node,
    # mapping return value of decide next node to classification to the next node
    {
        "handle_software_question": "handle_software_question",
        "handle_generic_question": "handle_generic_question"
    }
)

# add entry point
workflow.set_entry_point("question_classification")
# add edges to other nodes
workflow.add_edge('handle_software_question', END)
workflow.add_edge('handle_generic_question', END)

# compile the workflow
app = workflow.compile()

# invoke the workflow
inputs = {"question": "Hello, how are you?"}
result = app.invoke(inputs)

print(result)