---
name: analogical-thinking
description: Apply analogical reasoning to problems — find structural parallels across domains, ask the 4 core questions, detect when analogies break. Use when stuck on novel problems or when domain-specific tools aren't sufficient.
version: 1.0.0
trigger: Use when encountering a novel problem where standard approaches aren't working, when brainstorming solutions, or when trying to understand a new concept by connecting it to known domains.
---

# Analogical Thinking Skill

Apply structural pattern recognition across domains to solve novel problems. Based on the cognitive science of analogical reasoning (Hofstadter, Gentner, Munger).

## When to Use

- Stuck on a problem where domain-specific tools aren't working
- Trying to understand a new concept or system
- Brainstorming solutions — need fresh perspectives
- Explaining something complex to someone
- Designing architecture or systems — looking for proven patterns
- Debugging — the bug pattern may exist in a different domain

## The 4 Core Questions

Before jumping to solutions, ask:

1. **How does this work?** — Describe the underlying mechanism, not the surface appearance
2. **Where else have I seen something that works this way?** — Search across ALL domains you know, not just the current one
3. **What domain has a solved version of this problem?** — Find the analog that already has an answer
4. **What breaks when I push this comparison too far?** — Identify where the structural parallel ends

## Procedure

### Step 1: Surface the Problem Structure

Strip away domain-specific language and describe the problem in structural terms:

- What are the components?
- What are the relationships between components?
- What are the flows/transformations?
- What are the constraints?

Example: "Users are abandoning the signup flow" → structural: "A multi-step process where each step has dropout, and the value proposition isn't visible until the end."

### Step 2: Search for Structural Analogs

Look across domains for systems with the same structural pattern:

| Problem Pattern | Structural Analog Domains |
|---|---|
| Multi-step dropout | Sales funnels, game tutorials, dating, river migration |
| Resource allocation under uncertainty | Economics, biology (foraging), logistics |
| Coordination failure | Traffic systems, distributed computing, orchestras |
| Trust building | Relationships, diplomacy, banking, onboarding |
| Scaling bottlenecks | Biology (cell division), cities, networks, supply chains |
| Information overload | Libraries, immune system, search engines, evolution |
| Feedback loops | Thermostats, addiction, markets, ecosystems |

### Step 3: Extract the Solution

From the analog domain, extract:
- What solved this structural problem?
- What was the key insight?
- What approaches failed?

### Step 4: Map Back to Your Domain

Translate the solution from the analog domain:
- How does this structural solution map to my components?
- What needs to adapt?
- Does this generate insight I didn't have before?

### Step 5: Test the Analogy's Limits

Explicitly identify where the parallel breaks:
- "The analogy works for X but breaks at Y because..."
- If the solution depends on the part where it breaks → discard, try another analog
- If the solution depends on the part where it holds → proceed

## Quick Reference: Structural Pattern Library

Common structural patterns that appear across domains:

### Feedback Loops
- Positive (reinforcing): compound interest, viral growth, panic
- Negative (balancing): thermostat, supply-demand, predator-prey

### Bottlenecks
- Serial processes: the slowest step determines throughput
- Constraint theory (Theory of Constraints / Goldratt)

### diminishing Returns
- First unit of effort → large effect, nth unit → small effect
- Appears in: learning curves, marketing, exercise, investment

### Compounding
- Small consistent gains → exponential outcomes
- Appears in: finance, habits, knowledge, relationships

### Network Effects
- Value increases with number of participants
- Appears in: platforms, immune system, language, standards

### Adapters and Interfaces
- Translation layers between incompatible systems
- Appears in: APIs, enzymes, diplomats, design patterns

### Antifragility
- Systems that get stronger from stress (not just resilient)
- Appears in: muscles, immune system, democracy, open source

## Red Flags: When NOT to Use

- **Don't use decorative analogies** — if it doesn't generate new insight, it's rhetoric, not thinking
- **Don't commit prematurely** — try multiple analogs before settling on one
- **Don't push past the break point** — if the analogy breaks at the critical part, discard it
- **Don't skip the structural analysis** — surface-level "it reminds me of..." is not analogical thinking

## Integration with Other Tools

- **With [[daily-operator]]**: When the daily brief surfaces a novel blocker, apply analogical thinking before escalating
- **With [[memory-audit]]**: The wiki/index pattern IS a structural analog to a library card catalog
- **With coding skills**: Design patterns are structural analogs — MVC is an analog to restaurant kitchen organization (order → prep → serve)
- **With debugging**: "Have I seen this symptom pattern before in a different system?" is the analogical question

## Examples in Software Development

### Architecture
- Microservices ↔ City planning (zoning, independent services, shared infrastructure)
- Event sourcing ↔ Accounting ledger (append-only, reconstruct state from history)
- Circuit breaker ↔ Electrical systems (fail safe, prevent cascade)

### Process
- Code review ↔ Peer review in science (catch errors, improve quality, share knowledge)
- CI/CD ↔ Assembly line (automated quality gates, consistent output)
- Sprint planning ↔ Military campaign planning (objectives, resources, timelines, adaptation)

---

## Analogical Debugging Workflow

**Use with**: `systematic-debugging` skill — plugs into **Phase 2: Pattern Analysis** after root cause investigation is complete.

### Why Analogical Debugging Works

Most bugs are not truly novel — they are instances of structural patterns that have been solved in other domains, other codebases, or other systems. The same underlying failure mode (race condition, resource exhaustion, state desync) manifests with different surface symptoms in every stack.

Expert debuggers recognize the *shape* of a bug before they identify the *cause*. This is analogical thinking applied to debugging: matching the structural pattern of the failure, not the surface symptoms.

### When to Activate

Trigger analogical debugging when:
- You've completed Phase 1 of `systematic-debugging` (root cause investigation) but the cause is unclear
- The symptom is unusual or doesn't match common failure patterns for the stack
- You've tried 1-2 hypotheses and they failed (don't wait for 3)
- The bug crosses component boundaries and the failure pattern is unclear
- You're debugging in an unfamiliar codebase or stack

### The 5-Step Analogical Debug Procedure

#### Step 1: Abstract the Failure Pattern

Strip away stack-specific language. Describe what's happening structurally:

| Surface Symptom | Structural Pattern |
|---|---|
| "Vue component doesn't re-render after API call" | State update not reaching observer |
| "Job processes same record twice" | Duplicate processing / idempotency failure |
| "Tests pass locally, fail in CI" | Environment-dependent behavior |
| "Response time spikes at 2pm daily" | Time-correlated resource contention |
| "Upload fails for files > 50MB" | Threshold-bound failure |
| "Random 500 errors under load" | Resource exhaustion / timeout under concurrency |

#### Step 2: Search the Bug Pattern Library

Match your abstracted pattern against known structural bug patterns:

**Timing & Concurrency**
| Pattern | Structural Analog | Typical Root Cause |
|---|---|---|
| Race condition | Traffic intersection collision | Unsynchronized access to shared state |
| Deadlock | Mexican standoff | Circular dependency waiting |
| Intermittent failure | Weather (chaotic system) | Non-deterministic ordering / timing |
| Concurrency bug | Kitchen with too many cooks | Shared resource without coordination |

**State & Data**
| Pattern | Structural Analog | Typical Root Cause |
|---|---|---|
| Stale data | Expired food in pantry | Cache not invalidated after update |
| State desync | Two clocks showing different times | Divergent state between components |
| Off-by-one | Fencepost error | Boundary condition in counting/indexing |
| Data corruption | Telephone game | Data transformed incorrectly through layers |
| Silent data loss | Black hole | Data consumed but not persisted |

**Resource & Performance**
| Pattern | Structural Analog | Typical Root Cause |
|---|---|---|
| Memory leak | Slow water leak | Resources allocated but never freed |
| Cascading failure | Domino effect | No isolation between components |
| Thrashing | Spinning wheels in mud | Working hard but no progress (e.g., GC pressure) |
| Timeout under load | Highway traffic jam | Queue backup / resource saturation |

**Integration & Environment**
| Pattern | Structural Analog | Typical Root Cause |
|---|---|---|
| Works on my machine | Island vs mainland | Missing env dependency / config drift |
| Flaky test | Weather-dependent sport | Test depends on timing or external state |
| API contract mismatch | Diplomatic translation error | Producer/consumer schema out of sync |
| Permission denied | Wrong key for the lock | Auth/role mismatch |

#### Step 3: Find Cross-Stack Analogs

Search for the same structural pattern in OTHER stacks/domains where it's well-documented:

```
Bug: "Laravel queue jobs processed twice"

Structural pattern: Duplicate processing / idempotency failure

Cross-stack analogs:
- AWS Lambda: idempotency keys prevent duplicate processing
- Databases: UNIQUE constraints prevent duplicate inserts
- HTTP: idempotent methods (PUT, DELETE) handle duplicate requests
- Messaging: Kafka consumer groups + offset tracking

Key insight from analogs: The solution is always a uniqueness constraint at the processing layer, not at the submission layer.
```

**Where to look for analogs:**
- `session_search` — "Have I debugged this pattern before in this project?"
- Web search: `"[structural pattern] bug [different language/framework]"`
- LLM wiki patterns at `/Users/raymund/Projects/LLM-wiki/`

#### Step 4: Map the Solution Back

Translate the analog's solution to your stack:

```
Analog solution: Kafka uses consumer offset tracking
↓
Mapped to Laravel: Use $job->attempt() + unique job IDs + cache()->lock()
```

#### Step 5: Validate the Analog

Before implementing, check where the analogy breaks:

- Does the analog's solution depend on something your stack doesn't have?
- Is the failure mechanism actually identical, or just similar on the surface?
- Does your system have constraints the analog doesn't?

If the solution depends on the part where the analogy breaks → discard, try another analog.

### Real-World Debugging Analogy Examples

**Example 1: The "Phantom Auth" Bug**
```
Surface: User logs in as admin but sees regular user dashboard
Phase 1: Auth succeeds, middleware passes, but controller receives wrong user

Analogical match: State desync (two clocks showing different times)
Cross-stack analog: React stale closure bug — callback captures old state

Root cause: Session middleware caches user object, role update doesn't invalidate
Fix: Add role-invalidated timestamp to session, compare on each request
```

**Example 2: The "Midnight Crash"**
```
Surface: Server 500s every night at midnight
Phase 1: No code changes, no traffic spike, logs show "connection pool exhausted"

Analogical match: Time-correlated resource contention (highway traffic jam)
Cross-stack analog: Android battery drain from background sync — scheduled tasks all fire at once

Root cause: 12 cron jobs all scheduled for 00:00, each opens DB connections
Fix: Stagger cron schedules + add connection pool monitoring
```

**Example 3: The "Works in Test, Fails in Prod"**
```
Surface: Feature test passes, production returns 403
Phase 1: Same code, same request, different response

Analogical match: Environment-dependent behavior (island vs mainland)
Cross-stack analog: Docker "works on my machine" — missing env variable

Root cause: Test uses `actingAs()`, production hits a middleware that checks a feature flag
Fix: Add feature flag to test environment, or mock the middleware
```

### Integration with systematic-debugging

| Phase | Analogical Thinking Action |
|---|---|
| Phase 1: Root Cause | Not yet — gather evidence first |
| **Phase 2: Pattern Analysis** | **Apply analogical debugging here** — abstract the failure, match to structural patterns, find cross-stack analogs |
| Phase 3: Hypothesis | The analog's solution IS your hypothesis — test minimally |
| Phase 4: Implementation | Map solution back to your stack, validate analog boundaries, implement |

### Anti-Patterns in Analogical Debugging

| Anti-Pattern | Why It Fails |
|---|---|
| "It looks like the last bug" — surface matching | Different root cause, same symptom |
| "I saw this on StackOverflow" — copy-paste fix | Solution for different context/version |
| Forcing an analogy past its break point | Solution depends on where the parallel breaks |
| Skipping Phase 1 (evidence gathering) | Analogies without evidence are just guessing |
| "It's probably a [X] bug" — premature pattern lock | Confirmation bias — only seeing evidence that fits the pattern |
