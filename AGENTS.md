# PROJECT CONTRACT

This repository independently publishes the `harness-template-sync` plugin for Codex and Claude Code.

- Read `docs/CONTRACT.md` before changing behavior or package shape.
- Keep prompt and Skill entrypoints thin; put unique facts and rationale in repository artifacts.
- Do not add a migration CLI, bundled playbook, target inventory, or project-specific exception to the Skill.
- Keep `VERSION`, both plugin manifests, and both marketplace entries aligned.
- Run `python3 scripts/verify_release.py` and client validators before release.
- Use Conventional Commits and preserve unrelated changes.
