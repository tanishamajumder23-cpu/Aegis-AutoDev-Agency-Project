import os
from crewai import Agent, LLM
from tools.file_manager import list_directory_files, read_file_content, write_file_content, push_fix_to_github

# Stable LLM config
my_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1
)

class DevSquadAgents:
    def architect_agent(self):
        return Agent(
            role='Software Architect',
            goal='Plan code improvements for messy_code.py.',
            backstory='Expert system designer.',
            tools=[list_directory_files, read_file_content],
            llm=my_llm,
            verbose=True,
            allow_delegation=False
        )

    def developer_agent(self):
        return Agent(
            role='Senior Python Developer',
            goal='Rewrite code and push fixes to GitHub.',
            backstory='A coding genius who uses Write and Push tools perfectly.',
            tools=[read_file_content, write_file_content, push_fix_to_github],
            llm=my_llm,
            verbose=True,
            allow_delegation=False
        )

    def qa_agent(self):
        return Agent(
            role='Quality Assurance Engineer',
            goal='Audit the final code and provide approval.',
            backstory='Ruthless auditor.',
            tools=[read_file_content],
            llm=my_llm,
            verbose=True,
            allow_delegation=False
        )