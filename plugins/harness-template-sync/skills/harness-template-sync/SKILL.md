---
name: harness-template-sync
description: Use when a blank, mature, or Harness-enabled repository needs bootstrap, adoption, refresh, slimming, or ongoing entropy reduction against ai-first-go-template.
---

# Harness Template Sync

Use this Skill as a router for semantic repository work, never as a migration engine.

## Authority

- Reference template: `git@github.com:moss-site/ai-first-go-template.git`.
- Target instructions, artifacts, Git history, custom gates, and native checks own project facts.
- The selected template `BLUEPRINT.md` and `harness/scaffold_manifest.json` own the shared baseline.
- Inject and restore the repository constitution: thin prompts, thick artifacts and context, thin skills.

## Workflow

1. Classify `bootstrap`, `adopt`, `refresh`, or `govern`; route `govern` through `HARNESS-MAINTENANCE`.
2. Pin a clean template checkout; read both repositories before editing.
3. Compare with `git`, `rg`, and file diffs. Unknown target content is project-owned by default.
4. Relocate valid facts into canonical artifacts before slimming prompts, skills, scripts, or duplicate artifacts.
5. Preserve custom gates and native checks; edit only after ownership and live callers are understood.
6. Run target-native checks and proportional Harness verification. Report changes, preserved extensions, evidence, and blockers.

Stop on ambiguous ownership, conflicting authority, unrelated dirty changes, required approval, or failed gates.
