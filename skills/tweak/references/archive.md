# Archive Step

When a change reaches `DONE`, fold its delta specs into the system-wide source of truth under `<effective-root>/specs/<capability>.md` and move the change folder into `<effective-root>/archive/`. This is the difference between "we wrote 30 plans" and "we have a maintained spec of what the system does."

There is no CLI. The five actions below are deterministic copy-paste. Do them in order; do not skip the date stamp.

## When to archive

Archive **only** when all of these hold (your `tasks.md` `Done criteria` checklist):

- All `Verify:` commands in `tasks.md` pass.
- `git status` shows no files outside the in-scope list.
- `<effective-root>/README.md` status row is `DONE` (see [index.md](index.md)).
- The drift check has not surfaced anything you have not reconciled.

If the change was `REJECTED` (approach abandoned) or superseded by a later change, archive it without merging specs — see "Rejected / superseded" below.

## The five actions

### 1. Capture the archive slug

Format: `<YYYY-MM-DD>-<slug>/`. Date is the day you are archiving, not the day the change was created.

```bash
date +%Y-%m-%d
```

Example: `2025-04-22-add-rate-limiting/`.

### 2. Move the change folder

```bash
mkdir -p <effective-root>/archive
git mv <effective-root>/<slug> <effective-root>/archive/<archive-slug>
```

`git mv` preserves blame. If the repo does not use git, plain `mv` is fine.

### 3. Merge the delta specs

The change's `specs.md` is organized as `## Capability: <name>` sections, each containing `### ADDED Requirements` / `### MODIFIED Requirements` / `### REMOVED Requirements` blocks of `#### Requirement: <name>` entries. For each capability:

1. Open or create `<effective-root>/specs/<name>.md`. Treat this file as the system-wide source of truth for that capability, owned by no single change. Its format is a flat list of `#### Requirement: <name>` blocks — no `### ADDED Requirements` wrapper, since the delta operations have been resolved.
2. Under each operation block in the delta:
   - `### ADDED Requirements` → append each `#### Requirement:` block to the system-wide spec, preserving the requirement text, scenarios, and any other content under the `#### Requirement:` heading.
   - `### MODIFIED Requirements` → find the existing `#### Requirement: <name>` in the system-wide spec, replace it **in full** with the modified version. (Partial replacement loses detail at archive time — same pitfall OpenSpec warns about.)
   - `### REMOVED Requirements` → move the requirement under a `### Removed Requirements` block in the system-wide spec, with a `**Reason**:` and `**Migration**:` line preserved from the delta.

The merge is line-level deterministic. There is no merge conflict unless two changes modify the same `#### Requirement:` in the same window — in which case, the later change wins for now and the human reconciles by hand.

If `<effective-root>/specs/` is empty, this is the first archive — the directory is created here, and `specs/<capability>.md` is built from the delta's `### ADDED Requirements` block.

### 4. Update the system-wide spec's own drift stamp

At the top of the merged-into file, write:

```markdown
> **Last archived**: <YYYY-MM-DD> from `<archive-slug>`
```

Multiple changes fold into one capability; keep only the most recent date.

### 5. Update the index

In `<effective-root>/README.md`:

- Move the change's row from the active table to a new `## Archived` section, sorted newest-first.
- Keep the slug (now `<archive-slug>`), title, and `DONE` status. Add a one-line `Notes:` column if the archive step exposed anything reviewers should know (e.g. "merged into existing `rate-limiting` capability, superseded `fix-rate-limit-headers`").

`BLOCKED` changes that later get unblocked are archived the same way. `REJECTED` changes skip action 3 (no spec merge) and keep the slug in the `## Considered and rejected` section of the index.

## Why manual?

Standalone means no validator, no CLI. A 5-action checklist is the lightest discipline that still produces a maintained spec. OpenSpec automates this with `openspec archive`; we don't have that tool, so the merge is the cost of staying standalone.

If the merge starts feeling heavy (more than ~5 capabilities touched per change, or merges happening weekly), the right move is to `npm i -g @fission-ai/openspec` and let `tweak` drive it. Until then, the discipline pays for itself in a single file you can hand to a new contributor and ask "what does this system do?"

## Anti-patterns

- ❌ **Archive without merging specs.** The change folder becomes a tombstone. Lose the value of "what does the system do."
- ❌ **Edit the change folder after archiving.** It is now history. Update specs at the system-wide level and write a new change.
- ❌ **Skip the date stamp.** Without it, archive order is undecidable from the directory listing alone.
- ❌ **Partial replacement of a MODIFIED requirement.** Always paste the full `#### Requirement:` block — partial updates lose detail at the next archive.
- ❌ **Use `mv` instead of `git mv`.** You lose blame. (Skip this rule for non-git repos.)
