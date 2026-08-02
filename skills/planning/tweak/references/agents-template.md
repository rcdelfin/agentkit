# AGENTS.md Template (bootstrap, written once per effective root)

The fenced block below is what Storage Setup writes verbatim to
`<effective-root>/AGENTS.md` when absent. Copy the block's contents only — omit
this header and the fence markers — and substitute `<effective-root>`. The body
and footer are intentionally tool-agnostic: no skill names, no AI tool names,
no project-specific paths.

````markdown
# Change Planning

This folder holds change planning artifacts. Each change is a self-contained
directory of Markdown files describing **why**, **what**, **how**, and
**in what order**. Completed changes are archived and their delta specs
folded into a system-wide source of truth under `specs/`.

## Layout

```
<effective-root>/
  AGENTS.md                ← this file
  README.md                ← index of active + archived changes
  specs/                   ← system-wide source of truth (one file per capability)
    <capability>.md
  <slug>/
    proposal.md            ← why this change exists (intent, problem, success)
    specs.md               ← delta spec — what must be true after
    design.md              ← approach — how we'll build it
    tasks.md               ← ordered, verifiable implementation steps
  archive/                 ← completed changes (post-archive)
    <YYYY-MM-DD>-<slug>/
      proposal.md
      specs.md
      design.md
      tasks.md
```

`<slug>` is `kebab-case`, scoped, short (e.g. `add-rate-limiting`,
`fix-timezone-bug`).

## Workflow

`proposal.md` → `specs.md` → `design.md` → `tasks.md`, then update
`README.md`.

A change is **READY** to implement only when all four artifacts exist.
A change is **DONE** when `tasks.md` done-criteria pass.
A change is **ARCHIVED** when its delta specs have been folded into
`specs/<capability>.md` and the change folder has moved to
`archive/<YYYY-MM-DD>-<slug>/`.

## Status

Each row in `README.md` carries a status, which is the single source of
truth for where the change is. Do not duplicate status in `proposal.md`.

`DRAFT` → `READY` → `IN PROGRESS` → `DONE` → `ARCHIVED` | `BLOCKED` | `REJECTED`

## Reading a change

Open the four files in the change directory, in order: `proposal.md` →
`specs.md` → `design.md` → `tasks.md`. No tooling required.

## Writing a new change

Create a new `<slug>/` directory and write the four files in the order
above. Add a row to `README.md` with status `DRAFT`; promote to `READY`
when all four files exist. After implementation, run the archive step to
fold the delta specs into `specs/<capability>.md` and move the change
to `archive/`.

## Reading the system-wide spec

Open `specs/<capability>.md`. This file is owned by no single change; it
is the result of every change that touched the capability, folded in via
archive. If you are about to add or modify a requirement for that
capability, write a new change (not a direct edit to `specs/<capability>.md`).

---

This folder follows the four-artifact change-planning convention
(proposal → specs → design → tasks), with delta-spec archiving. The
convention is tool-agnostic — anyone can adopt it.
````
