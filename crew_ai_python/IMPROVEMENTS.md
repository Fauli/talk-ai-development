# Potential Improvements

This document lists potential improvements and known limitations of the CrewAI PixelPet demo.

---

## Memory & Embeddings

**Issue:** `memory=True` in crew.py requires OpenAI API key for ChromaDB embeddings, even though we use Claude/Anthropic for the LLM.

**Options:**
1. Disable memory (`memory=False`) - simplest, removes OpenAI dependency
2. Configure local embeddings (e.g., sentence-transformers)
3. Keep dual API keys (current approach)

**Impact:** Low - context is already passed via TODO.md and STATUS.json

---

## Agent Tools

### Missing Tools
- **delete_file** - Remove files from workspace (for cleanup/refactoring)
- **search_file** - Search within files (grep-like functionality)
- **run_python** - Execute arbitrary Python code for debugging

### Tool Improvements
- **pip_install** - Could cache installed packages to avoid re-installing
- **run_pytest** - Could parse output and return structured results
- **run_app** - Could do a basic HTTP health check, not just import test

---

## Iteration Loop

### Timeout/Cost Limits
- No maximum token/cost limit per iteration
- No timeout for individual agent tasks
- Could add early exit if stuck in a loop

### Better Error Detection
- Detect circular errors (same error appearing repeatedly)
- Classify errors (import error vs test failure vs syntax error)
- Prioritize fixing blocking errors first

---

## SPECS Improvements

### More Explicit Requirements
- Exact API response schemas (JSON structure)
- Error response format standardization
- Database migration handling

### Testing
- Minimum test coverage requirement
- End-to-end test requirement (full user flow)
- Performance/load testing specs

---

## Generated App Quality

### Security
- CSRF protection for forms
- Rate limiting on auth endpoints
- Password strength requirements
- Secure cookie settings (SameSite, Secure flags)

### Features
- Password reset flow
- Email verification
- Pet deletion/reset option
- Multiple save slots

### UX
- Loading states for actions
- Optimistic UI updates
- Better error messages to user
- Mobile responsiveness testing

---

## Developer Experience

### Documentation
- API documentation (OpenAPI/Swagger already available via FastAPI)
- Architecture diagram
- Sequence diagrams for auth flow

### Tooling
- Pre-commit hooks for linting
- CI/CD pipeline example
- Docker support for the generated app
- Hot reload for templates

---

## CrewAI Configuration

### Agent Tuning
- Temperature settings per agent (lower for Implementer?)
- Max retries per agent
- Agent-specific system prompts

### Observability
- Token usage tracking per agent
- Time tracking per task
- Success/failure metrics dashboard

---

## Priority Ranking

| Improvement | Impact | Effort |
|-------------|--------|--------|
| Remove OpenAI dependency | Medium | Low |
| Add delete_file tool | Low | Low |
| Circular error detection | High | Medium |
| Cost/token limits | Medium | Medium |
| Security hardening | High | High |
