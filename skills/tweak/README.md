# Tweak

> Lightweight change planning for AI coding agents. Turn "I want to change X"
> into a self-contained, four-artifact plan that a separate agent or person can
> execute with zero context — then fold the results into a living system spec.

Tweak is an **AI agent skill**, not an application. It is a single instruction
file (`SKILL.md`) that teaches any compatible agent to plan changes the same
> a senior engineer would: recon the code first, state assumptions explicitly,
> trace blast radius, and match the repo's own conventions.

It lives in the gap between **ad-hoc notes** (more structure than a sticky note)
and **[OpenSpec](https://github.com/Fission-AI/OpenSpec)** (lighter — no CLI, no
schemas, no tool adapters, nothing to install).

---

## What it produces

Every change gets exactly four Markdown files, written in order:

| Artifact | Answers | One-liner |
|----------|---------|-----------|
| `proposal.md` | **Why** | Intent, problem, assumptions, success criteria, capabilities |
| `specs.md` | **What** | Delta-style behavior contract keyed by capability |
| `design.md` | **How** | File-level approach, data structures, blast radius |
| `tasks.md` | **In what order** | Ordered, verifiable steps with real `Verify:` commands |

A change is **READY** when all four exist; **DONE** when the task checklist
passes; **ARCHIVED** when the delta specs have been folded into the system-wide
source of truth.

## The archive step — why it matters

Most planning tools stop at "here's a plan." Tweak goes one step further: on
archive, each change's delta specs are **merged into a single system-wide spec**
(`specs/<capability>.md`). After twenty changes you don't have twenty
tombstones — you have one maintained answer to *"what does this system do?"*

The merge is a deterministic five-action checklist (no CLI, no validator) — see
[`references/archive.md`](references/archive.md).

## How to use it

Tweak is triggered by intent words: **tweak**, *plan change*, *proposal*,
*design doc*, *RFC*, *change doc*, *scaffold feature*, *change set*.

1. **Install the skill** into your agent's skills directory:

   ```bash
   git clone https://github.com/rcdelfin/agentkit ~/.agents
   ```

   Tweak lives at `~/.agents/skills/tweak/`. Adjust the path to wherever your
   agent looks for skills — e.g. `~/.claude/skills/`, `~/.codex/skills/`, or a
   project-local `.agents/skills/`.

2. **Ask your agent to plan a change.** For example:

   > *Tweak: I want to add per-tier rate limiting to the public API.*

   The agent will walk you through confirming scope and slug, then produce the
   four artifacts under your repo's change-planning folder.

3. **Point a fresh agent (or a teammate) at the folder.** Every artifact is
   self-contained — it carries the drift SHA, frozen date, and all the context
   needed to execute without re-reading the original conversation.

### Where plans get stored

Tweak resolves an **effective root** the first time it runs, with this
precedence (first match wins):

1. `<repo>/plans/AGENTS.md` exists → use `plans/` (already bootstrapped).
2. `<repo>/plans/` has unrelated content → use `plans/tweaks/` (coexist).
3. `<repo>/plans/` is absent/empty/README-only → use `plans/`.
4. None of the above → use `<repo>/docs/tweaks/`.

Override entirely by naming a path in your message (*"store under `rfcs/`"*).

## Project layout

```
tweak/
├── SKILL.md                  ← the skill definition (read this first)
├── references/               ← per-artifact templates + the archive checklist
│   ├── proposal.md
│   ├── specs.md
│   ├── design.md
│   ├── tasks.md
│   ├── index.md              ← the changes-index template
│   ├── archive.md            ← the five-action archive step
│   └── agents-template.md    ← AGENTS.md bootstrapped into each root
└── examples/
    └── add-rate-limiting/    ← a complete worked example (all four artifacts)
```

## What it won't do

- **It never modifies source code.** Tweak is a *planning* skill — it produces
  Markdown only. A separate step (you, or another agent) implements the tasks.
- **It has no CLI, validator, or apply phase.** If you want schema-driven
  validation, apply-phase task tracking, or tool integrations for 30+ agents,
  use [OpenSpec](https://github.com/Fission-AI/OpenSpec) — Tweak is the
  standalone, zero-install fallback.
- **It's not a task board.** For tracking in-flight implementation across many
  changes, reach for a dedicated tracker.
- **It's not a repo-wide audit tool.** For "find things to improve," use a
  dedicated audit workflow.

## How it compares

| | Ad-hoc notes | **Tweak** | OpenSpec |
|---|---|---|---|
| Structure | Freeform | Same four artifacts, every time | Schemas + artifact DAG |
| System spec | — | Delta-spec archive (manual) | Delta-spec archive (CLI) |
| Install | — | Clone one file | `npm i -g @fission-ai/openspec` |
| Automation | — | None | Apply, validate, archive CLI |
| Best for | Quick ideas | Most teams, most changes | Large/regulated codebases |

## Principles

- **Recon is not optional** — read the code before writing about it.
- **State assumptions explicitly** — silent assumptions become broken plans.
- **Trace blast radius** — name what could break, and what looks related but is
  intentionally untouched.
- **Match the repo, don't invent** — every convention claim cites an exemplar
  `file:line`.
- **Be precise, not confident** — *"handles the happy path; the race at line
  130 needs investigation"* is a plan. *"Should work"* is not.

## Acknowledgements

Inspired by [OpenSpec](https://github.com/Fission-AI/OpenSpec) (artifact DAG,
change directory, delta-spec archive) and the
[improve](https://github.com/anthropics/skills) skill (self-contained plans,
hard rules, verification gates). The archive step is a manual, standalone port
of `openspec archive`.

## License

MIT
