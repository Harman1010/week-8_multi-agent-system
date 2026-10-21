from pydantic import BaseModel

from typing import Literal

AgentName = Literal["faq_agent", "research_agent", "code_agent"]

class PlanStep(BaseModel):

    agent : AgentName
    task : str

class SelectedPlan(BaseModel):

    decision: Literal["route","clarify"]

    selected_agents : list[AgentName]
    plan : list[PlanStep]

    clarification_question : str