from state import AgentState

import json

def get_task_name(state:AgentState,agent_name:str):

    for step in state["plan"]:

        if step["agent"] == agent_name:

            return step["task"]

    return None

def load_faq():

    with open("data/faq.json", "r", encoding="utf-8") as file:
        return json.load(file)

def is_retryable_error(error:str) -> bool:

    error = error.lower()

    keyword_errors = [
        "too many requests",
        "temporarily unavailable",
        "429",
        "502",
        "503",
        "connection",
        "service unavailable",
        "network",
        "time out",
        "timed out"
    ]

    return any(
        keyword in error
        for keyword in keyword_errors
    )