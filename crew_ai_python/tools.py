# tools.py
import os
import subprocess
from typing import List

from crewai_tools import BaseTool

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, "workspace")
SPECS_PATH = os.path.join(PROJECT_ROOT, "SPECS.md")


def _ensure_workspace():
    os.makedirs(WORKSPACE_ROOT, exist_ok=True)


class ReadSpecsTool(BaseTool):
    name = "read_specs"
    description = "Reads and returns the full content of SPECS.md, which describes the project requirements."

    def _run(self) -> str:
        if not os.path.exists(SPECS_PATH):
            return "ERROR: SPECS.md not found next to crew.py."
        with open(SPECS_PATH, "r", encoding="utf-8") as f:
            return f.read()


class ReadFileTool(BaseTool):
    name = "read_file"
    description = (
        "Read the content of a text file from the workspace. "
        "Input should be a relative file path from the workspace root, e.g. 'src/main.py'."
    )

    def _run(self, file_path: str) -> str:
        _ensure_workspace()
        safe_path = os.path.normpath(os.path.join(WORKSPACE_ROOT, file_path))
        if not safe_path.startswith(WORKSPACE_ROOT):
            return "Security error: path outside workspace."
        if not os.path.exists(safe_path):
            return f"File not found: {file_path}"
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()


class WriteFileTool(BaseTool):
    name = "write_file"
    description = (
        "Write text content to a file in the workspace, overwriting if it exists. "
        "Input must be a dict: {'path': 'relative/path.py', 'content': '...'}"
    )

    def _run(self, data: dict) -> str:
        _ensure_workspace()
        path = data.get("path")
        content = data.get("content")
        if not path or content is None:
            return "Error: 'path' and 'content' required."
        safe_path = os.path.normpath(os.path.join(WORKSPACE_ROOT, path))
        if not safe_path.startswith(WORKSPACE_ROOT):
            return "Security error: path outside workspace."

        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote file {path} (length {len(content)} chars)."


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "List all files under the workspace directory, relative paths."

    def _run(self) -> str:
        _ensure_workspace()
        result: List[str] = []
        for root, _, files in os.walk(WORKSPACE_ROOT):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, WORKSPACE_ROOT)
                result.append(rel)
        if not result:
            return "Workspace is currently empty."
        return "\n".join(sorted(result))


class RunPytestTool(BaseTool):
    name = "run_pytest"
    description = (
        "Run pytest in the workspace and return the output. "
        "Use this to verify tests. If tests fail, read and fix the offending files and run again."
    )

    def _run(self, extra_args: str = "") -> str:
        _ensure_workspace()
        cmd = ["pytest"]
        if extra_args:
            cmd.extend(extra_args.split())

        try:
            proc = subprocess.run(
                cmd,
                cwd=WORKSPACE_ROOT,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            return "ERROR: pytest command not found. Please install pytest in your environment."

        return (
            f"COMMAND: {' '.join(cmd)}\n"
            f"RETURN CODE: {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )


def get_all_tools():
    """Convenience for crew.py."""
    return [
        ReadSpecsTool(),
        ReadFileTool(),
        WriteFileTool(),
        ListFilesTool(),
        RunPytestTool(),
    ]
