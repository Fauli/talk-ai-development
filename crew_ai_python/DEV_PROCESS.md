# CrewAI Development Process

This document explains how the automated development crew works.

## Overview

The crew builds a PixelPet (Tamagotchi-style) web app based on `SPECS.md`. It runs in iterations until tests pass and the app works, or until max iterations are reached.

## Agents

| Agent | Role | Tools |
|-------|------|-------|
| **Architect** | Designs the project structure and testing strategy | read_specs, list_files |
| **Implementer** | Writes the actual code | read_specs, read_file, write_file, list_files |
| **Tester** | Runs tests, fixes bugs, validates the app | All tools + run_pytest, run_app |

## Iteration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      ITERATION 1 (initial)                  │
├─────────────────────────────────────────────────────────────┤
│  Architect ──► Implementer ──► Tester                       │
│     │              │              │                         │
│     │              │              ▼                         │
│  Design         Build        Test & Fix (up to 8x)          │
│  structure      code         Write TODO.md                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    check_success()?
                     /           \
                   Yes            No
                    │              │
                    ▼              ▼
              ✅ COMPLETE    Save error report
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   ITERATION 2+ (fixing)                     │
├─────────────────────────────────────────────────────────────┤
│  Implementer ──────────────────► Tester                     │
│       │                            │                        │
│       │                            ▼                        │
│  Read TODO.md                 Test & Fix                    │
│  Read error report            Update TODO.md                │
│  Apply fixes                                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         (repeat)
```

## Memory & Context

Agents maintain context between iterations through:

1. **CrewAI Memory** (`memory=True`)
   - Built-in semantic memory
   - Persists agent knowledge across runs

2. **TODO.md** (workspace file)
   - Written by Tester at end of each iteration
   - Contains: remaining bugs, missing features, suggested fixes
   - Read by Implementer at start of fix iterations

3. **Error Report** (STATUS.json)
   - Pytest output and import errors
   - Passed directly to Implementer's task description

## Files

| File | Purpose |
|------|---------|
| `SPECS.md` | Project requirements (input) |
| `STATUS.json` | Iteration tracking, error history |
| `workspace/` | Generated project code |
| `workspace/TODO.md` | Agent-written progress tracking |

## STATUS.json Structure

```json
{
  "iteration": 2,
  "phase": "fixing",
  "last_error_report": "PYTEST OUTPUT:\n...",
  "completed": false,
  "history": [
    {
      "iteration": 1,
      "phase": "initial",
      "timestamp": "2024-01-15T10:30:00",
      "tests_pass": false,
      "app_works": false,
      "success": false
    }
  ]
}
```

## Success Criteria

The loop exits successfully when both:
- `pytest` returns exit code 0 (all tests pass)
- `app.main` can be imported and has an `app` object

## Running

```bash
cd crew_ai_python
source .venv/bin/activate
python crew.py
```

To restart from scratch: delete `STATUS.json` and `workspace/`

## Configuration

- `MAX_ITERATIONS = 10` in `crew.py`
- LLM: `anthropic/claude-sonnet-4-20250514` (configurable)
- Tester internal fix cycles: 8 (in task description)

## Running the Generated App

Once the crew completes successfully, the PixelPet app is in `workspace/`. To run it:

```bash
cd crew_ai_python/workspace

# Install app dependencies (if requirements.txt exists)
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart jose

# Run the FastAPI server
uvicorn app.main:app --reload --port 1337
```

Then open http://localhost:1337 in your browser.

### Running Tests Manually

```bash
cd crew_ai_python/workspace
pytest -v
```

### Project Structure (typical)

```
workspace/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # SQLite + SQLAlchemy setup
│   ├── models.py        # User, Pet models
│   ├── auth.py          # Authentication
│   ├── pet_service.py   # Pet logic (feed, play, sleep)
│   ├── routes/
│   │   ├── pets.py
│   │   └── users.py
│   ├── templates/       # Jinja2 HTML templates
│   └── static/          # CSS, images
└── tests/
    ├── test_auth.py
    ├── test_pet_logic.py
    └── test_routes.py
```
