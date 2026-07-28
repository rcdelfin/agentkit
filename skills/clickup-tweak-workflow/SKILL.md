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

The canonical credential source is **`~/.zsh_secrets`**, sourced by `~/.zshrc`
and exporting `CLICKUP_API_KEY` (canonical) plus `CLICKUP_TEAM_ID` — and,
optionally, `CLICKUP_API_TOKEN` (legacy, same `pk_...` value). Hermes launches
from an interactive zsh, so the exported vars are **inherited by the agent's
non-interactive bash subprocess** and by MCP subprocesses — REST scripts find
them via `os.environ` directly, no `export` step needed. **Do not read
`~/.zsh_secrets`** — it is the user's secret store; trust the inherited env
instead.

| Var | Used by | Fallback if env missing |
|---|---|---|
| `CLICKUP_API_KEY` (canonical) | MCP server **and** REST scripts | MCP: `~/.pi/agent/mcp.json` → `mcpServers.clickup.env`; scripts: env → `~/.agents/.env` → `~/.hermes/.env` |
| `CLICKUP_API_TOKEN` (optional) | REST scripts read this first, then fall back to `KEY` | `~/.agents/.env` → `~/.hermes/.env` (legacy) |
| `CLICKUP_TEAM_ID` | both — custom-ID resolution | `5747865` |

Keep **one** var: `CLICKUP_API_KEY` (the MCP server mandates that exact name).
REST scripts read `CLICKUP_API_TOKEN` first, then fall back to `KEY`, so
`TOKEN` is optional and exists only for back-compat with `~/.hermes/.env`.

**Prefer the MCP server** when it is connected — `clickup_search_tasks`,
`clickup_task_comments`, `clickup_manage_task` are richer than the REST scripts
and are the canonical Hermes path. If the `clickup` server reports **not
connected** (cached tools only), it connects at Hermes startup with no
hot-reload — restart Hermes, or fall back to the REST scripts.

### Verify before starting

```bash
# Inherited env present? (do not cat ~/.zsh_secrets)
[ -n "$CLICKUP_API_TOKEN" ] && echo "env TOKEN ok" || echo "env TOKEN MISSING"
[ -n "$CLICKUP_API_KEY"   ] && echo "env KEY ok"   || echo "env KEY MISSING"
# Live test (scripts read env first):
python3 ~/.agents/skills/clickup/scripts/show_task.py GYMED-793 --meta
```

If the env checks fail (e.g. a daemon not launched from a zsh login shell),
fall back to the MCP server, or stop and ask the user — never guess card content.

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
   straight from the inherited env (see **Prerequisites**). Either way it
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

- **Never read `~/.zsh_secrets`** — it is the user's secret store. Trust the
  inherited env (`$CLICKUP_API_TOKEN` / `$CLICKUP_API_KEY`); only fall back to
  `~/.pi/agent/mcp.json` (MCP) or `~/.agents/.env` → `~/.hermes/.env` (legacy
  scripts) if the env is absent (e.g. a daemon not launched from a zsh login
  shell). Template: `cp ~/.agents/.env.sample ~/.agents/.env`.
- **Keep one token var**: `CLICKUP_API_KEY` is canonical (MCP mandates it); REST
  scripts read `CLICKUP_API_TOKEN` first then fall back to `KEY`. A stale
  `CLICKUP_API_KEY` in the shell env is silently ignored by MCP (which reads its
  own `mcp.json` copy) — verify the live value; don't assume two vars stay in sync.
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
