# Marketplace Namespace v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish version `2.0.0` of both Harness plugins with marketplace identifiers that differ from their plugin identifiers and with regression coverage for that invariant.

**Architecture:** Keep the two repositories and plugin packages independent. Each release validator owns its marketplace constant, verifies that the marketplace and plugin names differ, confirms the marketplace source resolves to the real plugin directory, and validates the Skill entrypoint. README and release notes own the breaking installation migration.

**Tech Stack:** Python 3 standard library, JSON plugin manifests, Codex CLI, Claude Code CLI, Git, GitHub CLI.

## Global Constraints

- Plugin names remain `harness-driven-development` and `harness-template-sync`.
- Marketplace names become `fueav-harness-development` and `fueav-harness-sync` respectively.
- Both releases use version `2.0.0` because the installation selector changes.
- Skill behavior and `SKILL.md` contents do not change.
- Existing v1 tags remain immutable.

---

### Task 1: Add marketplace-identity regression tests

**Files:**
- Create: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/scripts/test_verify_release.py`
- Create: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/scripts/test_verify_release.py`

**Interfaces:**
- Consumes: each repository's `scripts/verify_release.py` command-line exit contract.
- Produces: a `unittest` regression that requires same-name marketplace metadata to fail validation.

- [ ] Copy each source checkout into a temporary directory, set both marketplace root names equal to the plugin name, and execute the copied validator.
- [ ] Run `python3 scripts/test_verify_release.py` in each repository and confirm the new test fails because the current validator accepts the same-name marketplace.
- [ ] Commit no production changes until both failures are observed.

### Task 2: Implement Harness Driven Development v2 packaging

**Files:**
- Create: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/README.md`
- Modify: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/VERSION`
- Modify: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/.agents/plugins/marketplace.json`
- Modify: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/.claude-plugin/marketplace.json`
- Modify: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/plugins/harness-driven-development/.codex-plugin/plugin.json`
- Modify: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/plugins/harness-driven-development/.claude-plugin/plugin.json`
- Modify: `/Users/chris/.codex-worktrees/harness-driven-development-marketplace-v2/scripts/verify_release.py`

**Interfaces:**
- Consumes: repository root manifests and the local source path `./plugins/harness-driven-development`.
- Produces: plugin selector `harness-driven-development@fueav-harness-development` at version `2.0.0`.

- [ ] Add `MARKETPLACE_NAME = "fueav-harness-development"` and enforce both marketplace names, marketplace/plugin inequality, resolved source directory, and `skills/harness-driven-development/SKILL.md` existence.
- [ ] Update version and marketplace metadata to `2.0.0` and `fueav-harness-development`.
- [ ] Document fresh install, explicit v1 removal/re-add migration, upgrade, verification, and rollback commands.
- [ ] Run the regression test and `python3 scripts/verify_release.py`; expect both to pass.
- [ ] Validate plugin and Skill metadata with the client validators.
- [ ] Commit as `fix: separate marketplace and plugin identities`.

### Task 3: Implement Harness Template Sync v2 packaging

**Files:**
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/README.md`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/VERSION`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/docs/CONTRACT.md`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/.agents/plugins/marketplace.json`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/.claude-plugin/marketplace.json`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/plugins/harness-template-sync/.codex-plugin/plugin.json`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/plugins/harness-template-sync/.claude-plugin/plugin.json`
- Modify: `/Users/chris/.codex-worktrees/harness-template-sync-marketplace-v2/scripts/verify_release.py`

**Interfaces:**
- Consumes: repository root manifests and the local source path `./plugins/harness-template-sync`.
- Produces: plugin selector `harness-template-sync@fueav-harness-sync` at version `2.0.0`.

- [ ] Add `MARKETPLACE_NAME = "fueav-harness-sync"` and enforce both marketplace names, marketplace/plugin inequality, resolved source directory, and `skills/harness-template-sync/SKILL.md` existence.
- [ ] Update version, contract status, marketplace metadata, install commands, and migration commands.
- [ ] Run the regression test and `python3 scripts/verify_release.py`; expect both to pass.
- [ ] Validate plugin and Skill metadata with the client validators.
- [ ] Commit as `fix: separate marketplace and plugin identities`.

### Task 4: Publish and smoke-test both releases

**Files:**
- No additional source files.

**Interfaces:**
- Consumes: validated release commits on both feature branches.
- Produces: merged default branches, immutable Git tags, GitHub releases, and migrated local plugin installations.

- [ ] Push both branches, open ready PRs, and merge after required checks pass.
- [ ] Tag the merged commits as `harness-driven-development--v2.0.0` and `v2.0.0` respectively; push tags and create GitHub releases with exact migration instructions.
- [ ] Remove the old local Codex plugin selectors and marketplaces, add each repository again, and install the plugins under the new marketplace selectors.
- [ ] Run `codex plugin list`, verify both entries are enabled at `2.0.0`, and assert the installed `SKILL.md` paths use distinct marketplace/plugin path segments.
- [ ] Run both installed `SKILL.md` validators and record any Claude Code migration limitation as residual risk rather than mutating credentials or unrelated configuration.
