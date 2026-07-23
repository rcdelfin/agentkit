# ClickUp MCP Server Setup

## Official ClickUp MCP Server (OAuth only)

The official ClickUp MCP server is hosted at `https://mcp.clickup.com/mcp` as a remote HTTP server.

- URL: `https://mcp.clickup.com/mcp`
- Auth: **OAuth only** — browser-based authorization flow
- ❌ Personal API tokens (`pk_...`) are **rejected** (returns `"Failed to decode JWE header"`)
- ❌ Not compatible with Hermes HTTP MCP transport (Hermes only supports static headers)
- ✅ Works in Claude Desktop, Cursor, VS Code (these support OAuth redirect)

### Hermes Config (for Claude Desktop-style clients only)

```yaml
mcp_servers:
  clickup:
    url: "https://mcp.clickup.com/mcp"
    # No headers — client handles OAuth
```

## Premium Third-Party Server (`@taazkareem/clickup-mcp-server`)

This npm-based server uses personal API tokens but requires a separate license key.

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
      CLICKUP_MCP_LICENSE_KEY: ${CLICKUP_MCP_LICENSE_KEY}
```

### ⚠️ Hermes Filters MCP Subprocess Env Vars

Only vars explicitly listed in the `env:` block are passed to the MCP subprocess. If you set `CLICKUP_MCP_LICENSE_KEY` in your shell but don't list it under `env:`, the subprocess won't see it and will return:

```
🔒 Premium Feature Locked
A valid license key is required to use this tool.
```

### ⚠️ Template Variable Expansion May Not Work

The `${VAR}` syntax in MCP `env:` values may not be expanded by Hermes — the literal string `${CLICKUP_API_TOKEN}` might be passed instead of the resolved token value. If the MCP server fails auth despite the env var being set and listed in `env:`, try hardcoding the value directly.

## Recommended Approach for Hermes

Since both MCP server options have limitations:
- **Official**: OAuth-only, incompatible with Hermes
- **Premium**: Requires license key + may have template expansion issues

**Use the REST API directly** via `curl` with personal tokens. See `references/rest-api-task-lookup.md` for patterns, and `scripts/triage.py` for a working daily triage implementation.

## Env Vars Checked

```bash
echo "CLICKUP_API_TOKEN set: $([ -n \"$CLICKUP_API_TOKEN\" ] && echo 'YES' || echo 'NO')"
echo "CLICKUP_TEAM_ID set: $([ -n \"$CLICKUP_TEAM_ID\" ] && echo 'YES' || echo 'NO')"
echo "CLICKUP_MCP_LICENSE_KEY set: $([ -n \"$CLICKUP_MCP_LICENSE_KEY\" ] && echo 'YES' || echo 'NO')"
```
