# Harness Template Sync

`harness-template-sync` is an independent Codex and Claude Code plugin for semantic Harness migration and lifecycle governance. It compares a versioned `ai-first-go-template` checkout with a real target repository, preserves project-owned facts and extensions, and routes the Agent through bootstrap, adoption, refresh, or entropy-reduction work.

The plugin is intentionally thin: its Skill contains no migration program, file inventory, state lock, or project-specific exceptions. The full authority and safety contract lives in [`docs/CONTRACT.md`](docs/CONTRACT.md).

## Install in Codex

```bash
codex plugin marketplace add Fueav/harness-template-sync --ref v1.0.1
codex plugin add harness-template-sync@harness-template-sync
```

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-template-sync
claude plugin install harness-template-sync@harness-template-sync --scope user
```

## Verify a source checkout

```bash
python3 scripts/verify_release.py
```

This repository is packaged and released independently from `harness-driven-development`. The two plugins do not call or install each other: this plugin prepares and maintains the repository-level Harness contract that `harness-driven-development` later consumes during ordinary product work. `harnessctl` remains execution-layer infrastructure inside migrated Harness projects; it is not the migration controller.
