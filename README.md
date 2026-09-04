## Welcome to Multi-Agent System.

This project helps user to query and re-directs to suitable agent to solve it.

PS : You can ask FAQ questions regarding this project itself to gain insights!

Agents available :-

1. FAQ Agent
2. Research Agent
3. Code Agent

---

## Features

- Agentic AI System - Uses multiple specialized agents to handle different types of queries.
- Supervisor Agent - Plans tasks and delegates them to the appropriate specialized agents.
- Query Clarification - Detects vague or ambiguous queries and asks the user to provide a clearer query before execution.
- Input Guardrails - Performs basic validation and filtering of user queries.
- Result Validation - Validates whether the selected agents successfully produced results.
- Recovery Mechanism - Retries failed agents up to a defined recovery limit.
- Multi-Agent Routing - Routes tasks dynamically based on the supervisor's selected agents.
- Efficient Response Handling - Single-agent queries return the agent's validated result directly, avoiding an unnecessary final LLM call. Multi-agent results are synthesized when required.

---

## Tech Stack

### Core/AI

- LLM Model(s) : "gemini-2.5-flash"
- AI Framework(s) : LangChain,LangGraph

### Backend

- FastAPI
- Pydantic Validation

### Frontend

- HTML5
- CSS
- JavaScript

## Architecture

```text

User Query
    │
    ▼
Input Validation
    │
    ├── Invalid ──► Rejection
    │
    ▼
Supervisor
    │
    ├── Clarify ──► Clarification Response ──► END
    │
    ▼
Task Planning & Agent Delegation
    │
    ├───────────────┬───────────────┐
    ▼               ▼               ▼
FAQ Agent      Research Agent    Code Agent
    │               │               │
    └───────────────┼───────────────┘
                    ▼
             Result Validation
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
      Success          Partial / Failed
          │                    │
          ▼                    ▼
    Final Response       Recovery Node
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
                Retry Agents       Recovery Failed
                     │                   │
                     └─────────┬─────────┘
                               ▼
                         Final Response
                               │
                               ▼
                              END

```

---


## Project Structure

```text
project/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── schema.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── schemas/
│   ├── __init__.py
│   └── supervisor.py
│
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── prompts.py
│   ├── helpers.py
│   └── research.py
│
├── state.py
├── nodes.py
├── graph.py
|── test.py
│
├── .env.example
├── requirements.txt
└── README.md

```

---


## Setup Guide

1. Clone the repository

2. Add `.env` file (refer to `.env.example`) and add your API Key.

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run the application

```powershell
uvicorn backend.main:app --reload
```

5. Open the application at:

http://127.0.0.1:8000

---

## Limitations

- Lack streaming response
- Guardrails are not strict
- Authentication / Authorization not yet implemented

---