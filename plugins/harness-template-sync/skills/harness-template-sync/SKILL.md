---
name: harness-template-sync
description: Bootstrap or explicitly upgrade one repository from canonical ai-first-go-template.
---

# Harness Template Sync

Perform one Template Delivery, prove the handoff, then exit. Never use this Skill for normal target work or target Harness maintenance.

## Workflow

1. Require the exact clean canonical Scaffold Source Git root and one clean Target Repository by absolute path.
2. Choose `bootstrap` only when the target lacks `harness/scaffold.lock`; otherwise choose explicit `upgrade`. Run `harness/template_delivery.py preflight` before edits.
3. Use the audit and applicable instructions to find affected contracts, native checks, and callers. Unknown content stays target-owned; preserve independently visible gates during semantic merging.
4. Run `harness/template_delivery.py record` with explicit resolutions. Commit the target; run native checks and proportional verification. Repair change-caused failures within authorization, then re-record changed resolutions and verify the corrected candidate.
5. Run `harness/template_delivery.py complete`; report exact revisions, preserved extensions, evidence, and blockers, then exit.

Never invoke or install Harness Driven Development. It independently owns later target work after readiness.

Wrong source or unrelated dirt stops entry. Missing authority or unresolved ownership/contract conflicts block affected changes; failed gates block completion.
