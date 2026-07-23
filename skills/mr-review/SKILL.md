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

## Pitfalls

- **Stale `GITLAB_ACCESS_TOKEN` env var** — a wrapper or old config may inject an expired token that overrides `glab auth login`. Always prefix glab commands with `env -u GITLAB_ACCESS_TOKEN` to use the config-stored token.
- **AI Assistant severity ≠ must-fix** — review each suggestion critically. Low-severity items (style, DRY) are often worth fixing but don't change behavior. High/Medium (correctness, edge cases) should always be addressed.
- **Don't resolve threads on GitLab** — this skill is local-only. The MR author resolves threads after verifying the push, or the AI Assistant re-reviews automatically on new pushes.
- **Duplicate code across request/resource files** — the AI Assistant frequently flags duplication. Check if a `Concerns/` trait pattern already exists in the codebase before creating a new abstraction.
- **Inline code suggestions may not compile** — the AI Assistant's snippets are illustrative. Always adapt to the actual code context, don't paste blindly.

## Verification

- [ ] All actionable review comments addressed or explicitly skipped with rationale
- [ ] Pint formatting passes
- [ ] Affected tests pass
- [ ] Commit pushed to MR source branch
- [ ] AI Assistant re-reviews on push (automatic on GitLab Premium+)
