from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
from .subagents.citations_tracker.agent import citations_tracker
from .subagents.arxiv_tracker.agent import arxiv_tracker
from .subagents.inspirehep_agent.agent import inspirehep_agent
from .prompt import HEP_COORDINATOR_PROMPT

hep_coordinator = Agent(
    model='gemini-2.5-flash',
    name='hep_coordinator',
    description="""
        You are a research assistant in High Energy Physics, 
        tracking citations of user, locating current papers, 
        and providing research advices.
    """,
    instruction=HEP_COORDINATOR_PROMPT,
    tools=[AgentTool(citations_tracker), AgentTool(arxiv_tracker), AgentTool(inspirehep_agent)],
)

