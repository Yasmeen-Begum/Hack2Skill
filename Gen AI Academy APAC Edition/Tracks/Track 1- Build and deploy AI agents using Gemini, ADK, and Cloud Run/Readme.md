


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

```
 gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  compute.googleapis.com
```

