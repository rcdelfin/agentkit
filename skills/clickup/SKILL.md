---
name: clickup
description: "Work with ClickUp from Hermes: MCP server setup, REST API patterns, task card pulls, and triage workflows."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ClickUp, Project Management, Task, MCP]
    related_skills: [native-mcp]
---

# ClickUp

Use this skill when working with ClickUp — fetching tasks, creating/updating issues, managing lists, or configuring the ClickUp MCP server.

## Three Ways to Interact with ClickUp

### 1. Official ClickUp MCP Server (OAuth only — limited Hermes support)

The official ClickUp MCP server is at `https://mcp.clickup.com/mcp` but uses **OAuth** (browser-based authorization), **not** personal API tokens. This means:

- ❌ **Personal API tokens (`pk_...`) are rejected** — server returns `"Failed to decode JWE header"`
- ❌ **Bearer tokens from OAuth app** — also rejected unless you've gone through the full OAuth device-code flow
- ✅ **Works in Claude Desktop, Cursor, VS Code** — these clients support the interactive OAuth redirect flow
- ⚠️ **Does NOT work with Hermes HTTP MCP transport** — Hermes supports only static headers, not OAuth authorization flows

For environments that support OAuth MCP (like Claude Desktop), add as:
```yaml
mcp_servers:
  clickup:
    url: "https://mcp.clickup.com/mcp"
    timeout: 120
    # No headers needed — OAuth is handled by the client at connection time
```

### 2. REST API (recommended for Hermes)

Use the ClickUp REST API directly via `curl` or Python `urllib` — no MCP server needed:

```bash
# Personal API token in Authorization header
curl -s "https://api.clickup.com/api/v2/task/GYMED-425?custom_task_ids=true&team_id=$CLICKUP_TEAM_ID" \
  -H "Authorization: $CLICKUP_API_TOKEN" | python3 -m json.tool
```

Set env vars:
```
CLICKUP_API_TOKEN=pk_xxxxxxxxxxxxxxxxxxxx
CLICKUP_TEAM_ID=<your_workspace_id>
```

### 3. Premium Third-Party MCP Server (requires license key)

Some npm-based ClickUp MCP servers (e.g., `@taazkareem/clickup-mcp-server`) use personal API tokens but require a separate license key:

```yaml
mcp_servers:
  clickup:
    command: npx
    args:
      - -y
      - '@taazkareem/clickup-mcp-server@latest'
    env:
      CLICKUP_API_KEY: ${CLICKUP_API_TOKEN}
      CLICKUP_TEAM_ID: ${CLICKUP_TEAM_ID}
      CLICKUP_MCP_LICENSE_KEY: ${CLICKUP_MCP_LICENSE_KEY}    # REQUIRED
```

**⚠️ Hermes filters env vars for MCP subprocesses** — only vars explicitly listed in the `env:` block are passed through. If a required env var (`CLICKUP_MCP_LICENSE_KEY`, etc.) is set in your shell but not listed here, the subprocess won't see it.

## Custom Task IDs

ClickUp custom task IDs like `GYMED-425`, `SCHOOL-123`, `NV-456` require special query params:

```bash
curl -s "https://api.clickup.com/api/v2/task/GYMED-425?custom_task_ids=true&team_id=$CLICKUP_TEAM_ID" \
  -H "Authorization: $CLICKUP_API_TOKEN"
```

The `custom_task_ids=true` flag and `team_id` are **both required** for custom IDs. Without them you get `"Team not authorized"` errors.

## Common REST API Endpoints

| Purpose | Endpoint | Notes |
|---------|----------|-------|
| Get task | `GET /api/v2/task/{id}` | Add `?custom_task_ids=true&team_id=X` for custom IDs |
| Get task (by custom ID) | `GET /api/v2/task/{custom_id}?custom_task_ids=true&team_id=X` | |
| Create task | `POST /api/v2/list/{list_id}/task` | |
| Update task | `PUT /api/v2/task/{id}` | |
| Get tasks in list | `GET /api/v2/list/{list_id}/task` | Supports filters |
| Search tasks | `GET /api/v2/team/{team_id}/task` | Supports `?search_terms=`, status, assignee filters |
| Get spaces | `GET /api/v2/team/{team_id}/space` | |
| Get folders | `GET /api/v2/space/{space_id}/folder` | |
| Get lists | `GET /api/v2/folder/{folder_id}/list` | |
| Get comments | `GET /api/v2/task/{id}/comment` | |

## Single Task Card Pull

Fetch the full content of a single task by its custom ID (e.g. `NV-428`, `GYMED-425`).

### Recommended: reusable scripts

`scripts/show_task.py` and `scripts/show_comments.py` replace the inline
`curl | python3 -c "..."` one-liners. They auto-load credentials from the
environment, falling back to `~/.hermes/.env`, so no `export` step is needed.
Resolve `scripts/...` against this skill's directory.

```bash
# Full formatted card: status, priority, assignees, dates, tags, dependencies,
# linked tasks, custom fields, subtasks, description, URL. Parent task is
# auto-resolved to its custom ID + name + status when present.
python3 scripts/show_task.py GYMED-793

# Header / status / assignee only (no description body).
python3 scripts/show_task.py GYMED-793 --meta

# Raw API JSON (replaces `curl ... | python3 -m json.tool`).
python3 scripts/show_task.py GYMED-793 --json

# Comments — accepts a custom ID or UUID (resolves the UUID internally, since
# the comments endpoint needs the task's internal ID).
python3 scripts/show_comments.py GYMED-793
python3 scripts/show_comments.py GYMED-793 --only-resolved
python3 scripts/show_comments.py GYMED-793 --json
```

The raw `curl` snippets below remain useful as primitives and an offline fallback.

### Verify setup

```bash
if [ -z "$CLICKUP_API_TOKEN" ]; then
  echo "❌ CLICKUP_API_TOKEN is not set"
  exit 1
fi
echo "✅ CLICKUP_API_TOKEN found"
echo "   CLICKUP_TEAM_ID=${CLICKUP_TEAM_ID:-5747865}"
```

### Fetch a task by custom ID

Use uppercase with hyphen (`NV-428`, not `nv428` or `NV428`):

```bash
TASK_ID="NV-428"
TEAM_ID="${CLICKUP_TEAM_ID:-5747865}"

curl -s \
  -H "Authorization: $CLICKUP_API_TOKEN" \
  "https://api.clickup.com/api/v2/task/${TASK_ID}?custom_task_ids=true&team_id=${TEAM_ID}"
```

### Inline alternatives (no scripts)

The full card, meta-only, and parent-resolution cases are all covered by
`scripts/show_task.py`. Prefer the scripts: they handle credential loading,
custom-ID normalization, parent resolution, and custom-field rendering (e.g.
`Progress %` -> `0%` instead of `{'percent_complete': 0}`).

For a one-shot without the script, pipe the raw `curl` from "Fetch a task by
custom ID" into `python3 -m json.tool`, or into a small inline formatter.

### Task comments

Use `scripts/show_comments.py` (see above). The underlying endpoint
`GET /api/v2/task/{uuid}/comment` requires the task's **internal UUID**, not the
custom ID — which is why the script resolves the UUID for you.

## Task JSON Structure

Key fields when parsing task responses:

| Field | Description |
|-------|-------------|
| `id` | Internal task ID |
| `custom_id` | Human-readable ID (e.g., GYMED-425) |
| `name` | Task title |
| `text_content` | Plain text description |
| `description` | Rich/HTML description |
| `status.status` | Current status |
| `priority.priority` | 1=urgent, 2=high, 3=normal, 4=low |
| `assignees[].username` | Assignee names |
| `creator.username` | Created by |
| `tags[].name` | Tag names |
| `list.name` | Containing list |
| `folder.name` | Containing folder |
| `space.name` | Containing space |
| `date_created` | Unix ms timestamp |
| `date_updated` | Unix ms timestamp |
| `url` | Task URL |
| `custom_fields[]` | Array of `{name, value, type, type_config}` |
| `subtasks[]` | Array of `{id, name, status}` |

## Task Triage via REST API

For daily triage / cron jobs, use the team-level task endpoint with date filtering. See `scripts/triage.py` for a ready-to-run script.

### Running triage for your tasks only

```bash
# Tasks assigned to you (auto-detects user ID from /api/v2/user)
python3 scripts/triage.py --mine

# Filter by a specific user ID
python3 scripts/triage.py --assignee 37519886
```

The `--mine` flag calls `/api/v2/user` to get your ClickUp user ID, passes `&assignee=<id>` to the API for server-side filtering, then does an additional client-side pass for accuracy.

### Quick triage pattern

```python
# Fetch open tasks updated in last N days
url = (
    "https://api.clickup.com/api/v2/team/" + TEAM_ID + "/task"
    "?include_closed=false"
    "&date_updated_gt=" + str(month_ago_ms) +  # Unix ms
    "&order_by=updated&reverse=true"             # newest first
    "&subtasks=true"
    "&page=" + str(page)
)
```

### Triage categories

| Category | Criteria |
|----------|----------|
| 🔴 Critical | `priority.id == "1"` (urgent) OR `due_date < now` (overdue) |
| 🟡 Needs Attention | Stale in-progress (>7d no update), due within 3 days, or high priority + active |
| 🟢 On Track | Everything else with recent updates |

### Python string concatenation in URL building

When building ClickUp API URLs in Python scripts, use explicit `+` concatenation instead of implicit string joining (adjacent literals). Python's implicit joining breaks when variables are interpolated between segments.

```python
# ✅ Works reliably
url = "https://api.clickup.com/api/v2/team/" + TEAM_ID + "/task" + "?page=" + str(page)

# ❌ Can cause SyntaxError in some contexts
url = ("https://api.clickup.com/api/v2/team/" + TEAM_ID + "/task"
       "?page=" + str(page))  # implicit join may not parse
```

## Cron Job / Unattended Execution

When running ClickUp tasks from a Hermes cron job, environment variables (`CLICKUP_API_TOKEN`, `CLICKUP_TEAM_ID`) may **not** be available in the cron execution context. Fallback:

1. Read from `~/.hermes/.env` (grep for `CLICKUP_API_TOKEN=` and `CLICKUP_TEAM_ID=`)
2. Search session history in `~/.hermes/sessions/` for the token (starts with `pk_`)
3. The MCP server (if configured) has its own auth — but premium third-party servers may require a license key

**Prefer REST API via `curl` / Python `urllib` for cron jobs** — avoids MCP server dependency and license issues entirely.

## Pitfalls

- **`assignee` (singular), not `assignees`** — the team task endpoint uses `&assignee=USER_ID`, NOT `&assignees=USER_ID`. The plural form returns HTTP 400. Other formats that work: `&assignees[]=USER_ID`, `&assignee[]=USER_ID`.
- **`assignee` API filter is loose** — pass `&assignee=<id>` to the API for initial filtering, then **client-side filter** by checking the task's `assignees` array for the user ID. Without the client-side pass, you get extra results (watched/created tasks mixed in).
- **Custom task IDs break without `custom_task_ids=true&team_id=X`**. Always include both query params for `GYMED-*`, `SCHOOL-*`, `NV-*` etc.
- **Custom task ID format is uppercase with hyphen — `NV-428` works, `nv428` and `NV428` do not.** The API returns `"Team not authorized"` (not 404) when the format is wrong. Always use the canonical form: `PROJECT-###`. This applies to all custom IDs including `GYMED-425`, `NV-356`, `SCHOOL-123`, etc.
- **The `Authorization` header format is just `pk_xxxxx`** — no `Bearer` prefix for personal tokens. OAuth tokens use `Bearer`.
- **MCP config changes require a Hermes restart** — MCP servers connect at startup and don't hot-reload.
- **Premium MCP servers require a license key** — `@taazkareem/clickup-mcp-server` and similar return `CLICKUP_MCP_LICENSE_KEY` errors. Prefer the REST API fallback — no license, no OAuth, works everywhere.
- **Rate limits**: ClickUp API has rate limits per plan. Check `API availability by Plan` in docs.
- **The `linked_tasks` array may be empty depending on workspace configuration** (ClickUp's "Task Relationships" feature must be enabled).
- **REST API and MCP can coexist** — using the REST API doesn't interfere with the ClickUp MCP server if one is also running.
- **The `text_content` field may have truncated line breaks** — use `description` field for rich text when available.
- **Team task endpoint returns oldest first by default** — always use `&reverse=true` with `&order_by=updated` for newest-first. Without date filtering, you'll get 2018-era tasks.
- **`date_updated_gt` filter is essential** — without it, the team task endpoint returns ALL open tasks (potentially thousands of ancient ones). Set to last 30 days for triage.
- **Pagination**: Each page returns up to 100 tasks. Loop until `tasks` array is empty. For workspaces with 258+ spaces, limit pages to ~15 (1500 tasks) to stay within cron job timeouts.
