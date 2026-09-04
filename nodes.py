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

    try:

        task = get_task_name(
            state,
            "research_agent"
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
            "errors": [f"research_agent: {str(e)}"]
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
            "errors": [f"code_agent: {str(e)}"]
        }

def final_response(state: AgentState):

    results = state.get("results",{})

    selected_agents = state.get("selected_agents",[])

    if len(selected_agents) == 1 and selected_agents[0] in results:

        agent = selected_agents[0]

        return {
            "answer" : results[agent],
            "status" : "completed"
        }

    if state.get("status") == "recovery_failed":

        errors = state.get("errors", [])

        if errors:
            return {
                "answer": (
                    "The request could not be completed because "
                    "the agent encountered a non-retryable error."
                ),
                "status": "completed"
            }

        return {
            "answer": "The request could not be completed.",
            "status": "completed"
        }

    if not results:

        return {
            "answer" : "I was unable to generate an answer as no agent produced a result",
            "status" : "completed"
        }


    try:
        
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

    except Exception as e:

        print("Final Response Error",repr(e))

        return {
            "answer" : "The system completed the agent processing but was unable to generate the final response.",
            "status" : "completed",
            "errors" : [str(e)]
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
            "errors": [f"faq_agent: {str(e)}"]
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

    errors = state.get(
        "errors",
        []
    )

    if not failed_agents or recovery_iterations >= MAX_RECOVERY_ATTEMPTS:

        return {
            "status" : "recovery_failed"
        }

    retry_agents = []

    for agent in failed_agents:

        for error in errors:

            if is_retryable_error(error):

                retry_agents.append(agent)

                break

    if not retry_agents:

        return {
            "status" : "recovery_failed"
        }

    retry_agents = []

    for agent in failed_agents:

        agent_errors = [
            error
            for error in errors
            if error.startswith(f"{agent}:")
        ]

        for error in agent_errors:

            if is_retryable_error(error):

                retry_agents.append(agent)
                break

    if not retry_agents:

        return {
            "status": "recovery_failed"
        }

    return {
        "retry_agents": retry_agents,
        "recovery_iterations": recovery_iterations + 1,
        "status": "retrying"
    }