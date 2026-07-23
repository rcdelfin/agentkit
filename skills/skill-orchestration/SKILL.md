---
name: skill-orchestration
description: "Dynamic skill router — discovers available SKILL.md metadata, matches the current task to the smallest relevant skill set, and loads those skills before acting. Trigger proactively at the start of non-trivial tasks or whenever the available skill catalog may have changed."
---

# Skill Orchestration

Discover and select the right skills before acting. Skill metadata is the source
of truth; do not maintain a duplicate routing matrix here.

## Activation model

A skill is activated by reading its `SKILL.md` and following its instructions.
Discovery only reads frontmatter metadata. It must never execute scripts or load
full skill bodies speculatively.

## Procedure

1. **Ground in global rules.** Apply `SYSTEM.md` and the applicable `AGENTS.md`
   hierarchy first. Skills add domain guidance; they do not override it.
2. **Discover available skills.** Prefer the harness-provided skill catalog when
   it is present and current. Refresh from disk when the catalog is absent, a
   skill changed during the session, or a referenced skill cannot be found:

   ```bash
   python3 <skill-directory>/scripts/discover_skills.py
   ```

   Resolve `<skill-directory>` from this `SKILL.md` location. The scanner infers
   the shared `skills/` root, follows symlinked project namespaces, and emits
   `name`, `path`, and `description` as tab-separated values.
3. **Match semantically.** Compare the current request and relevant conversation
   state with each skill's `name` and `description`. Descriptions are trigger
   contracts, not marketing summaries.
4. **Choose the smallest sufficient set.** Prefer one primary workflow skill plus
   only the domain or verification skills required to complete the task.
5. **Load before acting.** Read every selected `SKILL.md`. When it references a
   relative file, resolve it from that skill's directory.
6. **Compose instructions.** Follow global rules first, then workflow skills,
   then domain-specific skills. A more specific matching skill controls its
   domain unless it conflicts with higher-level instructions.
7. **Route tools.** Use directly available tools by their descriptions. For MCP
   capabilities, search the MCP catalog when needed. Never invent an unavailable
   tool; selected skills may impose additional tool requirements.
8. **Act and verify.** Implement the smallest correct change and run the strongest
   applicable checks.

## Selection rules

- Explicit and mandatory triggers (`MUST`, `always invoke`, exact command names)
  outrank general semantic matches.
- Specific skills outrank broad skills. For example, a Pest test task selects a
  Pest skill before a general PHP skill.
- Multiple domains may match, but plausibility alone is not enough. Every loaded
  skill must have a concrete role in the task.
- Do not select `skill-orchestration` again after routing has started.
- Do not execute any discovered skill's bundled scripts during discovery.
- If two skills conflict, apply the more specific instruction unless a global or
  repository instruction has higher authority.
- If an unresolved ambiguity would materially change the work, ask the user.
- If no skill matches, continue with global and repository instructions only.

## Catalog validation

Run this after adding, moving, renaming, or removing skills:

```bash
python3 <skill-directory>/scripts/discover_skills.py --check
```

Validation fails for broken symlinks, unreadable or invalid frontmatter, missing
`name`/`description`, and duplicate skill names. A successful scan proves only
that skills are discoverable; task selection remains a semantic agent decision.

## Why discovery is dynamic

A static matrix drifts whenever a skill is installed, removed, renamed, or kept
in a private symlinked namespace. Dynamic discovery keeps routing aligned with
the actual filesystem while loading only the skill bodies needed for the task.
