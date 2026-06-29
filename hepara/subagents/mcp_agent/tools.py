from typing import List
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from .subagents import create_subagents

subagents = create_subagents()

def create_agent_tools() -> List[AgentTool] | None:
    agent_tools: List[AgentTool] = []
    if subagents:
        for subagent in subagents:
            agent_tools.append(AgentTool(subagent))
        return agent_tools
    else:
        return None

def list_mcp_servers():
    if subagents is None:
        return "No available MCP servers."

    server_names = ""
    for subagent in subagents:
        name = subagent.name
        server_names += f"{name}\n"
    return server_names

async def list_mcp_tools(name: str):
    if subagents is None:
        return "No available MCP servers."

    valid_names = [subagent.name for subagent in subagents]
    if name not in valid_names:
        return f"{name} is not a valid MCP server."

    mcp_toolsets = []
    for subagent in subagents:
        if subagent.name == name:
            mcp_toolsets = [
                tool for tool in subagent.tools if isinstance(tool, McpToolset)
            ]
            break

    if not mcp_toolsets:
        return f"No tool for MCP server: {name}."

    tool_names = []
    for toolset in mcp_toolsets:
        try:
            available_tools = await toolset.get_tools()
        except Exception as exc:
            return f"Could not list tools for MCP server {name}: {exc}"
        tool_names.extend(tool.name for tool in available_tools)

    if not tool_names:
        return f"No tool for MCP server: {name}."
    return "\n".join(tool_names) + "\n"
