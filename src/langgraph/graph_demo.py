from typing import Dict, TypedDict, Optional

# let's summarize the workflow
# 1. Define the state of the graph
# 1.1. Define the structure of the state
# 1.2. Define the initial state
# 2. Define the nodes
# 2.1. Define the node functions
# 2.2. Add the nodes to the workflow
# 3. Define the edges
# 3.1. Define the edge functions
# 3.2. Add the edges to the workflow
# 4. Compile the workflow
# 5. Invoke the workflow



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


# classify the input type. It can be a greeting or a search query
def classify_input_node(state):
    question = state.get('question', '').strip()
    classification = "greeting" if question.lower().startswith("hello") else "search"
    # returning new state with classification
    return {"classification": classification}

# handle greeting flow
def handle_greeting_node(state):
    print( state.get("classification", ""))
    # append response to the state
    return {"response": "Hello! How can I help you today?"}

# handle search flow
def handle_search_node(state):
    question = state.get('question', '').strip()
    search_result = f"Search result for '{question}'"
    # append response to the state
    return {"response": search_result}

# define all nodes
workflow.add_node("classify_input", classify_input_node)
workflow.add_node("handle_greeting", handle_greeting_node)
workflow.add_node("handle_search", handle_search_node)

def decide_next_node(state):
    return "handle_greeting" if state.get('classification') == "greeting" else "handle_search"

# make "classify_input" node as entry point and add conditional edges based on "classification"
workflow.add_conditional_edges(
    "classify_input",
    # based on the classification, decide the next node
    decide_next_node,
    # mapping return value of decide next node to classification to the next node
    {
        "handle_greeting": "handle_greeting",
        "handle_search": "handle_search"
    }
)

# add entry point
workflow.set_entry_point("classify_input")
# add edges to other nodes
workflow.add_edge('handle_greeting', END)
workflow.add_edge('handle_search', END)

# compile the workflow
app = workflow.compile()

# invoke the workflow
inputs = {"question": "Hello, how are you?"}
result = app.invoke(inputs)
print(result)