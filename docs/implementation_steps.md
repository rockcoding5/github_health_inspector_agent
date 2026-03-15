# GitHub Health Inspector Agent – Implementation Steps

## Step 1: Environment & API Setup

Run the following commands to prepare the Google Cloud environment.

### Set Project ID and Region

```bash
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
```

### Enable Required APIs

```bash
gcloud services enable \
run.googleapis.com \
artifactregistry.googleapis.com \
cloudbuild.googleapis.com \
aiplatform.googleapis.com \
compute.googleapis.com
```

### Create Project Directory

```bash
cd ~ && mkdir github_health_inspector_agent && cd github_health_inspector_agent
```

### Setup Python Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

---

# Step 2: Create Project Files

## requirements.txt

```bash
cat <<EOF > requirements.txt
google-adk==1.14.0
python-dotenv==1.0.1
google-cloud-logging==3.11.0
mcp>=1.8.0
requests>=2.32.4
EOF

uv pip install -r requirements.txt
```

## .env Configuration

```bash
SA_NAME=mcp-service-auth

cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL="gemini-2.5-flash"
GOOGLE_GENAI_USE_VERTEXAI=1
EOF
```

## **init**.py

```bash
echo "from . import agent" > __init__.py
```

---

# Step 3: Identity & IAM Permissions

Create the service account.

```bash
gcloud iam service-accounts create mcp-service-auth \
--display-name="MCP Project Service Account"
```

Grant Vertex AI access.

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:mcp-service-auth@$PROJECT_ID.iam.gserviceaccount.com" \
--role="roles/aiplatform.user"
```

---

# Step 4: Deployment

Deploy the agent to Cloud Run.

```bash
source .env

uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
--project=$PROJECT_ID \
--region=$REGION \
--service_name=github-health-inspector-agent \
--app_name=github_health_inspector_agent \
--with_ui \
. \
-- \
--service-account=$SERVICE_ACCOUNT \
--set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=1,MODEL=gemini-2.5-flash"
```

---

# Step 5: Testing Inputs

| # | User Input | Expected Response (Approximate) |
| :--- | :--- | :--- |
| 1 | `"Hello"` | "Hello! I am the GitHub Health Inspector Agent, and I use live MCP data to evaluate open-source repositories." |
| 2 | `"Can you run a health check on the openai/openai-python repo?"` | **Repository:** openai/openai-python<br><ul><li>**GitHub URL:** https://github.com/openai/openai-python</li><li>**Live Telemetry:**<ul><li>Languages: Python, Shell, Dockerfile</li><li>Stars: 30254</li><li>Forks: 4638</li><li>Watching: 348</li><li>Open Issues & PRs: 331</li><li>Archived Status: False</li><li>Last Updated: 2026-03-15T19:54:52Z</li><li>License: Apache License 2.0</li></ul></li><li>**Senior Engineer Analysis:** This repository displays robust health metrics. Its impressive star count and significant number of forks are indicative of strong community adoption and a thriving ecosystem...</li></ul>*Data retrieved dynamically via GitHub MCP Server.* |
| 3 | `"Tell me a joke."` | "I'm sorry, but I am specifically designed to act as a GitHub Health Inspector Agent and evaluate open-source repositories. I cannot tell jokes or assist with queries outside of this scope." |
| 4 | `"what are the top 3 mcp server github repos with python"` | Here are the top 3 MCP server GitHub repos with Python:<br><br>1. **PrefectHQ/fastmcp**<br>Stars: 23697<br>Primary Language: Python<br>Last Updated: 2026-03-15T20:51:56Z<br>Health Note: Highly popular and very actively maintained, with continuous recent development.<br>URL: https://github.com/PrefectHQ/fastmcp<br><br>2. **oraios/serena**<br>Stars: 21551<br>Primary Language: Python<br>Last Updated: 2026-03-15T22:07:06Z<br>Health Note: Very popular and actively maintained.<br>URL: https://github.com/oraios/serena<br><br>3. **BeehiveInnovations/pal-mcp-server**<br>Stars: 11252<br>Primary Language: Python<br>Last Updated: 2026-03-15T19:01:59Z<br>Health Note: Popular and actively maintained.<br>URL: https://github.com/BeehiveInnovations/pal-mcp-server<br><br>*Data retrieved dynamically via GitHub MCP Server.* |
| 5 | `"Fetch the live telemetry for the meta-llama/llama repo."` | **Repository:** meta-llama/llama<br><ul><li>**GitHub URL:** https://github.com/meta-llama/llama</li><li>**Live Telemetry:**<ul><li>Languages: Python, Shell</li><li>Stars: 59222</li><li>Forks: 9826</li><li>Watching: 536</li><li>Open Issues & PRs: 516</li><li>Archived Status: False</li><li>Last Updated: 2026-03-15T20:19:56Z</li><li>License: Other</li></ul></li><li>**Senior Engineer Analysis:** This repository demonstrates exceptional health and immense popularity. With over 59,000 stars and nearly 10,000 forks, it clearly signifies a project with widespread adoption...</li></ul>*Data retrieved dynamically via GitHub MCP Server.* |
| 6 | `"give me the top 3 repos under Artificial intelligence with python language"` | Here are the top 3 repositories under Artificial Intelligence with Python language:<br><br>1. **Significant-Gravitas/AutoGPT**<br>Stars: 182492<br>Primary Language: Python<br>Last Updated: 2026-03-15T22:16:38Z<br>Health Note: Exceptionally popular and highly active.<br>URL: https://github.com/Significant-Gravitas/AutoGPT<br><br>2. **hacksider/Deep-Live-Cam**<br>Stars: 80038<br>Primary Language: Python<br>Last Updated: 2026-03-15T21:44:44Z<br>Health Note: Very popular and actively maintained.<br>URL: https://github.com/hacksider/Deep-Live-Cam<br><br>3. **OpenHands/OpenHands**<br>Stars: 69160<br>Primary Language: Python<br>Last Updated: 2026-03-15T22:10:26Z<br>Health Note: Highly popular and very active.<br>URL: https://github.com/OpenHands/OpenHands<br><br>*Data retrieved dynamically via GitHub MCP Server.* |
| 7 | `"Check the telemetry for the apache/kafka repo."` | **Repository:** apache/kafka<br><ul><li>**GitHub URL:** https://github.com/apache/kafka</li><li>**Live Telemetry:**<ul><li>Languages: Java, Scala, Python</li><li>Stars: 32158</li><li>Forks: 15033</li><li>Watching: 1049</li><li>Open Issues & PRs: 330</li><li>Archived Status: False</li><li>Last Updated: 2026-03-15T19:57:29Z</li><li>License: Apache License 2.0</li></ul></li><li>**Senior Engineer Analysis:** The apache/kafka repository exhibits outstanding health and community engagement. With over 32,000 stars and an impressive 15,000+ forks, it's clear this is a highly influential project.</li></ul>*Data retrieved dynamically via GitHub MCP Server.* |
| 8 | `"Run a health analysis on the huggingface/transformers repo?"` | **Repository:** huggingface/transformers<br><ul><li>**GitHub URL:** https://github.com/huggingface/transformers</li><li>**Live Telemetry:**<ul><li>Languages: Python, Dockerfile, Makefile</li><li>Stars: 157860</li><li>Forks: 32489</li><li>Watching: 1187</li><li>Open Issues & PRs: 2311</li><li>Archived Status: False</li><li>Last Updated: 2026-03-15T21:56:05Z</li><li>License: Apache License 2.0</li></ul></li><li>**Senior Engineer Analysis:** The huggingface/transformers repository demonstrates an exceptional level of health and activity, indicative of a critical and highly influential project within the AI/ML domain.</li></ul>*Data retrieved dynamically via GitHub MCP Server.* |


![Accessing the Agent](Accessing_the_Agent_ADK_Web.png)