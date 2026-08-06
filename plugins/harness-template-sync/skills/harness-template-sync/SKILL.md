---
name: harness-template-sync
description: Use only from the exact canonical ai-first-go-template root to cold-start or explicitly upgrade one target repository.
---

# Harness Template Sync

Perform one Template Delivery, prove the handoff, then exit. Never use this Skill for normal target work or target Harness maintenance.

## Workflow

1. Require the current directory to be the exact clean canonical Scaffold Source Git root. Require one clean Target Repository by absolute path.
2. Choose `bootstrap` only when the target lacks `harness/scaffold.lock`; otherwise choose explicit `upgrade`. Run `harness/template_delivery.py preflight` before edits.
3. Read both repositories and the target's instructions, native checks, gates, CI, hooks, and relevant history. Unknown content stays target-owned.
4. Use the audit from preflight. Trace callers with `rg`; semantically merge managed paths without weakening independently visible gates.
5. Run `harness/template_delivery.py record` with explicit path resolutions. Commit the target, then run its native checks and proportional Harness verification.
6. Run `harness/template_delivery.py complete`; report exact revisions, preserved extensions, evidence, and blockers, then exit.

Never invoke or install Harness Driven Development. It independently owns later target work after readiness.

Stop on a wrong source root, dirty repository, ambiguous ownership, conflicting authority, required approval, protected semantics, or a failed gate.
