from state import AgentState

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate

from utils.config import settings

from utils.prompts import (QUERY_TRANSFORMATION_PROMPT,SUPERVISOR_PROMPT,FAQ_PROMPT,RESEARCH_PROMPT,CODE_AGENT,
FINAL_RESPONSE_PROMPT)

from schemas.supervisor import SelectedPlan

from utils.helpers import get_task_name,load_faq

from utils.research import search_wikipedia,search_arxiv,search_duckduckgo

import json

llm = ChatGoogleGenerativeAI(
    model = settings.model_name,
    google_api_key = settings.gemini_api_key,
    temperature=0
)

def transform_query(state:AgentState) -> dict:

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

    try:
        task = get_task_name(
            state,
            "research_agent"
        )

        wikipedia_result = search_wikipedia(task)
        arxiv_result = search_arxiv(task)
        duckduckgo_result = search_duckduckgo(task)

        context = f"""
Wikipedia:
{wikipedia_result}

ArXiv:
{arxiv_result}

DuckDuckGo:
{duckduckgo_result}
"""

        # Check whether all sources failed
        if (
            not wikipedia_result
            and not arxiv_result
            and not duckduckgo_result
        ):

            return {
                "failed_agents": ["research_agent"],
                "errors": ["All research sources failed."]
            }

        prompt = ChatPromptTemplate.from_template(
            RESEARCH_PROMPT
        )

        chain = prompt | llm

        response = chain.invoke({
            "task": task,
            "context": context
        })

        return {
            "results": {
                "research_agent": response.content.strip()
            }
        }

    except Exception as e:

        return {
            "failed_agents": ["research_agent"],
            "errors": [str(e)]
        }
    
def code_agent(state: AgentState):

    try:
        task = get_task_name(state,"code_agent")

        prompt = ChatPromptTemplate.from_template(
            CODE_AGENT
        )

        chain = prompt | llm

        response = chain.invoke({
            "task" : task
        })

        return {
            "results" : {
                "code_agent" : response.content.strip()
            }
        }

    except Exception as e:

        return {
            "failed_agents": ["code_agent"],
            "errors": [str(e)]
        }

def final_response(state: AgentState):

    prompt = ChatPromptTemplate.from_template(
        FINAL_RESPONSE_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke({
        "query": state["query"],
        "results": state["results"]
    })

    return {
        "answer": response.content.strip(),
        "status": "completed"
    }

def faq_agent(state:AgentState):

    try:

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

    except Exception as e:

        return {
            "failed_agents": ["faq_agent"],
            "errors": [str(e)]
        }

def validate_results(state: AgentState):

    selected_agents = state.get("selected_agents", [])
    results = state.get("results", {})

    successful_agents = list(results.keys())

    all_agents_succeeded = all(
        agent in successful_agents
        for agent in selected_agents
    )

    if all_agents_succeeded:

        return {
            "status": "validated_results"
        }

    if results:

        return {
            "status": "partial_failure"
        }

    return {
        "status": "failed"
    }

MAX_RECOVERY_ATTEMPTS = 2


def recovery_node(state: AgentState):

    recovery_iterations = state.get(
        "recovery_iterations",
        0
    )

    failed_agents = state.get(
        "failed_agents",
        []
    )

    if not failed_agents or recovery_iterations >= MAX_RECOVERY_ATTEMPTS:

        return {
            "status" : "recovery_failed"
        }

    return {
        "retry_agents": failed_agents,
        "recovery_iterations": recovery_iterations + 1,
        "status": "retrying"
    }