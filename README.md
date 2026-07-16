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
claude plugin marketplace add Fueav/harness-template-sync
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
claude plugin marketplace remove harness-template-sync
claude plugin marketplace add Fueav/harness-template-sync
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
```

This repository is packaged and released independently from `harness-driven-development`. The two plugins do not call or install each other: this plugin prepares and maintains the repository-level Harness contract that `harness-driven-development` later consumes during ordinary product work. `harnessctl` remains execution-layer infrastructure inside migrated Harness projects; it is not the migration controller.

## Roll back to v1

For Codex, replace the v2 installation with the immutable v1.0.2 release:

```bash
codex plugin remove harness-template-sync@fueav-harness-sync
codex plugin marketplace remove fueav-harness-sync
codex plugin marketplace add Fueav/harness-template-sync --ref v1.0.2
codex plugin add harness-template-sync@harness-template-sync
```

Claude Code can use the same remove-and-reinstall sequence with the `v1.0.2` marketplace source. Published tags are never moved.
