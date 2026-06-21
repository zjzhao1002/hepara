import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .prompt import PDG_AGENT_PROMPT

GOOGLE_MODEL = os.getenv("GOOGLE_MODEL") 
model = GOOGLE_MODEL if GOOGLE_MODEL else "gemini-2.5-flash"

pdg_agent = Agent(
    model=model,
    name='pdg_agent',
    description='A helpful assistant to retrieve data from PDG.',
    instruction=PDG_AGENT_PROMPT,
    # tools=[get_author_citations_tool, get_paper_citations_tool, track_citations_updates_tool, search_papers_tool],
    output_key="pdg_report"
)