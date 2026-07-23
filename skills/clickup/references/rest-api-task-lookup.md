# ClickUp REST API: Task Lookup Patterns

> **Prefer the scripts for common cases:** `scripts/show_task.py` (full card /
> `--meta` / `--json`, with parent resolution) and `scripts/show_comments.py`
> handle credential loading and formatting automatically. The raw patterns below
> are for one-shots, debugging, or fields the scripts don't cover.

## Fetch a Task by Custom ID (e.g., GYMED-425)

```bash
curl -s "https://api.clickup.com/api/v2/task/GYMED-425?custom_task_ids=true&team_id=$CLICKUP_TEAM_ID" \
  -H "Authorization: $CLICKUP_API_TOKEN" | python3 -m json.tool
```

**Required params for custom IDs:**
- `custom_task_ids=true` — tells the API the ID is a custom format
- `team_id=$CLICKUP_TEAM_ID` — scopes lookup to the right workspace

Without both, you get: `{"err": "Team not authorized", "ECODE": "OAUTH_027"}`

## Explode Task JSON into Readable Summary

```bash
curl -s "https://api.clickup.com/api/v2/task/GYMED-425?custom_task_ids=true&team_id=$CLICKUP_TEAM_ID" \
  -H "Authorization: $CLICKUP_API_TOKEN" | python3 -c "
import json, sys
task = json.load(sys.stdin)
print(f\"📋 {task.get('name', 'N/A')}\")
print(f\"🆔 Custom ID: {task.get('custom_id', 'N/A')}\")
print(f\"📊 Status: {task.get('status', {}).get('status', 'N/A')}\")
print(f\"🎯 Priority: {task.get('priority', {}).get('priority', 'N/A') if task.get('priority') else 'None'}\")
print(f\"👤 Assignees: {', '.join([a['username'] for a in task.get('assignees', [])]) or 'Unassigned'}\")
print(f\"📁 List: {task.get('list', {}).get('name', 'N/A')}\")
print(f\"📂 Folder: {task.get('folder', {}).get('name', 'N/A')}\")
print(f\"\\n📝 Description:\\n{task.get('text_content', 'No description')[:2000]}\")
"
```

## Get Custom Fields

```bash
curl -s "https://api.clickup.com/api/v2/task/GYMED-425?custom_task_ids=true&team_id=$CLICKUP_TEAM_ID" \
  -H "Authorization: $CLICKUP_API_TOKEN" | python3 -c "
import json, sys
task = json.load(sys.stdin)
for cf in task.get('custom_fields', []):
    print(f\"{cf.get('name')}: {cf.get('value')}\")
"
```

## Get Comments

```bash
curl -s "https://api.clickup.com/api/v2/task/86ex4aw2w/comment" \
  -H "Authorization: $CLICKUP_API_TOKEN" | python3 -m json.tool
```

(Note: comments use the internal ID, not the custom ID)
