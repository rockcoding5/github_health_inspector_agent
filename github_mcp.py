import requests
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("GitHubHealthServer")

@mcp.tool()
def github_insights(action: str, repo_name: str = "", query: str = "") -> str:
    """
    Fetches live GitHub repository health data.
    action: MUST be 'repo_details' or 'search_top'
    repo_name: e.g., 'google/adk-python' (required if action is repo_details)
    query: e.g., 'language:python topic:machine-learning' (required if action is search_top)
    """
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "MCP-Health-Inspector"}
    
    if action == "repo_details":
        # 1. Fetch main repo details
        url = f"https://api.github.com/repos/{repo_name}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200: return f"Error: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # 2. Fetch the language breakdown safely
        langs_url = f"https://api.github.com/repos/{repo_name}/languages"
        langs_resp = requests.get(langs_url, headers=headers)
        languages_list = ["Unknown"]
        if langs_resp.status_code == 200:
            langs_dict = langs_resp.json()
            if langs_dict:
                languages_list = list(langs_dict.keys())[:3]
                
        return str({
            "name": data.get("full_name"),
            "languages": languages_list,
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watching": data.get("subscribers_count"),
            "open_issues_and_prs": data.get("open_issues_count"),
            "is_archived": data.get("archived", False),
            "last_updated": data.get("updated_at"),
            "license": data.get("license", {}).get("name") if data.get("license") else "None",
            "url": data.get("html_url")
        })
        
    elif action == "search_top":
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200: return f"Error: {resp.status_code}"
        items = resp.json().get("items", [])
        results = [{"name": i.get("full_name"), "primary_language": i.get("language"), "stars": i.get("stargazers_count"), "last_updated": i.get("updated_at"), "url": i.get("html_url")} for i in items]
        return str(results)
        
    return "Error: Invalid action."

if __name__ == "__main__":
    mcp.run(transport="stdio")