---
name: mr-review
description: "Fetch and resolve GitLab MR review feedback (AI Assistant, human reviewers, bots). Trigger on: fix MR review, address review comments, fix AI assistant findings, resolve MR feedback, or any mention of MR review + fix. Covers the full loop: fetch comments → categorize by severity → fix locally → test → commit → push."
argument-hint: "[MR IID or URL]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - ast_grep_search
---

# MR Review

Fetch review feedback from a GitLab MR, understand each issue, fix it locally, verify, and push — all in one pass.

## When to Use

- User says "fix MR review", "address AI assistant findings", "fix review comments"
- A GitLab AI Assistant or human reviewer posted feedback on an MR
- User provides an MR number or URL with a "fix" or "review" intent

## Prerequisites

- `glab` CLI installed and authenticated (`glab auth login`)
- On the MR's source branch locally (or willing to checkout)
- Current working directory is the project root with `.git`

## Procedure

### 1. Fetch MR Comments

Prefer the bundled script — it handles auth (via `glab api`), severity parsing,
and the resolvable-aware open/resolved check in one call:

```bash
python3 scripts/show_threads.py <group/project> <iid>          # all threads
python3 scripts/show_threads.py <group/project> <iid> --open    # unresolved only
```

Resolve `scripts/...` against this skill's directory. Output:
`STATUS  [SEVERITY]  @author  <first line>  <discussion-id>`. The AI
review bot's informational "work complete" summary thread has no resolvable
note and is skipped automatically.

**Fallback** (no script, or debugging) — inline `glab api` + python:

```bash
# Get all non-system notes from the MR
env -u GITLAB_ACCESS_TOKEN glab api \
  "projects/<url-encoded-project-path>/merge_requests/<iid>/notes?per_page=100" \
  | python3 -c "
import sys, json
notes = json.load(sys.stdin)
for n in notes:
    if n.get('system'): continue
    author = n.get('author', {}).get('username', '?')
    body = n.get('body', '')
    created = n.get('created_at', '')[:19]
    print(f'--- @{author} ({created}) ---')
    print(body[:3000])
    print()
"
```

**Alternative** (if project path is unknown — auto-resolve from remote):

```bash
REMOTE=$(git remote get-url origin)
# SSH: git@gitlab.com:group/project.git → group%2Fproject
# HTTPS: https://gitlab.com/group/project.git → group%2Fproject
PROJECT=$(echo "$REMOTE" | sed 's/.*gitlab.com[:/]\(.*\)\.git/\1/' | python3 -c "import sys,urllib.parse;print(urllib.parse.quote(sys.stdin.read().strip(),safe=''))")
env -u GITLAB_ACCESS_TOKEN glab api "projects/$PROJECT/merge_requests/<iid>/notes?per_page=100"
```

### 2. Categorize Feedback

Parse each comment and classify by what action it requires:

| Category | Examples | Action |
|----------|----------|--------|
| **Straightforward fix** | Add guard clause, anchor regex, fix type hint, missing validation | Fix directly |
| **Architectural suggestion** | Extract trait, introduce abstraction, change pattern | Assess tradeoffs, implement if reasonable |
| **Needs clarification** | Ambiguous, subjective, or risky | Present to user, ask before acting |
| **Informational / dismissed** | "Nice work", false positive, out of scope | Skip |

Look for severity indicators the AI Assistant uses:

- 🔴 **High** — likely a bug or security issue
- 🟠 **Medium** — correctness edge case, should fix
- 🟡 **Low** — code quality, DRY, style
- ✅ — review complete / positive feedback

### 3. Implement Fixes

For each actionable item:

1. **Read the target file** — understand the current code before changing
2. **Apply the fix** — minimal change, follow existing code conventions
3. **Check for DRY** — if the same pattern exists in sibling files, fix all occurrences
4. **Add/update tests** — cover the new edge case or behavior

### 4. Verify

```bash
# Format (backend/Laravel)
vendor/bin/pint --dirty --format agent

# Run affected tests
php artisan test --compact --filter="<TestFileOrDescribeBlock>"
```

### 5. Commit and Push

```bash
# Stage only the changed files (never git add -A)
git add <specific-files>

# Commit with review-context message
git commit -m "fix(scope): TICKET-ID address MR review — <short summary>" \
           -m "<what changed and why>"

# Push (pre-push hooks will run full test suite)
env -u GITLAB_ACCESS_TOKEN git push
```

### 6. Reply to Each Finding and Resolve

After pushing, **close the loop on the MR**. For every finding thread, post a
note explaining the resolution, then mark the thread resolved. This is how the
AI Assistant and human reviewers see the disposition of each item — silent fixes
leave findings looking unaddressed.

For each thread in the MR (`/merge_requests/:iid/discussions`):

| Disposition | When | Comment content |
|---|---|---|
| **Accepted** | Fix matches the suggestion | "Fixed in `<short-sha>`. <one line on what changed>" |
| **Accepted with adjustment** | Fix implements the intent differently | "Fixed in `<short-sha>` with a documented deviation. <what you did instead, and WHY>" |
| **Partially accepted** | Only part of the suggestion applied | "Partially applied in `<short-sha>`. <what was done, what was skipped, and why>" |
| **Not accepted** | Suggestion rejected | "Not applying. <rationale — false positive, out of scope, or risk>" |

Post via `POST /projects/:id/merge_requests/:iid/discussions/:discussion_id/notes`,
then mark resolved via `PUT .../discussions/:discussion_id` with `resolved=true`.

Prefer the bundled script — it does both calls and sidesteps the rtk-wrapper
gotcha (building the URL in Python, not on the shell line):

```bash
python3 scripts/resolve_thread.py <group/project> <iid> <discussion_id> \
  "Fixed in <sha>: <one line on what changed>"
```

**Inline** (the script wraps these two calls) — **inline the discussion ID
literally** (see Pitfalls — shell variables in the URL path 404 under the rtk
wrapper):

```bash
PROJ="group%2Fproject"
glab api -X POST "projects/$PROJ/merge_requests/<iid>/discussions/<discussion_id>/notes" \
  -f body="Fixed in <sha>: <one line>"
glab api -X PUT "projects/$PROJ/merge_requests/<iid>/discussions/<discussion_id>" \
  -F resolved=true
```

**Verify after** (system notes return `resolved: null`, so filter to
resolvable notes — see Pitfalls):

```bash
glab api "projects/$PROJ/merge_requests/<iid>/discussions" | python3 -c "
import sys, json
for disc in json.load(sys.stdin):
    notes = disc.get('notes', [])
    findings = [n for n in notes if n.get('author',{}).get('username')=='dev_appetiser' and not n.get('system')]
    if not findings: continue
    open_notes = [n for n in notes if n.get('resolvable') and not n.get('resolved')]
    print('OPEN ' if open_notes else 'RESOLVED ', disc['id'][:12])
"
```

Rules:

- **Always name the commit SHA** so reviewers can diff-verify.
- **Deviations MUST be explained** — if you knowingly do the opposite of the
  suggestion (e.g. revert to `env()` after `config()` was suggested), state the
  reason in the note. An unexplained deviation looks like a mistake, not a
  decision.
- **Don't silently resolve a rejected finding** — post the rationale in the
  thread before marking it resolved.
- **Resolve only after a push** — resolving before pushing makes the fix
  untraceable if the push fails.

## Pitfalls

- **Stale `GITLAB_ACCESS_TOKEN` env var** — a wrapper or old config may inject an expired token that overrides `glab auth login`. Always prefix glab commands with `env -u GITLAB_ACCESS_TOKEN` to use the config-stored token.
- **rtk wrapper mangles variable-interpolated `glab api` URLs** — putting the discussion ID in a shell variable (`$DID`) and interpolating it into the API path (`.../discussions/$DID/notes`) silently 404s. The wrapper treats the `%2F`-encoded project path or the interpolated segment as a filesystem path. **Always inline the full discussion ID literally in the URL string** — no shell variables in the path. Calling `glab api` inside a `bash` function with `local` vars fails the same way; use flat sequential inline calls instead. Never redirect `glab api` output to `/dev/null` during resolution — the 404 is silent and you'll believe the thread resolved when it didn't. Verify thread state after.
- **System/auto notes return `resolved: null`, not `false`** — GitLab attaches non-resolvable system notes ("changed this line in version N of the diff", "added 1 commit") to discussion threads. A naive `all(n['resolved'] for n in notes)` check reports the thread as unresolved forever, because `None` is falsy. To check if a thread is actually open, filter to resolvable notes: `[n for n in notes if n.get('resolvable') and not n.get('resolved')]`. Empty → resolved.
- **The AI review "summary" thread is not a finding** — the review bot posts one informational thread ("✅ AI Assistant's work is complete" with a file-change table) alongside the actual findings. It has no resolvable note; the resolvable-aware check above naturally skips it. Don't try to resolve it as a finding.
- **AI Assistant severity ≠ must-fix** — review each suggestion critically. Low-severity items (style, DRY) are often worth fixing but don't change behavior. High/Medium (correctness, edge cases) should always be addressed.
- **Duplicate code across request/resource files** — the AI Assistant frequently flags duplication. Check if a `Concerns/` trait pattern already exists in the codebase before creating a new abstraction.
- **Inline code suggestions may not compile** — the AI Assistant's snippets are illustrative. Always adapt to the actual code context, don't paste blindly.

## Verification

- [ ] All actionable review comments addressed or explicitly skipped with rationale
- [ ] Pint formatting passes
- [ ] Affected tests pass
- [ ] Commit pushed to MR source branch
- [ ] Each finding has a posted note on its discussion thread with the resolution (accepted / adjusted / partial / rejected + commit SHA)
- [ ] Addressed threads marked resolved — confirm with `show_threads.py <project> <iid> --open` → "no open threads"
