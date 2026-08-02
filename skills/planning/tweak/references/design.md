# Design Template

Design is the **approach** — how we'll build it. File-level, concrete, referencing the actual repo conventions.

## When to fill this

After specs. Before tasks. If you can't name the files you'll touch, you haven't recon'd enough — go back.

## Template

````markdown
# Design: <slug>

> **Drift SHA**: <short SHA>
> **Frozen at**: <YYYY-MM-DD>

## Approach

One paragraph. The shape of the solution in plain language. No code yet.

## Files to change

| File | Role today | Change |
|------|------------|--------|
| `path/to/file.ext` | what this file does | what we'll do to it |
| ... | ... | ... |

(Cover every file from proposal.md's "what changes". New files go in
the same column with `(new)`.)

## Conventions to match

Bullet list. Each item names the convention and points to an exemplar in the
repo — never describe the convention in the abstract; show it.

- **Error handling** follows the `Result` pattern — see `src/lib/result.ts`,
  used in `src/users/api.ts:40-60`. Match it.
- **Test layout** is colocated with source as `<thing>.test.ts` — see
  `src/orders/api.test.ts` for the structural pattern.
- **Naming** uses `<verb><Noun>` for actions (`createOrder`), `is<Adj>`
  for predicates (`isActive`). No `get`/`set` prefixes.

## Key data structures / interfaces

Code-shaped, not free prose. Use the language's actual type syntax.
Inline, don't link to external docs.

```ts
interface RateLimitConfig {
  windowSeconds: number;   // sliding window
  maxRequests: number;
  keyBy: 'user_id' | 'ip'; // tier-aware
}
```

## Migrations

If any. Skip this section if not applicable.

- **What changes in the DB / schema / config**
- **Reversibility** — can we roll back without data loss?
- **Downtime** — zero-downtime vs. maintenance window
- **Order of operations** — what must land first

## Risks

What could go wrong. Each as a one-line bullet with mitigation.

- **Counter drift on multi-instance deploy** — mitigation: Redis-backed
  counter with `INCR` + `EXPIRE`.
- **Backward-compat break in API response** — mitigation: bump to `/v2/`.

## Out of scope

This is the authoritative out-of-scope list; `proposal.md`'s version is a
brief feature-level subset. Here, be at the implementation level — name
files that look related but must NOT be touched (blast-radius guardrails):

- We will not refactor the existing `auth/` module — the change isolates
  to a new middleware, not existing auth plumbing.
- We will not add per-endpoint overrides — flat config only this round.
- Do not touch `config/database.php` even though it configures Redis —
  the default connection is already set up.
````

## Guidance

- **Reference, don't describe.** Every convention should point to a real file in the repo with a line number.
- **Code blocks, not pseudocode.** Use the actual syntax. If the type isn't clear yet, that's a research task before you can design.
- **Migrations deserve their own section.** Don't bury them in prose.
- **Out of scope here is finer-grained than proposal.** Include both feature exclusions ("no public API change") and blast-radius guardrails ("do not touch `config/database.php` even though it configures Redis — the default connection is fine"). Naming adjacent files prevents the executor from drifting into them.

## Anti-patterns

- ❌ **"We'll use industry best practices"** — name the practice and the repo exemplar.
- ❌ **Diagrams only** — diagrams supplement, they don't replace file-level specificity.
- ❌ **No migrations section** when DB changes are involved.
- ❌ **Risks without mitigations** — a risk without a plan to address it is a finding, not a risk.
- ❌ **Out of scope is just proposal copy-pasted** — design-level excludes should be more specific, naming actual files.
