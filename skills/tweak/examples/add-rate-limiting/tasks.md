# Tasks: add-rate-limiting

> **Drift SHA**: 8a3f1c2
> **Frozen at**: 2024-11-15
>
> **Executor**: Follow each step in order. Run the Verify command after every step and confirm the expected result before moving on. Touch only the files listed under Scope. If a STOP condition triggers, stop and report — do not improvise.
>
> **Drift check (run first)**:
> `git diff --stat 8a3f1c2..HEAD -- app/Http/Middleware app/Http/Kernel.php config/rate-limit.php app/Auth/JwtTierResolver.php tests/Feature/RateLimitTest.php docs/operations/rate-limiting.md`
> If anything in scope changed since this plan was written, reconcile before executing. The plan was frozen at 2024-11-15.

## Commands you will need

| Purpose   | Command                                       | Expected on success        |
|-----------|-----------------------------------------------|----------------------------|
| Install   | `composer install`                            | exit 0                     |
| Tests     | `php artisan test --filter=RateLimit`         | all pass                   |
| Lint      | `vendor/bin/pint --dirty --format=agent`      | exit 0, no changes         |
| Routes    | `php artisan route:list --middleware=rate-limit` | lists API routes         |

## Scope

**In scope** (the only files you should modify):

- `app/Http/Middleware/RateLimit.php` (new)
- `app/Http/Kernel.php`
- `config/rate-limit.php` (new)
- `app/Auth/JwtTierResolver.php` (new)
- `tests/Feature/RateLimitTest.php` (new)
- `docs/operations/rate-limiting.md` (new)

**Out of scope** (do NOT touch):

- `app/Http/Middleware/Authenticate.php` — separate concern.
- Any JWT claim structure — tier comes from existing claims.
- Any route definition files — middleware is applied at the group level, no per-route changes.

## Steps

### Step 1: Add the config file

Create `config/rate-limit.php` with the tier limits per design.md's data structures section.

**Verify**: `php -r "var_export(require 'config/rate-limit.php');"` exits 0 and prints the expected array.

### Step 2: Add the JWT tier resolver

Create `app/Auth/JwtTierResolver.php`. Single public method `resolve(Request $request): string` returning `'free' | 'pro' | 'internal'`. Defaults to `'free'` if no claim, logs a warning via `Log::warning()`.

**Verify**: `composer dump-autoload && php -r "require 'vendor/autoload.php'; new App\Auth\JwtTierResolver();"` exits 0.

### Step 3: Add the middleware skeleton

Create `app/Http/Middleware/RateLimit.php` with constructor injecting `JwtTierResolver`. Stub `handle()` calls `$next($request)` directly — no limit logic yet.

**Verify**: `php -r "require 'vendor/autoload.php'; new App\Http\Middleware\RateLimit(new App\Auth\JwtTierResolver());"` exits 0.

### Step 4: Register the middleware

In `app/Http/Kernel.php`, add `rate-limit => \App\Http\Middleware\RateLimit::class` to the `api` middleware group. Don't apply to `web` — auth is API-only.

**Verify**: `php artisan route:list --middleware=rate-limit` lists the API routes.

### Step 5: Add the Redis `INCR` + `EXPIRE` logic

Replace the stubbed `handle()` body with the Redis logic per design.md. Use the `Redis` facade.

**Verify**: `php artisan tinker --execute "use Illuminate\Support\Facades\Redis; Redis::del('rl:test'); for (\$i=0; \$i<5; \$i++) Redis::incr('rl:test'); var_export((int) Redis::get('rl:test'));"` prints `5`.

### Step 6: Add the 429 response

Add a private `tooManyRequests(int $window): Response` method returning JSON `{"error":"rate_limited","retry_after":<seconds>}` with HTTP 429 and `Retry-After` header matching. Call from `handle()` when `$current > $limit`.

**Verify**: After step 8 lands, `php artisan test --filter=RateLimit --filter=testTooManyRequestsResponse` passes.

### Step 7: Internal-token bypass

In `handle()`, check for `X-Internal-Token` header against `config('app.internal_token')`. On match, skip the Redis check and call `$next($request)` directly.

**Verify**: `curl -i -H "X-Internal-Token: <secret>" http://localhost/api/v1/some-route` returns 200, not 429, even after free-tier limit hit. (Run after step 8.)

### Step 8: Write the tests

Create `tests/Feature/RateLimitTest.php` covering all 6 specs from `specs.md`. Use Laravel's `actingAs()` helper for auth. Use a real Redis connection (not `Redis::shouldReceive()`) — `INCR` semantics are easier to test for real than to mock. Add a `tearDown` that flushes `rl:*` keys so tests don't bleed.

Structural pattern: model after `tests/Feature/AuthTest.php`.

**Verify**: `php artisan test --filter=RateLimit` passes all 6 tests.

### Step 9: Runbook

Create `docs/operations/rate-limiting.md` with:

- How to read current counters: `redis-cli --scan --pattern 'rl:*'`.
- How to clear a client's counter: `redis-cli del rl:free:<client-id>`.
- How to temporarily raise a tier limit: edit `config/rate-limit.php`, then `php artisan config:cache`.
- What to do if Redis is down: fail-open behavior, alert channel.

**Verify**: File exists with all four sections.

## Done criteria

ALL must hold:

- [ ] `vendor/bin/pint --dirty --format=agent` exits 0
- [ ] `php artisan test --filter=RateLimit` exits 0; 6 tests pass
- [ ] `php artisan route:list --middleware=rate-limit` lists all API routes
- [ ] `redis-cli --scan --pattern 'rl:*'` works against local Redis and returns expected keys after a test request
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `<effective-root>/README.md` status row updated to `DONE`
- [ ] **Archive step run** per [archive.md](../../references/archive.md):
  `<effective-root>/archive/2024-11-15-add-rate-limiting/` exists;
  `<effective-root>/specs/rate-limiting.md` exists with all 6 `### Requirement:` blocks from `specs.md` (each preceded by a `> Last archived: <date>` line)

## STOP conditions

Stop and report (do not improvise) if:

- The middleware group in `app/Http/Kernel.php` doesn't have an `api` group (this codebase may use a different registration pattern; recon said it does — verify before stopping).
- The JWT claim for tier is named differently than what `JwtTierResolver` expects — confirm with the maintainer. **This is a silent failure:** mismatch means all clients default to `free` and pros get throttled at the free limit.
- Redis is not configured in `config/database.php` — that needs to be set up first; do not invent a fallback connection.
- A step's verification fails twice after a reasonable fix attempt.
- The archive step finds a `<effective-root>/specs/rate-limiting.md` already exists (a previous change created it) — surface the conflict before overwriting; this is a merge, not a replace.

## Maintenance notes

For whoever owns this code after the change lands:

- **Future: per-endpoint overrides.** When product asks, add an `endpoint_overrides` key to `config/rate-limit.php` and read it in `handle()` after the tier lookup.
- **Future: sliding window.** The current fixed window allows up to 2× the limit at window boundary. A sorted-set-based sliding window is a one-day spike when needed.
- **Reviewer scrutiny:** check the JWT claim name assumption in `JwtTierResolver` against the actual auth implementation. Mismatch = silent failure (all clients default to free).
- **Follow-ups deferred:** no `/v1/rate-limit/status` endpoint, no IP-based limits for unauth routes, no billing integration on limit hit.
- **Spec owner:** `<effective-root>/specs/rate-limiting.md` is now the canonical spec for this capability. Any future change that adds or modifies a rate-limit behavior goes through the same four-artifact flow, not a direct edit.
