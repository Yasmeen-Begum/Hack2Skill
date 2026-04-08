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

from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, Date, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Setup Logging and Environment ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()
logging.basicConfig(level=logging.INFO)

load_dotenv()
model_name = os.getenv("MODEL")  # e.g. gemini-1.5-pro
db_url = os.getenv("DATABASE_URL")  # must be URL-encoded if password has @

engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(bind=engine)

# --- ORM Models ---
Base = declarative_base()

class WellnessPlan(Base):
    __tablename__ = "wellness_plans"
    plan_id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    plan_name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Workout(Base):
    __tablename__ = "workouts"
    workout_id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("wellness_plans.plan_id", ondelete="CASCADE"))
    title = Column(String(255))
    recurrence_rule = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class DietLog(Base):
    __tablename__ = "diet_logs"
    diet_id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("wellness_plans.plan_id", ondelete="CASCADE"))
    meal_date = Column(Date, nullable=False)
    meal_description = Column(Text)
    calories = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("wellness_plans.plan_id", ondelete="CASCADE"))
    title = Column(String(255))
    appointment_date = Column(TIMESTAMP, nullable=False)
    reminder_minutes_before = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Note(Base):
    __tablename__ = "notes"
    note_id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("wellness_plans.plan_id", ondelete="CASCADE"))
    note_title = Column(String(255))
    note_content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

Base.metadata.create_all(bind=engine)

# --- Tool: Save user prompt into state ---
def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict[str, str]:
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# --- AlloyDB Tools ---
class AppointmentsTool:
    name = "appointments_tool"
    description = "Fetch upcoming appointments from AlloyDB"

    def run(self, query: str):
        session = SessionLocal()
        results = session.query(Appointment).filter(Appointment.appointment_date > func.now()).all()
        return [{"title": a.title, "date": str(a.appointment_date)} for a in results]

class WorkoutsTool:
    name = "workouts_tool"
    description = "Fetch workouts from AlloyDB"

    def run(self, query: str):
        session = SessionLocal()
        results = session.query(Workout).all()
        return [{"title": w.title, "recurrence": w.recurrence_rule} for w in results]

class DietLogsTool:
    name = "diet_logs_tool"
    description = "Fetch diet logs from AlloyDB"

    def run(self, query: str):
        session = SessionLocal()
        results = session.query(DietLog).order_by(DietLog.meal_date.desc()).limit(10).all()
        return [{"meal": d.meal_description, "calories": d.calories, "date": str(d.meal_date)} for d in results]

class NotesTool:
    name = "notes_tool"
    description = "Fetch notes from AlloyDB"

    def run(self, query: str):
        session = SessionLocal()
        results = session.query(Note).order_by(Note.note_id.desc()).limit(5).all()
        return [{"title": n.note_title, "content": n.note_content} for n in results]

# Wrap AlloyDB tools for LangChain
appointments_tool = LangchainTool(tool=AppointmentsTool())
workouts_tool = LangchainTool(tool=WorkoutsTool())
diet_logs_tool = LangchainTool(tool=DietLogsTool())
notes_tool = LangchainTool(tool=NotesTool())

# --- External Knowledge Tool (Wikipedia) ---
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# --- Researcher Agent ---
wellness_researcher = Agent(
    name="wellness_researcher",
    model=model_name,
    description="Researcher that gathers wellness info from AlloyDB and external sources.",
    instruction="""
    You are a helpful wellness researcher. Your goal is to fully answer the user's PROMPT.
    You have access to:
    1. Internal wellness data (appointments, workouts, diet logs, notes).
    2. Wikipedia for general health and lifestyle knowledge.

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one source, use that source.
    - If the prompt is complex and requires both internal wellness data AND Wikipedia,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results into preliminary data outputs.

    PROMPT:
    { PROMPT }
    """,
    tools=[appointments_tool, workouts_tool, diet_logs_tool, notes_tool, wikipedia_tool],
    output_key="research_data"
)

# --- Response Formatter Agent ---
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes wellness data into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Wellness Assistant.
    Your task is to take the RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - First, present the specific information from the wellness plan (appointments, workouts, diet logs, notes).
    - Then, add interesting general facts from external research.
    - If some information is missing, just present what you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    { research_data }
    """
)

# --- Workflow ---
wellness_workflow = SequentialAgent(
    name="wellness_workflow",
    description="Main workflow for handling a user's wellness request.",
    sub_agents=[
        wellness_researcher,
        response_formatter
    ]
)

# --- Root Agent ---
root_agent = Agent(
    name="greeter",
    model=model_name,
    description="Entry point for the Wellness Assistant.",
    instruction="""
    - Let the user know you will help them with their wellness queries.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    - After saving, transfer control to the 'wellness_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[wellness_workflow]
)

# --- Entrypoint ---
if __name__ == "__main__":
    tool_context = ToolContext()
    user_prompt = "Show me my upcoming appointments and healthy breakfast ideas."
    add_prompt_to_state(tool_context, user_prompt)
    response = root_agent.run(tool_context=tool_context)
    print(response.get("output", response))