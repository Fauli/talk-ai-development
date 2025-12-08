# crew.py
import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

from tools import get_all_tools, SPECS_PATH

load_dotenv()  # for OPENAI_API_KEY etc.


# --- Agents ----------------------------------------------------------------- #

def create_architect_agent(tools):
    return Agent(
        role="Software Architect",
        goal=(
            "Read the project specification and design a clean, modular Python architecture "
            "with a clear file structure and testing strategy."
        ),
        backstory=(
            "You are a seasoned software architect. You excel at turning vague product specs "
            "into precise, well-structured technical designs. You think in terms of modules, "
            "responsibilities, boundaries, and tests."
        ),
        tools=tools,  # can read SPECS and list workspace if needed
        verbose=True,
        allow_delegation=False,
    )


def create_implementer_agent(tools):
    return Agent(
        role="Senior Python Engineer",
        goal=(
            "Implement the full Python project in the workspace according to the architecture "
            "and specs, including tests."
        ),
        backstory=(
            "You are a highly pragmatic Python engineer who writes clean, idiomatic code. "
            "You favor clarity, modularity, and testability. You create all required files "
            "in the workspace and keep the structure organized."
        ),
        tools=tools,
        verbose=True,
        allow_delegation=False,
    )


def create_tester_agent(tools):
    return Agent(
        role="Test Engineer & Bug Fixer",
        goal=(
            "Ensure the project fully satisfies the spec and that all tests pass. "
            "Run pytest, analyze failures, fix the code or tests, and re-run until everything passes "
            "or there are no obvious fixes left."
        ),
        backstory=(
            "You are meticulous about quality. You run tests frequently, read stack traces carefully, "
            "and apply minimal, targeted fixes. You never introduce new functionality unless needed "
            "for the spec or to fix failing tests."
        ),
        tools=tools,
        verbose=True,
        allow_delegation=False,
    )


# --- Tasks ------------------------------------------------------------------ #

def create_plan_task(architect: Agent):
    description = f"""
1. Use the read_specs tool to read SPECS.md and understand the project requirements.
2. Extract the core responsibilities, external interfaces (CLI, API, etc.), and constraints.
3. Design a Python project architecture including:
   - A proposed directory structure under the 'workspace/' folder
   - Key modules and their responsibilities
   - Data flows between modules
   - A testing strategy (which modules get tests, at what level, etc.)
4. Make sure the design is realistic and implementable in a single session.

Output a clear, concise design document that the engineers can follow.
"""
    return Task(
        description=description,
        agent=architect,
        expected_output=(
            "A detailed design document with:\n"
            "- A bullet list of features and requirements from SPECS.md\n"
            "- A directory tree for the workspace\n"
            "- A list of modules and their responsibilities\n"
            "- A test plan (which tests to create, how they are organized)\n"
        ),
    )


def create_implementation_task(implementer: Agent):
    description = """
Using the design produced by the architect and the content of SPECS.md:

1. Create all necessary Python modules, packages, and support files in the 'workspace/' directory.
2. Implement the functionality as described in SPECS.md and the design.
3. Follow these rules:
   - Use idiomatic Python, with type hints where helpful.
   - Keep functions small and focused.
   - Document non-trivial functions/classes with short docstrings.
4. Create tests using pytest:
   - Place tests under 'tests/' in the workspace.
   - Ensure tests cover core behavior and edge cases mentioned in the spec.
5. Use the write_file tool to write code and test files, and list_files / read_file to inspect them.

Do NOT run pytest in this task; that is the tester's job.
"""
    return Task(
        description=description,
        agent=implementer,
        expected_output=(
            "All project source files and tests created in the workspace, "
            "ready to be executed with pytest."
        ),
    )


def create_test_and_fix_task(tester: Agent):
    description = """
Your job is to verify and harden the project.

1. Use the run_pytest tool to run the test suite in the workspace.
2. If tests fail or errors occur:
   - Inspect the error messages and stack traces.
   - Use read_file to open the relevant files.
   - Make targeted fixes using write_file.
   - Re-run run_pytest to confirm that the issue is resolved.
3. Repeat this loop until:
   - pytest exits with return code 0 (all tests pass), OR
   - You believe further automated fixes are not obvious or safe.
4. Also check that the behavior matches SPECS.md (via read_specs), and if there is a mismatch, fix code/tests accordingly.

In your final answer, provide:
- A short summary of the test runs (how many times, high-level issues fixed).
- The final pytest result.
- A brief checklist of how the implementation satisfies the spec.
"""
    return Task(
        description=description,
        agent=tester,
        expected_output=(
            "A final report that all tests pass or a clear explanation of remaining failures, "
            "plus a summary of how the implementation aligns with the specification."
        ),
    )


# --- Crew factory ----------------------------------------------------------- #

def create_crew():
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
        process=Process.sequential,  # plan -> implement -> test/fix
        verbose=True,
    )
    return crew


def main():
    if not os.path.exists(SPECS_PATH):
        raise SystemExit("SPECS.md not found. Please create SPECS.md next to crew.py.")

    crew = create_crew()
    result = crew.kickoff()
    print("\n=== FINAL RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()
