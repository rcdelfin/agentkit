# Changes Index Template

The index file lives at the resolved effective root: `<effective-root>/README.md`
(where `<effective-root>` is `plans/` if dedicated, `plans/tweaks/` if `plans/`
has unrelated content, or `docs/tweaks/` if no `plans/` exists).
It is the single source of truth for what's planned, in flight, and done —
**and the only place change status is recorded**. Do not duplicate status in
`proposal.md`.

## Template

```markdown
# Changes

Newest first.

## Active

| Slug | Title | Status | Capabilities | Depends on | Notes |
|------|-------|--------|--------------|------------|-------|
| `<slug>` | <one-line title> | DRAFT | `<capability-1>`, `<capability-2>` | — | — |

## Archived

| Archived at | Slug | Title | Capabilities | Merged into |
|-------------|------|-------|--------------|-------------|
| `<YYYY-MM-DD>` | `<slug>` | <one-line title> | `<capability>` | `<effective-root>/specs/<capability>.md` |

## Considered and rejected

- ~~`<old-slug>`~~ — not worth doing because <one line>. (So nobody
  re-plans it next session.)

## Status values

- **DRAFT** — being written, not ready to implement.
- **READY** — all four artifacts present; executor can start.
- **IN PROGRESS** — tasks being executed.
- **DONE** — done criteria verified; archive step still pending.
- **ARCHIVED** — archive step complete; moved to `archive/<YYYY-MM-DD>-<slug>/`.
- **BLOCKED** — see notes in the change directory; one-line reason here.
- **REJECTED** — approach abandoned; recorded under "Considered and rejected".

## Dependency notes

- `<slug-2>` requires `<slug-1>` because <reason>.

## Changelog conventions

When updating an existing change, append a `## Changelog` section to its
`proposal.md` rather than rewriting history. Keep the original intent
visible; future readers need to know what was decided and why.
```

## Guidance

- **One row per change.** Don't list duplicate slugs.
- **Status reflects the artifact state, then the archive state.** A change moves `DRAFT → READY` when all four files exist. `READY → IN PROGRESS` when an executor starts tasks. `IN PROGRESS → DONE` when done criteria pass. `DONE → ARCHIVED` only after [archive.md](archive.md) has run. A `DONE` change that hasn't been archived is a finding — call it out in `Notes`.
- **Capabilities column is the merge key.** The values here must match the `## Capability:` sections in `specs.md` exactly (and the `<effective-root>/specs/<capability>.md` filenames the archive step writes to).
- **Dependencies are other slugs.** If change B can't start until change A is `ARCHIVED`, B's row says `Depends on: <A>`. Keep this graph small — chains longer than 3 changes usually mean scope creep.
- **Don't delete rows for REJECTED changes** — strike them through and record why. Otherwise someone re-plans the same thing next session.
- **Status is not in `proposal.md`.** If you see a status field in a proposal, it's a stale template — re-read the proposal template.
