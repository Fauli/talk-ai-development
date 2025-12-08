# tools.py
import os
import subprocess
import traceback
from typing import List, Dict, Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, "workspace")
SPECS_PATH = os.path.join(PROJECT_ROOT, "SPECS.md")


def _ensure_workspace() -> None:
    os.makedirs(WORKSPACE_ROOT, exist_ok=True)


class EmptyInput(BaseModel):
    """Empty input schema."""
    pass


class FilePathInput(BaseModel):
    """Input schema for file path."""
    file_path: str = Field(description="Relative file path from workspace root")


class WriteFileInput(BaseModel):
    """Input schema for writing files."""
    path: str = Field(description="Relative file path from workspace root")
    content: str = Field(description="Content to write to the file")


class PytestInput(BaseModel):
    """Input schema for pytest."""
    extra_args: str = Field(default="", description="Extra pytest arguments")


class ReadSpecsTool(BaseTool):
    name: str = "read_specs"
    description: str = (
        "Reads and returns the full content of SPECS.md, which describes the "
        "project requirements."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        if not os.path.exists(SPECS_PATH):
            return "ERROR: SPECS.md not found next to crew.py."
        with open(SPECS_PATH, "r", encoding="utf-8") as f:
            return f.read()


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = (
        "Read the content of a text file from the workspace. "
        "Input should be a relative file path from the workspace root, "
        "e.g. 'app/main.py' or 'tests/test_pets.py'."
    )
    args_schema: Type[BaseModel] = FilePathInput

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
    name: str = "write_file"
    description: str = (
        "Write text content to a file in the workspace, overwriting if it exists. "
        "Always use read_file first when modifying an existing file, then apply a "
        "minimal diff and write the full updated content back."
    )
    args_schema: Type[BaseModel] = WriteFileInput

    def _run(self, path: str, content: str) -> str:
        _ensure_workspace()
        if not path or content is None:
            return "Error: 'path' and 'content' required."
        safe_path = os.path.normpath(os.path.join(WORKSPACE_ROOT, path))
        if not safe_path.startswith(WORKSPACE_ROOT):
            return "Security error: path outside workspace."

        os.makedirs(os.path.dirname(safe_path) or ".", exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote file {path} (length {len(content)} chars)."


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = (
        "List all files under the workspace directory, relative paths. "
        "Use this to understand the current project structure."
    )
    args_schema: Type[BaseModel] = EmptyInput

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
    name: str = "run_pytest"
    description: str = (
        "Run pytest in the workspace and return the output. "
        "Use this to verify tests. If tests fail, read and fix the offending files "
        "and run again.\n\n"
        "Optional input: a string with extra pytest arguments, e.g. '-q' or 'tests/'."
    )
    args_schema: Type[BaseModel] = PytestInput

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
            return (
                "ERROR: pytest command not found. Please ensure pytest is installed "
                "in the current Python environment."
            )

        return (
            f"COMMAND: {' '.join(cmd)}\n"
            f"RETURN CODE: {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )


class RunAppTool(BaseTool):
    name: str = "run_app"
    description: str = (
        "Check that the FastAPI app can be imported successfully. "
        "This tool attempts to import 'app.main' from the workspace and access a "
        "FastAPI instance named 'app'.\n\n"
        "It does NOT start a real HTTP server, it only verifies that the module "
        "imports without runtime errors and that an 'app' object exists."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        _ensure_workspace()
        import sys
        import importlib

        original_sys_path = list(sys.path)
        try:
            if WORKSPACE_ROOT not in sys.path:
                sys.path.insert(0, WORKSPACE_ROOT)

            try:
                module = importlib.import_module("app.main")
            except Exception as e:
                tb = traceback.format_exc()
                return (
                    "Failed to import 'app.main'.\n"
                    f"Error: {e}\n\n"
                    f"Traceback:\n{tb}"
                )

            app_obj = getattr(module, "app", None)
            if app_obj is None:
                return (
                    "Imported 'app.main' successfully, but no attribute 'app' was found. "
                    "Make sure you expose your FastAPI instance as 'app' in app/main.py."
                )

            return (
                "Successfully imported 'app.main' and found a FastAPI 'app' object. "
                "This indicates the application can start without import-time errors."
            )
        finally:
            sys.path = original_sys_path


def get_all_tools():
    """Convenience for crew.py."""
    return [
        ReadSpecsTool(),
        ReadFileTool(),
        WriteFileTool(),
        ListFilesTool(),
        RunPytestTool(),
        RunAppTool(),
    ]
