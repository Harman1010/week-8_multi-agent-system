from langgraph.graph import StateGraph, START, END

from state import AgentState
from nodes import (transform_query,validate_input,supervisor,faq_agent,research_agent,code_agent,final_response,
validate_results,recovery_node)

def route_after_validation(state:AgentState):

    if state["status"] == "validated":

        return "queryTransformer"

    return END

def route_after_supervisor(state:AgentState):

    return state["selected_agents"]

def route_after_result_validation(state: AgentState):

    status = state["status"]

    if status == "validated_results":
        return "final_response"

    if status in ["partial_failure", "failed"]:
        return "recovery_node"

    return "final_response"


def route_after_recovery(state: AgentState):

    status = state["status"]

    if status == "recovery_failed":
        return "final_response"

    if status == "retrying":
        return state["retry_agents"]

    return "final_response"

         
def create_graph():

    builder = StateGraph(AgentState)

    builder.add_node("queryDetector",validate_input)
    builder.add_node("queryTransformer",transform_query)
    builder.add_node("supervisor",supervisor)
    builder.add_node("faq_agent",faq_agent)
    builder.add_node("research_agent",research_agent)
    builder.add_node("code_agent",code_agent)
    builder.add_node("final_response",final_response)
    builder.add_node("validate_results",validate_results)
    builder.add_node("recovery_node",recovery_node)
   

    builder.add_edge(START,"queryDetector")

    builder.add_conditional_edges("queryDetector",route_after_validation)

    builder.add_edge("queryTransformer","supervisor")

    builder.add_conditional_edges("supervisor",route_after_supervisor)

    builder.add_conditional_edges(
        "validate_results",
        route_after_result_validation
    )

    builder.add_conditional_edges(
        "recovery_node",
        route_after_recovery
    )

    builder.add_edge("faq_agent", "validate_results")
    builder.add_edge("research_agent", "validate_results")
    builder.add_edge("code_agent", "validate_results")

    builder.add_edge("final_response", END)

    return builder.compile()

