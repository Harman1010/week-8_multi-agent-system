from typing import TypedDict , Dict , Any , List, Annotated

def merge_results(existing:Dict[str,Any],new:Dict[str,Any]):

    return {
        **existing,
        **new
    }

def merge_lists(existing: list, new: list):

    return existing + new


class AgentState(TypedDict):

    """A blueprint for the shared state that follows throughout the graph"""

    query : str

    transformed_query : str

    plan : List[Dict[str,Any]]

    selected_agents : List[str]

    failed_agents : Annotated[List[str],merge_lists]

    retry_agents : List[str]

    results : Annotated[Dict[str,Any],merge_results]

    needs_transformation : bool

    observations : List[str]

    decision : str

    clarification_question : str

    errors : Annotated[List[str],merge_lists]

    num_iterations : int

    recovery_iterations : int

    status : str

    answer : str

