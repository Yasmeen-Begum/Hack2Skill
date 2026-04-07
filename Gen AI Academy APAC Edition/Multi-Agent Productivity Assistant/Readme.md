
## Set your project

In the terminal, set your project with this command:
```
gcloud config set project [PROJECT_ID]
```
You should see this message:

Updated property [core/project]

## Enable APIs

To use Cloud Run, Artifact Registry, Cloud Build, Vertex AI, and Compute Engine, you need to enable their respective APIs in your Google Cloud project.

In the terminal, enable the APIs:
```
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com
```
When this finishes running, you should see an output like the following:

Operation "operations/acat.p2-[GUID]" finished successfully.

## Prepare your development environment

### Create the directory

In the terminal, create the project directory and the necessary subdirectories:
```
cd && mkdir zoo_guide_agent && cd zoo_guide_agent
```
In the terminal, run the following command to open the zoo_guide_agent directory in the Cloud Shell Editor explorer:
```
cloudshell open-workspace ~/zoo_guide_agent
```
The explorer panel on the left will refresh. You should now see the directory you created. 


### Install requirements

1.Run the following command in the terminal to create the requirements.txt file.
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
## Set up environment variables

Use the following command in the terminal to create the .env file.
```
# 1. Set the variables in your terminal first
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SA_NAME=lab2-cr-service

# 2. Create the .env file using those variables
cat <<EOF > .env
PROJECT_ID=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
SA_NAME=$SA_NAME
SERVICE_ACCOUNT=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
MODEL="gemini-2.5-flash"
EOF
```
## Create Agent Workflow
### Create __init__.py file

Create the init.py file by running the following in the terminal:
```
cloudshell edit __init__.py
```
This file tells Python that the zoo_guide_agent directory is a package.

Add the following code to the new __init__.py file:
```
from . import agent
```

### Create the agent.py file

Create the main agent.py file by pasting the following command into the terminal.
```
cloudshell edit agent.py
```

## Prepare the application for deployment
Check the final structure

Before deploying, verify that your project directory contains the correct files.

### Set up IAM permissions

1.With your local code ready, the next step is to set up the identity your agent will use in the cloud.

In the terminal, load the variables into your shell session.
```
source .env
```
2.Create a dedicated service account for your Cloud Run service so that it has its own specific permission. Paste the following into the terminal:
```
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="Service Account for lab 2 "
```
3.By creating a dedicated identity for this specific application, you ensure the agent only has the exact permissions it needs, rather than using a default account with overly broad access.
Grant the service account the Vertex AI User role, which gives it permission to call Google's models.
```
# Grant the "Vertex AI User" role to your service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```
##  Deploy the agent using the ADK CLI

With your local code ready and your Google Cloud project prepared, it's time to deploy the agent. You will use the adk deploy cloud_run command, a convenient tool that automates the entire deployment workflow. This single command packages your code, builds a container image, pushes it to Artifact Registry, and launches the service on Cloud Run, making it accessible on the web.

Run the following command in the terminal to deploy your agent.
```
# Run the deployment command
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
      --project=$PROJECT_ID \
      --region=europe-west1 \
      --service_name=zoo-tour-guide \
      --with_ui \
      . \
      -- \
      --labels=dev-tutorial=codelab-adk \
      --service-account=$SERVICE_ACCOUNT
```

Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in region 
[europe-west1] will be created.

Do you want to continue (Y/n)?

If so, Type Y and hit ENTER.

If you are prompted with the following:

Allow unauthenticated invocations to [your-service-name] (y/N)?.

Type y and hit ENTER. This allows unauthenticated invocations for this lab for easy testing.

Upon successful execution, the command will provide the URL of the deployed Cloud Run service. (It will look something like 
