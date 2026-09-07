# Delivery request and audit context

Upgrade this already-delivered target to the current canonical Repository Contract. The owner has approved replacing inherited Harness workflow policy, including the old rule that every deployment requires a Specification. Project-owned production checks must survive.

The preflight history comparison attributes `scripts/run_checker_self_tests.sh` and the every-deployment Specification rule to the retired scaffold, with no project changes. The target added `scripts/production_release_gate.sh` and appended its call to `harness/gates/release_self_tests.sh`. The supplied profile and AGENTS.md are the only wrapper callers in this bounded fixture. The current scaffold removes the old checker implementation; it retains independent project gates through its custom-gate interface.

These are supplied audit facts for a routing simulation. Do not claim that Git history, checks, or a delivery command actually ran during the simulation.
