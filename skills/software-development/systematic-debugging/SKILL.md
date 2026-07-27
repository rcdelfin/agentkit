---
name: systematic-debugging
description: "4-phase root cause debugging: understand bugs before fixing."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
metadata:
  hermes:
    tags: [debugging, troubleshooting, problem-solving, root-cause, investigation]
    related_skills: [test-driven-development, systems-thinking, skill-orchestration]
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:

- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**

- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**

- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Someone wants it fixed NOW (systematic is faster than thrashing)

## The Four Phases

You MUST complete each phase before proceeding to the next.

---

## Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

### 1. Read Error Messages Carefully

- Don't skip past errors or warnings
- They often contain the exact solution
- Read stack traces completely
- Note line numbers, file paths, error codes

**Action:** Use `read` on relevant source files. Use `bash`/`symbol_search` to find the error and its callers.

### 2. Build a Tight Feedback Loop

Create one fast, deterministic command that fails on the exact symptom and
passes after the fix. Prefer, in order: a focused test, HTTP/CLI repro, a
small harness, then a scripted manual flow. Assert the wrong behavior, not
merely "doesn't crash". If the issue is flaky, raise reproduction rate before
forming theories.

**Action:** Run the loop at least once before proposing a fix:

```bash
pytest tests/test_module.py::test_name -v
# or: python scripts/repro_bug.py
```

### 3. Check Recent Changes

- What changed that could cause this?
- Git diff, recent commits
- New dependencies, config changes

**Action:**

```bash
# Recent commits
git log --oneline -10

# Uncommitted changes
git diff

# Changes in specific file
git log -p --follow src/problematic_file.py | head -100
```

### 4. Gather Evidence in Multi-Component Systems

**WHEN system has multiple components (API → service → database, CI → build → deploy):**

**BEFORE proposing fixes, add diagnostic instrumentation:**

For EACH component boundary:

- Log what data enters the component
- Log what data exits the component
- Verify environment/config propagation
- Check state at each layer

Run once to gather evidence showing WHERE it breaks.
THEN analyze evidence to identify the failing component.
THEN investigate that specific component.

### 5. Trace Data Flow

**WHEN error is deep in the call stack:**

- Where does the bad value originate?
- What called this function with the bad value?
- Keep tracing upstream until you find the source
- Fix at the source, not at the symptom

**Action:** Use `symbol_search` for identifiers or `bash`/`grep` for raw strings to trace references:

```python
# Find where the function is called
grep -R "function_name(" src/ --include='*.py'

# Find where the variable is set
grep -R "variable_name[[:space:]]*=" src/ --include='*.py'
```

### Phase 1 Completion Checklist

- [ ] Error messages fully read and understood
- [ ] Tight loop exists, was run, and asserts the exact symptom
- [ ] Recent changes identified and reviewed
- [ ] Evidence gathered (logs, state, data flow)
- [ ] Problem isolated to specific component/code
- [ ] Ranked root-cause hypotheses can be stated and tested

**STOP:** Do not proceed to Phase 2 until you understand WHY it's happening.

---

## Phase 2: Pattern Analysis

**Find the pattern before fixing:**

### 0. Minimize the Reproduction

Remove inputs, callers, config, and steps one at a time, rerunning the tight
loop after each removal. Done when removing any remaining element makes the
loop pass.

### 1. Find Working Examples

- Locate similar working code in the same codebase
- What works that's similar to what's broken?

**Action:** Use `symbol_search` or `bash`/`grep` to find comparable patterns:

```python
grep -R "similar_pattern" src/ --include='*.py'
```

### 2. Compare Against References

- If implementing a pattern, read the reference implementation COMPLETELY
- Don't skim — read every line
- Understand the pattern fully before applying

### 3. Identify Differences

- What's different between working and broken?
- List every difference, however small
- Don't assume "that can't matter"

### 4. Understand Dependencies

- What other components does this need?
- What settings, config, environment?
- What assumptions does it make?

---

## Phase 3: Hypothesis and Testing

**Scientific method:**

### 1. Rank Falsifiable Hypotheses

- Generate 3–5 plausible causes and rank by likelihood plus cheapness to test.
- State each prediction: "If X causes this, Y should be observable and Z should
  change."
- Try to disprove the highest-ranked hypothesis before changing production code.

### 2. Test Minimally

- Use the smallest probe and change one variable at a time.
- Don't fix multiple things at once.

### 3. Verify Before Continuing

- Did it work? → Phase 4
- Didn't work? → Form NEW hypothesis
- DON'T add more fixes on top

### 4. When You Don't Know

- Say "I don't understand X"
- Don't pretend to know
- Ask the user for help
- Research more

---

## Phase 4: Implementation

**Fix the root cause, not the symptom:**

### 1. Create Failing Test Case

- Simplest possible reproduction
- Automated test if possible
- MUST have before fixing
- Use the `test-driven-development` skill

### 2. Implement Single Fix

- Address the root cause identified
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### 3. Verify Fix

```bash
# Run the specific regression test
pytest tests/test_module.py::test_regression -v

# Run full suite — no regressions
pytest tests/ -q
```

### 4. If Fix Doesn't Work — The Rule of Three

- **STOP.**
- Count: How many fixes have you tried?
- If < 3: Return to Phase 1, re-analyze with new information
- **If ≥ 3: STOP and question the architecture (step 5 below)**
- DON'T attempt Fix #4 without architectural discussion

### 5. If 3+ Fixes Failed: Question Architecture

**Pattern indicating an architectural problem:**

- Each fix reveals new shared state/coupling in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**

- Is this pattern fundamentally sound?
- Are we "sticking with it through sheer inertia"?
- Should we refactor the architecture vs. continue fixing symptoms?

**Discuss with the user before attempting more fixes.**

This is NOT a failed hypothesis — this is a wrong architecture.

---

## Framework-Specific Pitfalls

> See also `references/laravel-filament-pitfalls.md` for expanded detail and verification patterns.
> See also `references/mac-dev-environment-fixes.md` for macOS dev environment issues (pyenv locks, slow zsh startup).

### Filament: Single-Page Resource Route Key

A Filament resource with only a custom `Page` (no `ListRecords`) must register it as `'index'` in `getPages()`, not `'view'`. Filament navigates to `index` by default — a `view` key at path `/` causes `LogicException: does not have an [index] page`.

### Laravel: Eloquent Relationship Method vs Dynamic Property

A common source of `Undefined property` errors after "fixing" a missing-method error:

```php
// WRONG — returns BelongsTo relationship object (never null), then ?->id 
// accesses property on the relationship object, not the model
$entityId = $user->entity()?->id;   // Error: Undefined property: BelongsTo::$id

// CORRECT — dynamic property access returns the related model (or null)
$entityId = $user->entity?->id;     // Returns model->id or null
```

**Why this happens:** Calling the relationship as a method (`entity()`) returns the Eloquent relationship instance (BelongsTo, HasMany, etc.). The nullsafe operator `?->` doesn't convert it to the model — it just short-circuits if the left side is null, but a relationship object is never null. Use dynamic property syntax (no parentheses) to get the actual related model.

**When this surfaces:** Often appears as a two-step error:

1. First error: `Call to undefined method User::ifrsEntity()` → developer renames to correct method name
2. Second error: `Undefined property: BelongsTo::$id` → developer used method call syntax with `?->`

**Phase 3 checkpoint:** After any fix that changes a method name on an Eloquent model, verify the call pattern (method vs property) before declaring success.

---

## Language-Specific Debug References

### Python Debugging → `references/python-debugging.md`

pdb REPL quick reference, debugpy remote attach (DAP), remote-pdb for terminal agents, pytest debugging tips, and common pitfalls (xdist, asyncio, ptrace).

### Node.js Debugging → `references/nodejs-debugging.md`

`node inspect` REPL reference, CDP scripting via `chrome-remote-interface`, attaching to running processes (SIGUSR1), Vitest debugging, heap snapshots & CPU profiling, and Hermes ui-tui debugging patterns.

---

## Red Flags — STOP and Follow Process

If you catch yourself thinking:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals a new problem in a different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (Phase 4 step 5).

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern, don't fix again. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, trace data flow | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, identify differences | Know what's different |
| **3. Hypothesis** | Form theory, test minimally, one variable at a time | Confirmed or new hypothesis |
| **4. Implementation** | Create regression test, fix root cause, verify | Bug resolved, all tests pass |

## Tool Routing

Use available tools, not copied framework names:

- `read` for complete error/source context.
- `bash` for tests, repros, git history, and narrow probes.
- `symbol_search`/`module_report` for callers and structure when available.
- `lsp_navigation` for definitions/references when activated.

For bug fixes, pair the process with `test-driven-development`: RED regression
loop → root-cause fix → GREEN verification.
