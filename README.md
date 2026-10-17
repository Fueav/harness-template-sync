# Harness Template Sync

`harness-template-sync` performs one cold start or explicit upgrade from the exact canonical `ai-first-go-template` root to a named target, checks migration structure, runs the target's native checks, and exits. It is not used for daily target work or target Harness maintenance.

The package is a thin semantic router. The Scaffold Source owns `template_delivery.py`, and suite contract v4; the target owns its product facts, extensions, and native checks. See [`docs/CONTRACT.md`](docs/CONTRACT.md).

This checkout is an unpublished **5.0.0 candidate**. The installation commands below describe distribution coordinates; they do not publish or install this checkout.

## Install in Codex

Scaffold maintainers install the delivery plugin from the umbrella marketplace:

```bash
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-template-sync@fueav-harness
```

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-template-sync@fueav-harness --scope user
```

Restart the client or open a new session after installation.

## Use

Open the exact canonical Scaffold Source root, then use one natural-language request with an absolute target path:

```text
Use $harness-template-sync to upgrade /absolute/path/to/target and stop after delivery.
```

The source owns `harness/template_delivery.py init`, `inspect --target ABSOLUTE_PATH` and `verify --target ABSOLUTE_PATH`. Targets keep `AGENTS.md`, `Makefile`, `.ai-boundaries.yml` and their native product checks. Retired runtime paths leave entirely. Source verification requires clean candidates and checks migration structure only; execute native verification and independent acceptance separately. Daily work uses target commands directly.

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
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/harness-template-sync/skills/harness-template-sync
claude plugin validate plugins/harness-template-sync --strict
claude plugin validate . --strict
```

Checked-in forward results are bound to the current Skill package digest. The model cases execute bounded migrations; parent checks inspect resulting files and rerun native checks. These establish migration behavior, not real-product acceptance.

