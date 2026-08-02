---
name: systems-thinking
description: Apply a deeper systems lens when state ownership, correctness feedback, or change blast radius is unclear. Use for cross-boundary changes, architecture work, difficult debugging, and reviews of AI-generated code involving hidden coupling; the core lens already applies through SYSTEM.md.
category: software-development
tags: [systems-thinking, architecture, debugging, code-review, planning, design]
---

# Systems Thinking for Software Engineering

Use this skill to deepen the systems-thinking principle in
`../../instructions/SYSTEM.md`. The canonical instructions remain authoritative;
this skill adds an operational method and does not replace the normal workflow.

## Conceptual Foundation

A system is not merely a collection of parts. It is the pattern of how those
parts affect one another over time. A locally correct component can still make
the whole system incoherent when ownership, feedback, or dependencies are wrong.

Following Peter Naur's idea of programming as theory building, the code is not
the complete program. The maintained theory is the understanding of:

- which parts exist and how they connect
- why those connections and boundaries were chosen
- how data and effects move through the system over time
- what changes, fails, or disappears when one part is altered

Code is an expression of that theory. AI can generate the expression, but that
does not establish understanding or correctness. Generated code therefore
remains a proposal to inspect, understand, and verify.

Unlike a deterministic compiler, an LLM does not guarantee a correct
translation from intent to implementation. It may produce strong boilerplate
while quietly missing a business rule, race, security boundary, or failure path.
This uneven capability is the **jagged frontier**. Systems judgment means knowing
which output is routine and which output requires deeper scrutiny.

> AI can reduce typing. It does not remove responsibility for the system.

## When to Load

Load this skill when one or more of these are true:

- State crosses a database, cache, queue, session, filesystem, or external API.
- A change spans multiple components or alters an architectural boundary.
- A failure involves stale data, races, retries, asynchronous work, or unclear
  ownership.
- A review needs to trace hidden coupling or transitive impact beyond the diff.
- AI-generated code is substantial enough that its system role is not yet
  understood.
- The user asks where state lives, how correctness is known, or what the blast
  radius is.

Do not load it only to restate the core lens for a small, localized change whose
state, feedback, and blast radius are already clear. Capability routing should
still use the smallest sufficient skill set.

## Core Lens

Before modifying existing code, answer only as deeply as the risk requires.
These questions should be explainable before implementation; verification still
requires appropriate evidence afterward.

### State — What owns the source of truth?

Identify:

- the authoritative owner
- who can read and write it
- copies such as caches, projections, or client state
- synchronization, consistency, and lifecycle boundaries
- how the state changes over time

Multiple representations are not automatically multiple owners. The important
question is which representation is authoritative and how the others converge.
If two components independently believe they own the same truth, treat that as a
latent defect until the ownership contract proves otherwise.

### Feedback — How do we know the system is working?

Distinguish two forms of feedback:

- **Development evidence:** tests, type checks, linting, compilation, and runtime
  validation that verify the change.
- **Operational signals:** errors, logs, metrics, alerts, health checks, and
  user-visible outcomes that reveal production behavior.

Identify failures that may be silent, swallowed, delayed, or misleading. Do not
add observability speculatively, but do not call a system reliable when material
failure modes have no visible signal.

### Blast Radius — What breaks if this changes or disappears?

Trace:

- direct callers and dependents
- data contracts and side effects
- asynchronous consumers and external integrations
- behavior over retries, failures, and partial completion
- migration, compatibility, rollback, and deletion consequences

The deletion test—"If I delete this, what breaks and how badly?"—is a practical
way to expose missing theory. It is not the only blast-radius test: a component
can remain present while a changed contract breaks its dependents.

If the relevant blast radius cannot be explained, investigate before modifying.
Do not guess across an unknown boundary.

## Working with AI-Generated Code

Treat comprehension as part of correctness. Shipping generated code whose role,
assumptions, and effects cannot be explained creates **comprehension debt**.

For every meaningful generated change:

1. Trace the actual code path instead of accepting plausible-looking output.
2. Explain why the approach fits existing ownership and boundaries.
3. Identify alternatives and why they were rejected.
4. Inspect edge cases, business rules, authorization, concurrency, and failure
   paths according to risk.
5. Verify with evidence independent of the model that produced the code.

Do not infer system quality from generated volume, speed, or local elegance. AI
can make each individual piece look reasonable while the whole remains
incoherent.

## Deliberate Systems Practices

The source transcript recommends four practices for building the theory that AI
cannot supply on its own. Apply them proportionally rather than creating
mandatory artifacts for every edit.

### 1. Design before prompting

For a complex feature, sketch the relevant components, data flows, state owners,
and failure surfaces before asking for implementation. Use a short list or prose
when that is sufficient; draw a diagram when interactions over time would
otherwise remain unclear.

### 2. Use specifications as scaffolding

Before implementation, establish the what and why:

- problem and intended outcome
- constraints and ownership boundaries
- success criteria
- important failure modes

A short plan may be enough. Use a formal specification only when task complexity
or repository guidance warrants one.

### 3. Run the deletion test

Choose each important component or integration point and ask what would fail if
it disappeared. An unknown answer defines the next investigation step; it is not
permission to guess.

### 4. Study generated output

Require a walkthrough of meaningful generated code, challenge its assumptions,
and compare alternatives. For deliberate learning, reconstructing a small piece
without generation can expose whether the underlying model is actually
understood. This is a training practice, not a required artifact for every task.

## Aligned Workflow

Follow the canonical workflow while applying the systems lens inside it:

1. **Understand** — inspect applicable instructions and the relevant code path.
   Build the minimum theory needed to explain interactions over time.
2. **Route** — use the current skill catalog and choose the smallest sufficient
   set of skills and tools.
3. **Plan** — state `Plan`, `Assumptions`, `Tradeoffs`, and `Verification` for
   non-trivial work. Include the relevant system map and alternatives; divide
   large work into incremental, verifiable steps.
4. **Implement** — make the smallest correct change, preserve existing ownership
   and contracts, and avoid speculative abstractions or unrelated cleanup.
5. **Verify** — use the strongest practical evidence and check affected
   boundaries, not only the edited unit.
6. **Summarize** — report the change, evidence, remaining risk, and anything that
   could not be verified.

Skill selection and composition belong to `skill-orchestration`; do not maintain
a static integration matrix here. Pair this lens only with skills selected from
the current catalog when the task actually requires them.

## Task-Specific Use

### Debugging

- Trace every relevant representation of the failing state.
- Find the first point where actual behavior diverges from expected behavior.
- Check whether retries, caching, ordering, or eventual consistency explain the
  divergence.
- Find feedback gaps that allowed the failure to remain hidden.
- Fix the root cause, then verify the affected boundary and regression path.

### Review

- Read the code path, not only the diff.
- Check whether ownership or contracts changed implicitly.
- Confirm new failure modes have proportionate verification or observability.
- Challenge generated code at the jagged frontier rather than reviewing every
  line with equal intensity.
- Report only actionable findings supported by evidence.

### Planning and Architecture

- Define component boundaries and ownership before proposing abstractions.
- Describe relevant interactions over time, including failure and recovery.
- Compare alternatives and make compatibility, migration, rollback, and
  verification costs explicit.
- Prefer reversible, incremental changes over broad rewrites.

## Lightweight Output

For work where the systems analysis should be visible, use:

```text
Theory
- Components and why they connect:
- Relevant behavior over time:

State
- Source of truth:
- Readers/writers:
- Copies or consistency boundaries:

Feedback
- Development evidence:
- Operational signals, if relevant:

Blast Radius
- Direct dependents:
- Transitive or external impact:
- Failure, rollback, or deletion consequence:

Jagged Frontier
- Routine output:
- High-judgment areas requiring deeper verification:
```

Keep this private or collapse it into the normal plan when a separate artifact
would add noise.

## Guardrails

- Do not create diagrams, specifications, monitoring, or documentation unless
  they are needed by the task or represent a durable changed contract.
- Do not turn every localized edit into an architecture exercise.
- Do not treat tests as the only feedback mechanism or logs as a substitute for
  verification.
- Do not mistake a plausible explanation from an AI for independent evidence.
- Do not silently choose between materially different interpretations.
- Do not claim completion without appropriate evidence.

## Canonical References

- Peter Naur, "Programming as Theory Building" (1985)

Behavioral authority:

- `../../instructions/SYSTEM.md` — behavioral principles and systems-thinking
  contract
- `../../instructions/AGENTS.md` — global
  Understand → Route → Plan → Implement → Verify → Summarize workflow
- `../skill-orchestration/SKILL.md` — dynamic skill discovery and composition
