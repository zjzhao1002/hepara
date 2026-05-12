# Project Overview
HEP-AI-Assistant is a research assistant specialized in High Energy Physics (HEP). It is built using the `google-adk` framework and leverages Gemini models (e.g., `gemini-2.5-flash`) to answer user questions and perform searches using integrated tools like Google Search.

## Technologies
- **Language:** Python 3.13+
- **Framework:** `google-adk` (Google Agent Development Kit)
- **Model:** Gemini 2.5 Flash
- **Tools:** Google Search
- **Environment Management:** `uv`

# Building and Running
The project uses `uv` for dependency management.

## Installation
```bash
uv sync
```

## Running the Assistant
The entry point for the application is `main.py`. It runs the agent in an `InMemoryRunner`.
```bash
uv run main.py
```

## Configuration
The project uses `.env` files for environment variables (e.g., API keys). Ensure you have a `.env` file in the root directory.

# Architecture
- `main.py`: The entry point that initializes the environment and runs the `root_agent`.
- `hepara/agent.py`: Defines the `root_agent` (coordinator) which orchestrates sub-agents.
- `hepara/subagents/`: Contains specialized agents:
    - `arxiv_agent`: Monitors arXiv for trends.
    - `inspirehep_agent`: Tracks user citations and searches for papers on INSPIRE-HEP.
- `hepara/`: Main package containing agent definitions and ADK-related artifacts (`.adk/`).

# Development Conventions
- **Agent Definition:** New agents or modifications to existing ones should be done in `hepara/agent.py`.
- **Framework Usage:** Follow `google-adk` patterns for agent creation and tool integration.
- **Asynchronous Code:** Use `asyncio` for running agents and handling tool calls.

# License
This project is licensed under the MIT License. See the `LICENSE` file for full details.
