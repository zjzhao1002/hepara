import os
from pathlib import Path
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .tools import create_mcp_toolset_list, list_mcp_servers_from_file
from .prompt import MCP_AGENT_PROMPT

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")
model = GOOGLE_MODEL if GOOGLE_MODEL else "gemini-2.5-flash"

def get_mcp_list_path() -> Path:
    configured_path = os.getenv("MCP_LIST_PATH")
    if configured_path:
        path = Path(configured_path).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path
    return PROJECT_ROOT / "mcp_list.json"


def list_mcp_servers() -> str:
    return list_mcp_servers_from_file(get_mcp_list_path())


list_mcp_servers_tool = FunctionTool(func=list_mcp_servers)
mcp_tools = create_mcp_toolset_list(get_mcp_list_path())

all_tools = [list_mcp_servers_tool] + mcp_tools

mcp_agent = Agent(
    model=model,
    name="mcp_agent",
    description="A MCP manager to call tools from external MCP servers.",
    tools=all_tools, # type: ignore
    instruction=MCP_AGENT_PROMPT
) if mcp_tools else None
