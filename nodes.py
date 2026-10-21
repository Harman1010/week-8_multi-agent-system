from concurrent.futures import ThreadPoolExecutor

from state import AgentState

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate

from utils.config import settings

from utils.prompts import (SUPERVISOR_PROMPT,FAQ_PROMPT,RESEARCH_PROMPT,CODE_AGENT,
FINAL_RESPONSE_PROMPT)

from schemas.supervisor import SelectedPlan

from utils.helpers import get_task_name,load_faq

from utils.research import search_wikipedia,search_arxiv,search_duckduckgo

import json

from utils.helpers import is_retryable_error

llm = ChatGoogleGenerativeAI(
    model = settings.model_name,
    google_api_key = settings.gemini_api_key,
    temperature=0
)

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
        "status": "validated"
    }

structured_llm = llm.with_structured_output(SelectedPlan)

def is_vague_query(query: str) -> bool:

    vague_patterns = [
        "tell me about it",
        "explain it",
        "what about it",
        "help me with this",
        "what is this",
        "explain this",
        "tell me more",
    ]

    query_lower = query.lower().strip()

    return any(
        pattern in query_lower
        for pattern in vague_patterns
    )

def supervisor(state:AgentState):

    try:
        prompt = ChatPromptTemplate.from_template(
        SUPERVISOR_PROMPT)

        chain = prompt | structured_llm

        query = state["query"]

        response = chain.invoke({
            "query" : query
        })

        return {
            "selected_agents" : response.selected_agents,
            "plan" : [
                step.model_dump()
                for step in response.plan
            ],
            "status" : "task delegated",
            "decision" : response.decision,
            "clarification_question" : response.clarification_question
        }

    except Exception as e:

        return {
            "status": "failed",
            "errors": [str(e)]
        }


def research_agent(state: AgentState):

    agent = "research_agent"

    try:

        task = get_task_name(
            state,
            agent
        )

        with ThreadPoolExecutor(max_workers=3) as executor:

            wikipedia_future = executor.submit(
            search_wikipedia,
            task
        )

            arxiv_future = executor.submit(
                search_arxiv,
                task
            )

            duckduckgo_future = executor.submit(
                search_duckduckgo,
                task
            )

            wikipedia_result = wikipedia_future.result()
            arxiv_result = arxiv_future.result()
            duckduckgo_result = duckduckgo_future.result()

        context = f"""
    Wikipedia:
    {wikipedia_result}

    ArXiv:
    {arxiv_result}

    DuckDuckGo:
    {duckduckgo_result}
    """
        error = f"{agent} : All research sources failed."
        if (
            not wikipedia_result
            and not arxiv_result
            and not duckduckgo_result
        ):

            return {
                "agent_statuses": {agent : "failed"},
                "agent_errors" : {agent : error},
                "errors" : [error] 
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
            "results" : {agent : response.content.strip()},
            "agent_statuses" : {agent : "succeeded"},
            "agent_errors" : {agent : ""},

        }
    
    except Exception as e:

        error = f"{agent} : {str(e)}"
    
        return {
            "agent_statuses" : {agent : "failed"},
            "agent_errors" : {agent : error},
            "errors": [error]
        }
    
def code_agent(state: AgentState):

    agent = "code_agent"

    try:
        task = get_task_name(state,agent)

        prompt = ChatPromptTemplate.from_template(
            CODE_AGENT
        )

        chain = prompt | llm

        response = chain.invoke({
            "task" : task
        })

        return {
            "results" : {
                agent : response.content.strip()
            },
            "agent_statuses" : {agent : "succeeded"},
            "agent_errors" : {agent : ""},

        }

    except Exception as e:

        error = f"{agent} : {str(e)}"

        return {
            "agent_statuses" : {agent : "failed"},
            "agent_errors" : {agent : error},
            "errors": [error]
        }

def final_response(state: AgentState):

    results = state.get("results", {})
    selected_agents = state.get("selected_agents", [])

    if state.get("status") == "failed":
        return {
            "answer": "There was an issue with the delegation. Please try again.",
            "status": "completed"
        }

    if state.get("status") == "recovery_failed":
        return {
            "answer": (
                "The request could not be completed because "
                "one or more agents failed and recovery was unsuccessful."
            ),
            "status": "completed"
        }

    if not results:
        return {
            "answer": "I was unable to generate an answer as no agent produced a result",
            "status": "completed"
        }

    if len(selected_agents) == 1 and selected_agents[0] in results:
        agent = selected_agents[0]
        return {
            "answer": results[agent],
            "status": "completed"
        }

    try:
        prompt = ChatPromptTemplate.from_template(FINAL_RESPONSE_PROMPT)
        chain = prompt | llm

        response = chain.invoke({
            "query": state["query"],
            "results": results
        })

        return {
            "answer": response.content.strip(),
            "status": "completed"
        }

    except Exception as e:
        print("Final Response Error", repr(e))

        return {
            "answer": "The system completed the agent processing but was unable to generate the final response.",
            "status": "completed",
            "errors": [str(e)]
        }

def faq_agent(state:AgentState):

    agent = "faq_agent"

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
                agent : response.content.strip()
            },
            "agent_statuses" : {agent : "succeeded"},
            "agent_errors" : {agent : ""}
        }

    except Exception as e:

        error = f"{agent} : {str(e)}"

        return {
            "agent_statuses" : {agent :"failed"},
            "agent_errors" : {agent : error},
            "errors": [error]
        }

def validate_results(state: AgentState):

    selected_agents = state.get("selected_agents", [])
    agent_statuses = state.get("agent_statuses", {})

    failed_agents = []

    successful_agents = []

    for agent in selected_agents:

        if agent_statuses.get(agent) != "succeeded":

            failed_agents.append(agent)

        else:

            successful_agents.append(agent)

    if not failed_agents:

        status = "validated_results"

    elif successful_agents:

        status = "partial_failure"

    else:

        status = "failed"

    return {
        "failed_agents" : failed_agents,
        "status" : status
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

    agent_errors = state.get(
        "agent_errors",
        {}
    )

    if not failed_agents or recovery_iterations >= MAX_RECOVERY_ATTEMPTS:

        return {
            "status" : "recovery_failed"
        }

    retry_agents = []

    for agent in failed_agents:

        error = agent_errors.get(agent,"")

        if error and is_retryable_error(error):
            retry_agents.append(agent)

    if not retry_agents:
        return {
            "status" : "recovery_failed"
        }


    return {
        "retry_agents": retry_agents,
        "recovery_iterations": recovery_iterations + 1,
        "status": "retrying"
    }