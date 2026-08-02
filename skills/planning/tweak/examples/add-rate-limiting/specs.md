# Specs: add-rate-limiting

> **Drift SHA**: 8a3f1c2
> **Frozen at**: 2024-11-15

> Specs are delta-style. The `## Capability:` section below maps to a file
> at `<effective-root>/specs/rate-limiting.md` after archive. This is the
> first change for this capability, so only `### ADDED Requirements` is
> used.

## Capability: rate-limiting

### ADDED Requirements

#### Requirement: Free tier rate-limited at 60 req/min

The system SHALL limit free-tier clients to 60 requests per 60-second window
and return HTTP 429 with a `Retry-After` header on the limit-exceeding
request.

**Given** an authenticated client on the free tier
**When** they make 61 requests within 60 seconds
**Then** the 61st request returns HTTP 429 with `Retry-After: <seconds-until-window-reset>`

#### Requirement: Pro tier unaffected at high volume

The system SHALL NOT rate-limit pro-tier clients at the free-tier threshold.

**Given** an authenticated client on the pro tier
**When** they make 1000 requests within 60 seconds
**Then** all 1000 requests succeed

#### Requirement: Counter survives API restart

The system SHALL persist the rate-limit counter across API process restarts
so a restart does not reset a client to a fresh window.

**Given** a free-tier client has made 50 requests in the current window
**When** the API process restarts
**Then** the next request still counts toward the same window (i.e. the
61st request from the new process returns 429)

#### Requirement: Multi-instance consistency

The system SHALL count a client's requests across all API instances, not
per-instance, so a load-balanced client cannot evade the limit by spreading
requests.

**Given** the API is running on 3 instances behind a load balancer
**And** a free-tier client has made 30 requests total, distributed across instances
**When** the client makes 31 more requests
**Then** no more than 1 of those requests succeeds (the 31st total) and the rest return 429

#### Requirement: Error response shape

The system SHALL respond to a rate-limited request with a JSON body and
matching `Retry-After` header, so clients can parse and back off.

**Given** any rate-limited request
**When** the limit is exceeded
**Then** the response body is JSON `{"error":"rate_limited","retry_after":<seconds>}`
with HTTP 429 and a `Retry-After` header whose value equals the body's
`retry_after`

#### Requirement: Internal traffic bypassed

The system SHALL bypass rate limiting for requests carrying a valid
`X-Internal-Token` header, so internal tooling and admin jobs are not
throttled by the same window.

**Given** a request with the `X-Internal-Token` header matching the configured secret
**When** the request would otherwise exceed the free-tier limit
**Then** the request succeeds without incrementing the counter

## Non-goals

- Per-endpoint limits — flat per-tier only.
- IP-based limits — different change.
- Backwards-compat with clients that don't handle 429 — they're already broken and we won't soften the blow.
