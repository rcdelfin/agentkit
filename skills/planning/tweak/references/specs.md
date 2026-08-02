# Specs Template

Specs are the **behavior contract** — what must be true after this change lands. They are written as **deltas** keyed by capability, so the archive step can fold them into `<effective-root>/specs/<capability>.md` mechanically.

A reviewer should be able to argue with each spec ("does this spec actually hold?").

## When to fill this

After proposal, before design. Specs are testable; if you can't write a test for one, it's not a spec, it's a wish.

## Style

Pick **one** style per change and use it throughout. Don't mix.

- **Given/When/Then** — recommended for behavior-driven changes.
- **SHALL / SHALL NOT / MUST** — recommended for contract-driven changes (RFC 2119 flavor). The system-wide spec at `<effective-root>/specs/<capability>.md` typically uses this style; mirror it.

The examples below use Given/When/Then. If you use SHALL, replace the bullets with declarative requirement text and keep the `#### Scenario:` blocks (the archive step uses scenario bodies for validation, regardless of style).

## Template

```markdown
# Specs: <slug>

> **Drift SHA**: <short SHA>
> **Frozen at**: <YYYY-MM-DD>

> Specs are delta-style. Each `## Capability:` section below maps to a file
> at `<effective-root>/specs/<capability>.md` after archive. Use the
> `kebab-case` capability name from `proposal.md`'s Capabilities section.
> If the proposal's Capabilities section says "None", this file is just the
> change-specific contract and is not archived into `specs/`.

## Capability: <kebab-case name from proposal>

### ADDED Requirements

#### Requirement: <short requirement name>

<One paragraph of normative text — what the system SHALL do, or what is true
in the Given state.>

**Given** <precondition — the state before the action>
**When** <action — what the actor does>
**Then** <observable outcome — what is now true>

(Continue with more ADDED requirements. Each requirement MUST have at least
one scenario.)

### MODIFIED Requirements

#### Requirement: <existing requirement name>

> **FROM** `<effective-root>/specs/<capability>.md`:
>
> <paste the existing requirement block in full, then edit below>

<Updated normative text.>

**Given** <updated precondition>
**When** <updated action>
**Then** <updated outcome>

> **Why changed**: <one-line reason this requirement is being modified, not
> replaced or added.>

### REMOVED Requirements

#### Requirement: <requirement being removed>

> **Reason**: <why this is being removed.>
> **Migration**: <what existing callers should do instead, or "no callers"
> if the dead code path is safe to delete.>

## Non-goals

Behaviors we are NOT promising. Saves argument time later.

- Does not need to handle <X> (out of scope — see proposal.md).
- Does not optimize for <Y> (different change).
```

## How the archive step reads this file

For each `## Capability: <name>` section:

- `### ADDED Requirements` block → append each `#### Requirement:` to `<effective-root>/specs/<name>.md`.
- `### MODIFIED Requirements` block → replace the existing `#### Requirement:` in `<effective-root>/specs/<name>.md` **in full** (the FROM: paste is the source of truth for what was there before archive).
- `### REMOVED Requirements` block → move to `## Removed Requirements` in `<effective-root>/specs/<name>.md`, preserving the `**Reason**:` and `**Migration**:` lines.

If `<effective-root>/specs/<name>.md` does not exist, it is created on the first ADDED block.

## Guidance

- **One capability per section.** A change that touches two capabilities has two `## Capability:` sections. The archive merge stays deterministic.
- **Each spec names an actor** ("the user", "the API client", "the background job"). Implicit actors produce ambiguous specs.
- **Be observable, not internal.** "Returns 429 with `Retry-After` header" is a spec. "Checks the counter" is an implementation detail (that goes in `design.md`).
- **Error specs are specs.** They're the ones reviewers will actually check. Don't skip them.
- **MODIFIED requirements are full replacement.** Always paste the original in the `> FROM:` block, then write the new version. Partial updates lose detail at the next archive — the same pitfall OpenSpec calls out.
- **If this is the first change for a capability**, write only `### ADDED Requirements`. MODIFIED and REMOVED without a corresponding existing requirement is a finding, not a spec.

## Example

```markdown
## Capability: rate-limiting

### ADDED Requirements

#### Requirement: Free tier rate-limited at 60 req/min

The system SHALL limit free-tier clients to 60 requests per 60-second window.

**Given** an authenticated client on the free tier
**When** they make 61 requests within 60 seconds
**Then** the 61st request returns HTTP 429 with `Retry-After: <seconds-until-window-reset>`

#### Requirement: Pro tier unaffected at high volume

The system SHALL NOT rate-limit pro-tier clients at the free-tier threshold.

**Given** an authenticated client on the pro tier
**When** they make 1000 requests within 60 seconds
**Then** all 1000 requests succeed

#### Requirement: Internal traffic bypassed

The system SHALL bypass rate limiting for requests carrying a valid `X-Internal-Token` header.

**Given** a request with `X-Internal-Token` matching the configured secret
**When** the request would otherwise exceed the free-tier limit
**Then** the request succeeds without incrementing the counter

#### Requirement: Counter survives API restart

The system SHALL persist the rate-limit counter across API process restarts.

**Given** a free-tier client has made 50 requests in the current window
**When** the API process restarts
**Then** the next request still counts toward the same window
```

## Anti-patterns

- ❌ **"Works correctly"** — not a spec.
- ❌ **Specs that describe implementation** — those belong in `design.md`.
- ❌ **More than ~10 specs per capability** — the change is too big; split it.
- ❌ **No error specs** — the failure modes are where the risk lives.
- ❌ **Mixing Given/When/Then and SHALL in the same file** — pick one.
- ❌ **MODIFIED without a FROM: paste** — the archive step needs the original to do a full replacement.
- ❌ **Capability name not matching `proposal.md`'s Capabilities list** — the archive merge won't find the right file.
