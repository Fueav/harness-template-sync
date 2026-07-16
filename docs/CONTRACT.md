# Harness Template Sync Contract

Status: v1.0.1 release contract

## Decision

Harness Template Sync is an independent Agent lifecycle plugin, not a generic migration program. The Agent reads a pinned `ai-first-go-template` checkout and the real target repository, reasons about project semantics, edits the target, and proves the result with target-native gates.

It is a packaging and release peer of `harness-driven-development`, but the two have a directional repository-contract handoff. They do not contain, install, or call each other. This plugin produces and maintains the Harness-enabled repository contract that `harness-driven-development` can later consume during ordinary product work. `harnessctl` is part of the Harness execution architecture that a target may receive; it does not inspect, plan, apply, or roll back migrations.

## Integration boundary

`ai-first-go-template` owns the shared Harness baseline. Harness Template Sync consumes that baseline plus target-owned context and turns the target into, or keeps it as, a valid Harness-enabled repository. The resulting repository owns its instructions, workflow declarations, specifications, profiles, gates, and project extensions. Harness Driven Development may then route product work through those declarations without knowing how they arrived.

This is contract compatibility, not package dependency or lockstep versioning:

- Harness Template Sync currently understands `harness/scaffold_manifest.json` schema version 1.
- A template content release does not require a Sync release unless the manifest schema, migration semantics, or safety contract changes.
- A Harness Driven Development release does not require a Sync release unless the repository contract it consumes changes.
- `govern` follows the target repository's declared `HARNESS-MAINTENANCE` workflow directly; it does not invoke the Harness Driven Development Skill.
- If one request combines Harness migration with product behavior work, complete and verify the migration phase first, then route the product phase through Harness Driven Development.

## Architecture constitution

- Thin prompts select workflows and point to authority.
- Thick artifacts and context own unique project facts, decisions, contracts, and evidence.
- Thin skills route the Agent through those facts and define stop conditions.
- Mechanical facts stay in manifests, scripts, or tests; semantic ownership remains with the Agent and repository context.
- Prompt and Skill maintenance is net-zero or net-negative. Valid facts are relocated before duplicate routing text is removed.

Migration injects this constitution into both blank and established projects. Governance restores it when normal development introduces drift, duplicate authority, or vendored execution logic.

## Sources of truth

| Authority | Owns | Does not own |
| --- | --- | --- |
| Target repository | Product contracts, custom gates, native checks, local extensions, Git history | Shared template baseline |
| Template `BLUEPRINT.md` | Human-readable Harness architecture and completion contract | Target-specific policy |
| Template `harness/scaffold_manifest.json` | Managed paths, retired paths, merge strategies | Semantic deletion decisions |
| This Skill | Trigger, authority pointers, compact workflow, stop conditions | Migration code, template inventory, project exceptions |
| Agent | Comparison, reference tracing, semantic merge, scoped edits, evidence synthesis | Inventing undocumented project policy |
| `harnessctl` | Pinned execution and post-migration Harness gates | Migration orchestration |

Unknown target content is project-owned by default. A path used by a custom gate or live caller stays project-owned until that caller is deliberately migrated. A historical byte match can show origin but is never sufficient authority to delete.

## Lifecycle modes

### Bootstrap

For a blank repository, install only the minimum baseline: a thin root prompt, Blueprint/context map, boundaries, Harness configuration, pinned execution wrappers, and required symlinks. Do not create speculative product artifacts, placeholder specifications, or placeholder Skills.

### Adopt

For a mature repository without Harness, audit its instructions, CI, docs, scripts, tests, hooks, and conventions before injection. Extract durable facts from long prompts into canonical project artifacts, then leave thin pointers. Preserve native checks rather than duplicating them.

### Refresh

For an existing Harness repository, treat the target as a divergent overlay. Preserve custom gates, native checks, project artifacts, and workflow contracts. Remove superseded wrappers or duplicated execution code only after ownership and the post-change call graph are understood.

### Govern

Route ongoing entropy reduction through the target's `HARNESS-MAINTENANCE` workflow. Compare the current Harness surface with the pinned template and the target's Harness-related Git history. Relocate unique facts before deleting duplicated prompts, Skills, scripts, stale pointers, or orphaned artifacts. Finish with no weakened gate and a net-zero or net-negative prompt-and-Skill delta.

Governance is event-driven: use it after material template updates, when size budgets drift, when duplicate authority appears, or before a release whose Harness growth cannot be justified.

## Trigger ownership

| Request | Owning Skill |
| --- | --- |
| Bootstrap Harness into a blank repository | Harness Template Sync |
| Adopt Harness in a mature non-Harness repository | Harness Template Sync |
| Refresh or slim Harness prompts, Skills, wrappers, or gates | Harness Template Sync |
| Reduce accumulated Harness entropy | Harness Template Sync |
| Implement or change product behavior inside a Harness repository | Harness Driven Development |
| Handle incidents, refactors, releases, or deployments under declared workflows | Harness Driven Development |

## Semantic migration flow

1. Select and pin the exact template commit or release; reject an unintentionally dirty source.
2. Read the nearest target instructions and inspect its Git state, Harness assets, custom gates, CI, hooks, Make targets, docs, and native checks.
3. Compare all manifest-managed and retired paths. Treat unlisted target paths as project-owned.
4. Trace live references with `rg` and inspect Git history as evidence. Evaluate the call graph after proposed wrapper changes.
5. Classify each candidate as exact baseline, semantic merge, preserve, relocate, retire, or blocked.
6. Edit the target directly. Copy exact baseline files only where ownership is clear; semantically merge policy and overlays.
7. Re-run comparison, native tests, configuration contracts, and proportional Harness release gates.
8. Report the template commit, additions, updates, deletions, preserved extensions, evidence, and unresolved blockers.

Git and the target worktree provide review and rollback. The plugin does not introduce `plan`, `apply`, transaction, state-lock, or automatic reference-closure machinery.

## Principle injection

The constitution is injected through existing authority layers:

1. The root prompt states the three principles once and points to `BLUEPRINT.md`.
2. `BLUEPRINT.md` defines what each layer may contain and where project facts live.
3. `harness/scaffold_manifest.json` makes the prompt, Blueprint, and relevant Skill entrypoints visible to comparison without duplicating prose.
4. Existing Harness size and no-net-growth checks enforce the mechanical budget. Equivalent project-native checks remain authoritative.

The slogan stays in the prompt; its explanation stays in the artifact. No new policy file is created in a target solely for this constitution.

## Safety and stop conditions

- Preserve unknown content and project extensions.
- Relocate valid facts before slimming their old container.
- Never name a specific product repository as a shared exception.
- Stop on ambiguous ownership, conflicting authority, unrelated dirty changes, required human approval, or failed/unavailable mandatory gates.
- Do not weaken target checks to make a migration pass.
- Do not change protected business semantics under the label of Harness maintenance.

## Distributed package

The release has its own repository, semver, tag, GitHub release, Codex marketplace, and Claude Code marketplace. `VERSION`, both plugin manifests, and both marketplace entries must match. Its version is independent from template and Harness Driven Development versions.

The distributed Skill contains exactly:

- `SKILL.md`, at most 30 lines and 200 words.
- `agents/openai.yaml`.

It ships no executable migration scripts, playbook, fixtures, target inventory, state file, or CLI documentation. Release validation mechanically enforces this shape and client metadata.

## Non-goals

- One-command migration of arbitrary repositories.
- Automatic semantic merges or deletion based only on names or hashes.
- Encoding named-project exceptions in shared tooling.
- Turning `harnessctl` into a migration controller.
- Scheduling automatic deletion of project content.
- Owning the `harness-driven-development` workflow.
