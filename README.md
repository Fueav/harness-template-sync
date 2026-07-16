# Harness Template Sync

`harness-template-sync` is an independent Codex and Claude Code plugin for semantic Harness migration and lifecycle governance. It compares a versioned `ai-first-go-template` checkout with a real target repository, preserves project-owned facts and extensions, and routes the Agent through bootstrap, adoption, refresh, or entropy-reduction work.

The plugin is intentionally thin: its Skill contains no migration program, file inventory, state lock, or project-specific exceptions. The full authority and safety contract lives in [`docs/CONTRACT.md`](docs/CONTRACT.md).

## Install in Codex

```bash
codex plugin marketplace add Fueav/harness-template-sync
codex plugin add harness-template-sync@fueav-harness-sync
```

The default install intentionally omits `--ref`, so marketplace upgrades follow the repository's default branch. Use a release tag only for an intentionally immutable installation; a tagged marketplace remains pinned until it is rebound.

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-template-sync --scope user
claude plugin install harness-template-sync@fueav-harness-sync --scope user
```

## Migrate from v1

Version 2 separates the marketplace identity from the plugin identity. The marketplace cannot be renamed in place, so remove the v1 selector and add the repository again.

For Codex:

```bash
codex plugin remove harness-template-sync@harness-template-sync
codex plugin marketplace remove harness-template-sync
codex plugin marketplace add Fueav/harness-template-sync
codex plugin add harness-template-sync@fueav-harness-sync
```

For Claude Code:

```bash
claude plugin uninstall harness-template-sync@harness-template-sync --scope user
claude plugin marketplace remove harness-template-sync --scope user
claude plugin marketplace add Fueav/harness-template-sync --scope user
claude plugin install harness-template-sync@fueav-harness-sync --scope user
```

Restart the client or open a new session after migration.

## Upgrade

```bash
codex plugin marketplace upgrade fueav-harness-sync
codex plugin add harness-template-sync@fueav-harness-sync
claude plugin marketplace update fueav-harness-sync
claude plugin update harness-template-sync@fueav-harness-sync
```

## Verify a source checkout

```bash
python3 scripts/test_verify_release.py
python3 scripts/verify_release.py
CODEX_PYTHON="${CODEX_PYTHON:-python3}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/harness-template-sync
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" plugins/harness-template-sync/skills/harness-template-sync
claude plugin validate plugins/harness-template-sync --strict
claude plugin validate . --strict
```

`CODEX_PYTHON` must point to a Python environment with PyYAML for the Codex plugin validator.

This repository is packaged and released independently from `harness-driven-development`. The two plugins do not call or install each other: this plugin prepares and maintains the repository-level Harness contract that `harness-driven-development` later consumes during ordinary product work. `harnessctl` remains execution-layer infrastructure inside migrated Harness projects; it is not the migration controller.

## Roll back to v1

For Codex, replace the v2 installation with the immutable v1.0.2 release:

```bash
codex plugin remove harness-template-sync@fueav-harness-sync
codex plugin marketplace remove fueav-harness-sync
codex plugin marketplace add Fueav/harness-template-sync --ref v1.0.2
codex plugin add harness-template-sync@harness-template-sync
```

For Claude Code:

```bash
claude plugin uninstall harness-template-sync@fueav-harness-sync --scope user
claude plugin marketplace remove fueav-harness-sync --scope user
claude plugin marketplace add Fueav/harness-template-sync@v1.0.2 --scope user
claude plugin install harness-template-sync@harness-template-sync --scope user
```

Published tags are never moved.
