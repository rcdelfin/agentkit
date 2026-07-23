# Proposal Template

The proposal is the "why" — short enough to read in one sitting, dense enough to argue with.

## When to fill this

After recon. Before specs. If the proposal can't be written crisply, the change is too vague to plan.

## Template

```markdown
# Proposal: <slug>

> **Drift SHA**: <short SHA — `git rev-parse --short HEAD` at planning time>
> **Frozen at**: <YYYY-MM-DD>

> **Status** lives in `<effective-root>/README.md`. Do not duplicate it here.

## Why

What's the concrete cost of not doing this? One paragraph max. Numbers,
incidents, or user-visible behavior beats abstract pain.

Examples of good "why":

- "p95 dashboard load is 4.2s on production; stakeholders won't load it
  on mobile and have started exporting to CSV instead."
- "Onboarding new developers takes a full day because there's no
  `.env.example`; three of the last four onboarding sessions have hit it."

## What changes

2–4 bullets. The shape of the change at the level a stakeholder would
recognize. No file paths here — save those for design.md.

- <User-visible thing 1>
- <User-visible thing 2>
- <Internal thing 3, if relevant>

## Capabilities

The merge keys for the archive step. Each entry becomes a `## Capability: <name>`
section in `specs.md` and folds into `<effective-root>/specs/<name>.md` on
archive. Use `kebab-case` so the archive path resolves cleanly. If this
change does not add or modify any system-wide capability (e.g. a pure
refactor), write `None — see Out of scope` and skip the Capabilities
section in `specs.md`.

- `<capability-1>`: <one-line description>
- `<capability-2>`: <one-line description, if multiple capabilities are touched>

## Assumptions

What you take for granted about the codebase or dependencies. The executor
cannot guess these — write them down. Each assumption should be checkable
against the repo (file:line or config key if possible).

- The `auth/` module uses JWT claims for user metadata (verified in
  `app/Auth/JwtTierResolver.php:15`).
- Redis is configured and available under the `redis.default` connection
  (confirmed in `config/database.php:34`).

## Out of scope (brief, feature-level)

What we're explicitly NOT building, at the feature level. Keep it to 1–3
bullets — the detailed file-level blast-radius list (which files must NOT
be touched and why) lives in design.md, so don't duplicate it here.

- We will not refactor <X> — separate concern.
- We will not change the public API shape — clients depend on it.

## Success criteria

How will we know this worked? Be specific. "p95 latency under 200ms"
beats "feels faster." "New devs can run the app in under 10 minutes"
beats "easier onboarding."

- <Measurable outcome 1>
- <Measurable outcome 2>

## Open questions

Things the plan should resolve but doesn't yet. Each as a one-line bullet
with a recommended default in parens. The user picks.

- Cache TTL — 60s (recommended) vs. 5min vs. per-user invalidation?
- Error response shape — match existing `api/v1` (recommended) or RFC 7807?

## Changelog (only on update)

- <YYYY-MM-DD> — <what changed and why>
```

## Anti-patterns

- ❌ **Vague why** — "improve performance" without a number.
- ❌ **Solutions in the proposal** — that's design.md. Proposal is intent, not implementation.
- ❌ **No out-of-scope** — guarantees later arguments.
- ❌ **Open questions without defaults** — wastes a round trip.
- ❌ **No assumptions stated** — the executor fills the gaps with guesses, and guesses become bugs.
- ❌ **Capabilities missing or non-`kebab-case`** — breaks the archive merge keys.
- ❌ **Status duplicated here** — the index is the single source of truth. Don't put a status field in this file.
