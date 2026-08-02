---
name: local-wiki
description: "Ingest source content (ClickUp cards, meeting notes, transcripts, specs) into the project's governed local knowledge base. Dynamically locates the wiki (prefers docs/wiki/), then obeys the wiki's own AGENTS.md for structure and rules. Trigger: 'ingest into the wiki', 'add to wiki', 'capture this card/note locally', or any workflow that needs to persist a source doc locally before working on it."
metadata:
  version: "1.0.0"
  scope: "global"
---

# Local Wiki

Ingest source content into the project's **governed local wiki** — the append-only
raw corpus + rebuild-only topic pages that capture knowledge before it scrolls
away in ClickUp/chat. This skill locates the wiki **dynamically** and defers to
its own governance for the exact structure; it does not hardcode one layout.

## Locate the wiki (dynamic — prefer `docs/wiki/`)

A wiki is "governed" if it has an `AGENTS.md` (or `CLAUDE.md`) defining its
layout. Search in this order, use the first match, **prefer `docs/wiki/`**:

```bash
for d in docs/wiki wiki docs/kb docs/knowledge docs/notes; do
  if [ -f "$d/AGENTS.md" ] || [ -f "$d/CLAUDE.md" ]; then echo "WIKI=$d"; break; fi
done
```

- **Found** → set `WIKI=<dir>`, read **`<WIKI>/AGENTS.md`** and obey it (DOX: nearest AGENTS.md wins).
- **Ambiguous** (several candidates, none `docs/wiki/`) → list them and ask the user.
- **None found** → ask the user where the wiki lives, or whether to bootstrap a minimal `docs/wiki/`. Do **not** silently invent a structure.

## Obey the wiki's own governance

The wiki's `AGENTS.md` is the source of truth for: the raw-corpus layout, page
format, what's append-only vs rebuild-only, whether the tree is git-ignored, and
URL-sourcing rules. **Read it before writing.** Never hand-edit rebuild-only
pages; never delete from the append-only raw corpus.

## Ingestion pattern (adapt to the wiki's actual structure)

1. **Fetch the source** via the right skill — `clickup` for a ClickUp card
   (`show_task.py <ID>` + `show_comments.py <ID>`). For meeting notes /
   transcripts / specs, take the user-provided content.
2. **Write to the append-only raw corpus** at the wiki-defined path, with the
   wiki-required front-matter. For the standard `docs/wiki` layout:
   - ClickUp card → `<WIKI>/raw/clickup/<ID>-<slug>.md` with `custom_id:` and
     `url:` **copied from the card** (never retype a URL).
   - Other sources → the subdir the wiki's AGENTS.md specifies.
3. **Rebuild the topic page** per the wiki's rebuild flow — for `docs/wiki`:
   `pages/<slug>.md` in the canonical meta-block format, then update `index.md`
   and append a one-line `log.md` entry.
4. **Don't touch a consumer-facing changelog** (e.g. `docs/wiki/CURRENT-CHANGELOG.md`)
   from ingestion — it has its own separate, human-reviewed workflow.

## Reference implementation (`docs/wiki`)

The convention this skill defaults to when the wiki's AGENTS.md is silent:

| Path | Role | Rule |
|---|---|---|
| `raw/clickup/` | one file per `GYMED-XXX` ClickUp task | append-only |
| `raw/` (other) | meeting notes, transcripts, exports | append-only |
| `pages/` | one topic page per source, AI-built | **rebuild-only — never hand-edit** |
| `glossary/` | domain terms | rebuild-only |
| `queries/` | saved query outputs | add; rewrite only if stale |
| `index.md` | catalog | update on every page change |
| `log.md` | wiki changelog | append-only |
| `CURRENT-CHANGELOG.md` | consumer release notes | separate workflow — don't touch on ingest |

## Pitfalls

- **Nearest AGENTS.md wins** — if `<WIKI>/AGENTS.md` contradicts this skill, follow the wiki, not this file.
- **Pages are rebuild-only** — to change a page, rebuild it from `raw/`; don't hand-edit.
- **`raw/` is append-only** — never delete or overwrite an existing export.
- **URLs are copied, never retyped** — paste from the source front-matter/body.
- **Often git-ignored / local-only** — the whole tree commonly stays on contributor machines; don't assume it's committed.
- **Don't auto-create a wiki** — if none is found, ask; bootstrapping a governed wiki is a decision, not a side effect.
