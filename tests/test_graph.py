from unittest.mock import MagicMock, patch
import graph as graph_module


def test_graph_successful_faq_flow(monkeypatch):
    def fake_supervisor(state):
        return {
            "selected_agents": ["faq_agent"],
            "plan": [
                {
                    "agent": "faq_agent",
                    "task": "Find the opening hours"
                }
            ],
            "status": "task delegated",
            "decision": "route",
            "clarification_question": ""
        }

    def fake_faq_agent(state):
        return {
            "results": {
                "faq_agent": "We are open from 9 AM to 5 PM."
            },
            "agent_statuses": {"faq_agent": "succeeded"},
            "agent_errors": {"faq_agent": ""}
        }

    def fake_final_response(state):
        return {
            "answer": "We are open from 9 AM to 5 PM.",
            "status": "completed"
        }

    monkeypatch.setattr(
        graph_module, "supervisor", fake_supervisor
    )
    monkeypatch.setattr(
        graph_module, "faq_agent", fake_faq_agent
    )
    monkeypatch.setattr(
        graph_module, "final_response", fake_final_response
    )

    graph = graph_module.create_graph()

    result = graph.invoke({
        "query": "What are your opening hours?"
    })

    assert result["answer"] == "We are open from 9 AM to 5 PM."
    assert result["status"] == "completed"
    assert result["agent_statuses"]["faq_agent"] == "succeeded"


import graph as graph_module
import nodes as nodes_module


def test_graph_recovers_after_retryable_agent_failure(monkeypatch):
    calls = {"research_agent": 0}

    def fake_supervisor(state):
        return {
            "selected_agents": ["research_agent"],
            "plan": [
                {
                    "agent": "research_agent",
                    "task": "Research artificial intelligence",
                }
            ],
            "status": "task delegated",
            "decision": "route",
            "clarification_question": "",
        }

    def fake_research_agent(state):
        calls["research_agent"] += 1

        # First attempt fails; the retry succeeds.
        if calls["research_agent"] == 1:
            error = "research_agent : Temporary API failure"
            return {
                "agent_statuses": {"research_agent": "failed"},
                "agent_errors": {"research_agent": error},
                "errors": [error],
            }

        return {
            "results": {
                "research_agent": "AI research findings recovered successfully."
            },
            "agent_statuses": {"research_agent": "succeeded"},
            "agent_errors": {"research_agent": ""},
        }

    # Keep the real recovery_node, but make the simulated error retryable.
    monkeypatch.setattr(
        nodes_module,
        "is_retryable_error",
        lambda error: True,
    )

    monkeypatch.setattr(graph_module, "supervisor", fake_supervisor)
    monkeypatch.setattr(
        graph_module,
        "research_agent",
        fake_research_agent,
    )

    graph = graph_module.create_graph()

    result = graph.invoke({
        "query": "Research artificial intelligence"
    })

    # The agent ran once, failed, and then succeeded on retry.
    assert calls["research_agent"] == 2

    # Recovery was attempted exactly once.
    assert result["recovery_iterations"] == 1

    # The latest agent status and error should reflect success.
    assert result["agent_statuses"]["research_agent"] == "succeeded"
    assert result["agent_errors"]["research_agent"] == ""
    assert result["failed_agents"] == []

    # The graph should finish normally with the recovered result.
    assert result["status"] == "completed"
    assert result["answer"] == (
        "AI research findings recovered successfully."
    )
