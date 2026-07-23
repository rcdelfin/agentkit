# agentkit — Cross-Harness AI Skills & Instructions

> One set of engineering instructions. Every AI coding assistant you use. No duplication.

## What's Included

Three things that make every AI coding agent on your machine behave like a
senior engineer who respects your codebase:

| Pillar | What it is | Where |
|--------|-----------|-------|
| **Instructions** | Agent identity + development workflow | `instructions/` |
| **Skills** | Procedural knowledge the agent loads on demand | `skills/` |
| **Setup** | One command to link everything into every harness | `setup.sh` |

---

## Instructions

Two canonical files define how your AI agent thinks and works. Edit them once;
every linked harness picks up changes instantly via symlinks.

### SYSTEM.md — Agent Identity & Principles

Defines **who the agent is** and **how it approaches problems**. This is the
behavioral bedrock — project instructions can add to it but never weaken it.

| Principle | What it enforces |
|-----------|-----------------|
| **Think Before Acting** | Understand the problem, inspect existing code, identify assumptions, choose the simplest solution. Ask when missing info — never guess. |
| **Capability Routing** | Identify applicable skills and tools, load the smallest sufficient set, and never assume unavailable capabilities. |
| **Systems Thinking** | Before modifying code, understand **State** (who owns truth), **Feedback** (how correctness is verified), and **Blast Radius** (what could break). |
| **Planning** | Non-trivial work must present: `Plan · Assumptions · Tradeoffs · Verification`. Break large work into incremental, verifiable steps. |
| **Implementation** | Small focused changes, readable code, existing patterns, explicit behavior, composition over abstraction. No speculative features, no premature optimization. |
| **Verification** | Never declare work complete without evidence — compilation, type checking, linting, tests, runtime validation. State why if verification isn't possible. |
| **Decision Making** | When multiple approaches exist: explain tradeoffs, recommend one, identify risks, never assume silently. |
| **Communication** | Concise. State assumptions. Summarize completed work. Transparent about uncertainty. Never exaggerate confidence. |

Every completed task must improve at least one of: **correctness,
maintainability, readability, performance, security, developer experience** —
without degrading another.

### AGENTS.md — Development Workflow

Defines **how the agent works inside a repository**. This is the operational
rulebook — the process, conventions, and guardrails.

**Core workflow** (every non-trivial task):

```text
1. Understand → 2. Route → 3. Plan → 4. Implement → 5. Verify → 6. Summarize
```

**Key rules:**

| Rule | What it does |
|------|-------------|
| **Repository Awareness (DOX)** | Before architectural decisions, walk the doc hierarchy: Child `AGENTS.md` → Parent → Root → `CLAUDE.md` → other docs. Nearest doc wins. |
| **Skill and Tool Routing** | Use dynamic skill discovery, load the smallest sufficient set, and select only currently available tools. |
| **Minimal Changes** | Only what the request requires. No future-proofing, no single-use abstractions, no unrelated refactors, no "cleanup" of adjacent code. Every modified line traces to the request. |
| **Verification by type** | Bug fix: reproduce → fix → verify. Refactor: preserve behavior, verify before & after. Feature: verify expected behavior, ensure no regressions. |
| **Documentation (DOX)** | Docs evolve with architecture. Update existing before creating new. Child `AGENTS.md` only for meaningful architectural boundaries. |
| **Continuous Improvement** | Recurring mistakes, constraints, conventions get recorded in the appropriate doc level — not repeated every session. |
| **Engineering Expectations** | Deterministic behavior, explicit ownership, small diffs, reversible changes. Long-term maintainability over clever implementations. |

### RTK.md — Optional

RTK (Rust Token Killer) CLI reference for token-optimized shell commands.
Included for users who run RTK; harmless one-line reference for everyone else.
Remove the `@RTK.md` line from `AGENTS.md` and delete `RTK.md` if unused.

### Customizing

```sh
$EDITOR ~/.agents/instructions/SYSTEM.md   # identity & principles
$EDITOR ~/.agents/instructions/AGENTS.md   # workflow & conventions
```

Every linked harness sees changes immediately — symlinks resolve at read time.

---

## Quick Start

```sh
git clone https://github.com/rcdelfin/agentkit ~/.agents
cd ~/.agents
./setup.sh
```

The script detects installed harnesses, backs up existing configs (`.bak`),
and symlinks them to `instructions/`. **Idempotent** — safe to re-run.

```sh
./setup.sh --unlink   # removes symlinks, restores .bak files
```

---

## How It Works

```
~/.agents/instructions/          ← canonical source of truth
├── SYSTEM.md
├── AGENTS.md
└── RTK.md
        ↑
        ├── ~/.pi/agent/{SYSTEM,AGENTS,RTK}.md     (symlinks)
        ├── ~/.claude/{SYSTEM,AGENTS,RTK}.md       (symlinks)
        │   └── CLAUDE.md                           = @SYSTEM.md + @AGENTS.md
        ├── ~/.codex/AGENTS.md                      (symlink)
        └── ~/.gemini/GEMINI.md                     (symlink)
```

Edit once in `instructions/` → every harness sees the update. No rebuild,
no re-install.

---

## Supported Harnesses

| Harness | Config File | Method |
|---------|-------------|--------|
| **Pi** | `~/.pi/agent/` | Direct symlinks (`SYSTEM.md` + `AGENTS.md` + `RTK.md`) |
| **Claude Code** | `~/.claude/CLAUDE.md` | Thin `@import` wrapper + symlinks |
| **Codex** | `~/.codex/AGENTS.md` | Direct symlink |
| **Gemini CLI** | `~/.gemini/GEMINI.md` | Direct symlink |

### Adding a Harness

```bash
# Append to setup.sh:
if [ -d "${HOME}/.your-harness" ]; then
  echo "Your Harness"
  link "${INSTRUCTIONS}/AGENTS.md" "${HOME}/.your-harness/INSTRUCTIONS.md"
  echo ""
fi
```

---

## Skills

Auto-discovered from `SKILL.md` files under `~/.agents/skills/`, including
nested and symlinked project namespaces. Each compatible harness loads the
catalog; [`skill-orchestration`](skills/skill-orchestration/) can refresh it from
disk and select the smallest matching skill set.

### Featured: Tweak — Change Planning

[Tweak](skills/tweak/) turns *"I want to change X"* into a self-contained,
four-artifact plan that a separate agent or teammate can execute with zero
context — then folds the results into a living system spec on archive.

**Zero install.** No CLI, no schemas, no tool adapters.

| Artifact | Answers | Contains |
|----------|---------|----------|
| `proposal.md` | **Why** | Intent, problem, assumptions, success criteria |
| `specs.md` | **What** | Delta-style behavior contract (Given/When/Then or SHALL) |
| `design.md` | **How** | File-level approach, data structures, blast radius |
| `tasks.md` | **In what order** | Ordered steps with real `Verify:` commands |

A change is **READY** when all four exist. **DONE** when tasks pass.
**ARCHIVED** when delta specs fold into `specs/<capability>.md`.

Just tell your agent:

> *Tweak: I want to add per-tier rate limiting to the public API.*

- **Full docs:** [`skills/tweak/README.md`](skills/tweak/README.md)
- **Worked example:** `skills/tweak/examples/add-rate-limiting/`

### Skill Catalog

Skills are grouped by the kind of decision they support. The directory is the
source of truth; this catalog highlights the public skills shipped with the
repository.

#### Planning, review, and architecture

| Skill | What it does |
|-------|-------------|
| [skill-orchestration](skills/skill-orchestration/) | Dynamically discovers and loads the smallest matching skill set |
| [tweak](skills/tweak/) | Turns a change request into a self-contained implementation plan |
| [scrutinize](skills/scrutinize/) | Reviews plans, PRs, and code changes from an outsider perspective |
| [improve](skills/improve/) | Audits a codebase and writes prioritized implementation plans |
| [systems-thinking](skills/systems-thinking/) | Traces state ownership, feedback, and blast radius |
| [dox](skills/dox/) | Maintains the self-documenting AGENTS.md hierarchy |

#### Debugging and reasoning

| Skill | What it does |
|-------|-------------|
| [investigate](skills/investigate/) | Leads systematic root-cause investigation |
| [systematic-debugging](skills/software-development/systematic-debugging/) | Provides a four-phase debugging workflow |
| [analogical-thinking](skills/analogical-thinking/) | Uses structural analogies when standard approaches stall |
| [ponytail](skills/ponytail/) | Enforces the smallest solution that actually works |

#### Knowledge, operations, and discovery

| Skill | What it does |
|-------|-------------|
| [local-wiki](skills/local-wiki/) | Ingests source material into a governed local knowledge base |
| [clickup](skills/clickup/) | Retrieves and triages ClickUp tasks |
| [clickup-issue-workflow](skills/clickup-issue-workflow/) | Drives a ClickUp issue from intake through review |
| [mr-review](skills/mr-review/) | Fetches and resolves merge-request review feedback |
| [find-skills](skills/find-skills/) | Discovers and installs skills from the ecosystem |
| [openspec](skills/openspec/) | Runs artifact-driven change workflows |

#### Communication and UI quality

| Skill | What it does |
|-------|-------------|
| [impeccable](skills/impeccable/) | Provides production-grade frontend design and iteration |
| [caveman](skills/caveman/) | Compresses communication while preserving technical accuracy |
| [caveman-commit](skills/caveman-commit/) | Generates concise Conventional Commit messages |

#### Development bundles

| Directory | What it contains |
|-----------|------------------|
| [software-development/](skills/software-development/) | Laravel, PHP, TDD, security, TailwindCSS, and related guidance |
| `projects/` | Private project-specific skills excluded from this repository |

### Local wiki workflow

The [`local-wiki`](skills/local-wiki/) skill supports governed project knowledge
bases. It discovers a wiki dynamically, reads its nearest `AGENTS.md` before
writing, appends source material to the raw corpus, and rebuilds derived pages.
If no governed wiki exists, the skill asks whether to bootstrap one instead of
creating an undocumented structure.

### Install from [skills.sh](https://www.skills.sh)

```sh
# Skills from the public registry are tracked in .skill-lock.json
# (gitignored — each dev installs what they need)
```

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

---

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
    ├── skill-orchestration/   ← skill and MCP routing
    ├── tweak/                 ← change planning (featured)
    ├── scrutinize/            ← code review & second opinions
    ├── improve/               ← codebase audit & roadmap
    ├── systems-thinking/      ← state, feedback & blast-radius analysis
    ├── dox/                   ← self-documenting AGENTS.md hierarchy
    ├── investigate/           ← root-cause debugging
    ├── analogical-thinking/   ← cross-domain reasoning
    ├── local-wiki/            ← governed knowledge-base ingestion
    ├── openspec/              ← artifact-driven workflows
    ├── impeccable/            ← frontend design & iteration
    ├── find-skills/           ← skill discovery
    ├── software-development/  ← Laravel, TDD, PHP, security, and more
    └── projects/              ← private skills (gitignored)
```

---

## For New Developers

1. **Clone** this repo to `~/.agents`
2. **Run** `./setup.sh` — it detects your harnesses and links everything
3. **Install skills** you want from [skills.sh](https://www.skills.sh) or add
   your own under `skills/`
4. **Customize** `instructions/` to match your team's conventions
5. **Commit** your changes — the canonical files are the shared source of truth

---

## License

MIT for the instruction files, setup script, and README.
Individual skills under `skills/` retain their own licenses.
