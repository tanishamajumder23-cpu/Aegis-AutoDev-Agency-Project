import os
import json
import subprocess
from crewai.tools import tool

# The local folder name of the target git repo to fix.
# Clone your target repo here before running Aegis:
#   git clone https://github.com/your-user/your-repo ai-maintenance-demo
REPO_FOLDER = os.getenv("REPO_FOLDER", "ai-maintenance-demo")
TARGET_REPO_URL = os.getenv(
    "TARGET_REPO_URL",
    "https://github.com/tanishamajumder23-cpu/ai-maintenance-demo.git",
)


def _validate_repo_folder() -> str | None:
    """Returns an error message if REPO_FOLDER is not a valid git repo, else None."""
    if not os.path.isdir(REPO_FOLDER):
        return (
            f"ERROR: Target repo folder '{REPO_FOLDER}' does not exist. "
            f"Clone your target repo first: git clone <url> {REPO_FOLDER}"
        )
    if not os.path.isdir(os.path.join(REPO_FOLDER, ".git")):
        return (
            f"ERROR: '{REPO_FOLDER}' exists but is not a git repository (.git folder missing)."
        )
    return None


@tool("List Directory Files")
def list_directory_files(directory_path: str):
    """
    Lists all files in a given directory.

    To list files inside the target repo, pass 'ai-maintenance-demo'.
    To list files in the Aegis project root, pass '.'.
    Never pass an empty string.
    """
    # Bug 17 fix: guard empty/whitespace input
    if not directory_path or not directory_path.strip():
        directory_path = "."

    directory_path = directory_path.strip("'\" ")

    try:
        if not os.path.isdir(directory_path):
            return f"Error: Directory '{directory_path}' does not exist."
        files = [
            f for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))
        ]
        return f"Files in '{directory_path}': {', '.join(files) if files else 'none found'}"
    except Exception as e:
        return f"Error listing '{directory_path}': {e}"


@tool("Read File Content")
def read_file_content(file_path: str):
    """
    Reads and returns the content of a source file.

    Input: relative path to the file, e.g. 'ai-maintenance-demo/messy_code.py'.
    """
    try:
        # Bug 6 fix: use os.path.normpath instead of lstrip("./") which strips individual chars
        path = os.path.normpath(file_path.strip("'\" "))
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading '{file_path}': {e}"


@tool("Write File Content")
def write_file_content(tool_input: str):
    """
    Saves code content to a file.

    Input format (REQUIRED): 'FILE_PATH|||CODE_CONTENT'
    The separator is three pipe characters: |||
    Example: 'ai-maintenance-demo/fixed.py|||def hello():\\n    return 1'

    Do NOT use any other format. Always include the ||| separator.
    """
    # Bug 3 fix: single-string input with ||| delimiter (CrewAI tools must be single-arg)
    if "|||" not in tool_input:
        return (
            "ERROR: Invalid format. Use: 'file_path|||code_content'. "
            "Example: 'ai-maintenance-demo/fixed.py|||def hello(): return 1'"
        )

    file_path, content = tool_input.split("|||", 1)
    file_path = file_path.strip("'\" ")

    try:
        # Bug 6 fix: safe path normalisation
        path = os.path.normpath(file_path.strip())

        # Bug 10 fix: use json.loads to safely extract content if the LLM wrapped it in JSON,
        # rather than a fragile regex that truncates at escaped quotes
        data = content
        if data.strip().startswith("{"):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict) and "content" in parsed:
                    data = parsed["content"]
            except json.JSONDecodeError:
                pass  # not valid JSON — use the raw string

        # Strip markdown code fences if the LLM wrapped the code in ```python ... ```
        data = data.strip()
        if data.startswith("```python"):
            data = data[len("```python"):].lstrip("\n")
        if data.startswith("```"):
            data = data[3:].lstrip("\n")
        if data.endswith("```"):
            data = data[:-3].rstrip()

        # Bug 11 fix: create parent directories before writing
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(data)

        return f"SUCCESS: '{path}' saved ({len(data)} characters)."
    except Exception as e:
        return f"ERROR writing '{file_path}': {str(e)}"


@tool("Push Fix to GitHub")
def push_fix_to_github(commit_message: str):
    """
    Commits and pushes all changes in the target repo to GitHub.

    Input: a professional git commit message describing what was fixed.
    Example: 'refactor: clean up messy_code.py — fix indentation and naming'
    """
    # Bug 2 fix: validate repo folder existence before os.chdir
    err = _validate_repo_folder()
    if err:
        return err

    original_dir = os.getcwd()

    # Bug 9 fix: always restore working directory via try/finally
    try:
        os.chdir(REPO_FOLDER)

        # Ensure the target repo remote is set to the desired repo URL.
        target_repo_url = TARGET_REPO_URL.strip()
        if target_repo_url:
            current_remote = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True
            )
            current_remote_url = current_remote.stdout.strip()
            if current_remote.returncode == 0:
                if current_remote_url != target_repo_url:
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", target_repo_url],
                        check=True,
                    )
            else:
                subprocess.run(
                    ["git", "remote", "add", "origin", target_repo_url],
                    check=True,
                )

        # Bug 12 fix: inject GITHUB_TOKEN into remote URL for HTTPS auth if provided
        token = os.getenv("GITHUB_TOKEN")
        if token:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True
            )
            remote_url = result.stdout.strip()
            if remote_url.startswith("https://") and f"@" not in remote_url:
                auth_url = remote_url.replace("https://", f"https://{token}@")
                subprocess.run(
                    ["git", "remote", "set-url", "origin", auth_url],
                    check=True
                )

        # Fetch the latest remote state first, then commit and push.
        subprocess.run(["git", "fetch", "origin"], check=True)

        subprocess.run(["git", "add", "."], check=True)

        # check=False intentionally: if nothing changed, commit is a no-op (not an error)
        subprocess.run(["git", "commit", "-m", commit_message], check=False)

        # Bug 14 fix: explicitly specify remote and branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True
        )
        branch = branch_result.stdout.strip() or "main"

        push_result = subprocess.run(
            ["git", "push", "origin", branch],
            capture_output=True, text=True
        )
        if push_result.returncode != 0:
            stderr = push_result.stderr.strip()
            if "non-fast-forward" in stderr.lower() or "rejected" in stderr.lower():
                fetch_result = subprocess.run(
                    ["git", "fetch", "origin"],
                    capture_output=True, text=True
                )
                if fetch_result.returncode != 0:
                    return f"ERROR: git fetch failed:\n{fetch_result.stderr.strip()}"

                merge_result = subprocess.run(
                    [
                        "git",
                        "merge",
                        "--no-edit",
                        "--allow-unrelated-histories",
                        "-X",
                        "ours",
                        f"origin/{branch}",
                    ],
                    capture_output=True, text=True
                )
                if merge_result.returncode != 0:
                    return (
                        f"ERROR: git merge origin/{branch} failed. "
                        f"Resolve conflicts manually first.\n{merge_result.stderr.strip()}"
                    )

                push_result = subprocess.run(
                    ["git", "push", "origin", branch],
                    capture_output=True, text=True
                )
                if push_result.returncode != 0:
                    return f"ERROR: git push failed after merge:\n{push_result.stderr.strip()}"
            else:
                return f"ERROR: git push failed:\n{stderr}"

        repo_display_url = target_repo_url
        if repo_display_url.endswith(".git"):
            repo_display_url = repo_display_url[: -len(".git")]
        return (
            f"SUCCESS: Changes pushed to {repo_display_url}/tree/{branch} 🚀\n"
            f"Repo URL: {repo_display_url}"
        )

    except Exception as e:
        return f"Git Error: {str(e)}"
    finally:
        # Bug 9 fix: always restore CWD even if an exception is raised
        os.chdir(original_dir)