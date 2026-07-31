---
name: clickup-tweak-workflow
description: "Use when fixing or building a ClickUp card ID (e.g. GYMED-100) end-to-end, including branch, verification, and MR review."
metadata:
  version: "5.1.0"
  scope: "global"
---

# ClickUp Tweak Workflow

Take a ClickUp-tracked card end-to-end — bug fix **or** new feature. Maps to the
standard flow: **Understand → Route → Plan → Implement → Verify → Ship**. This
skill orchestrates: **`clickup`** (fetch the card), **`local-wiki`** (persist it
locally), **`investigate`** / **`systems-thinking`** (understand — type-
dependent), **`skill-orchestration`** (route the domain skills the change needs),
**`tweak`** (plan when non-trivial), **`scrutinize`** (sanity-check risky plans /
changes), **`git-actions`** (branch / commit / push / MR), and **`mr-review`**
(drive the review-thread fix loop).

**Scope:** any implementable ClickUp card — defect, feature, or hotfix.
Understand path depends on type: **Bugfix / Hotfix** → `investigate` (root
cause; a ticket names a symptom, not the bug); **Feature** →
`systems-thinking` (state ownership, feedback loops, blast radius).

## Prerequisites — ClickUp Credentials

Credentials live in **`~/.agents/.env`** or the process environment. The
scripts read `CLICKUP_API_KEY` (canonical), optional `CLICKUP_API_TOKEN`, and
`CLICKUP_TEAM_ID` from inherited env first, then `~/.agents/.env`. Do not print
or expose secret values.

| Var | Used by | Fallback if env missing |
|---|---|---|
| `CLICKUP_API_KEY` (canonical) | MCP server **and** REST scripts | `~/.agents/.env` |
| `CLICKUP_API_TOKEN` (optional) | REST scripts; legacy alias for `KEY` | `~/.agents/.env` |
| `CLICKUP_TEAM_ID` | both — custom-ID resolution | `5747865` |

**Prefer the MCP server** when connected — `clickup_search_tasks`,
`clickup_task_comments`, and `clickup_manage_task` are richer than the REST
scripts. If it is unavailable, use the REST scripts; they read the same
credentials from `~/.agents/.env`.

### Verify before starting

```bash
[ -n "$CLICKUP_API_TOKEN" ] && echo "env TOKEN ok" || echo "env TOKEN MISSING"
[ -n "$CLICKUP_API_KEY"   ] && echo "env KEY ok"   || echo "env KEY MISSING"
# Live test (scripts read env first):
python3 ~/.agents/skills/clickup/scripts/show_task.py GYMED-793 --meta
```

If credentials are unavailable, stop and ask the user — never guess card content.

## When to Use

Use when the user gives a ClickUp task ID and wants the card implemented end to
end in a GitLab-backed repo. Do not use for non-ClickUp work, review-only tasks,
cards the user only wants summarized, or non-GitLab repos unless the workflow
stops after local verification.

## Steps

1. **Ingest the card into the local wiki.** Persist the ClickUp card **before**
   writing any code, so the context survives. Hand off to **`local-wiki`** (it
   locates the wiki — prefers `docs/wiki/` — and obeys the wiki's own
   `AGENTS.md`). It fetches the card via **`clickup`** — prefer the MCP server's
   `clickup_search_tasks` / `clickup_task_comments` when connected; otherwise
   the REST scripts (`show_task.py <ID>`, `show_comments.py <ID>`) read creds
   from inherited env or `~/.agents/.env` (see **Prerequisites**). Either way it
   writes the append-only raw corpus + rebuilds the topic page per the wiki's
   governance.

2. **Classify & branch.** Classify the card, pick the prefix + base, then branch
   off the base the user confirms — never assume. Use **`git-actions`**.

   | Signal | Type | Prefix | Suggested base |
   |---|---|---|---|
   | Urgent prod breakage — "hotfix", "urgent", critical priority on a defect | Hotfix | `hotfix/` | `main` |
   | Something broken — "bug", "fix", "error", a Bug task type/tag | Bugfix | `bugfix/` | `develop` |
   | New capability or behavior change — "add", "implement", "enhance", a Feature/Story type | Feature | `feature/` | `develop` |

   Branch name: `{prefix}/{CUSTOM_ID}-{short-title}` (e.g.
   `bugfix/TUKS-490-login-null-crash`, `feature/RT-812-invite-external-users`).

   **Trivial card?** One-line fix, no logic — skip steps 3–4; jump to step 5
   (implement & verify).

3. **Understand — type-dependent.**

   - **Bugfix / Hotfix** → **`investigate`**: root-cause the defect before
     touching code (4 phases: investigate → analyze → hypothesize → implement).
     For a **hotfix**, keep it tight — root cause first, even under time
     pressure.
   - **Feature** → **`systems-thinking`**: map state ownership, feedback loops,
     and blast radius before changing anything; a feature is usually a
     cross-boundary / architecture change.

   If a bugfix turns out to need design work (behavior change, multiple
   approaches), give it the **`systems-thinking`** pass too.

4. **Route & plan.**

   - **Route** → hand off to **`skill-orchestration`** to discover and load the
     smallest set of domain skills the actual change needs (e.g.
     `laravel-conventions`, `api-endpoint-development`, `nuxt-*`, `pest-testing`
     — whatever the code / language / framework touched calls for). Don't guess;
     let it match from the catalog.
   - **Plan when needed** → if the change is non-trivial, plan it with
     **`tweak`** (proposal → specs → design → tasks) before implementing.
   - **Scrutinize when needed** → after planning and before implementation, run
     **`scrutinize`** for cross-boundary, risky, public-contract, security,
     multiple-approach, or explicitly requested sanity-check work. Skip it for
     trivial one-file fixes and routine docs/config changes.

5. **Implement, then verify.** Build the change on the branch, then **verify
   before any push or MR** — run the project's tests / typecheck / lint (the
   strongest applicable evidence). Don't push unverified code.

6. **Do not open a merge request on your own.** Only create the MR — targeting
   the base from step 2 — when the user explicitly asks.

7. **Check for `ai_code_review` after the MR exists.** If the pipeline exists,
   wait for it using `glab ci list` (filter by branch ref) or `glab mr view <iid>`.
   If no matching pipeline exists, record that the AI review gate is not
   configured and do not poll indefinitely; inspect available CI/review status
   instead.

8. **Work through every unresolved review thread:** run **`mr-review`**, which
   owns local fixes, verification, replies, and resolution. Never resolve first.
   Repeat after each push until no resolvable threads remain.

## Pitfalls

- **Keep one token var**: `CLICKUP_API_KEY` is canonical; REST scripts accept
  `CLICKUP_API_TOKEN` as a legacy alias. Keep credentials in `~/.agents/.env`
  and never print their values.
- Never assume branch base, branch type, or MR creation is authorized.
- Do not skip root-cause investigation for hotfixes because urgency increases
  the cost of a wrong patch.
- Do not push unverified code or resolve review threads before fixes are pushed.
- Do not assume `ai_code_review` exists; record a missing gate instead of polling
  forever.
- Do not load every domain skill; route only skills required by touched code.
- Do not use `scrutinize` as a substitute for tests or post-MR `mr-review`.

## Verification

- [ ] Card and comments persisted in the governed local wiki.
- [ ] Card type, branch name, and base confirmed before branching.
- [ ] Required domain skills routed; non-trivial work planned with `tweak`.
- [ ] Risky/non-trivial plan or change scrutinized, or skip was justified.
- [ ] Tests, typecheck, lint, or strongest applicable checks pass.
- [ ] MR created only when explicitly requested.
- [ ] When present, AI review completed; otherwise missing gate recorded.
- [ ] Every resolvable review thread fixed or explained, replied to, and resolved.
