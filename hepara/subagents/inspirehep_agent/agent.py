from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from .prompt import INSPIREHEP_AGENT_PROMPT
from dotenv import load_dotenv

load_dotenv()

inspirehep_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command = "uvx", 
            args = ["inspirehep-mcp"]
        )
    )
)

inspirehep_agent = Agent(
    model="gemini-2.5-flash",
    name="InspireHepAgent",
    description="You are an assistant for the InspireHEP MCP API. Use the tools provided to interact with the API.",
    instruction=INSPIREHEP_AGENT_PROMPT,
    tools=[inspirehep_toolset],
    output_key="inspirehep_report"
)