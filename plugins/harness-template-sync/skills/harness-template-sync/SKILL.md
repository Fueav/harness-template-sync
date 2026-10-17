---
name: harness-template-sync
description: Bootstrap or explicitly migrate a repository from canonical ai-first-go-template to native project execution.
---

# Project Migration

Work only from the clean canonical source root. Read its suite contract. For a new target, use `harness/template_delivery.py init` with the requested target, module, service and owner. For an existing Git root, run `harness/template_delivery.py inspect --target ABSOLUTE_PATH`; preserve unrelated dirty work and isolate conflicting changes when useful.

Preserve product contracts, target-owned checks, boundaries and unknown content. Resolve material ownership conflicts before changing affected paths. Retire copied runtime paths only after their product checks remain reachable through native commands. Keep instructions concise and project-specific; deliver no engine, workbench, descriptor, lock or compatibility entry.

Run `harness/template_delivery.py verify --target ABSOLUTE_PATH` on clean candidates; it checks migration structure only. Run the target's native verification and independent acceptance when defined. Report revisions, actual outcomes and remaining gaps separately; failures block completion while authorized repair continues. Migration grants no deployment or unrelated installation authority. Daily work uses the target's own commands.
