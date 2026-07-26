---
name: clickup-tweak-workflow
description: "Take a ClickUp-tracked card end-to-end by ID (e.g. GYMED-100): ingest the card into the local wiki → classify & branch (feature/bugfix/hotfix) → understand (investigate for fixes, systems-thinking for features) → route domain skills via skill-orchestration → plan with tweak when non-trivial → implement & verify → push (no MR until asked) → wait for the ai_code_review pipeline → resolve every review thread. Uses the clickup, investigate, systems-thinking, skill-orchestration, tweak, git-actions, mr-review, and local-wiki skills. Trigger: a ClickUp-tracked card keyed by its ID (e.g. 'fix GYMED-100' or 'build GYMED-100')."
metadata:
  version: "5.0.0"
  scope: "global"
---

# ClickUp Tweak Workflow

Take a ClickUp-tracked card end-to-end — bug fix **or** new feature. Maps to the
standard flow: **Understand → Route → Plan → Implement → Verify → Ship**. This
skill orchestrates: **`clickup`** (fetch the card), **`local-wiki`** (persist it
locally), **`investigate`** / **`systems-thinking`** (understand — type-
dependent), **`skill-orchestration`** (route the domain skills the change needs),
**`tweak`** (plan when non-trivial), **`git-actions`** (branch / commit / push /
MR), and **`mr-review`** (drive the review-thread fix loop).

**Scope:** any implementable card — a defect to fix, a feature to build, or a
hotfix. Understand path depends on type: **Bugfix / Hotfix** → `investigate`
(root cause; a ticket names a symptom, not the bug); **Feature** →
`systems-thinking` (state ownership, feedback loops, blast radius).

## Steps

1. **Ingest the card into the local wiki.** Persist the ClickUp card **before**
   writing any code, so the context survives. Hand off to **`local-wiki`** (it
   locates the wiki — prefers `docs/wiki/` — and obeys the wiki's own
   `AGENTS.md`). It fetches the card via **`clickup`** (`show_task.py <ID>` +
   `show_comments.py <ID>`) and writes the append-only raw corpus + rebuilds the
   topic page per the wiki's governance.

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

5. **Implement, then verify.** Build the change on the branch, then **verify
   before any push or MR** — run the project's tests / typecheck / lint (the
   strongest applicable evidence). Don't push unverified code.

6. **Do not open a merge request on your own.** Only create the MR — targeting
   the base from step 2 — when the user explicitly asks.

7. **After the MR exists, wait for the `ai_code_review` pipeline.** It's injected
   by an included CI template (so it won't appear in the repo's own
   `.gitlab-ci.yml`); poll via `glab ci list` (filter by branch ref) or
   `glab mr view <iid>`.

8. **Work through every unresolved review thread:** apply the fix (or, if a
   comment isn't applicable, explain why). After each is fixed or addressed,
   **resolve the thread and leave a comment** describing what was done.
   - Run **`mr-review`** to fix locally → test → commit → push. **Fix locally
     first, then resolve on GitLab** — never resolve a thread before its local
     fix is pushed.
   - Then, via `glab api`, reply in-thread with what was done and mark the
     discussion `resolved=true`:

     ```bash
     env -u GITLAB_ACCESS_TOKEN glab api -X POST \
       "projects/<project>/merge_requests/<iid>/discussions/<discussion_id>/notes" \
       -f body="Fixed in <commit-sha>: <one line on what was done>"

     env -u GITLAB_ACCESS_TOKEN glab api -X PUT \
       "projects/<project>/merge_requests/<iid>/discussions/<discussion_id>" \
       -F resolved=true
     ```

   - Pushing triggers the AI to re-review, which may open new threads — repeat
     step 8 until no unresolved threads remain.
