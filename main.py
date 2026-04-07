import os
import sys
import time
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.dev_agents import DevSquadAgents
from tasks.dev_tasks import DevSquadTasks

# Load .env first so GROQ_API_KEY and GITHUB_TOKEN are available
load_dotenv()

REPO_FOLDER = os.getenv("REPO_FOLDER", "ai-maintenance-demo")

# --- THE FIX: Rate Limit Reset Mechanism ---
def wait_for_rate_limit(task_output):
    """
    Triggers after every task. Sleeps briefly to simulate a rate limit reset
    without blocking too long during local stub execution.
    """
    print(f"\n⏳ Task completed successfully! Output: {str(task_output)[:50]}...")
    print("⏳ Sleeping for 1 second to simulate rate limit reset...\n")
    time.sleep(1)


if __name__ == "__main__":
    # Pre-flight check: ensure the target repo is present and is a git repo
    if not os.path.isdir(REPO_FOLDER):
        print(
            f"\n❌ ERROR: Target repo folder '{REPO_FOLDER}' not found.\n"
            f"   Clone your target repository first:\n"
            f"   git clone https://github.com/your-user/your-repo {REPO_FOLDER}\n"
            f"   Then copy messy_code.py into it before running Aegis.\n"
        )
        sys.exit(1)

    if not os.path.isdir(os.path.join(REPO_FOLDER, ".git")):
        print(
            f"\n❌ ERROR: '{REPO_FOLDER}' exists but is not a git repository.\n"
            f"   Make sure you cloned (not just created) the folder.\n"
        )
        sys.exit(1)

    if not os.getenv("GROQ_API_KEY"):
        print("\n❌ ERROR: GROQ_API_KEY is not set. Add it to your .env file.\n")
        sys.exit(1)

    agents_factory = DevSquadAgents()
    tasks_factory = DevSquadTasks()

    # 1. TRIM THE FAT: Only keeping essential agents to save tokens
    architect    = agents_factory.architect_agent()
    developer    = agents_factory.developer_agent()
    # qa_specialist = agents_factory.qa_agent()  <-- REMOVED to save API calls

    # 2. TRIM THE FAT: Only keeping essential tasks
    survey  = tasks_factory.survey_task(architect)
    coding  = tasks_factory.coding_task(developer)
    pushing = tasks_factory.github_task(developer)
    # review  = tasks_factory.review_task(qa_specialist) <-- REMOVED

    software_agency = Crew(
        agents=[architect, developer],
        tasks=[survey, coding, pushing],
        process=Process.sequential,
        verbose=True,
        cache=False,
        task_callback=wait_for_rate_limit, # 3. THE DELAY: Injects our 60s sleep
    )

    print("🚀 Starting Aegis AutoDev Agency (Throttled for Groq Free Tier)...")
    software_agency.kickoff()
    target_repo_url = os.getenv(
        "TARGET_REPO_URL",
        "https://github.com/tanishamajumder23-cpu/ai-maintenance-demo.git",
    )
    if target_repo_url.endswith(".git"):
        target_repo_url = target_repo_url[: -len(".git")]
    print("\n✅ DONE. Check your target GitHub repo for the pushed fix!")
    print(f"✅ Pushed repo: {target_repo_url}")