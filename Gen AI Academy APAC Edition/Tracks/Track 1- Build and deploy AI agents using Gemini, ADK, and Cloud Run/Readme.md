


# Project setup

-Sign-in to the Google Cloud Console

-Sign-in to the Google Cloud Console using a personal Google account.


# Enable Billing

-Set up a personal billing account

-If you set up billing using Google Cloud credits, you can skip this step.

-To set up a personal billing account, go here to enable billing in the Cloud Console.


# Create a project

<img width="449" height="62" alt="Image" src="https://github.com/user-attachments/assets/3cd8e8dc-a843-46e7-8b0f-2782024e9719" />

-click on new project

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/efd5df41-ce6f-4b45-9432-73c29ecbf5a7" />

-Enter project name 

-Choose Billing Account

-click on create

-copy project ID

<img width="454" height="298" alt="Image" src="https://github.com/user-attachments/assets/576abdca-3cdd-4174-bf66-13e2e18ae92e" />



# Open Cloud Shell Editor

-Click this link to navigate directly to Cloud Shell Editor

-If prompted to authorize at any point today, click Authorize to continue.Click to authorize Cloud Shell

<img width="235" height="125" alt="Image" src="https://github.com/user-attachments/assets/27545d38-51aa-4efe-a8d9-5ab2f66d9d47" />

-If the terminal doesn't appear at the bottom of the screen, open it:

- Click View
  
- Click Terminal

<img width="366" height="231" alt="Image" src="https://github.com/user-attachments/assets/44f2b515-9112-41a9-8725-a211bfbb5321" />

# Set your project

-In the terminal, set your project with this command:
```
gcloud config set project [PROJECT_ID]
```
-You should see this message:

Updated property [core/project].

 # Enable APIs
 
To use Cloud Run, Artifact Registry, Cloud Build, Vertex AI, and Compute Engine, you need to enable their respective APIs in your Google Cloud project.

In the terminal, enable the APIs
```
 gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com
```
When this finishes running, you should see an output like the following:

Operation "operations/acat.p2-830710432020-1605ff2c-71b8-4c88-bbdc-2fee76d3f21b" finished successfully.

# Prepare your development environment

1.In the terminal, create the project directory and the necessary subdirectories

```
cd && mkdir hotel_food_agent && cd hotel_food_agent
```

2.In the terminal, run the following command to open the  hotel_food_agent directory in the Cloud Shell Editor explorer:

```
cloudshell open-workspace ~/hotel_food_agent
```
# Install requirements

Run the following command in the terminal to create the requirements.txt file

```
cloudshell edit requirements.txt
```
Add the following into the newly created requirements.txt file

```
google-adk==1.14.0
langchain-community==0.3.27
wikipedia==1.4.0
```
In the terminal, create and activate a virtual environment using uv. This ensures your project dependencies don't conflict with the system Python.

```
uv venv
source .venv/bin/activate
```
Install the required packages into your virtual environment in the terminal.

```
uv pip install -r requirements.txt
```

# Set up environment variables
Use the following command in the terminal to create the .env file.

1. Set the variables in your terminal first

```
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=lab2-cr-service
```

2. Create the .env file using those variables
```
cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL="gemini-2.5-flash"
EOF
```
#  Create Agent Workflow

1.Create the init.py file by running the following in the terminal
```
cloudshell edit __init__.py
```
Add the following code to the new __init__.py file
```
from . import agent
```
Create the agent.py file

Create the main agent.py file by pasting the following command into the terminal.
```
cloudshell edit agent.py
```
Imports and Initial Setup: Add the following code to your currently empty agent.py file

```
import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# --- Setup Logging and Environment ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.5-flash")

# --- Helper tool: save user prompt into state ---
def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# --- Wikipedia Tool ---
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# --- Agents ---
# 1. Researcher Agent
food_researcher = Agent(
    name="food_researcher",
    model=model_name,
    description="Researches hotel food items and cuisines using Wikipedia.",
    instruction="""
    You are a helpful food researcher. Your goal is to fully answer the user's PROMPT.
    You have access to a tool for searching Wikipedia for general knowledge (facts, ingredients, cuisines, history).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by Wikipedia alone, use that tool.
    - If the prompt is complex, gather all necessary information.
    - Synthesize the results into preliminary data outputs.

    PROMPT:
    { PROMPT }
    """,
    tools=[wikipedia_tool],
    output_key="research_data"
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Summarizes hotel food research into a concise, user-friendly response.",
    instruction="""
    You are the friendly voice of the Hotel Food Summarizer.
    Your task is to take the RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - Present the key facts about the dish or cuisine.
    - Add interesting general facts from the research.
    - If some information is missing, just present what you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    { research_data }
    """
)

# Workflow: researcher → formatter
food_summary_workflow = SequentialAgent(
    name="food_summary_workflow",
    description="Workflow for handling a user's hotel food query.",
    sub_agents=[food_researcher, response_formatter]
)

# Root agent
root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Hotel Food Summarizer.",
    instruction="""
    - Let the user know you will help them learn about hotel food and cuisines.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    After using the tool, transfer control to the 'food_summary_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[food_summary_workflow]
)
```
# Prepare the application for deployment

Check the final structure
Before deploying, verify that your project directory contains the correct files.


hotel_food_agent/

├── .env

├── __init__.py

├── agent.py

└── requirements.txt

# Set up IAM permissions

With your local code ready, the next step is to set up the identity your agent will use in the cloud.

In the terminal, load the variables into your shell session.
```
source .env
```

Create a dedicated service account for your Cloud Run service so that it has its own specific permission. Paste the following into the terminal:
```
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="Service Account for lab 2 "
```

By creating a dedicated identity for this specific application, you ensure the agent only has the exact permissions it needs, rather than using a default account with overly broad access.

Grant the service account the Vertex AI User role, which gives it permission to call Google's models.

# Grant the "Vertex AI User" role to your service account
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```
# Deploy the agent using the ADK CLI
```
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=clean-machine-491510-p0\
  --region=us-east4 \
  --service_name=hotel-food-summarizer \
  --with_ui \
  . \
  -- \
  --labels=category=food \
  --service-account=$SERVICE_ACCOUNT
```
-If you are prompted with the following:

Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in region 
[europe-west1] will be created.

Do you want to continue (Y/n)?


If so, Type Y and hit ENTER.

-If you are prompted with the following:

Allow unauthenticated invocations to [your-service-name] (y/N)?.

Type y and hit ENTER. This allows unauthenticated invocations for this lab for easy testing.

-Upon successful execution, the command will provide the URL of the deployed Cloud Run service.

Copy the URL of the deployed Cloud Run service for the next task.
```
service url: https://hotel-food-summarizer-830710432020.us-east4.run.app
```
#  Test the deployed agent
```
Summarize popular breakfast items served in hotels
```

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/7a18cc8a-a1e1-43d9-b45b-791df6cc9ee4" />

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/ceed65ad-7577-4581-a4f8-05c941eda54a" />

```
what are the items available in breakfast
```
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/bb0d0674-4269-4c5d-8248-cbb7818ebcb4" />
