---
name: systems-thinking
description: Apply systems thinking to every engineering decision — trace state ownership, feedback loops, and deletion blast radius before writing, reviewing, or debugging code. Integrates existing skills (debugging, code review, security audit, planning) into a unified systems lens.
category: software-development
tags: [systems-thinking, architecture, debugging, code-review, planning, design]
---

# Systems Thinking for Software Engineering

## When to Load

Load this skill when:
- Starting a new feature or refactor — "design before you prompt"
- Debugging a mysterious failure — trace the system, not just the code
- Reviewing a PR — check for systems-level concerns (state leaks, blind feedback, hidden coupling)
- Planning an architecture change — map blast radius before touching anything
- Auditing an AI-generated codebase — the jagged frontier assessment
- User says "trace this", "map the system", "what's the blast radius", "where does state live"

## Core Framework

> **AI replaces typing. It doesn't replace thinking in systems.**

Based on Hak's systems thinking thesis and Peter Naur's "Programming as Theory Building" (1985):
The code is just the shadow — the real program is the mental model in your head. AI generates the shadow, but you must build the theory.

### The Three Questions

Before writing, reviewing, or debugging ANY change, answer these three:

**1. Where does state live?**
Who owns the truth? Database, cache, session, filesystem, external API? If two pieces each think they own it, you have a bug — you just haven't triggered it yet.

**2. Where does feedback live?**
What tells you the system is working or not? Logs, metrics, error tracking, health checks, user reports? If nothing tells you, the system is pretending to work.

**3. What breaks if I delete this?**
Can you trace the blast radius of any component in your head before touching it? Maps, services, jobs, listeners, queues, webhook subscribers — trace them all.

### The Deletion Test

Pick any component and ask: "If I delete this, what breaks and how badly?"
- If you can't answer, you don't understand the system — study first, then act.
- This is the litmus test for whether you've built the theory or just accepted the shadow.

## Integration with Existing Skills

| When you… | Load this + existing skill | Systems thinking adds |
|---|---|---|
| Debugging a bug | `systems-thinking` + `systematic-debugging` | Trace state ownership to find latent bugs, map feedback gaps causing silent failures |
| Reviewing a PR | `systems-thinking` + `requesting-code-review` | Check for state leaks, missing feedback, hidden coupling, blast radius not considered |
| Writing a plan | `systems-thinking` + `writing-plans` or `plan` | Map component boundaries first; mark where state lives and feedback surfaces in the plan |
| Security audit | `systems-thinking` + `code-security-audit` | Trace auth boundary ownership, feedback for breaches, blast radius of a compromise |
| Spec-driven dev | `systems-thinking` + `openspec` | Add failure modes and state diagram to the spec |
| Validating an idea | `systems-thinking` + `spike` | Ask the three questions before building the spike — targets the experiment |
| Subagent work | `systems-thinking` + `subagent-driven-development` | Include the three questions in delegation context so subagents trace the system too |

## Workflows

### Workflow A: Design Before You Prompt

When starting a new feature or significant change:

1. **Draw the system** — on paper or markdown, map:
   - Components (services, controllers, models, jobs, listeners)
   - State boundaries (database tables, Redis keys, external APIs)
   - Data flows (arrows between components)
   - Feedback loops (logs, events, webhooks, notifications)
2. **Answer the three questions** — write them down
3. **Run the deletion test** on each new component
4. **Write the spec** (load `openspec` or `writing-plans`) with the system map embedded
5. **Prompt the AI** — now you know what to build, not just how to prompt

### Workflow B: Debugging with Systems Thinking

When a bug report comes in and `systematic-debugging` alone isn't working:

1. **Map the state** — trace every place the relevant data lives. Is there a stale cache? Race condition between two state owners? Eventual consistency delay?
2. **Map the feedback** — does the bug reach logs? Error tracking? User-facing errors? If it's silent, that's a separate system failure.
3. **Trace the blast radius** — what else depends on the failing component?
4. **Fix the system, not just the symptom** — a race condition fix without adding a state owner or a cache with TTL isn't a fix.
5. **Add the missing feedback** — if this bug was silent, add monitoring so the next one isn't.

### Workflow C: Code Review with Systems Thinking

Before approving any PR (add these after `requesting-code-review` checks pass):

1. **State check** — does this change introduce a second owner for state that already has an owner? Does it assume state is fresh when it might be stale?
2. **Feedback check** — does this change add new failure modes without corresponding logs/metrics? Can you tell if this new code is working in production?
3. **Deletion check** — if someone deletes this new method/class/service tomorrow, what breaks? Is it obvious from the code?
4. **AI-generated code check** — if AI wrote any part of this:
   - Did the author verify correctness, not just accept output?
   - Are there security vulnerabilities the model might have quietly introduced?
   - Does the author demonstrate understanding (comments, alternative decisions considered)?

### Workflow D: AI-Generated Code Audit

When auditing a codebase built primarily with AI tools (Lovable, Bolt, Cursor, Claude Code):

1. **Find the single-source-of-truth violations** — AI tools tend to duplicate state logic across files. Search for redundant caching, duplicate database writes, conflicting validations.
2. **Find the feedback gaps** — AI rarely adds error handling, logging, or monitoring. Search for bare `try/catch` with empty blocks, missing `logger`, missing health check endpoints.
3. **Find the coupling** — AI-generated code often puts everything in one file (the "7000-line-file" anti-pattern). Check for tight coupling between unrelated concerns.
4. **Run the deletion test on every integration point** — webhook receivers, queue workers, third-party API clients. These are where AI-generated code fails most.
5. **Document findings** in the project's CLAUDE.md or CONTEXT.md so the next agent doesn't repeat the same patterns.

## The Jagged Frontier Assessment

Harvard's "jagged frontier" — AI is sharp in some areas and dull in others. For each task, rate:

| Dimension | AI is good at | AI is bad at | You must verify |
|---|---|---|---|
| Boilerplate | CRUD routes, migrations, form fields | Edge cases, error paths, state transitions | Validation logic, error handling |
| Patterns | Standard design patterns, framework conventions | Novel architecture, cross-cutting concerns | System integration, coupling |
| Testing | Unit tests for simple functions | Integration tests, race condition tests | State-dependent tests, async behaviour |
| Security | Common vulnerability patterns | Business logic flaws, auth boundaries | Authorization, data ownership |

## The New Literacy

In the age of agentic engineering:
- **Knowing where the jagged frontier sits** — what the model nails vs what it quietly gets wrong — is now a core developer skill
- **Spec-driven workflows, coding agents, agent harnesses** are the stack now
- **Generalists who can hold the whole system in their head** have the advantage — AI handles depth in any lane, but can't see the big picture

## Connection to Harness Engineering

The three questions map directly to the harness engineering layers (Cole Medin / Archon):

| Systems Thinking Question | Harness Engineering Equivalent |
|---|---|
| Where does state live? | Built-in layer vs AI layer — who owns the context? |
| Where does feedback live? | Hooks (post-edit lint, stop validation), sensors (test results, review agents) |
| What breaks if I delete this? | Blast radius of removing a skill, hook, or MCP server from the AI layer |

The "feed-forward loop" from harness engineering (session failures → evolving principles → next session's guardrails) is systems thinking applied to agent context management. See [[pages/harness-engineering-cole-medin]], [[glossary/harness-engineering-layers]], [[glossary/agent-hooks-and-sensors]].

## References

- LLM wiki: pages/systems-thinking-ai-age, glossary/systems-thinking, glossary/programming-as-theory-building
- `systematic-debugging` — 4-phase debugging skill
- `requesting-code-review` — pre-commit review skill
- `code-security-audit` — OWASP security audit skill
- `writing-plans` — implementation planning skill

## In the Wild

This skill's framework is baked into Pi's global AGENTS.md (`~/.pi/agent/AGENTS.md`):
- **Rule 1** = Systems Thinking (three questions + deletion test)
- **Rule 5** = Stop validation (don't trust "done" signal)
- **Rule 6** = Feed-forward (every failure evolves context)
- **Rule 4** = DOX breadcrumbs (document durable boundaries)

If you're working in a Pi coding agent session, these rules are already active — this skill adds the deeper workflows (Debugging, Code Review, AI Code Audit) and the jagged frontier assessment.
