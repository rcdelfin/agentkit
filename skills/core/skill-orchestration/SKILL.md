---
name: skill-orchestration
description: "Dynamic skill router — discovers available SKILL.md metadata, matches the current task to the smallest relevant skill set, and loads those skills before acting. Trigger proactively at the start of non-trivial tasks or whenever the available skill catalog may have changed."
---

# Skill Orchestration

Discover and select the right skills before acting. Skill metadata is the source
of truth; do not maintain a duplicate routing matrix here.

## Activation model

A skill is activated by reading its `SKILL.md` and following its instructions.
Discovery only reads frontmatter metadata. The bundled discovery helper is the
sole script exception; never execute candidate-skill scripts or load full skill
bodies speculatively.

## Procedure

1. **Ground.** Apply `SYSTEM.md` and the applicable `AGENTS.md` hierarchy before
   skill guidance. Skills add domain detail; they do not override global rules.
2. **Discover.** Use the harness catalog only for candidate names and
   descriptions. It is not authoritative for paths. When absent or stale, run
   the bundled helper beside this file:

   ```bash
   python3 <skill-directory>/scripts/discover_skills.py
   ```

   For project work, set `SKILL_AGENT=pi` or `SKILL_AGENT=claude` when the
   harness is known. The helper then searches the agent-specific root first
   (`.pi/skills` then `.agents/skills` for Pi; `.claude/skills` then
   `.agents/skills` for Claude), followed by shared `~/.agents/skills`. With
   `SKILL_AGENT=auto` (the default), it searches generic `.agents/skills`, then
   agent-specific project roots:

   ```bash
   python3 <skill-directory>/scripts/discover_skills.py \
     --agent "${SKILL_AGENT:-auto}"
   ```

   Earlier roots win by skill name. It follows symlinked
   namespaces and emits `name`, absolute `path`, and `description`. Treat emitted
   paths as metadata; resolve selected names in step 4.

3. **Route.** Match the request against skill descriptions, then select the
   smallest sufficient set: normally one workflow skill plus only required
   domain or verification skills. If no skill matches, continue with global rules.
4. **Resolve paths.** Before reading any selected skill, resolve each name through
   the bundled helper, even when the catalog supplied a location:

   ```bash
   python3 <skill-directory>/scripts/discover_skills.py \
     --agent "${SKILL_AGENT:-auto}" --name <skill-name>
   ```

   Earlier roots win. Use returned path verbatim; never flatten a category or
   project namespace. A nonzero result means missing or duplicate skill;
   handle it as a gap, never guess or create an alias.
5. **Handle gaps.** If a needed skill is not installed, ask before searching or
   installing. After approval, load `find-skills`, install only through it, then
   rerun discovery. Otherwise proceed without the skill.
6. **Load and act.** Read each resolved file, then resolve its relative references
   from that file's directory. On `ENOENT`, rerun the same agent-aware `--name`
   lookup once and retry the returned path; if it fails again, report the
   filesystem error. Compose global →
   workflow → domain guidance, route only available tools, and implement the
   smallest correct change.
7. **Verify.** Run the strongest applicable checks and report any remaining
   uncertainty.

## Selection rules

- Explicit and mandatory triggers (`MUST`, `always invoke`, exact command names)
  outrank general semantic matches.
- Specific skills outrank broad skills. For example, a Pest test task selects a
  Pest skill before a general PHP skill.
- Multiple domains may match, but plausibility alone is not enough. Every loaded
  skill must have a concrete role in the task.
- Do not select `skill-orchestration` again after routing has started.
- Do not execute candidate-skill scripts during discovery; only run the
  skill-orchestration discovery helper when refreshing the catalog.
- Do not install skills during routing. Install only through `find-skills`, only
  after explicit user approval, then rerun discovery.
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
