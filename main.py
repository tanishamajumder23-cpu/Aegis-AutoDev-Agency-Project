import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents.dev_agents import DevSquadAgents
from tasks.dev_tasks import DevSquadTasks

load_dotenv()

agents_factory = DevSquadAgents()
tasks_factory = DevSquadTasks()

architect = agents_factory.architect_agent()
developer = agents_factory.developer_agent()
qa_specialist = agents_factory.qa_agent()

software_agency = Crew(
    agents=[architect, developer, qa_specialist],
    tasks=[
        tasks_factory.survey_task(architect),
        tasks_factory.coding_task(developer),
        tasks_factory.github_task(developer),
        tasks_factory.review_task(qa_specialist)
    ],
    process=Process.sequential,
    verbose=True,
    cache=False,
    # Slower but steady to avoid the "Rate Limit" crash
    max_rpm=10 
)

if __name__ == "__main__":
    print("🚀 Starting the FAST run...")
    software_agency.kickoff()
    print("\n✅ DONE. Check GitHub!")