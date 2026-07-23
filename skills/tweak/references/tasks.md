# Tasks Template

Tasks are the **ordered, verifiable implementation steps**. Written for a weaker executor model with zero context — every step is self-contained, every verify command has an expected result. The change is "done" only after the executor also runs the archive step (see [archive.md](archive.md)).

## When to fill this

After design. The design names the files; tasks name the exact edits and the order to make them so the codebase is never broken between steps.

## Template

```markdown
# Tasks: <slug>

> **Drift SHA**: <short SHA>
> **Frozen at**: <YYYY-MM-DD>
>
> **Executor**: Follow each step in order. Run the Verify command after
> every step and confirm the expected result before moving on. Touch only
> the files listed under Scope. If a STOP condition triggers, stop and
> report — do not improvise.
>
> **Drift check (run first)**:
> `git diff --stat <Drift SHA above>..HEAD -- <in-scope paths>`
> If anything in scope changed since this plan was written, reconcile
> before executing. The plan was frozen at `<Frozen at above>`.

## Commands you will need

| Purpose   | Command                  | Expected on success |
|-----------|--------------------------|---------------------|
| Install   | `pnpm install`           | exit 0              |
| Typecheck | `pnpm typecheck`         | exit 0, no errors   |
| Tests     | `pnpm test -- <filter>`  | all pass            |
| Lint      | `pnpm lint`              | exit 0              |

(Exact commands from this repo — verified during recon, not guessed.
If a row doesn't apply to this change, remove it.)

## Scope

**In scope** (the only files you should modify):
- `src/<path>/<file>.ts`

**Out of scope** (list files only — rationale lives in design.md's
blast-radius table; don't re-prose it here):
- `src/<path>/<other>.ts`

## Steps

### Step 1: <imperative title>

What to do, precisely. Reference exact files/symbols. Inline full code
**only** for non-obvious logic (guards, branching, recursion-safety);
describe migrations and boilerplate services as a one-line intent +
reversibility — design.md already specifies the data structure, so don't
rewrite the up/down bodies or class skeletons here.

**Verify**: `<command>` → <expected output>

### Step 2: ...

(Each step small enough to verify independently. Order steps so the
codebase is never broken between steps — e.g. add new path, switch
callers, then remove old path.)

## Done criteria

Machine-checkable, and lean — the essential gates, not a grep for every
file you touched (the per-step Verify already covered those). ALL must hold:

- [ ] `<primary verification command>` exits 0; new tests for <X> pass
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `<effective-root>/README.md` status row updated to DONE
- [ ] **Archive step run** per [archive.md](archive.md):
  `<effective-root>/archive/<YYYY-MM-DD>-<slug>/` exists;
  `<effective-root>/specs/<capability>.md` updated or created

## STOP conditions

Stop and report (do not improvise) if:

- <Plan-specific condition 1 — name a risk from design.md's Risks section>
- <Plan-specific condition 2 — name a recon-discovered gotcha>
- <Plan-specific condition 3 — name an external dependency that may not be set up>
- A step's verification fails twice after a reasonable fix attempt

STOP conditions are **plan-specific**. The template's role is to remind you
to write them, not to copy them. See `examples/add-rate-limiting/tasks.md`
for the bar: name the actual middleware pattern, the actual JWT claim
name, the actual config key that the recon verified. Boilerplate STOPs
("code doesn't match what design.md says") are restatements of the
executor contract and add no signal.

## Maintenance notes

For whoever owns this code after the change lands:

- What future changes will interact with this.
- What a reviewer should scrutinize in the PR.
- Follow-ups explicitly deferred (and why).
```

## Guidance

- **Each step is independently verifiable.** If you can't run a check after a step, the step is too big.
- **Order so the codebase stays green between steps.** Add new path → switch callers → remove old path. Never delete-then-add.
- **Verify commands are commands, not prose.** "Should still work" is not a verify command. `pnpm test` returning 0 is.
- **Describe, don't transcribe.** A migration is "add nullable JSON `config` column, reversible: dropColumn" — not the full `up()`/`down()` bodies, because `design.md` already holds the data structure. Reserve full code blocks for the load-bearing, non-obvious bits (a guard's condition, a branching delete, recursion-safety). Boilerplate the executor can write from the description.
- **Tests go inline, not in a summary table.** Write each test as its own step (or the tail of the step that produces the code it covers), naming the pattern file in that step's body. A separate "Test plan" table that restates those tests is duplication and a drift surface.
- **Match the repo's git workflow.** Look at recent commits: `git log --oneline -20`. Match the style.
- **Stamp once at planning time.** `git rev-parse --short HEAD` once, paste the result into every artifact's `Drift SHA` line and the `Frozen at` line. After any recon that re-checks the codebase, re-stamp all four artifacts.

## Anti-patterns

- ❌ **"Implement the feature"** as a single step. Decompose.
- ❌ **Steps that depend on later steps.** Reorder or split.
- ❌ **Verify: `looks good`** — not a command.
- ❌ **Full migration/service boilerplate** when design.md already specifies the structure — write the intent + reversibility, not the up/down bodies or class skeleton.
- ❌ **A separate test-summary table** that duplicates the test stubs already written inline in steps — one source of truth.
- ❌ **Done criteria with a grep per file** — the per-step Verify covered those; keep criteria to the essential gates.
- ❌ **No out-of-scope section** — drift magnet.
- ❌ **STOP conditions copy-pasted from another plan or the template** — make them specific to this plan's actual risks.
- ❌ **Done criteria without the archive step** — the change is not done until `<effective-root>/specs/<capability>.md` has been updated.
