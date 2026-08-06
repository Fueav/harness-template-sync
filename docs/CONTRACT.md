# Harness Template Sync Contract

Status: v3.0 release contract

## Decision

Harness Template Sync is the semantic adapter for one Template Delivery. It is invoked only while the Agent's current directory is the exact clean canonical `ai-first-go-template` Git root, cold-starts or explicitly upgrades one clean Target Repository named by absolute path, proves the handoff, and exits.

Normal target work is outside this plugin. After delivery, product changes, incidents, releases, deployments, refactors, and target Harness maintenance use Harness Driven Development alone. The plugins are independent release peers: neither contains, installs, invokes, or coordinates the other at runtime.

## Interfaces

| Interface | Owner | Contract |
| --- | --- | --- |
| `harness/suite_contract.json` | Scaffold Source | Versioned repository handoff and canonical source identity |
| `harness/template_delivery.py preflight` | Scaffold Source | Rejects the wrong root, dirty source/target, relative target, and mismatched intent before edits |
| `harness/template_delivery.py record` | Scaffold Source | Materializes the content-addressed target scaffold record after semantic decisions |
| `harness/template_delivery.py complete` | Scaffold Source | Requires clean convergence and target `repository_verification.py ready`, then ends delivery |
| `harnessctl scaffold audit|record` | Pinned engine | Deterministic comparison and record rendering; never semantic edits |
| Target-native checks | Target Repository | Product, project, deployment, and extension safety |

The Skill routes through these interfaces and never bundles their code or inventories. Supported suite and template contract versions are declared once in `contracts/suite-compatibility.json`.

## Delivery flow

1. Verify the exact canonical Scaffold Source root and choose `bootstrap` for a target without a scaffold record or `upgrade` for a target with one.
2. Run preflight before mutation. Read both repositories, nearest instructions, native checks, custom gates, CI, hooks, and relevant Git history.
3. Treat the target as a divergent overlay. Unknown content is target-owned; trace callers before changing wrappers or gates.
4. Resolve every managed path as exact baseline, semantic merge, preserve, relocate, retire, or blocked. Never infer deletion from a name or historical byte match.
5. Record the resolved scaffold state, commit a clean candidate, run target-native checks and its proportional Harness profile, then run complete.
6. Report exact source and target commits, preserved extensions, checks, and blockers; exit. Do not continue into the target's requested daily work in the same Skill phase.

Git supplies review and rollback. The scaffold lock is a convergence record, not plugin state, an execution transaction, or permission to overwrite target facts.

## Safety

- Stop on ambiguous ownership, conflicting authority, unrelated dirty changes, required approval, failed gates, or protected business semantics.
- Never weaken a target check, hide an expensive gate in a wrapper, or copy `harnessctl` engine source.
- Never run from a fork, target, sibling checkout, subdirectory, or merely similar template. Canonical Git identity and exact root are mandatory.
- Never add a migration CLI, bundled playbook, target inventory, project exception, background lifecycle, or plugin-to-plugin call.

## Distribution

This repository independently publishes one plugin and keeps its own semver, tags, GitHub releases, evals, and per-repository marketplaces. The recommended human onboarding uses the `fueav-harness` umbrella marketplace; that index does not change package independence.

The distributed Skill contains only `SKILL.md` and `agents/openai.yaml`. Release validation binds checked-in behavioral results to the package digest and mechanically rejects the retired multi-mode lifecycle.
