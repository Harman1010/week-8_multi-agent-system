from unittest.mock import MagicMock, patch
from nodes import faq_agent,supervisor


@patch("nodes.load_faq")
@patch("nodes.ChatPromptTemplate.from_template")
def test_faq_agent(mock_from_template, mock_load_faq):
    mock_load_faq.return_value = {
        "hours": "Open 9 AM to 5 PM"
    }

    mock_response = MagicMock()
    mock_response.content = "  The hours are 9 AM to 5 PM  "

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response

    mock_prompt = MagicMock()
    mock_prompt.__or__.return_value = mock_chain
    mock_from_template.return_value = mock_prompt

    state = {
        "plan": [
            {
                "agent": "faq_agent",
                "task": "Find the opening hours"
            }
        ]
    }

    result = faq_agent(state)

    assert result["results"]["faq_agent"] == "The hours are 9 AM to 5 PM"
    assert result["agent_statuses"]["faq_agent"] == "succeeded"
    assert result["agent_errors"]["faq_agent"] == ""


from unittest.mock import patch
from nodes import research_agent


@patch("nodes.search_duckduckgo")
@patch("nodes.search_arxiv")
@patch("nodes.search_wikipedia")
def test_research_agent_failure(
    mock_wikipedia,
    mock_arxiv,
    mock_duckduckgo
):
    mock_wikipedia.return_value = ""
    mock_arxiv.return_value = ""
    mock_duckduckgo.return_value = ""

    state = {
        "plan": [
            {
                "agent": "research_agent",
                "task": "Research artificial intelligence"
            }
        ]
    }

    result = research_agent(state)

    assert result["agent_statuses"]["research_agent"] == "failed"
    assert result["agent_errors"]["research_agent"] == (
        "research_agent : All research sources failed."
    )
    assert result["errors"] == [
        "research_agent : All research sources failed."
    ]


from unittest.mock import MagicMock, patch
from nodes import code_agent


@patch("nodes.ChatPromptTemplate.from_template")
def test_code_agent_success(mock_from_template):
    mock_response = MagicMock()
    mock_response.content = "  print('Hello, World!')  "

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response

    mock_prompt = MagicMock()
    mock_prompt.__or__.return_value = mock_chain
    mock_from_template.return_value = mock_prompt

    state = {
        "plan": [
            {
                "agent": "code_agent",
                "task": "Write a Python hello world program"
            }
        ]
    }

    result = code_agent(state)

    assert result["results"]["code_agent"] == "print('Hello, World!')"
    assert result["agent_statuses"]["code_agent"] == "succeeded"
    assert result["agent_errors"]["code_agent"] == ""


from unittest.mock import patch
from nodes import supervisor


@patch("nodes.ChatPromptTemplate.from_template")
def test_supervisor_failure(mock_from_template):
    mock_from_template.side_effect = Exception("LLM unavailable")

    state = {
        "query": "Explain artificial intelligence"
    }

    result = supervisor(state)

    assert result["status"] == "failed"
    assert result["errors"] == ["LLM unavailable"]

