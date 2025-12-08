#!/bin/bash
cd "$(dirname "$0")/workspace"

echo "Checking if app is ready..."

# Check if app can be imported
python3 -c "from app.main import app; print('App import: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "App import: FAILED"
    exit 1
fi

# Check if tests pass
pytest -q 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Tests: PASSED"
    echo ""
    echo "Ready! Run with:"
    echo "  cd workspace && uvicorn app.main:app --reload --port 1337"
else
    echo "Tests: FAILED"
    exit 1
fi
