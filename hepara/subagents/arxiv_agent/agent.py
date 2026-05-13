from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .prompt import ARXIV_TRACKER_PROMPT
from .tools import recommend_by_trends

recommend_by_trends_tool = FunctionTool(func=recommend_by_trends)

arxiv_agent = Agent(
    model='gemini-2.5-flash',
    name='arxiv_tracker',
    description="An arXiv tracker that can track the trending papers in the user's research field.",
    instruction=ARXIV_TRACKER_PROMPT,
    tools=[recommend_by_trends_tool],
    output_key="arxiv_report"
)
