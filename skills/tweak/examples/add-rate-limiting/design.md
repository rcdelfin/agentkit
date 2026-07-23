# Design: add-rate-limiting

> **Drift SHA**: 8a3f1c2
> **Frozen at**: 2024-11-15

## Approach

A single middleware applied to all authenticated API routes. The middleware reads the authenticated client's tier from a JWT claim, looks up the per-tier limit, and checks Redis for a fixed-window counter. On miss, increment; on limit hit, respond 429. Internal traffic bypasses the counter via a shared-secret header.

## Files to change

| File | Role today | Change |
|------|------------|--------|
| `app/Http/Middleware/RateLimit.php` | does not exist | create — the middleware |
| `app/Http/Kernel.php` | registers middleware groups | add `rate-limit` to the `api` group |
| `config/rate-limit.php` | does not exist | create — tier limits and Redis connection name |
| `app/Auth/JwtTierResolver.php` | does not exist | create — extract tier from JWT claim |
| `tests/Feature/RateLimitTest.php` | does not exist | create — covers all 6 specs |
| `docs/operations/rate-limiting.md` | does not exist | create — runbook for incidents |

## Conventions to match

- **Middleware naming** follows `PascalCase` + `Middleware` suffix — see `app/Http/Middleware/Authenticate.php` for the structural pattern.
- **Config files** live under `config/` and return typed arrays — see `config/auth.php` for shape.
- **Test layout** — feature tests in `tests/Feature/`, named `<Subject>Test.php` — see `tests/Feature/AuthTest.php` for the structural pattern.
- **Logging** uses Laravel's `Log::` facade with structured context arrays — see `app/Services/OrderProcessor.php:88` for the pattern.
- **Errors** throw typed exceptions from `app/Exceptions/` — never `throw new \Exception('msg')`.

## Key data structures

```php
// config/rate-limit.php
return [
    'tiers' => [
        'free'     => ['limit' => 60,   'window' => 60],
        'pro'      => ['limit' => 1000, 'window' => 60],
        'internal' => ['limit' => PHP_INT_MAX, 'window' => 60],
    ],
    'redis_connection' => 'default',
    'key_prefix' => 'rl',
];
```

```php
// app/Http/Middleware/RateLimit.php
final class RateLimit
{
    public function __construct(
        private readonly JwtTierResolver $tierResolver,
    ) {}

    public function handle(Request $request, Closure $next): Response
    {
        $tier = $this->tierResolver->resolve($request);
        $config = config("rate-limit.tiers.{$tier}");
        $key = "rl:{$tier}:".$this->clientId($request);

        try {
            $current = Redis::incr($key);
            if ($current === 1) {
                Redis::expire($key, $config['window']);
            }
        } catch (RedisException $e) {
            Log::warning('rate_limit.redis_unavailable', ['error' => $e->getMessage()]);
            return $next($request); // fail open
        }

        if ($current > $config['limit']) {
            return $this->tooManyRequests($config['window']);
        }

        return $next($request);
    }
}
```

## Migrations

None — Redis-only state, no schema change.

## Risks

- **Multi-instance counter race** — two instances could both `INCR` concurrently and overshoot the limit slightly. Mitigation: `INCR` is atomic in Redis; overshoot is bounded by instance count. Documented in runbook.
- **Clock-skew at window boundary** — fixed window allows up to 2× the limit briefly. Mitigation: documented in runbook; sliding window is a future optimization.
- **JWT without tier claim** — middleware should default to free tier rather than fail closed. Mitigation: `JwtTierResolver` falls back to `'free'` with a logged warning.
- **Redis outage** — fail open or fail closed? Recommendation: **fail open** with structured logging. Rate limiting is a guardrail, not a security boundary; blocking all traffic because Redis is down is worse than briefly allowing over-limit traffic.

## Out of scope

- We will not change the existing `Authenticate` middleware.
- We will not add per-endpoint overrides — flat config only this round.
- We will not add a `/v1/rate-limit/status` endpoint — clients get current state from response headers only.
- We will not change the JWT claim structure — tier comes from whatever claim exists today.
