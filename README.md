# Harness Template Sync

`harness-template-sync` is an independent Codex and Claude Code plugin for semantic Harness migration and lifecycle governance. It compares a versioned `ai-first-go-template` checkout with a real target repository, preserves project-owned facts and extensions, and routes the Agent through bootstrap, adoption, refresh, or entropy-reduction work.

The plugin is intentionally thin: its Skill contains no migration program, file inventory, state lock, or project-specific exceptions. The full authority and safety contract lives in [`docs/CONTRACT.md`](docs/CONTRACT.md).

## Install in Codex

```bash
codex plugin marketplace add Fueav/harness-template-sync
codex plugin add harness-template-sync@harness-template-sync
```

The default install intentionally omits `--ref`, so marketplace upgrades follow the repository's default branch. Use a release tag only for an intentionally immutable installation; a tagged marketplace remains pinned until it is rebound.

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-template-sync
claude plugin install harness-template-sync@harness-template-sync --scope user
```

## Upgrade

For an unpinned Codex marketplace:

```bash
codex plugin marketplace upgrade harness-template-sync
codex plugin add harness-template-sync@harness-template-sync
```

If Codex was originally installed with `--ref`, rebind the marketplace once, then future upgrades can use the commands above:

```bash
codex plugin marketplace remove harness-template-sync
codex plugin marketplace add Fueav/harness-template-sync
codex plugin add harness-template-sync@harness-template-sync
```

For Claude Code:

```bash
claude plugin marketplace update harness-template-sync
claude plugin update harness-template-sync@harness-template-sync
```

Restart the client or open a new session after upgrading.

## Verify a source checkout

```bash
python3 scripts/verify_release.py
```

This repository is packaged and released independently from `harness-driven-development`. The two plugins do not call or install each other: this plugin prepares and maintains the repository-level Harness contract that `harness-driven-development` later consumes during ordinary product work. `harnessctl` remains execution-layer infrastructure inside migrated Harness projects; it is not the migration controller.
