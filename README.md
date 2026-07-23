# ~/.agents — Cross-Harness AI Skills & Instructions

> One set of engineering instructions. Every AI coding assistant you use. No duplication.

## The Problem

Every AI coding harness (Claude Code, Codex, Gemini CLI, Pi, …) reads its own
config file in its own location. When you improve your workflow rules, you edit
the same content in 3–4 places — and they drift.

## The Solution

Canonical instruction files live in `~/.agents/instructions/`. A setup script
symlinks each harness's config file back to those canonical copies. Edit once,
every harness sees the update instantly.

```
~/.agents/instructions/AGENTS.md          ← you edit THIS
        ↑
        ├── ~/.pi/agent/AGENTS.md          (symlink)
        ├── ~/.claude/AGENTS.md            (symlink)
        ├── ~/.codex/AGENTS.md             (symlink)
        └── ~/.gemini/GEMINI.md            (symlink)
```

## Quick Start

```sh
git clone https://github.com/rcdelfin/agentkit ~/.agents
cd ~/.agents
./setup.sh
```

The script:

- Detects which harnesses are installed
- Backs up existing config files (`.bak` suffix)
- Creates symlinks to `instructions/`
- Is **idempotent** — safe to re-run any time

To undo:

```sh
./setup.sh --unlink   # removes symlinks, restores .bak files
```

## Directory Structure

```
~/.agents/
├── README.md                  ← this file
├── setup.sh                   ← auto-link harness configs
├── .gitignore                 ← excludes private skills
├── instructions/              ← canonical instruction files (edit these)
│   ├── SYSTEM.md              ← agent identity & engineering principles
│   ├── AGENTS.md              ← global development workflow
│   └── RTK.md                 ← RTK token-killer reference (optional)
└── skills/                    ← skill library (auto-discovered)
    ├── tweak/                 ← change planning (featured skill)
    ├── impeccable/            ← frontend design (skills.sh)
    ├── investigate/           ← systematic debugging
    ├── scrutinize/            ← code review & second opinions
    ├── improve/               ← codebase audit & roadmap
    ├── dox/                   ← self-documenting AGENTS.md hierarchy
    ├── ponytail/              ← YAGNI / minimal-solution enforcement
    ├── caveman/               ← ultra-compressed communication mode
    ├── find-skills/           ← skill discovery (skills.sh)
    └── software-development/  ← general dev skills (Laravel, TDD, PHP, …)
```

## Supported Harnesses

| Harness | Config File | Method |
|---------|-------------|--------|
| **Pi** | `~/.pi/agent/AGENTS.md` + `SYSTEM.md` | Direct symlinks |
| **Claude Code** | `~/.claude/CLAUDE.md` | Thin `@import` wrapper + symlinks |
| **Codex** | `~/.codex/AGENTS.md` | Direct symlink |
| **Gemini CLI** | `~/.gemini/GEMINI.md` | Direct symlink |

### Adding a Harness

Append a block to `setup.sh`:

```bash
if [ -d "${HOME}/.your-harness" ]; then
  echo "Your Harness"
  link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.your-harness/INSTRUCTIONS.md"
  echo ""
fi
```

## Skills

Skills are Markdown files with YAML frontmatter, auto-discovered from
`~/.agents/skills/<name>/SKILL.md`. Each harness that supports the skills
format picks them up automatically.

### Install from [skills.sh](https://www.skills.sh)

Skills from the public registry are managed by the skills CLI and tracked
in `.skill-lock.json` (gitignored — each dev installs what they need).

### Write Your Own

```sh
mkdir -p ~/.agents/skills/my-skill
cat > ~/.agents/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: What this skill does and when to trigger it.
---
# My Skill

Step-by-step instructions the agent follows when this skill activates.
EOF
```

## Featured: Tweak — Change Planning Skill

[Tweak](skills/tweak/) is the flagship skill in this repo.
It turns *"I want to change X"* into a self-contained, four-artifact plan that
a separate agent or teammate can execute with zero context — then folds the
results into a living system spec on archive.

**Zero install.** No CLI, no schemas, no tool adapters. Just a `SKILL.md` that
teaches any compatible agent to plan changes the way a senior engineer would.

### The four artifacts

Every change gets exactly four Markdown files, written in order:

| Artifact | Answers | What it contains |
|----------|---------|------------------|
| `proposal.md` | **Why** | Intent, problem, assumptions, success criteria |
| `specs.md` | **What** | Delta-style behavior contract (Given/When/Then or SHALL) |
| `design.md` | **How** | File-level approach, data structures, blast radius |
| `tasks.md` | **In what order** | Ordered steps with real `Verify:` commands |

A change is **READY** when all four exist. **DONE** when tasks pass. **ARCHIVED**
when delta specs fold into `specs/<capability>.md` — so after twenty changes
you have one maintained answer to *"what does this system do?"* instead of
twenty tombstones.

### Quick example

Just tell your agent:

> *Tweak: I want to add per-tier rate limiting to the public API.*

The agent confirms scope, runs recon, then produces the four artifacts under
your repo's change-planning folder (`plans/<slug>/` or `docs/tweaks/<slug>/`).

### Where to learn more

- **Full docs:** [`skills/tweak/README.md`](skills/tweak/README.md)
- **Source:** bundled in this repo at `skills/tweak/`
- **Worked example:** `skills/tweak/examples/add-rate-limiting/`

## Customizing Instructions

Edit the canonical files directly:

```sh
$EDITOR ~/.agents/instructions/SYSTEM.md   # identity & principles
$EDITOR ~/.agents/instructions/AGENTS.md   # workflow & conventions
```

Every linked harness picks up changes immediately (symlinks resolve at read
time). No rebuild, no re-install.

### What's in Each File

| File | Purpose |
|------|---------|
| `SYSTEM.md` | Agent identity, engineering principles, decision-making framework |
| `AGENTS.md` | Repository workflow: understand → plan → implement → verify → summarize. DOX documentation hierarchy. Minimal-change rules. Verification gates. |
| `RTK.md` | RTK (Rust Token Killer) CLI reference for token-optimized commands |

### The `@import` Directive

`AGENTS.md` ends with `@RTK.md`. Pi and Claude Code resolve this as a file
import. Other harnesses see it as a harmless text reference.

- **Use RTK?** Keep it — the setup script links `RTK.md` automatically.
- **Don't use RTK?** Delete the `@RTK.md` line from `AGENTS.md` and remove
  `RTK.md` from `instructions/`.

## For New Developers

1. **Clone** this repo to `~/.agents`
2. **Run** `./setup.sh` — it detects your harnesses and links everything
3. **Install skills** you want from [skills.sh](https://www.skills.sh) or add
   your own under `skills/`
4. **Customize** `instructions/` to match your team's conventions
5. **Commit** your changes — the canonical files are the shared source of truth

## License

MIT for the instruction files, setup script, and README.
Individual skills under `skills/` retain their own licenses.
