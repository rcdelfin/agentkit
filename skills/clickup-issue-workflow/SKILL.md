---
name: clickup-issue-workflow
description: "Fix a ClickUp-tracked issue end-to-end by ID (e.g. GYMED-100): ingest the card into the local wiki → branch as fix/{clickup_id} → fix on the branch → push (no MR until asked) → wait for the ai_code_review pipeline → resolve every review thread. Uses the clickup, tweak, git-actions, mr-review, and local-wiki skills. Trigger: a ClickUp-tracked issue keyed by its ID (e.g. 'fix GYMED-100')."
metadata:
  version: "2.0.0"
  scope: "global"
---

# ClickUp Issue Workflow

Fix a ClickUp-tracked issue end-to-end. This skill orchestrates: **`clickup`**
(fetch the card), **`local-wiki`** (persist it locally first), **`tweak`** (plan
the fix if it's non-trivial), **`git-actions`** (branch / commit / push / MR),
and **`mr-review`** (drive the review-thread fix loop).

## Before step 1 — ingest the card locally

Persist the ClickUp card into the project's local wiki **before** writing any
fix code, so the context survives. Hand off to **`local-wiki`** (it locates
the wiki — prefers `docs/wiki/` — and obeys the wiki's own `AGENTS.md`). It
fetches the card via **`clickup`** (`show_task.py <ID>` +
`show_comments.py <ID>`) and writes the append-only raw corpus + rebuilds the
topic page per the wiki's governance.

## Steps

1. **Branch first.** Before writing any code, ask which **base branch — develop or main**. Create the working branch from that base, named `fix/{clickup_id}` (e.g. `fix/TUKS-490`). Use **`git-actions`** for the branch.

2. **Fix the issue on that branch.** If the fix is non-trivial, plan it with **`tweak`** first.

3. **Do not open a merge request on your own.** Only create the MR — targeting **develop** — when the user explicitly asks for it.

4. **After the MR exists, wait for the `ai_code_review` pipeline to finish.** It's injected by an included CI template (so it won't appear in the repo's own `.gitlab-ci.yml`); poll via `glab ci list` (filter by branch ref) or `glab mr view <iid>`.

5. **Work through every unresolved review thread:** apply the fix (or, if the comment is not applicable, explain why). After each is fixed or addressed, **resolve the thread and leave a comment** describing what was done.
   - Run **`mr-review`** to fix locally → test → commit → push. **Fix locally first, then resolve on GitLab** — never resolve a thread before its local fix is pushed.
   - Then, via `glab api`, reply in-thread with what was done and mark the discussion `resolved=true`:
     ```bash
     env -u GITLAB_ACCESS_TOKEN glab api -X POST \
       "projects/<project>/merge_requests/<iid>/discussions/<discussion_id>/notes" \
       -f body="Fixed in <commit-sha>: <one line on what was done>"

     env -u GITLAB_ACCESS_TOKEN glab api -X PUT \
       "projects/<project>/merge_requests/<iid>/discussions/<discussion_id>" \
       -F resolved=true
     ```
   - Pushing triggers the AI to re-review, which may open new threads — repeat step 5 until no unresolved threads remain.
