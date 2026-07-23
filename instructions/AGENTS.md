# AGENTS.md

# Global Development Workflow

This file defines repository-wide engineering workflow.

More specific `AGENTS.md` files override local conventions.

`CLAUDE.md`, DOX documentation, and module documentation provide additional context but never weaken these workflow rules.

---

# Workflow

For non-trivial work:

1. Understand
2. Plan
3. Implement
4. Verify
5. Summarize

Present assumptions whenever uncertainty exists.

Do not silently choose between multiple reasonable interpretations.

---

# Repository Awareness

Always inspect nearby documentation before making architectural decisions.

Priority:

1. Child `AGENTS.md`
2. Parent `AGENTS.md`
3. Root `AGENTS.md`
4. `CLAUDE.md`
5. Other project documentation

The nearest documentation has highest authority for local conventions.

---

# Minimal Changes

Implement only what the request requires.

Do not:

- add future-proofing without request
- introduce single-use abstractions
- rewrite working code unnecessarily
- modify unrelated files
- "clean up" adjacent code

Every modified line should directly support the requested outcome.

---

# Verification

Bug fix

- reproduce when practical
- implement fix
- verify behavior

Refactor

- preserve behavior
- verify before and after

Feature

- verify expected behavior
- ensure no regressions

Run appropriate project verification whenever available:

- tests
- lint
- formatter
- type checker
- build

If something cannot be verified, explain why.

---

# Documentation (DOX)

Documentation should evolve with architecture.

Update existing documentation before creating new documentation.

Create child `AGENTS.md` only when introducing a meaningful architectural boundary or persistent local convention.

Child documents should describe:

- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child Documentation Index

Avoid duplicating information already documented higher in the hierarchy.

---

# Continuous Improvement

When discovering:

- recurring mistakes
- architectural constraints
- module ownership
- hidden assumptions
- important conventions

record them in the appropriate documentation level rather than repeating them in future sessions.

Temporary discoveries belong in responses, not documentation.

---

# Engineering Expectations

Prefer:

- deterministic behavior
- explicit ownership
- small diffs
- reversible changes
- maintainable solutions

Value long-term maintainability over clever implementations.

---

# Success Signals

A healthy repository demonstrates:

- small, focused commits
- minimal unnecessary diffs
- consistent conventions
- accurate documentation
- repeatable verification
- fewer repeated mistakes

---

<!--
DOX

Load the "dox" skill when documentation updates are required.

Hierarchy:

Root
├── Global Preferences
├── Child Documentation Index

Child
├── Purpose
├── Ownership
├── Local Contracts
├── Work Guidance
├── Verification
└── Child Documentation Index
-->

@RTK.md