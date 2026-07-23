# Proposal: add-rate-limiting

> **Drift SHA**: 8a3f1c2
> **Frozen at**: 2024-11-15

> **Status** lives in `<effective-root>/README.md`. Do not duplicate it here.

## Why

Our public API currently has no rate limiting. Three production incidents in the last quarter:

- **2024-09-12**: A single misbehaving client made 50k requests in 10 minutes, saturating our worker pool and causing 18 minutes of 503s for everyone else.
- **2024-10-03**: A webhook partner retried aggressively during a partial outage and amplified load by ~40x.
- **2024-11-02**: A scraping bot pulled the entire products table at 200 req/s for 6 hours, ballooning egress costs by ~$400.

We need per-client throttling to protect other tenants and bound infrastructure costs.

## What changes

- New `RateLimit` middleware applied to all authenticated API routes.
- Per-tier limits (free: 60/min, pro: 1000/min, internal: unlimited).
- Response on limit: HTTP 429 with `Retry-After` header.
- Counter storage: Redis (already in our stack, low-friction to add).

## Capabilities

The merge key for the archive step. The single capability below is new — no
existing `<effective-root>/specs/rate-limiting.md` is being modified.

- `rate-limiting`: per-tier request throttling backed by Redis with a fixed-window counter.

## Assumptions

- The API uses a single `api` middleware group in `app/Http/Kernel.php` (verified: `Kernel.php:23`). We add `rate-limit` to this group; no per-route changes.
- The JWT issued by the auth service carries a `tier` claim with values `free` | `pro` | `internal` (verified: `app/Auth/JwtParser.php:41`).
- Redis is configured and reachable under the `default` connection (verified: `config/database.php:78`).
- `app/Exceptions/` already defines the typed exception hierarchy used by the rest of the app (verified: `app/Exceptions/Handler.php:1`).

## Out of scope

- Per-endpoint overrides — all endpoints get the same per-tier limit.
- IP-based limits for unauthenticated routes — separate change.
- Billing integration — when a client hits the free-tier limit, we don't (yet) prompt upgrade.

## Success criteria

- p99 added latency from the middleware ≤ 5ms.
- No new false positives (legitimate clients should never see 429).
- On simulated 10k req/s load from a single client, that client gets 429s while other clients remain unaffected.

## Open questions

- Counter TTL — 60s fixed window (recommended) vs. sliding window?
- Should we expose current usage via an `X-RateLimit-Remaining` response header? (recommended yes; standard practice)

## Changelog (only on update)

- 2024-11-15 — Initial draft.
