# Examples

Worked examples of completed change planning sets. Each subdirectory is a sample change with all four artifacts (`proposal.md`, `specs.md`, `design.md`, `tasks.md`) filled in.

These exist so future invocations of the skill have a concrete reference. Read one end-to-end before writing your own change set.

## Available examples

- `add-rate-limiting/` — typical backend feature: middleware, Redis counter, tier-aware limits. Demonstrates plan-specific STOP conditions and the Capabilities key in `proposal.md` that the archive step merges on.

(More to be added as real changes get planned.)

## Using these as templates

The examples are **demos, not templates**. Don't copy-paste their structure verbatim — your change will have different files, different verification commands, different risks. Read them to internalize the conventions (drift SHA at the top of every artifact, capability-keyed delta specs, scope boundaries, verify-command style, plan-specific STOPs), then write your own from scratch.