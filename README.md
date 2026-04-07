
<div align="center">

# 🛡️ Aegis AutoDev Agency

**An Autonomous Multi-Agent Framework for Self-Healing Code**

*Powered by CrewAI · Llama 3.3-70B · Groq · GitHub*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-0.36+-FF4B4B?style=for-the-badge&logo=robot&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3-F55036?style=for-the-badge&logo=meta&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

</div>

---

## 📖 What is Aegis?

**Aegis** is an autonomous multi-agent system that deploys a specialized AI squad to:

1. 🔍 **Audit** legacy Python files and detect code quality issues
2. 🏗️ **Architect** a structured refactor plan
3. 🛠️ **Rewrite** the code autonomously using AI
4. 🚀 **Push** the fix directly to GitHub — no human needed

Aegis eliminates technical debt by transforming manual code maintenance into a fully automated, intelligent pipeline.

---

## 🧠 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Aegis AutoDev Agency                    │
│                  ( CrewAI Sequential Pipeline )             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │     🔍 Software Architect    │
        │  Reads & audits messy code   │
        │  Produces 3-point fix plan   │
        │  Tools: List Files, Read File│
        └──────────────┬──────────────┘
                       │ Plan passed via context
        ┌──────────────▼──────────────┐
        │   🛠️  Senior Python Dev      │
        │  Rewrites code from scratch  │
        │  Saves fixed file to repo    │
        │  Tools: Read, Write, Push    │
        └──────┬───────────┬───────────┘
               │           │
          Writes file   Pushes to
          to repo dir   GitHub
               │
        ┌──────▼──────────────────────┐
        │   ✅ QA Engineer             │
        │  Reads the fixed code        │
        │  Issues Stamp of Approval    │
        │  Tools: Read File            │
        └─────────────────────────────┘
```

### Agents

| Agent | Role | Tools |
|-------|------|-------|
| **Software Architect** | Audits legacy code and writes a structured improvement plan | `list_directory_files`, `read_file_content` |
| **Senior Python Developer** | Rewrites the code cleanly and pushes it to GitHub | `read_file_content`, `write_file_content`, `push_fix_to_github` |
| **QA Engineer** | Reviews the fixed code and issues a final verdict | `read_file_content` |

---

## 📂 Project Structure

```
Aegis-AutoDev-Agency/
│
├── main.py                  # Entry point — wires agents, tasks, and crew
├── config.py                # LLM configuration (Groq / Llama 3.3)
├── messy_code.py            # Sample legacy file for the agents to fix
├── requirements.txt         # Python dependencies
├── .env.example             # Template for required environment variables
│
├── agents/
│   ├── __init__.py
│   └── dev_agents.py        # Architect, Developer, QA agent definitions
│
├── tasks/
│   ├── __init__.py
│   └── dev_tasks.py         # Task descriptions passed to each agent
│
└── tools/
    ├── __init__.py
    └── file_manager.py      # Custom CrewAI tools: read, write, list, push
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com) (free tier available)
- A [GitHub Personal Access Token](https://github.com/settings/tokens) with `repo` scope
- `git` installed and accessible from the terminal

### 1. Clone Aegis

```bash
git clone https://github.com/tanishamajumder23-cpu/Aegis-AutoDev-Agency
cd Aegis-AutoDev-Agency
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_pat_here
```

### 4. Clone your *target* repository

Aegis needs a separate git repo to audit and push fixes to. Clone it locally as `ai-maintenance-demo`:

```bash
git clone https://github.com/your-user/your-target-repo ai-maintenance-demo
```

> 💡 `messy_code.py` (included in the Aegis root) is the sample file the agents will fix.  
> The developer agent writes the fixed version into `ai-maintenance-demo/` and pushes it.

### 5. Run Aegis

```bash
python main.py
```

Aegis will execute the full pipeline — survey → code → push → review — and print live agent reasoning as it runs.

---

## 🔧 How It Works — Step by Step

```
1. main.py loads .env and validates that ai-maintenance-demo/ is a git repo.
2. Architect reads messy_code.py → writes 3-point improvement plan.
3. Developer reads plan + messy_code.py → rewrites code → saves to
   ai-maintenance-demo/autonomous_fixed_code.py.
4. Developer runs git pull --rebase → git add → git commit → git push origin <branch>.
5. QA reads autonomous_fixed_code.py → issues Stamp of Approval.
6. Done! The fixed file is live on GitHub.
```

---

## 🐛 Bugs Fixed (v1.0 → v1.1)

This section documents all **17 bugs** found and fixed from the original codebase.

---

### 🔴 Critical

#### Bug 1 — `messy_code.py`: Python `IndentationError`
**File:** `messy_code.py`  
The sample file had no indentation — Python raised `IndentationError` before any agent could even read it.

```python
# Before (broken):
def calc( a,b):
res =a+ b       # not indented — SyntaxError
 return res     # 1-space indent — IndentationError

# After (fixed):
def calc(a, b):
    res = a + b
    return res
```

---

#### Bug 2 — `push_fix_to_github`: Unconditional `os.chdir()` crashes on missing folder
**File:** `tools/file_manager.py`  
`os.chdir("ai-maintenance-demo")` ran without checking if the folder existed, producing a silent `FileNotFoundError`.

**Fix:** Added `_validate_repo_folder()` guard that checks for both folder existence and `.git/` presence before changing directory.

---

#### Bug 10 — Regex truncates code content at escaped quotes
**File:** `tools/file_manager.py`  
The pattern `re.search(r'"content":\s*"(.*?)"', data, re.DOTALL)` stops at the **first `"` character** it finds. Any code with string literals is silently chopped in half.

```python
# Before (broken): regex stops mid-code
match = re.search(r'"content":\s*"(.*?)"', data, re.DOTALL)
data = match.group(1).encode().decode('unicode_escape')

# After (fixed): safe JSON parsing
if data.strip().startswith("{"):
    try:
        parsed = json.loads(data)
        if isinstance(parsed, dict) and "content" in parsed:
            data = parsed["content"]
    except json.JSONDecodeError:
        pass
```

---

### 🟠 High

#### Bug 3 — `write_file_content`: Two-argument tool incompatible with CrewAI
**File:** `tools/file_manager.py`  
CrewAI LLM tool calls pass a single string. A `(file_path, content)` two-argument function causes agent failures with smaller models like Llama 3.3.

**Fix:** Converted to a single `tool_input: str` argument using `|||` as a path/content delimiter. Task descriptions explicitly teach the LLM the format.

```python
# Usage: 'ai-maintenance-demo/fixed.py|||def hello(): return 1'
```

---

#### Bug 4 — Tasks reference non-existent `ai-maintenance-demo/` subdirectory
**File:** `tasks/dev_tasks.py`  
All tasks described file paths like `ai-maintenance-demo/messy_code.py`, but `messy_code.py` is at the Aegis **project root**, not inside a subfolder.

**Fix:** Task descriptions updated to point to `messy_code.py` (root) for reading, and `ai-maintenance-demo/autonomous_fixed_code.py` for writing — matching where the git repo actually lives.

---

#### Bug 11 — `write_file_content` has no `os.makedirs`
**File:** `tools/file_manager.py`  
`open(path, 'w')` throws `FileNotFoundError` if any parent directory doesn't exist. Writing to `ai-maintenance-demo/fixed.py` fails if the folder was never created.

**Fix:**
```python
os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
```

---

#### Bug 12 — No GitHub token handling — `git push` fails over HTTPS
**File:** `tools/file_manager.py`  
GitHub removed password authentication in 2021. `git push` with no credentials fails silently on fresh machines.

**Fix:** `GITHUB_TOKEN` from `.env` is automatically injected into the HTTPS remote URL before pushing:
```python
auth_url = remote_url.replace("https://", f"https://{token}@")
subprocess.run(["git", "remote", "set-url", "origin", auth_url])
```

---

#### Bug 13 — `git pull --rebase` failure silently ignored
**File:** `tools/file_manager.py`  
`check=False` on the rebase meant merge conflicts left the repo in a broken `REBASING` state. The next `git push` then failed with a cryptic error.

**Fix:** Return value is now checked. On failure, rebase is aborted and a clear error message is returned to the agent.

---

### 🟡 Medium

#### Bug 5 — `config.py` never imported — LLM defined twice
**Files:** `agents/dev_agents.py`, `config.py`  
`config.py` defined `my_llm` but `dev_agents.py` redefined it identically without importing `config`. Two sources of truth.

**Fix:** `dev_agents.py` now does `from config import my_llm`.

---

#### Bug 6 — `lstrip("./")` strips individual characters, not a path prefix
**File:** `tools/file_manager.py`  
`lstrip("./")` removes any leading `.` or `/` characters (not just the two-char sequence `"./"`), corrupting valid paths like `../sibling/file.py`.

**Fix:**
```python
path = os.path.normpath(file_path.strip("'\" "))
```

---

#### Bug 7 — `Crew()` instantiated at module import level
**File:** `main.py`  
Agents, tasks, and the Crew were all constructed outside the `if __name__ == "__main__":` guard. Importing `main.py` triggered a full CrewAI run.

**Fix:** Everything moved inside the guard, along with pre-flight env checks.

---

#### Bug 14 — `git push` with no remote or branch specified
**File:** `tools/file_manager.py`  
Bare `git push` relies on upstream tracking which may not be configured on fresh clones.

**Fix:**
```python
branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], ...).stdout.strip()
subprocess.run(["git", "push", "origin", branch], check=True)
```

---

#### Bug 15 — File write target ≠ git repo directory
**Files:** `tasks/dev_tasks.py`, `tools/file_manager.py`  
The code was saved to one location while `git add .` ran inside a different directory, meaning the push committed nothing related to the fix.

**Fix:** All tasks, write paths, and the git push now consistently operate inside `ai-maintenance-demo/`.

---

#### Bug 16 — `my_llm` in `dev_agents.py` missing `max_tokens`
**File:** `agents/dev_agents.py`  
The locally defined LLM omitted `max_tokens=4000`, causing the Groq provider to use its default (often too low for full code rewrites), truncating responses mid-output.

**Fix:** Resolved by Bug 5's fix — importing from `config.py` which already has `max_tokens=4000`.

---

### 🔵 Low

#### Bug 8 — Missing `requirements.txt`, `__init__.py`, and `.env.example`
**Fix:** Added all three:
- `requirements.txt` with `crewai>=0.36.0` and `python-dotenv>=1.0.0`
- `agents/__init__.py`, `tasks/__init__.py`, `tools/__init__.py`
- `.env.example` documenting `GROQ_API_KEY`, `GITHUB_TOKEN`, and `REPO_FOLDER`

---

#### Bug 9 — `os.chdir()` not in a `finally` block — working directory leaks
**File:** `tools/file_manager.py`  
If an exception occurred after `os.chdir(REPO_FOLDER)`, the original working directory was never restored, breaking every subsequent tool call.

**Fix:** `os.chdir(original_dir)` moved into a `finally:` block that always runs.

---

#### Bug 17 — `list_directory_files` default arg misleads LLMs
**File:** `tools/file_manager.py`  
The default `directory_path="."` is invisible to LLMs in the tool schema. Agents passed empty strings, causing `os.listdir("")` → `FileNotFoundError`.

**Fix:** Default removed; empty input guarded; docstring explicitly instructs the LLM on what to pass.

---

## 📋 Bug Fix Summary Table

| # | File | Severity | Issue | Status |
|---|------|:--------:|-------|:------:|
| 1 | `messy_code.py` | 🔴 Critical | `IndentationError` on import | ✅ |
| 2 | `tools/file_manager.py` | 🔴 Critical | No guard before `os.chdir(REPO_FOLDER)` | ✅ |
| 3 | `tools/file_manager.py` | 🟠 High | Two-arg tool breaks CrewAI LLM calls | ✅ |
| 4 | `tasks/dev_tasks.py` | 🟠 High | Tasks reference non-existent folder | ✅ |
| 5 | `agents/dev_agents.py` | 🟡 Medium | `config.py` never imported, LLM defined twice | ✅ |
| 6 | `tools/file_manager.py` | 🟡 Medium | `lstrip("./")` corrupts valid paths | ✅ |
| 7 | `main.py` | 🟡 Medium | Crew constructed outside `__main__` guard | ✅ |
| 8 | Project | 🟡 Medium | Missing `requirements.txt`, `__init__.py`, `.env.example` | ✅ |
| 9 | `tools/file_manager.py` | 🔵 Low | `os.chdir` not in `finally` — working dir leaks | ✅ |
| 10 | `tools/file_manager.py` | 🔴 Critical | Regex truncates code at escaped quotes | ✅ |
| 11 | `tools/file_manager.py` | 🟠 High | No `os.makedirs` — nested paths always fail | ✅ |
| 12 | `tools/file_manager.py` | 🟠 High | No GitHub token handling — push fails over HTTPS | ✅ |
| 13 | `tools/file_manager.py` | 🟠 High | `git pull --rebase` failure silently ignored | ✅ |
| 14 | `tools/file_manager.py` | 🟡 Medium | `git push` with no remote/branch | ✅ |
| 15 | `tasks/dev_tasks.py` | 🟡 Medium | File write target ≠ git repo directory | ✅ |
| 16 | `agents/dev_agents.py` | 🟡 Medium | `max_tokens` missing — LLM output truncated | ✅ |
| 17 | `tools/file_manager.py` | 🔵 Low | Default arg in `list_directory_files` misleads LLMs | ✅ |

---

## 🛠️ Configuration Reference

| Variable | Required | Description |
|----------|:--------:|-------------|
| `GROQ_API_KEY` | ✅ | API key from [console.groq.com](https://console.groq.com) |
| `GITHUB_TOKEN` | ✅ | GitHub PAT with `repo` scope for pushing fixes |
| `REPO_FOLDER` | ⬜ | Local folder name for the target repo (default: `ai-maintenance-demo`) |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

<div align="center">
Built with ❤️ using <a href="https://www.crewai.com">CrewAI</a> · <a href="https://groq.com">Groq</a> · <a href="https://github.com">GitHub</a>
</div>
=======

