from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from .subagents.inspirehep_agent.agent import inspirehep_agent
from .subagents.arxiv_agent.agent import arxiv_agent
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
    tools=[AgentTool(inspirehep_agent), AgentTool(arxiv_agent)],
)

