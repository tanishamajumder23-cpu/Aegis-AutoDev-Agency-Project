import os
import re
import subprocess
from crewai.tools import tool

# MUST match your cloned folder name exactly
REPO_FOLDER = "ai-maintenance-demo"

@tool("List Directory Files")
def list_directory_files(directory_path: str = "."):
    """Lists files in a directory. Use '.' to see the repo folder."""
    try:
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        return f"Files found: {', '.join(files)}"
    except Exception as e:
        return f"Error: {e}"

@tool("Read File Content")
def read_file_content(file_path: str):
    """Reads code from a file. Input: 'ai-maintenance-demo/messy_code.py'."""
    try:
        path = file_path.strip("'\" ").lstrip("./")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

@tool("Write File Content")
def write_file_content(file_path: str, content: str):
    """Saves code to a file. Call with (filename, code_string)."""
    try:
        path = file_path.strip("'\" ").lstrip("./")
        data = str(content)

        if '"content":' in data:
            match = re.search(r'"content":\s*"(.*?)"', data, re.DOTALL)
            if match:
                data = match.group(1).encode().decode('unicode_escape')

        data = data.replace("```python", "").replace("```", "").strip()

        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        return f"SUCCESS: {path} saved."
    except Exception as e:
        return f"ERROR: {str(e)}"

@tool("Push Fix to GitHub")
def push_fix_to_github(commit_message: str):
    """Commits and pushes changes. Handles syncing automatically."""
    try:
        original_dir = os.getcwd()
        os.chdir(REPO_FOLDER)
        
        # Pull first to avoid the "Your branch is behind" error
        subprocess.run(["git", "pull", "--rebase"], check=False)
        
        subprocess.run(["git", "add", "."], check=True)
        # check=False here because if there's nothing new, it shouldn't crash
        subprocess.run(["git", "commit", "-m", commit_message], check=False)
        subprocess.run(["git", "push"], check=True)
        
        os.chdir(original_dir)
        return f"🚀 SUCCESS: Pushed to GitHub!"
    except Exception as e:
        os.chdir(original_dir)
        return f"Git Error: {str(e)}"