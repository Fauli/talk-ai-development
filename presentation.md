# **Agentic Programming**
### When Software Starts Writing Software

**A talk for new programmers**

💡 *How we got here · What’s happening now · Where it’s going*

---

## Who Am I?

- Franz Faul    
- Working with AI-assisted and agentic development
- Passionate about how software development is changing

👉 This talk will give you a mental map of the shift happening in programming.

---

## Warm-Up Question

**How many of you already use AI when writing code?**

- 🟩 Regularly
- 🟨 A few times
- 🟥 Never

💬 *Whatever your answer — it will matter in your career.*

---

## Agenda

1. 🔙 History — how we got here  
2. 🧠 LLMs & coding assistants  
3. 🤖 From assistants → agents  
4. 🧰 Current tools & examples  
5. ⚠️ Challenges, risks & ethics  
6. 🚀 Future & your role

---

# Part 1  
## How We Got Here

---

## From Punch Cards to Prompting

Programming keeps increasing in **abstraction**:

- Machine code → Assembly  
- C → Java → Frameworks  
- Cloud → Containers → DevOps  
- AI-assisted programming

🧠 Each step moves us away from syntax toward ideas.

---

## The 3 Eras of Software (Karpathy)

| Era | Description |
|------|------------|
| **Software 1.0** | Humans write code |
| **Software 2.0** | Humans train models (NNs = code) |
| **Software 3.0** | Humans write *goals & prompts* |

🔥 Today, we are transitioning between 2.0 → 3.0.

---

## Why AI for Code?

Code is:

- Structured  
- Repetitive  
- Publicly available (GitHub, docs, StackOverflow)  
- Has rules and patterns

Perfect learning material for large language models.

---

## Timeline: How We Got Here

- 2010–2018 → Deep learning boom  
- 2020 → GPT-3: first big general language model  
- 2022 → ChatGPT gives coding superpowers  
- 2023–2025 → Agentic AI appears (AutoGPT, Devin, CrewAI)

---

# Part 2  
## LLMs & Coding Assistants

---

## What Is an LLM?

A model trained to **predict the next word/token**.

It learns from:

- Natural language  
- Code repositories  
- Documentation  
- Patterns and structure

⚙️ Not human reasoning — but powerful pattern synthesis.

---

## Coding Assistants

Examples:

- GitHub Copilot  
- ChatGPT  
- Cursor  
- Codeium

They can:

- Generate scaffolding  
- Suggest fixes  
- Write tests  
- Explain unfamiliar code

👉 Still **reactive** — you ask, it answers.

---

## The New Workflow

Old way:

```

Google → StackOverflow → copy/paste → debug → repeat

```

New way:

```

Describe intent → AI drafts → You review → iterate

```

You shift from **typing code** to **thinking about code**.

---

# Part 3  
## From Assistants to Agents

---

## What Is an AI Agent?

> 🚀 **An agent is an AI system that can pursue a goal autonomously using tools, memory, and feedback loops.**

Unlike assistants, agents:

- Plan  
- Execute  
- Observe and evaluate  
- Iterate

---

## Assistant vs Agent

| Feature | Assistant | Agent |
|--------|-----------|--------|
| Input | Prompt | Goal |
| Behavior | One response | Multi-step loop |
| Memory | Short | Long-term + contextual |
| Tools | Limited | Can run code, tests, browser, repo |
| Autonomy | Low | Medium–High |

---

## The Agent Loop

1. 🎯 Receive a goal  
2. 🧩 Plan steps  
3. 🛠️ Execute actions  
4. 👀 Observe results  
5. 🔁 Reflect & adjust  
6. 🏁 Repeat until done

---

## Anatomy of a Coding Agent

- 🧠 **LLM brain**  
- 🧰 **Tool layer** (FS, CLI, browser, APIs)  
- 💾 **Memory** (context + vector stores)  
- 🗂️ **Orchestration framework** (LangChain, CrewAI, ReAct)

---

# Part 4  
## Current Tools & Examples

---

## Ecosystem Snapshot (2025)

- AutoGPT / BabyAGI *(early prototypes)*
- LangChain *(general agent framework)*
- CrewAI *(multi-agent collaboration)*
- OpenDevin / Devin *(autonomous software development)*

The space is evolving *fast.*

---

## “AI Software Engineer” Examples

Claims include:

- Understand a repository  
- Plan features  
- Modify multiple files  
- Run tests  
- Create PRs

👉 Still requires human review — think **intern**, not senior developer.

---

## Example: Real Task

> “Add logging to all API endpoints and return standardized error JSON.”

Agent steps:

- Scans repo  
- Proposes plan  
- Modifies multiple files  
- Runs tests  
- Iterates based on failures

This goes beyond autocomplete.

---

# Part 5  
## Limitations, Risks & Ethics

---

## Where Agents Fail

- Hallucinated or incorrect solutions  
- Infinite loops  
- False confidence  
- Lack of domain knowledge  
- Overfitting to patterns instead of reasoning

---

## Security & Reliability Concerns

- Vulnerabilities  
- Dependencies injected silently  
- Licensing ambiguity  
- Insecure patterns copied blindly

🛑 Trust — but verify.

---

## Human in the Loop

You are still responsible for:

- Architecture  
- Code review  
- Testing  
- Production quality  
- Ethics & safety

👩‍💻 Agents accelerate **engineering** — they don’t replace it.

---

# Part 6  
## The Future & Your Role

---

## What’s Next?

- Repo-aware agents  
- Multi-agent teams (architect + coder + tester)  
- Continuous self-maintaining codebases  
- “Vibe coding” — describe the *feeling*, not the syntax

---

## What Skills Matter Now?

- Problem solving  
- System design  
- Reading and validating code  
- Communicating intent clearly  
- Understanding trade-offs & architecture

AI writes faster — but *you* decide **what should be written.**

---

# Q&A + Resources

📚 Recommended paths:

- LangChain / CrewAI tutorials  
- Karpathy: Software 2.0 and 3.0  
- Try using AI for your next project — but review everything.

---

## Thanks ✨

Ready to explore the future of programming?

