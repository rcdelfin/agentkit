---
name: hermes-agent-skill-authoring
description: "Use when creating, editing, or reviewing SKILL.md files. Keep triggers precise, context progressive, and bodies lean."
version: 1.0.0
author: Private skills
authoring_source: Hermes Agent 1.1.0
license: MIT
metadata:
  tags: [skills, authoring, conventions, token-budget]
---

# Skill Authoring

Create skills that change agent behavior without repeating system guidance or
loading a large playbook on every matching turn. This is a Pi/private-tree
adaptation of Hermes Agent's `hermes-agent-skill-authoring` skill.

## When to Use

- Creating or editing non-project `SKILL.md` files under `~/.agents/skills/`.
- Reviewing a skill for trigger quality, duplication, or token waste.
- Porting a skill from another agent framework.

Do not use this for ordinary Markdown documentation, one-off task notes, or
company-owned skills under `~/.agents/skills/projects/`.

## Ownership and placement

- Non-project directories under `~/.agents/skills/` are the open-source/private
  skill source tree; edit them directly with `write` or `edit`, preserving their
  category and existing conventions.
- `~/.agents/skills/projects/` is company-owned. Never create, edit, delete, or
  reformat files there from this skill.
- `skill_manage` creates persistent Pi-native skills in its own managed store;
  it is not a substitute for editing this private source tree.
- Before editing, read applicable `AGENTS.md` files and the target skill body.

## Procedure

1. **Check for an existing skill.** Search by trigger, name, and behavior. Extend
   the closest skill instead of creating a duplicate. Done when one owner for
   the behavior is identified.
2. **Define the trigger.** State what user request activates the skill and what
   distinctive behavior it adds. Put the trigger in the first sentence of the
   description. Done when a non-matching request is easy to name.
3. **Write valid frontmatter.** Start at byte 0 with `---`; include `name` and
   `description`; close with `---` before a non-empty body. Use lowercase,
   hyphenated names and keep names ≤64 characters.
4. **Write the smallest useful body.** Keep always-needed rules in `SKILL.md`.
   Include actionable steps, relevant tool names, failure boundaries, and
   checkable completion criteria. Cut generic advice and duplicated system rules.
5. **Progressively disclose detail.** Move branch-specific commands, long
   examples, and reference material to `references/`, `templates/`, or
   `scripts/`; link them from the body and load them only when that branch is
   active.
6. **Port carefully.** Replace source-framework paths, tools, hooks, and APIs
   with capabilities that exist here. Never copy instructions that silently
   invoke unavailable tools or mutate unrelated state.
7. **Validate.** Run the checks below. Done means frontmatter parses, metadata is
   discoverable, no duplicate name exists, and the changed file is accounted for.

## Low-token rules

- Description: one trigger-focused sentence; aim for ≤200 characters. The first
  57 characters should still identify when to use the skill.
- Body: aim for ≤6,000 characters for a workflow skill; split larger branches
  instead of making every invocation pay for them.
- Prefer one strong rule over several paraphrases. Keep a pitfall only when it
  prevents a recurring failure.
- Avoid tool catalogs, generic "best practices," long rationale, and examples
  that do not change decisions.
- End ordered steps with observable completion criteria; this prevents premature
  completion more cheaply than extra prose.

## Compact shape

```markdown
# Skill title

## Overview
What behavior this skill makes reliable.

## When to Use
Triggers and counter-triggers.

## Procedure
Numbered actions with completion criteria.

## Pitfalls
Only recurring, concrete failures.

## Verification
Smallest checks that prove the skill is valid and its work is complete.
```

## Validation

For a private-tree skill, run:

```bash
python3 - <<'PY'
from pathlib import Path
import re

p = Path("~/.agents/skills/<category>/<name>/SKILL.md").expanduser()
s = p.read_text()
assert s.startswith("---\n")
match = re.search(r"\n---\n", s[4:])
assert match, "unterminated frontmatter"
frontmatter = s[4:match.start() + 4]
assert re.search(r"^name:\s*[^\n]+$", frontmatter, re.M)
assert re.search(r"^description:\s*[^\n]+$", frontmatter, re.M)
assert len(s) <= 100_000
print(f"valid: {p} ({len(s)} chars)")
PY
python3 ~/.agents/skills/skill-orchestration/scripts/discover_skills.py \
  --root ~/.agents/skills --check
```

Also inspect the diff and confirm no unrelated skill or generated file changed.

## Pitfalls

1. `skill_manage(action='create')` writes its managed Pi skill store, not this
   private source tree.
2. A copied skill can contain valid Markdown but invalid local tool names,
   paths, hooks, or delegation APIs.
3. A generic or late trigger makes the skill expensive and easy to misroute.
4. Adding detail without deleting replaced wording creates skill sediment.
5. A large body is not thoroughness; branch-specific detail belongs behind a
   reference link.

## Verification checklist

- [ ] Existing skill ownership checked; no duplicate behavior added.
- [ ] Trigger is precise and front-loaded in description.
- [ ] Frontmatter starts at byte 0 and has required fields.
- [ ] Body is concise, actionable, and locally compatible.
- [ ] Branch-specific detail is progressively disclosed.
- [ ] Private-tree validation and discovery checks pass.
- [ ] Diff contains only intended skill changes.
