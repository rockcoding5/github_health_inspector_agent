import os
import sys
import logging
import datetime
import google.cloud.logging
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

# Setup Logging
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()
load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")

# Grab the current UTC date when the container spins up
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

instructions = f"""
You are the 'GitHub Health Inspector Agent'. You evaluate GitHub repositories to ensure they are safe for production use.
You MUST use the 'GitHubHealthServer' MCP tool to fetch real-time data.

Task 1: If the user asks about a specific repository (e.g., google/adk-python):
- Use action='repo_details'.
- Output a 'Live Telemetry' section (Stars, Issues, Last Updated, License).
- Provide a 'Senior Engineer Verdict' (Healthy/Caution).
- ALWAYS include the clickable GitHub URL.

Task 2: If the user asks for top/healthiest repos for a topic:
- Use action='search_top'.
- Output a ranked Top 5 list with Stars, Last Update, and a Health Note.
- ALWAYS include clickable URLs for each.

IMPORTANT CONTEXT: 
- Today's date is {current_date} (UTC). 
- When evaluating the 'Last Updated' timestamp, use this current date to accurately determine how recently the code was updated. Do NOT hallucinate or claim that recent dates are in the future.

IMPORTANT FOOTER: Always include this exact text at the bottom of your response:
"---"
"Data retrieved dynamically via GitHub MCP Server."
"""

# Resolve absolute path to ensure container execution stability
mcp_script_path = os.path.join(os.path.dirname(__file__), "github_mcp.py")

# Connect the ADK Agent via stdio using the absolute path and inheriting system environment
github_mcp_server = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[mcp_script_path],
            env=dict(os.environ)
        ),
        timeout=60,
    )
)

root_agent = Agent(
    name="github_health_inspector_agent",
    model=model_name,
    instruction=instructions,
    tools=[github_mcp_server]
)