from typing import TypedDict , Dict , Any , Optional, List

class AgentState(TypedDict):

    """A blueprint for the shared state that follows throughout the graph"""

    query : str

    transformed_query : str

    plan : List[Dict[str,Any]]

    results : Dict[str,Any]

    observations : List[str]

    agents_selected : List[str]

    num_iterations : int

    recovery_iterations : int #Error

    status : str

    answer : str

