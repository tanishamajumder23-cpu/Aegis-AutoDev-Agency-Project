from crewai import Task


# Bug 4 fix: Paths updated from non-existent 'ai-maintenance-demo/' subdirectory
#            to the actual locations (repo root for messy_code.py).
# Bug 15 fix: All tasks now consistently point to 'ai-maintenance-demo/' as the
#             git repo folder — write target and git push target are aligned.
#             The developer saves to 'ai-maintenance-demo/autonomous_fixed_code.py'
#             and push_fix_to_github commits from inside 'ai-maintenance-demo/'.


class DevSquadTasks:
    def survey_task(self, agent):
        """Architect reads messy_code.py and produces a 3-point improvement plan."""
        return Task(
            description=(
                "Use the Read File Content tool to read 'messy_code.py' (in the current directory). "
                "Analyse the code thoroughly and write a structured 3-point improvement plan "
                "covering: naming conventions, code structure, and any bugs or issues you find."
            ),
            expected_output=(
                "A structured 3-point architectural improvement plan for messy_code.py, "
                "with clear recommendations the developer can act on."
            ),
            agent=agent,
        )

    def coding_task(self, agent):
        """Developer rewrites messy_code.py and saves the fixed version."""
        
        # THE FIX: Read the file natively with Python to bypass LLM tool costs
        try:
            with open("messy_code.py", "r", encoding="utf-8") as f:
                code_to_fix = f.read()
        except FileNotFoundError:
            code_to_fix = "# ERROR: messy_code.py not found"

        return Task(
            description=(
                f"Here is the original code to fix:\n\n```python\n{code_to_fix}\n```\n\n"
                "Apply the architect's improvement plan to this code. "
                "Write the updated code.\n\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. You must output ONLY the raw, valid Python code.\n"
                "2. DO NOT include any conversational text (e.g., 'Here is the code').\n"
                "3. DO NOT use markdown code fences (no ```python ... ```).\n"
                "Your exact output will be written directly to a file."
            ),
            expected_output="Clean, raw, valid Python code implementing the improvements.",
            agent=agent,
            output_file="ai-maintenance-demo/autonomous_fixed_code.py" 
        )

    def github_task(self, agent):
        """Developer pushes the fixed file from inside the ai-maintenance-demo git repo."""
        return Task(
            description=(
                "Use the Push Fix to GitHub tool to commit and push all changes in 'ai-maintenance-demo'. "
                "Write a professional commit message that describes what was fixed, "
                "e.g. 'refactor: rewrite messy_code.py — fix indentation, naming and structure'."
            ),
            expected_output="The message 'SUCCESS: Changes pushed to origin/<branch> 🚀'",
            agent=agent,
        )

    def review_task(self, agent):
        """QA agent reads the fixed file and issues a Stamp of Approval."""
        return Task(
            description=(
                "Use the Read File Content tool to read "
                "'ai-maintenance-demo/autonomous_fixed_code.py'. "
                "Review it for correctness, clean style, and adherence to the architect's plan. "
                "Issue your final QA verdict."
            ),
            expected_output=(
                "A final QA report ending with '✅ STAMP OF APPROVAL' if the code passes, "
                "or detailed issues if it does not."
            ),
            agent=agent,
        )