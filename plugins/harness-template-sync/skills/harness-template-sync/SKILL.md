---
name: harness-template-sync
description: Use when a repository needs Harness bootstrap, adoption, refresh, or entropy reduction against ai-first-go-template.
---

# Harness Template Sync

Use this Skill for semantics; `harnessctl` handles mechanical convergence.

## Authority

- Reference template: `git@github.com:moss-site/ai-first-go-template.git`.
- Target instructions, gates, and checks own project facts.
- Template `BLUEPRINT.md` and `harness/scaffold_manifest.json` own the shared baseline.
- `harnessctl scaffold audit|record` owns comparison and records; the Agent owns merges.
- Restore thin prompts, thick artifacts and context, thin skills.

## Workflow

1. Classify `bootstrap`, `adopt`, `refresh`, or `govern`; route `govern` through `HARNESS-MAINTENANCE`.
2. Pin a clean template checkout; read both repositories before editing.
3. Run `harnessctl scaffold audit` first; its JSON inventories drift, while unknown target content stays project-owned.
4. Trace callers with `rg` and history. Relocate valid facts before slimming prompts, skills, scripts, or artifacts.
5. Keep gates independently visible; split composite wrappers only after tracing callers.
6. Resolve each semantic path, render `harness/scaffold.lock` with `harnessctl scaffold record`, save its exact JSON, then rerun audit to convergence.
7. On a clean candidate, run native checks and proportional Harness verification. Report decisions, extensions, evidence, latency, and blockers.

Stop on ambiguous ownership, conflicting authority, unrelated dirty changes, required approval, or failed gates.
