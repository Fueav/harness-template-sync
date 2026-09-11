---
name: harness-template-sync
description: Bootstrap or explicitly upgrade a repository from canonical ai-first-go-template.
---

# Template Delivery

Start at the clean canonical Scaffold Source root. Run `harness/template_delivery.py preflight --intent bootstrap|upgrade --target ABSOLUTE_PATH` to inspect a clean target and its delivery differences.

Adapt the affected shared files while preserving target-owned contracts, native checks and unknown content. Apply existing authorization only to its stated scope. When retiring a wrapper, keep target-owned checks reachable from their native gates. Resolve material ownership conflicts before changing those paths.

Run `harness/template_delivery.py finish` with --intent, --target, --compare-ref and any --resolution path=decision (see --help) to record, verify and complete delivery. Report the resulting revision and relevant evidence. A failed check blocks completion while authorized repair continues. Delivery does not imply deployment or permission to install software.
