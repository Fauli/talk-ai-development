# crew.py
import os
import subprocess
import json
from datetime import datetime

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

from tools import get_all_tools, SPECS_PATH

load_dotenv()  # for ANTHROPIC_API_KEY

# Configure Anthropic Claude
llm = LLM(model="anthropic/claude-sonnet-4-20250514", temperature=0.7)


# --- Agents ----------------------------------------------------------------- #


def create_architect_agent(tools):
    return Agent(
        role="Software Architect",
        goal=(
            "Read the PixelPet Tamagotchi-style web app specification and design "
            "a clean, modular Python / FastAPI architecture with a clear file "
            "structure and testing strategy."
        ),
        backstory=(
            "You are a seasoned software architect for web applications. "
            "You excel at turning product specs into precise, well-structured "
            "technical designs. You think in terms of modules, responsibilities, "
            "boundaries, and tests.\n\n"
            "For this project, you know it is a small but complete PixelPet web "
            "application with FastAPI backend, SQLite + SQLAlchemy, and simple "
            "HTML templates or a minimal frontend."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_implementer_agent(tools):
    return Agent(
        role="Senior Python Web Engineer",
        goal=(
            "Implement the full PixelPet FastAPI web application in the workspace "
            "according to the architecture and specs, including tests."
        ),
        backstory=(
            "You are a highly pragmatic Python engineer who writes clean, "
            "idiomatic web services. You use FastAPI, SQLAlchemy, and pytest "
            "comfortably. You design for clarity, modularity, and testability.\n\n"
            "You are implementing a Tamagotchi-style PixelPet app where users can "
            "log in, manage a single pet with hunger/energy/happiness, and "
            "interact through a small web UI."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_tester_agent(tools):
    return Agent(
        role="Test Engineer & Bug Fixer",
        goal=(
            "Ensure the PixelPet web application fully satisfies the spec and "
            "that all tests pass, and the FastAPI app can start without crashing."
        ),
        backstory=(
            "You are meticulous about quality and correctness in web backends. "
            "You run tests frequently, read stack traces carefully, and apply "
            "minimal, targeted fixes. You never introduce new functionality "
            "unless it is required by the spec or to fix a failing test.\n\n"
            "You know this app uses FastAPI, SQLAlchemy, and pytest, and you use "
            "the provided tools to run pytest and attempt to start the app."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


# --- Tasks ------------------------------------------------------------------ #


def create_plan_task(architect: Agent):
    description = f"""
You are the architect for a PixelPet (Tamagotchi-style) web application.

Steps:

1. Use the read_specs tool to read SPECS.md and fully understand the project
   requirements for the PixelPet app (including backend, frontend, persistence,
   and tests).

2. Extract the core responsibilities and constraints:
   - Web framework (FastAPI).
   - Database (SQLite + SQLAlchemy).
   - Auth, pet state machine, scheduling/decay logic, web UI, tests.

3. Design a Python project architecture under the 'workspace/' directory that
   follows these conventions:
   - Application package: 'app/'
   - Suggested minimal structure:
       app/
         __init__.py
         main.py              # FastAPI app, routers mounted here
         database.py          # SQLAlchemy setup, SessionLocal, Base
         models.py            # SQLAlchemy models (User, Pet)
         auth.py              # auth helpers, password hashing, dependency
         pet_service.py       # business logic for pet state transitions
         scheduler.py         # background task / decay logic if needed
         routes/
           __init__.py
           pets.py            # pet-related API routes
           users.py           # auth/user routes (optional)
         templates/
           base.html
           index.html
           pet.html
         static/
           css/
             style.css
           img/
             pixel_pet.png    # placeholder sprite
       tests/
         test_auth.py
         test_pet_logic.py
         test_routes.py

   - If the SPECS.md suggests a slightly different structure, adapt carefully
     but keep it similarly modular.

4. Include a testing strategy:
   - What tests to write.
   - Which modules they should target.
   - How to run tests (pytest).
   - Any fixtures/in-memory DB setup.

5. Make sure the design is realistic and implementable by a single engineer
   in one session.

Output a clear, concise design document that the implementer can follow.
"""
    return Task(
        description=description,
        agent=architect,
        expected_output=(
            "A detailed design document with:\n"
            "- A bullet list of features and requirements from SPECS.md\n"
            "- A directory tree for the workspace/app\n"
            "- A list of modules and their responsibilities\n"
            "- A test plan (which tests to create, how they are organized)\n"
        ),
    )


def create_implementation_task(implementer: Agent):
    description = """
You are the Senior Python Web Engineer implementing the PixelPet FastAPI app.

Context:
- You have the design produced by the architect (previous task output).
- You have access to SPECS.md through the read_specs tool.
- You are working inside the 'workspace/' directory.

Follow this process:

1. Project structure
   - First, create the basic folder structure and placeholder files using the
     write_file tool (they can be minimal at first).
   - Suggested structure (adapt if design changed):
       app/
         __init__.py
         main.py
         database.py
         models.py
         auth.py
         pet_service.py
         scheduler.py
         routes/
           __init__.py
           pets.py
           users.py
         templates/
           base.html
           index.html
           pet.html
         static/
           css/
             style.css
           img/
             pixel_pet.png
       tests/
         test_auth.py
         test_pet_logic.py
         test_routes.py

2. Implement backend logic
   - Configure FastAPI app in app/main.py.
   - Configure SQLite + SQLAlchemy in app/database.py.
   - Define User and Pet models in app/models.py according to the spec.
   - Implement authentication helpers in app/auth.py (password hashing, dependencies).
   - Implement pet state business logic (hunger, happiness, energy, decay,
     actions like feed/play/sleep, evolution) in app/pet_service.py.
   - Implement routes in app/routes/pets.py and app/routes/users.py (or similar),
     wiring them into FastAPI in app/main.py.
   - Implement a simple scheduler/decay mechanism in app/scheduler.py (e.g.,
     background tasks or approximate logic on each request).

3. Implement frontend/templates
   - Use Jinja2 templates in app/templates to render pet status, action buttons,
     and a simple login/registration page.
   - Keep it minimal but visually understandable (bars, labels, basic CSS).

4. Tests
   - Under tests/, create pytest-based tests:
     - Authentication logic (login/registration).
     - Pet state machine transitions and decay rules.
     - Basic route tests using FastAPI's TestClient.

5. Code quality
   - Use idiomatic, clean Python.
   - Use type hints for function signatures.
   - Add short docstrings for non-trivial functions and classes.
   - When modifying existing files, ALWAYS:
     - use list_files/read_file to inspect the current content;
     - then compute a minimal but complete new version and write it back with write_file.
   - Do NOT rewrite the entire project or delete important files unless it is
     clearly required.

6. Tools
   - Use write_file to create/modify files.
   - Use list_files to understand the current structure.
   - Use read_file to inspect existing code.

Important constraints:
- Do NOT run pytest or start the app in this task; that is the tester's job.
- Prefer incremental edits and small, focused modules.

Your final answer should briefly describe which files you created/updated and
what remains for testing.
"""
    return Task(
        description=description,
        agent=implementer,
        expected_output=(
            "All project source files and tests created in the workspace, "
            "ready to be executed with pytest. A short summary of the created "
            "files and their responsibilities."
        ),
    )


def create_test_and_fix_task(tester: Agent):
    description = """
You are the Test Engineer & Bug Fixer for the PixelPet FastAPI web app.

Your job is to verify and harden the project.

Definition of Done:
- pytest exits with return code 0 (all tests pass).
- The FastAPI app can be started (imported) without crashing.
- The behavior matches the key requirements from SPECS.md.

Process:

1. Initial understanding
   - Use list_files to see what files exist under workspace/.
   - Optionally use read_specs to refresh your understanding of the PixelPet spec.

2. Run tests
   - Use run_pytest (optionally with arguments like '-q') to run the test suite.
   - Carefully read the RETURN CODE, STDOUT, and STDERR.

3. If there are failures or errors:
   - Identify the most relevant error(s) from the pytest output.
   - Use read_file to open the involved source or test files.
   - Apply minimal, targeted fixes using write_file.
   - Avoid large rewrites; focus on the failing paths first.
   - Run run_pytest again to verify the fix.

4. Repeat:
   - Repeat this fix/test cycle as needed, but at most 8 times.
   - If tests are still failing after ~8 iterations or the remaining issues
     are too complex, stop and produce a clear report of remaining problems.

5. Verify app importability
   - Once pytest return code is 0, use run_app to attempt to import the FastAPI app.
   - Inspect the output to confirm that:
     - 'app.main' can be imported from the workspace.
     - a FastAPI instance named 'app' exists in that module.
   - If there are import errors or missing 'app', treat them like test failures:
     inspect files, fix, re-run run_app, and re-run run_pytest if necessary.

6. Alignment with SPECS.md
   - Optionally re-check SPECS.md and confirm that:
     - User has a pet with hunger/energy/happiness.
     - Pet actions (feed/play/sleep) behave as described.
     - Authentication and basic UI flow are consistent with the spec.
   - If there is a mismatch, fix code or tests accordingly (within reason).

Important constraints:
- Prefer multiple small, precise fixes over large refactors.
- Never delete large parts of the project unless clearly broken beyond repair.
- Focus first on making tests pass and the app start; extra polish is secondary.

Your final answer MUST include:
- A short summary of how many times you ran pytest and with what outcomes.
- The final pytest result (return code).
- Whether run_app indicates a successful startup.
- A brief checklist of how the implementation satisfies the main points of SPECS.md.
- If anything remains broken or incomplete, list it explicitly.

IMPORTANT: Before finishing, use write_file to create/update 'TODO.md' in the workspace with:
- Any remaining bugs or failing tests
- Missing features from SPECS.md
- Suggested next steps
This helps the next iteration know what to work on.
"""
    return Task(
        description=description,
        agent=tester,
        expected_output=(
            "A final QA report: number of pytest runs, remaining issues if any, "
            "confirmation that the app can start, and a checklist of spec coverage."
        ),
    )


# --- Fix implementation task (for subsequent iterations) -------------------- #


def create_fix_implementation_task(implementer: Agent, error_report: str):
    """Task for implementer to fix issues based on tester's error report."""
    description = f"""
You are the Senior Python Web Engineer. The tester found issues with your implementation.

TESTER'S ERROR REPORT:
{error_report}

Your job is to FIX these issues. Follow this process:

1. FIRST: Use read_file to check 'TODO.md' in the workspace - it contains the tester's
   notes about remaining bugs, missing features, and suggested fixes.

2. Read the error report above and identify the root causes.

3. Use list_files to see the current project structure.

4. Use read_file to examine the problematic files mentioned in the error report or TODO.md.

5. Apply targeted fixes using write_file:
   - Fix import errors
   - Fix missing dependencies
   - Fix logic bugs
   - Fix test failures
   - Ensure all required files exist

6. Do NOT rewrite everything from scratch. Make minimal, focused fixes.

7. After fixing, briefly summarize what you changed.

Important:
- Always read TODO.md first for context
- Focus on the errors mentioned in the report
- Read existing code before modifying
- Keep changes minimal and targeted
"""
    return Task(
        description=description,
        agent=implementer,
        expected_output=(
            "A summary of fixes applied to resolve the issues from the error report. "
            "List each file modified and what was changed."
        ),
    )


# --- Crew factories --------------------------------------------------------- #


def create_initial_crew():
    """First iteration: Architect → Implementer → Tester"""
    tools = get_all_tools()

    architect = create_architect_agent(tools)
    implementer = create_implementer_agent(tools)
    tester = create_tester_agent(tools)

    plan_task = create_plan_task(architect)
    implementation_task = create_implementation_task(implementer)
    test_task = create_test_and_fix_task(tester)

    crew = Crew(
        agents=[architect, implementer, tester],
        tasks=[plan_task, implementation_task, test_task],
        process=Process.sequential,
        memory=True,  # Enable persistent memory across runs
        verbose=True,
    )
    return crew


def create_fix_crew(error_report: str):
    """Subsequent iterations: Implementer (with errors) → Tester"""
    tools = get_all_tools()

    implementer = create_implementer_agent(tools)
    tester = create_tester_agent(tools)

    fix_task = create_fix_implementation_task(implementer, error_report)
    test_task = create_test_and_fix_task(tester)

    crew = Crew(
        agents=[implementer, tester],
        tasks=[fix_task, test_task],
        process=Process.sequential,
        memory=True,  # Enable persistent memory across runs
        verbose=True,
    )
    return crew


# --- Main loop with status tracking ----------------------------------------- #

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(PROJECT_ROOT, "STATUS.json")
WORKSPACE_ROOT = os.path.join(PROJECT_ROOT, "workspace")


def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {
        "iteration": 0,
        "phase": "initial",  # "initial" or "fixing"
        "last_error_report": None,
        "history": [],
        "completed": False
    }


def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def check_success():
    """Check if tests pass and app can be imported. Returns (success, tests_pass, app_works, error_details)"""
    error_details = []

    # Run pytest
    try:
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        tests_pass = result.returncode == 0
        if not tests_pass:
            error_details.append(f"PYTEST OUTPUT:\n{result.stdout}\n{result.stderr}")
    except Exception as e:
        tests_pass = False
        error_details.append(f"PYTEST ERROR: {e}")

    # Check app import
    try:
        import sys
        import importlib
        if WORKSPACE_ROOT not in sys.path:
            sys.path.insert(0, WORKSPACE_ROOT)
        importlib.invalidate_caches()
        # Clear cached modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("app"):
                del sys.modules[mod]
        module = importlib.import_module("app.main")
        app_works = hasattr(module, "app")
        if not app_works:
            error_details.append("APP ERROR: 'app' object not found in app.main")
    except Exception as e:
        app_works = False
        error_details.append(f"APP IMPORT ERROR: {e}")

    error_report = "\n\n".join(error_details) if error_details else None
    return tests_pass and app_works, tests_pass, app_works, error_report


def main():
    if not os.path.exists(SPECS_PATH):
        raise SystemExit("SPECS.md not found. Please create SPECS.md next to crew.py.")

    MAX_ITERATIONS = 10
    status = load_status()

    if status["completed"]:
        print("Project already completed! Delete STATUS.json to restart.")
        return

    while status["iteration"] < MAX_ITERATIONS:
        status["iteration"] += 1
        iteration = status["iteration"]

        print(f"\n{'='*60}")
        print(f"  ITERATION {iteration} / {MAX_ITERATIONS}")
        print(f"  Phase: {status['phase']}")
        print(f"{'='*60}\n")

        # Choose crew based on phase
        if status["phase"] == "initial":
            print("Running: Architect → Implementer → Tester")
            crew = create_initial_crew()
        else:
            print("Running: Implementer (fixing) → Tester")
            crew = create_fix_crew(status["last_error_report"] or "No previous error report")

        # Run the crew
        result = crew.kickoff()

        # Check success
        success, tests_pass, app_works, error_report = check_success()

        # Log this iteration
        status["history"].append({
            "iteration": iteration,
            "phase": status["phase"],
            "timestamp": datetime.now().isoformat(),
            "tests_pass": tests_pass,
            "app_works": app_works,
            "success": success
        })

        # Update phase and error report for next iteration
        status["phase"] = "fixing"  # After first run, always in fixing mode
        status["last_error_report"] = error_report
        save_status(status)

        print(f"\n--- Iteration {iteration} Result ---")
        print(f"Tests pass: {tests_pass}")
        print(f"App works:  {app_works}")
        print(f"Success:    {success}")

        if success:
            status["completed"] = True
            save_status(status)
            print("\n✅ PROJECT COMPLETE!")
            print(f"\n=== FINAL RESULT ===\n{result}")
            return

        print(f"\n⚠️  Not complete yet.")
        if error_report:
            print(f"\nError summary (will be passed to next iteration):\n{error_report[:500]}...")

    print(f"\n❌ Max iterations ({MAX_ITERATIONS}) reached without success.")
    print("Check STATUS.json for history. You can increase MAX_ITERATIONS or debug manually.")


if __name__ == "__main__":
    main()
