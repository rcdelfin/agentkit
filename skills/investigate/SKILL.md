---
name: investigate
version: 2.0.0
description: |
  Systematic debugging with evidence-first root-cause analysis. Use when asked to
  debug, fix a bug, explain unexpected behavior, investigate an error, or perform
  root-cause analysis. Do not implement a fix until its cause is supported by evidence.
triggers:
  - debug this
  - fix this bug
  - why is this broken
  - root cause analysis
  - investigate this error
---

# Investigate

## Mission

Find and verify the cause before changing code. Fix the narrowest shared cause,
not each visible symptom. Keep an evidence trail so conclusions are reviewable.

## Procedure

### 1. Frame the failure

Record:

- observed symptom and exact error text
- expected behavior
- reproduction steps, inputs, environment, and frequency
- affected users, paths, or data
- first known bad version, if available

If missing context blocks useful work, ask one focused question. Otherwise continue
with explicit assumptions.

### 2. Map the actual path

Read repository guidance before code. Trace from entry point to symptom:

1. locate the failing symbol, route, job, command, or UI event
2. inspect callers and callees, not only the named file
3. follow data, state ownership, validation, and error handling
4. inspect tests covering the path
5. inspect recent changes to affected files

Use semantic navigation when available; fall back to identifier search and targeted
file reads. Do not edit during this phase.

### Historical cross-check

When behavior or intent is ambiguous, inspect target-symbol history:

- use blame/log to find introducing, modifying, reverting, or related commits
- check accompanying tests, docs, migrations, or issue references
- compare historical contract with current callers and behavior
- treat commit messages as context, not proof; current evidence wins

Skip broad history archaeology for obvious local errors.

### 3. Reproduce and collect evidence

Prefer a deterministic minimal reproduction. Run the smallest relevant check first,
then broaden it. Capture command, input, result, and whether result supports or
contradicts each hypothesis.

If reproduction fails, do not claim the bug is fixed. Increase observability with a
temporary assertion/log/diagnostic, or report the limitation and request the missing
evidence.

### 4. Form testable hypotheses

Write one specific claim:

> `Component/state X produces value Y because condition Z, causing symptom S.`

Rank alternatives by evidence. Check common shapes without assuming them:

- null or invalid input propagation
- wrong state owner or stale state
- boundary/serialization mismatch
- race, ordering, retry, or transaction failure
- configuration or environment drift
- cache or generated-artifact staleness
- dependency or external-service contract change

For each hypothesis, name one observation that would confirm it and one that would
falsify it. Test the highest-value hypothesis first. Never call a plausible story a
root cause.

### 5. Confirm before fixing

Use the least invasive discriminating check: existing test, focused reproduction,
assertion, trace, query, or controlled input. Remove temporary diagnostics after
confirmation. If evidence contradicts the hypothesis, return to path mapping and
form a new one.

After three failed hypotheses, stop and report that the issue may be architectural,
intermittent, or under-observed. Ask whether to continue with a new evidence source,
add instrumentation, or escalate.

### 6. Implement the smallest root-cause fix

- change the shared layer used by all affected callers when possible
- preserve existing project patterns
- avoid unrelated refactors and speculative hardening
- add validation at trust boundaries and preserve data-loss prevention
- add a regression test that fails before the fix and passes after it
- if the change spans more than five files, explain the blast radius before editing

### 7. Verify

Run, in order:

1. original reproduction, now passing
2. new regression test
3. focused suite/typecheck/lint/build relevant to changed code
4. broader suite when practical
5. relevant edge cases and error paths

Separate verified facts from remaining uncertainty. Never say “should fix” without
running evidence.

## Output

```text
DEBUG REPORT
Symptom:         ...
Root cause:      ...
Fix:             file:line and behavior changed
Evidence:        commands/results proving cause and fix
Regression test: file:line, or why unavailable
Blast radius:    callers/modules checked
Open concerns:   none, or explicit limitation
Status:          DONE | DONE_WITH_CONCERNS | BLOCKED
```

## Hard rules

- No fix without a supported root cause.
- No symptom-only guards when a shared cause is reachable.
- No broad rewrite to solve a narrow failure.
- Do not hide failed reproductions or contradictory evidence.
- Do not modify unrelated files.
- Escalate after three failed hypotheses or when verification is impossible.
