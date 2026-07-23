---
name: skill-orchestration
description: "Skill router — activates at the start of any non-trivial task to match the task to the right domain skills and MCP tools before acting. Trigger proactively on every task, or when unsure which skills apply. Provides a decision matrix mapping task signals to skills and MCP routes. Reduces missed skill activations and ensures MCP tools are used where they add value."
---

# Skill Orchestration

Match the task to the right skills and MCP tools **before** acting. Do not start implementation until you have identified and loaded the relevant skills.

## Procedure

1. **Ground in global principles.** Apply SYSTEM.md and AGENTS.md first — think before acting, trace state/feedback/blast-radius, plan, minimal changes. These are always-on and never overridden by skills.
2. **Classify** the task using the matrix below (one or more domains may apply).
3. **Load** every matching skill's `SKILL.md` via the `read` tool.
4. **Route** to MCP tools where the matrix indicates — especially `search-docs` before writing framework code.
5. **Act** following global principles + the loaded skill's domain-specific instructions.
6. **Verify** per SYSTEM.md / AGENTS.md — tests, type-check, lint, build.

## Decision Matrix

### Backend — Laravel / PHP

| Task Signal | Skills to Load | MCP Route |
|-------------|---------------|-----------|
| Controller, model, migration, form request, policy, job, service class | `laravel-best-practices`, `laravel-conventions` | `search-docs` (Laravel version-specific syntax) |
| Eloquent query, N+1, slow query, eager loading | `database-optimization`, `eloquent-best-practices` | `database-query` (read-only verification), `database-schema` (before migrations) |
| Filament resource, page, widget, relation manager | `cms-development` | `search-docs` (Filament), `list-artisan-commands` |
| Writing or fixing Pest/PHPUnit tests | `pest-testing`, `backend-testing` | — |
| Timezone-aware scheduling, date conversion | `handling-timezones` | `search-docs` |
| Multi-tenant context, tenant models, tenant migrations | `tenancy-handling` | `search-docs` |
| Horizon queue config, supervisors, dashboard | `configuring-horizon` | `search-docs` |
| External API, OAuth, webhook, service client | `service-integration` | — |
| Merge conflict resolution | `resolving-merge-conflicts` | — |
| Dependency update, vulnerability, advisory | `dependency-audit` | — |
| Debugging a bug or unexpected behavior | `systematic-debugging` | `browser-logs`, `database-query` |

### Backend — API Design

| Task Signal | Skills to Load | MCP Route |
|-------------|---------------|-----------|
| REST endpoint, controller, API resource, request validation | `api-endpoint-development` | `search-docs`, `database-schema` |
| Lego module (auth, notifications, media, payments, etc.) | `lego-modules` | — |
| Sonic / Slack endpoint announcement | `sonic-notification` | — |

### Frontend — Vue / Nuxt / PrimeVue

| Task Signal | Skills to Load | MCP Route |
|-------------|---------------|-----------|
| Any Vue component or page | `base-components` | — |
| PrimeVue wrapper, theme, pass-through | `primevue` | — |
| Form with validation, Zod schema, maska | `form-patterns`, `zod-schemas` | — |
| Pinia store | `pinia-patterns` | — |
| Data fetching, useFetch, useAsyncData, SSR/ISR | `nuxt-data-fetching` | — |
| Nuxt config, runtime vars, routeRules | `nuxt-config` | — |
| Nuxt module (@nuxt/fonts, @nuxt/icon, @sentry, color-mode) | `nuxt-ecosystem` | — |
| Nuxt layer creation or boundaries | `nuxt-layers` | — |
| TypeScript typing, generics, defineProps | `typescript-patterns` | — |
| Performance, bundle size, reactivity bottleneck | `senior-frontend` | — |
| Error boundary, Sentry capture, error states | `error-handling` | — |
| Tailwind utility classes, responsive layout | `tailwindcss` | — |
| Accessibility, WCAG, ARIA, keyboard nav | `accessibility` | — |
| Responsive layout, container queries, touch | `responsive-design` | — |
| SCSS mixins, variables, typography | `scss-globals` | — |
| Meta tags, sitemap, Open Graph, Core Web Vitals | `seo` | — |
| Figma design → component implementation | `figma` | — |
| New AppXxx base component, compound pattern | `component-library` | — |
| High-design-quality UI, landing page, beautification | `frontend-design` | — |
| Vitest unit test for component/composable/store | `unit-testing` | — |
| Playwright E2E test | `playwright` | — |

### Frontend — API Consumption

| Task Signal | Skills to Load | MCP Route |
|-------------|---------------|-----------|
| Fetching from backend, useApiModel, pagination, CRUD | `api-patterns` | — |
| Auth flow, route protection, session, @sidebase/nuxt-auth | `auth-patterns` | — |

### Cross-Cutting

| Task Signal | Skills to Load | MCP Route |
|-------------|---------------|-----------|
| Git commit, push, branch, stage, MR | `git-actions` | — |
| GitLab MR fetch, apply diff, resolve comments | `gitlab-actions` | — |
| Worktree setup, cleanup, switch | `worktree-actions` | — |
| Security audit of a PR or code change | `security-audit-light`, `php-best-practices` | — |
| Review / audit / sanity-check a plan or PR | `scrutinize` | — |
| Codebase audit, improvement plan, roadmap | `improve` | — |
| Architecture decision, trace state/feedback/blast-radius | `systems-thinking` | — |
| TDD workflow (RED-GREEN-REFACTOR) | `test-driven-development` | — |
| Database diagram, DBML, ER diagram | `creating-database-diagrams` | — |
| ClickUp task management | `clickup` | — |
| Project documentation / DOX hierarchy | `dox` | — |
| Concise commit message | `caveman-commit` | — |

## MCP Quick Reference

| MCP Tool | When to Use |
|----------|-------------|
| `search-docs` | **Before writing any framework code.** Always. Version-specific syntax for Laravel, Filament, etc. |
| `database-schema` | Before writing migrations or models — inspect table structure |
| `database-query` | Read-only query verification — instead of raw SQL in tinker |
| `browser-logs` | Debug frontend errors and exceptions |
| `get-absolute-url` | Before sharing any project URL with the user |
| `list-artisan-commands` | Discover available Filament/Artisan commands |
| `herd` tools | Site management, PHP version, service control |

## Rules

- **Global principles come first.** SYSTEM.md and AGENTS.md are the foundation — think before acting, systems thinking, minimal changes, verification. Apply them on every task before loading any skill. Skills add domain expertise on top; they never override these principles.
- **Skills are layered, not leading.** A skill provides how-to detail for a specific domain. The decision of *what* to do and *whether* to do it follows global principles first.
- **Load before acting.** Never start implementation without checking the matrix.
- **Multiple domains are normal.** A task like "add a Filament form with API validation" hits both backend and frontend rows — load all matching skills.
- **`search-docs` is mandatory** before writing Laravel or Filament code. Do not rely on memory for version-specific syntax.
- **Skip skills that don't match.** Do not load skills speculatively — only those the matrix identifies.
- **When no skill matches**, global principles alone are sufficient — proceed without forcing a skill.
