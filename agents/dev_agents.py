import os
from crewai import Agent

# Bug 5 fix: import from config.py instead of redefining LLM here
# Bug 16 fix: config.py now has max_tokens=4000, preventing LLM output truncation
from config import my_llm

from tools.file_manager import (
    list_directory_files,
    read_file_content,
    write_file_content,
    push_fix_to_github,
)


class DevSquadAgents:
    def architect_agent(self):
        return Agent(
            role="Software Architect",
            goal="Audit messy_code.py and produce a 3-point improvement plan.",
            backstory=(
                "You are an expert software architect who specialises in Python code quality. "
                "You use the List Directory Files tool to locate files, then Read File Content "
                "to inspect them before writing your improvement plan."
            ),
            tools=[list_directory_files, read_file_content],
            llm=my_llm,
            verbose=True,
            allow_delegation=False,
        )

    def developer_agent(self):
        return Agent(
            role="Senior Python Developer",
            goal="Rewrite the messy code cleanly and output ONLY raw, valid Python code.",
            backstory=(
                "You are a coding expert who writes clean, PEP-8 compliant Python. "
                "You read the architect's plan, and rewrite the code perfectly. "
            ),
            tools=[push_fix_to_github], # THE FIX: read_file_content removed
            llm=my_llm,
            verbose=True,
            allow_delegation=False,
        )

    def qa_agent(self):
        return Agent(
            role="Quality Assurance Engineer",
            goal="Review the fixed code file and issue a Stamp of Approval.",
            backstory=(
                "You are a ruthless code auditor. You read the fixed file using Read File Content "
                "and verify it is clean, well-structured, and correct before issuing your verdict."
            ),
            tools=[read_file_content],
            llm=my_llm,
            verbose=True,
            allow_delegation=False,
        )