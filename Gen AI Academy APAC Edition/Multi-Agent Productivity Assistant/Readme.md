
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

1.Create the directory

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
