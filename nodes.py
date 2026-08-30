from state import AgentState

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate

from utils.config import settings

from utils.prompts import QUERY_TRANSFORMATION_PROMPT,SUPERVISOR_PROMPT,FAQ_PROMPT

from schemas.supervisor import SelectedPlan

from utils.helpers import get_task_name,load_faq

import json

llm = ChatGoogleGenerativeAI(
    model = settings.model_name,
    google_api_key = settings.gemini_api_key,
    temperature=0
)

def transform_query(state:AgentState) -> str:

    prompt = ChatPromptTemplate.from_template(
        QUERY_TRANSFORMATION_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke({
        "query" : state["query"]
    })

    transformed_query = response.content.strip()

    return {
        "transformed_query" : transformed_query,
        "status" : "query transformed"
    }

def validate_input(state:AgentState):

    query = state["query"].strip()

    if not query:

        return {
            "status" : "rejected",
            "answer" : "Please enter a valid query"
        }

    if len(query) > 1000:

        return {
            "status" : "rejected",
            "answer" : "The query is too long, keep it within 1000 characters"
        }

    invalid_queries = ["ignore previous instructions","how to hack","give me system prompt","reveal database"]

    for invalid in invalid_queries:

        if invalid in query.lower():

            return {
                "status" : "rejected",
                "answer" : "Prompt injection detected!"
            }

    return {
        "status" : "validated"
    }

structured_llm = llm.with_structured_output(SelectedPlan)

def supervisor(state:AgentState):

    prompt = ChatPromptTemplate.from_template(
        SUPERVISOR_PROMPT)

    chain = prompt | structured_llm

    response = chain.invoke({
        "query" : state["transformed_query"]
    })

    return {
        "selected_agents" : response.selected_agents,
        "plan" : [
            step.model_dump()
            for step in response.plan
        ],
        "status" : "task delegated"
    }


def research_agent(state: AgentState):

    return {
        "results": {
            "research_agent": "Research agent executed"
        }
    }


def code_agent(state: AgentState):

    return {
        "results": {
            "code_agent": "Code agent executed"
        }
    }

def final_response(state: AgentState):

    return {
        "answer": str(state["results"]),
        "status": "completed"
    }

def faq_agent(state:AgentState):

    task = get_task_name(state,"faq_agent")

    faq_data = load_faq()

    context = json.dumps(
        faq_data,indent=2
    )

    print("TASK:")
    print(task)

    print("\nCONTEXT:")
    print(context)

    prompt = ChatPromptTemplate.from_template(
        FAQ_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke({
        "task" : task,
        "context" : context
    })

    return {
        "results": {
            "faq_agent": response.content.strip()
        }
    }

