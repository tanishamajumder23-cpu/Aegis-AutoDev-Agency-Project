from crewai import Task

class DevSquadTasks:
    def survey_task(self, agent):
        return Task(
            description="Identify 'ai-maintenance-demo/messy_code.py' and write a 3-point improvement plan.",
            expected_output="A structured 3-point architectural plan.",
            agent=agent
        )

    def coding_task(self, agent):
        return Task(
            description="Rewrite the messy code and save it as 'ai-maintenance-demo/autonomous_fixed_code.py'.",
            expected_output="File saved successfully in the repo folder.",
            agent=agent
        )

    def github_task(self, agent):
        return Task(
            description="Push the fixed code in 'ai-maintenance-demo' to GitHub using a professional commit message.",
            expected_output="Confirmation of a successful git push.",
            agent=agent
        )

    def review_task(self, agent):
        return Task(
            description="Read 'ai-maintenance-demo/autonomous_fixed_code.py' and give a 'Stamp of Approval'.",
            expected_output="Final QA report.",
            agent=agent
        )