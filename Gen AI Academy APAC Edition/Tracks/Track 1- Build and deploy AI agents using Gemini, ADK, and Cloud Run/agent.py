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
