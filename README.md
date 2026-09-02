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
- Query Transformation - Transforms user queries before task planning and delegation.
- Input Guardrails - Performs basic validation and filtering of user queries.
- Result Validation - Validates whether the selected agents successfully produced results.
- Recovery Mechanism - Retries failed agents up to a defined recovery limit.
- Multi-Agent Routing - Routes tasks dynamically based on the supervisor's selected agents.

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
    ├── Invalid ──► Final Response / Rejection
    │
    ▼
Query Transformation
    │
    ▼
Supervisor
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

2. Add .env file (refer to .env.example) and add your API Key

3. Run the backend

```powershell

uvicorn backend.main:app

```

4. Run the frontend

- Live Server (not recommended since it reloads automatically)
- Open integrated browser from "frontend/index.html" if using VS Code or similar editor

---

## Limitations

- Lack streaming response
- Guardrails are not strict
- Authentication / Authorization not yet implemented

---