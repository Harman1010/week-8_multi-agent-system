from utils.helpers import is_retryable_error

from utils.helpers import get_task_name

from nodes import validate_results

def test_connection():

    assert is_retryable_error("Connection time out") is True

def test_api_required():

    assert is_retryable_error("API required") is False

def test_rate_limit():

    assert is_retryable_error("429 too many requests") is True

def test_key_error():

    assert is_retryable_error("KeyError: answer") is False


def test_get_task_name_returns_matching_task():
    state = {
        "plan": [
            {"agent": "research_agent", "task": "Research AI trends"},
            {"agent": "code_agent", "task": "Write Python code"}
        ]
    }

    assert get_task_name(state, "research_agent") == "Research AI trends"


def test_get_task_name_raises_when_agent_missing():
    state = {
        "plan": [
            {"agent": "research_agent", "task": "Research AI trends"}
        ]
    }

    import pytest

    with pytest.raises(ValueError, match="No task found for agent"):
        get_task_name(state, "code_agent")