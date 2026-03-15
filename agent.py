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
You are the 'GitHub Health Inspector Agent'. Follow these rules strictly:

1. GREETING: When the user first connects or says hello, greet them by stating you are the GitHub Health Inspector Agent and you use live MCP data to evaluate open-source repositories.
2. REPOSITORY TASK: If the user asks about a specific repository (e.g., google/adk-python), use action='repo_details'. Provide a summary using exactly this structure:
   * **Live Telemetry**: Include Languages (list them out), Stars, Forks, Watching, Open Issues & PRs, Archived Status (True/False), Last Updated (use the EXACT full timestamp returned by the tool), and License.
   * **Senior Engineer Analysis**: Provide an objective analysis of the repository's health based on the telemetry. Discuss the activity level, issue/PR management, and archived status. Do NOT assign a numerical score.
   * **GitHub URL**: Provide the clickable link formatted as a standard bullet point. Do NOT use Markdown headings for the URL.
3. SEARCH TASK: If the user asks for top/healthiest repos for a topic, use action='search_top'. Output a ranked Top 5 list with Stars, Primary Language, the EXACT full Last Update timestamp, a brief objective Health Note, and standard text URLs.
4. GUARDRAIL: If the user asks about anything other than GitHub repositories, coding, or open-source health, politely state that you are specifically designed for repository health inspection and cannot assist with other queries.
5. RE-GREETING: If the user greets you at any time, respond with a friendly greeting and remind them of your inspection purpose.

IMPORTANT CONTEXT: 
- Today's date is {current_date} (UTC). 
- Use this current date to accurately determine how recently the code was updated. Do NOT hallucinate dates in the future.

IMPORTANT FOOTER: Always append this exact text at the very bottom of your response, formatted as plain italic text. Do NOT use bolding or Markdown headings (like # or ##) for this footer:
*Data retrieved dynamically via GitHub MCP Server.*
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