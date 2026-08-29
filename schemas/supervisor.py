from pydantic import BaseModel

class PlanStep(BaseModel):

    agent : str
    task : str

class SelectedPlan(BaseModel):

    selected_agents : list[str]
    plan : list[PlanStep]