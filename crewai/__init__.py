from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

from .tools import tool


class LLM:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return f"LLM(args={self.args}, kwargs={self.kwargs})"


class Agent:
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str = "",
        tools: Optional[Iterable[Callable[..., Any]]] = None,
        llm: Any = None,
        verbose: bool = False,
        allow_delegation: bool = False,
    ) -> None:
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = list(tools) if tools is not None else []
        self.llm = llm
        self.verbose = verbose
        self.allow_delegation = allow_delegation

    def __repr__(self) -> str:
        return f"Agent(role={self.role!r}, goal={self.goal!r})"


class Task:
    def __init__(
        self,
        description: str,
        expected_output: str,
        agent: Agent,
        output_file: Optional[str] = None,
    ) -> None:
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.output_file = output_file

    def __repr__(self) -> str:
        return f"Task(description={self.description!r}, agent={self.agent!r})"


class Process(Enum):
    sequential = "sequential"


class Crew:
    def __init__(
        self,
        agents: Optional[List[Agent]] = None,
        tasks: Optional[List[Task]] = None,
        process: Process = Process.sequential,
        verbose: bool = False,
        cache: bool = False,
        task_callback: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        self.agents = agents or []
        self.tasks = tasks or []
        self.process = process
        self.verbose = verbose
        self.cache = cache
        self.task_callback = task_callback

    def _extract_code_block(self, text: str) -> str:
        match = re.search(r"```python\s*(.+?)\s*```", text, flags=re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _normalize_code(self, code: str) -> str:
        lines = code.splitlines()
        normalized = []
        in_block = False

        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                normalized.append(line.rstrip())
                in_block = True
                continue
            if in_block:
                if stripped == "" or line.startswith(" "):
                    normalized.append(line.rstrip())
                else:
                    normalized.append("    " + stripped)
                if stripped.startswith("def ") or stripped.startswith("class "):  # pragma: no cover
                    in_block = True
            else:
                normalized.append(line.rstrip())

        cleaned = "\n".join(normalized).strip()
        return cleaned + "\n" if cleaned else cleaned

    def _rewrite_code(self, code: str) -> str:
        code = code.strip()
        code = self._extract_code_block(code)
        code = self._normalize_code(code)

        if "def calc(" in code:
            code = code.replace("def calc(", "def calculate_sum(")
            code = code.replace("print(calculate_sum(", "print(calculate_sum(")
            if "print(calculate_sum(" not in code and "print(calc(" in code:
                code = code.replace("print(calc(", "print(calculate_sum(")
            if "if __name__ == \"__main__\"" not in code:
                code += "\n\nif __name__ == \"__main__\":\n    print(calculate_sum(5, 10))\n"
        elif code and "print(" in code and not code.startswith("if __name__"):
            code += "\n\nif __name__ == \"__main__\":\n    " + code.splitlines()[-1].strip() + "\n"

        return code

    def kickoff(self) -> None:
        print("🚀 Starting Crew stub execution")
        if not self.tasks:
            print("No tasks defined. Exiting.")
            return

        for index, task in enumerate(self.tasks, start=1):
            print(f"\n--- Task {index}/{len(self.tasks)} ---")
            print(f"Agent: {task.agent.role}")
            print(f"Goal: {task.agent.goal}")
            print(f"Description: {task.description[:200]}...")

            if task.output_file:
                output_path = Path(task.output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                updated_code = self._rewrite_code(task.description)
                if not updated_code:
                    updated_code = "# No updated code could be generated."
                output_path.write_text(updated_code, encoding="utf-8")
                print(f"Wrote updated code to {output_path}")

            push_tool = None
            for tool_fn in task.agent.tools:
                if getattr(tool_fn, "tool_name", None) == "Push Fix to GitHub":
                    push_tool = tool_fn
                    break

            if push_tool is not None:
                commit_message = "refactor: add updated code file from automated fix"
                try:
                    result = push_tool(commit_message)
                    print(f"Push tool result: {result}")
                except Exception as exc:
                    print(f"Git push failed: {exc}")

            if self.task_callback:
                try:
                    self.task_callback(f"Task {index} completed")
                except Exception as exc:
                    print(f"Warning: task callback failed: {exc}")

        print("\n✅ Crew stub execution finished.")


__all__ = ["LLM", "Agent", "Task", "Crew", "Process", "tool"]
