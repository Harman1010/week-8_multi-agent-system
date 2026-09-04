from pydantic import BaseModel

from typing import Literal

class PlanStep(BaseModel):

    agent : str
    task : str

class SelectedPlan(BaseModel):

    decision: Literal["route","clarify"]

    selected_agents : list[str]
    plan : list[PlanStep]

    clarification_question : str