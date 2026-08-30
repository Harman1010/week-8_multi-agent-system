from typing import TypedDict , Dict , Any , List, Annotated

def merge_results(existing:Dict[str,Any],new:Dict[str,Any]):

    return {
        **existing,
        **new
    }


class AgentState(TypedDict):

    """A blueprint for the shared state that follows throughout the graph"""

    query : str

    transformed_query : str

    plan : List[Dict[str,Any]]

    selected_agents : List[str]

    results : Annotated[Dict[str,Any],merge_results]

    observations : List[str]

    num_iterations : int

    recovery_iterations : int #Error

    status : str

    answer : str

