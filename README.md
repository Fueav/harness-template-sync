# Harness Template Sync

`harness-template-sync` performs one cold start or explicit upgrade from the exact canonical `ai-first-go-template` root to a named target, proves readiness, and exits. It is not used for daily target work or target Harness maintenance.

The package is a thin semantic router. The Scaffold Source owns `template_delivery.py`, the suite contract, and deterministic `harnessctl` adapters; the target owns its product facts, extensions, and native checks. See [`docs/CONTRACT.md`](docs/CONTRACT.md).

## Install in Codex

Scaffold maintainers install both independent plugins from the umbrella marketplace:

```bash
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-template-sync@fueav-harness
codex plugin add harness-driven-development@fueav-harness
```

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-template-sync@fueav-harness --scope user
claude plugin install harness-driven-development@fueav-harness --scope user
```

Restart the client or open a new session after installation.

## Use

Open the exact canonical Scaffold Source root, then use one natural-language request with an absolute target path:

```text
Use $harness-template-sync to upgrade /absolute/path/to/target and stop after delivery.
```

Use “cold-start” instead of “upgrade” when the target has no `harness/scaffold.lock`. The Skill refuses forks, sibling checkouts, subdirectories, dirty repositories, relative targets, and intent/record mismatches. After completion, work in the target with Harness Driven Development only.

## Upgrade

```bash
codex plugin marketplace upgrade fueav-harness
codex plugin add harness-template-sync@fueav-harness
claude plugin marketplace update fueav-harness
claude plugin update harness-template-sync@fueav-harness
```

## Migrate from the v2 per-repository marketplace

Codex:

```bash
codex plugin remove harness-template-sync@fueav-harness-sync
codex plugin marketplace remove harness-template-sync
codex plugin marketplace remove fueav-harness-sync
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-template-sync@fueav-harness
```

Claude Code:

```bash
claude plugin uninstall harness-template-sync@fueav-harness-sync --scope user
claude plugin marketplace remove harness-template-sync --scope user
claude plugin marketplace remove fueav-harness-sync --scope user
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-template-sync@fueav-harness --scope user
```

The per-repository `fueav-harness-sync` marketplace remains an independently published distribution coordinate, but the umbrella path is the supported default onboarding.

## Verify a source checkout

```bash
python3 scripts/test_verify_release.py
python3 scripts/verify_release.py
python3 scripts/test_verify_evals.py
python3 scripts/verify_evals.py --results evals/results.json
CODEX_PYTHON="${CODEX_PYTHON:-python3}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/harness-template-sync
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" plugins/harness-template-sync/skills/harness-template-sync
claude plugin validate plugins/harness-template-sync --strict
claude plugin validate . --strict
```

Checked-in forward results are bound to the current Skill package digest. Cross-component proof is owned by `make verify-suite` in the canonical Scaffold Source, not by this package.

## Roll back to v2

Use the immutable `v2.1.0` tag through the standalone repository marketplace if the v3 source-only delivery contract is not yet supported. Published tags are never moved.
