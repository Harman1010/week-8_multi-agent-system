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