import os
import gradio as gr
from dotenv import load_dotenv

# ADK imports
from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.tool_context import ToolContext

# LangChain community imports
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Gemini model
from google.generativeai import GenerativeModel

# --- Setup ---
load_dotenv()
model_name = os.getenv("MODEL")
model = GenerativeModel(model_name, api_key=os.getenv("GOOGLE_API_KEY"))

# --- Tool setup ---
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# --- Agents ---
# Researcher agent: pulls food info from Wikipedia
food_researcher = Agent(
    name="food_researcher",
    model=model_name,
    description="Researches restaurant dishes and cuisines using Wikipedia.",
    instruction="""
    You are a helpful food guide. Use the Wikipedia tool to gather information
    about restaurant dishes, cuisines, or ingredients mentioned in the query.
    Then summarize the findings concisely.
    """,
    tools=[wikipedia_tool],
    output_key="food_data"
)

# Formatter agent: makes the response user-friendly
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Formats food research into a concise restaurant guide response.",
    instruction="""
    Take the FOOD_DATA and present it as a short, clear restaurant food guide.
    Be conversational and helpful.
    FOOD_DATA: { food_data }
    """
)

# Workflow: researcher → formatter
food_guide_workflow = SequentialAgent(
    name="food_guide_workflow",
    description="Workflow for restaurant food guide queries.",
    sub_agents=[food_researcher, response_formatter]
)

# Root agent
root_agent = Agent(
    name="restaurant_food_guide",
    model=model_name,
    description="Entry point for restaurant food guide queries.",
    instruction="Answer user queries about restaurant food using the workflow.",
    sub_agents=[food_guide_workflow]
)

# --- Gradio function ---
def food_guide(query: str):
    if not query:
        return "No query provided."
    result = root_agent.run(query)
    return result

# --- Gradio UI ---
demo = gr.Interface(
    fn=food_guide,
    inputs=gr.Textbox(label="Enter your restaurant food query"),
    outputs=gr.Textbox(label="Food Guide Response"),
    title="Restaurant Food Guide Agent",
    description="Ask about restaurant dishes, cuisines, or food recommendations."
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
