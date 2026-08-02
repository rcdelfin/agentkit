---
name: tweak-workflow
description: "Use for end-to-end project changes: understand, route, plan, implement, verify, and ship."
metadata:
  version: "1.2.0"
  scope: "global"
---

# Tweak Workflow

Take an implementable project change end to end:
**Understand → Route → Plan → Implement → Verify → Ship**.

## When to Use

Use when the user wants a bug fix, feature, or hotfix carried through the
repository workflow. Do not use for plan-only work (`tweak`), review-only work,
or requests to summarize an existing change.

## Steps

1. **Set destination and boundary.** State the one-sentence done condition,
   explicit out-of-scope work, and any blocking unknowns. Read repository
   guidance and relevant code, then classify the change:
   - **Bugfix / hotfix** → use `investigate` before editing.
   - **Feature / cross-boundary change** → use `systems-thinking` before editing.
   - **Trivial one-file change** → skip deep investigation and planning.

   If destination or safe path remains unclear, stop and ask; do not invent tasks.

2. **Branch safely.** Use `git-actions`. Follow repository branch conventions,
   confirm the base when it is ambiguous, and never assume a protected branch is
   safe to modify directly.

3. **Route and plan.** Use `skill-orchestration` to load only skills required by
   touched code. For non-trivial work, use `tweak` to produce proposal, specs,
   design, and tasks before implementation. Keep unresolved decisions explicit;
   plan only what recon supports. If blocking decisions remain, stop and ask to
   clarify or split. If work exceeds one session but its destination is clear,
   complete the plan and leave an explicit handoff checkpoint in its tasks or
   handoff note; do not pretend to finish or execute speculative scope. Use
   `scrutinize` before implementation when the change is risky, public-contract,
   security-sensitive, cross-boundary,
   or has multiple reasonable approaches.

4. **Implement and verify.** Follow the plan, then run the strongest applicable
   tests, typechecks, linters, and builds. Fix failures before any push. Keep the
   diff focused; do not add speculative scope.

5. **Ship only when requested.** Commit and push through `git-actions`. Create an
   MR/PR only when explicitly requested. Never force-push or skip hooks.

6. **Handle review feedback.** If review feedback exists after shipping, use the
   applicable review workflow to fix, verify, reply, and resolve each thread.
   Never resolve a thread before its fix is verified.

## Pitfalls

- Do not treat a ticket or request description as proof of root cause.
- Do not continue without a clear destination or resolved blocking decisions.
- Do not claim multi-session work complete without a handoff checkpoint.
- Do not pre-slice unknown work into speculative tasks.
- Do not load every domain skill; route from the files and behavior actually touched.
- Do not push unverified code or open an MR/PR without explicit approval.
- Do not resolve review feedback before implementing and verifying the fix.

## Verification

- Destination, boundary, and blocking unknowns recorded before implementation.
- Multi-session work has a plan and explicit handoff checkpoint.
- Repository guidance read before implementation.
- Required skills loaded from exact discovered paths.
- Tests, typechecks, lint, or strongest applicable checks pass.
- No unexplained unstaged changes remain before shipping.
- Commit/push/MR/PR actions match explicit user intent.
