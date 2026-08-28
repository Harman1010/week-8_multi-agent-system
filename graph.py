from langgraph.graph import StateGraph, START, END

from state import AgentState
from nodes import transform_query

def create_graph():

    builder = StateGraph(AgentState)

    builder.add_node("queryTransformer",transform_query)

    builder.add_edge(START,"queryTransformer")
    builder.add_edge("queryTransformer",END)

    return builder.compile()

