# Marketplace Namespace v2 Design

## Goal

Prevent Codex agents from mistaking the marketplace directory for the plugin directory by ensuring the two identifiers are never equal, while preserving each plugin's independent source repository and release lifecycle.

## Decision

Release both plugins as version `2.0.0` with unchanged plugin names and new marketplace names:

| Repository | Plugin | Marketplace |
| --- | --- | --- |
| `Fueav/harness-driven-development` | `harness-driven-development` | `fueav-harness-development` |
| `Fueav/harness-template-sync` | `harness-template-sync` | `fueav-harness-sync` |

The repositories remain independent. A shared umbrella marketplace is rejected because it would require a third source repository or duplicate one plugin's source of truth.

## Package Changes

Each repository will:

- bump `VERSION`, both plugin manifests, and the Claude marketplace entry to `2.0.0`;
- rename the Codex and Claude marketplace roots without renaming the plugin or its directory;
- document the new install selector `<plugin>@<marketplace>` and the explicit v1-to-v2 migration;
- make release validation reject a marketplace name equal to the plugin name;
- resolve each marketplace source path to the real plugin directory and verify the declared Skill entrypoint exists.

No `SKILL.md` behavior changes are required.

## Migration

Marketplace identity cannot be upgraded in place. Existing installations must remove the v1 plugin selector and marketplace, add the same GitHub repository again, and install the plugin under the new v2 marketplace selector. Release notes and README files will contain exact Codex and Claude Code commands.

## Verification

Before release, each repository must pass:

1. a red-green regression proving the old same-name marketplace fails the strengthened validator;
2. `python3 scripts/verify_release.py`;
3. the Codex plugin validator;
4. the Skill validator;
5. Claude strict plugin and marketplace validation.

After both GitHub releases are published, the local Codex installation must be migrated and checked with `codex plugin list`. The installed cache paths must have distinct marketplace and plugin segments and contain the expected `SKILL.md` files at version `2.0.0`.

## Release Shape

- `harness-driven-development--v2.0.0` for `Fueav/harness-driven-development`.
- `v2.0.0` for `Fueav/harness-template-sync`, preserving its existing tag convention.
- GitHub releases include the breaking install-coordinate migration and validation evidence.

## Rollback

The v1 tags remain immutable. A user can remove the v2 marketplace and reinstall the corresponding v1 tag explicitly. Source rollback is a normal Git revert followed by a new release; published tags are never moved.
