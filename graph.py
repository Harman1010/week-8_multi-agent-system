from langgraph.graph import StateGraph, START, END

from state import AgentState
from nodes import transform_query,validate_input,supervisor

def route_after_validation(state:AgentState):

    if state["status"] == "validated":

        return "queryTransformer"

    return END

def create_graph():

    builder = StateGraph(AgentState)

    builder.add_node("queryDetector",validate_input)
    builder.add_node("queryTransformer",transform_query)
    builder.add_node("supervisor",supervisor)
   

    builder.add_edge(START,"queryDetector")

    builder.add_conditional_edges("queryDetector",route_after_validation)

    builder.add_edge("queryTransformer","supervisor")
    builder.add_edge("supervisor",END)

    return builder.compile()

