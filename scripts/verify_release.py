#!/usr/bin/env python3
"""Validate the independently releasable Harness Template Sync package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "harness-template-sync"
MARKETPLACE_NAME = "fueav-harness-sync"
PLUGIN = ROOT / "plugins" / NAME
SKILL = PLUGIN / "skills" / NAME


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON at {path.relative_to(ROOT)}: {exc}") from exc


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_declared_skill_path(
    manifest: dict,
    label: str,
    expected: str | list[str],
    errors: list[str],
) -> None:
    declared = manifest.get("skills")
    valid = declared == expected
    require(valid, f"{label} declared Skill path is invalid", errors)
    if not valid:
        return

    relative = declared if isinstance(declared, str) else declared[0]
    declared_root = PLUGIN / relative
    try:
        resolved_root = declared_root.resolve(strict=True)
        resolved_plugin = PLUGIN.resolve(strict=True)
    except OSError:
        errors.append(f"{label} declared Skill path is invalid")
        return

    skill_entry = resolved_root / NAME / "SKILL.md"
    require(
        resolved_root.is_relative_to(resolved_plugin)
        and skill_entry.is_file()
        and skill_entry.resolve().is_relative_to(resolved_plugin),
        f"{label} declared Skill path is invalid",
        errors,
    )


def validate_marketplace_source(source: object, label: str, errors: list[str]) -> None:
    expected = f"./plugins/{NAME}"
    require(source == expected, f"{label} marketplace source is wrong", errors)
    if source != expected:
        return

    source_path = ROOT / expected
    try:
        resolved_root = ROOT.resolve(strict=True)
        resolved_source = source_path.resolve(strict=True)
    except OSError:
        errors.append(f"{label} marketplace source is missing")
        return

    require(
        not source_path.is_symlink()
        and resolved_source.is_relative_to(resolved_root)
        and resolved_source.is_dir(),
        f"{label} marketplace source must stay within repository",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    version_path = ROOT / "VERSION"
    version = version_path.read_text().strip() if version_path.exists() else ""
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "VERSION must be strict semver", errors)

    readme_path = ROOT / "README.md"
    readme_text = readme_path.read_text() if readme_path.exists() else ""
    codex_heading = "## Install in Codex"
    if codex_heading in readme_text:
        codex_install = readme_text.split(codex_heading, 1)[1].split("\n## ", 1)[0]
        codex_add_commands = [
            line.strip()
            for line in codex_install.splitlines()
            if line.strip().startswith("codex plugin marketplace add ")
        ]
        require(
            codex_add_commands == [f"codex plugin marketplace add Fueav/{NAME}"],
            "Codex default install must use one unpinned marketplace command",
            errors,
        )
    else:
        errors.append("README must document Codex installation")
    for command in (
        f"codex plugin marketplace add Fueav/{NAME}",
        f"codex plugin marketplace upgrade {MARKETPLACE_NAME}",
        f"codex plugin marketplace remove {NAME}",
        f"codex plugin add {NAME}@{MARKETPLACE_NAME}",
        f"claude plugin marketplace remove {NAME} --scope user",
        f"claude plugin marketplace add Fueav/{NAME} --scope user",
        f"claude plugin update {NAME}@{MARKETPLACE_NAME}",
    ):
        require(command in readme_text, f"README must document: {command}", errors)

    json_paths = [
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
        ROOT / ".agents" / "plugins" / "marketplace.json",
        ROOT / ".claude-plugin" / "marketplace.json",
    ]
    documents: dict[Path, dict] = {}
    for path in json_paths:
        try:
            documents[path] = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))

    codex = documents.get(json_paths[0], {})
    claude = documents.get(json_paths[1], {})
    codex_market = documents.get(json_paths[2], {})
    claude_market = documents.get(json_paths[3], {})

    for label, manifest in (("Codex", codex), ("Claude", claude)):
        require(manifest.get("name") == NAME, f"{label} plugin name must be {NAME}", errors)
        require(manifest.get("version") == version, f"{label} plugin version must match VERSION", errors)
        require(manifest.get("repository") == f"https://github.com/Fueav/{NAME}", f"{label} repository is wrong", errors)
    validate_declared_skill_path(codex, "Codex plugin", "./skills/", errors)
    validate_declared_skill_path(claude, "Claude plugin", ["./skills/"], errors)

    codex_plugins = codex_market.get("plugins", [])
    codex_marketplace_name = codex_market.get("name")
    claude_marketplace_name = claude_market.get("name")
    require(codex_marketplace_name == MARKETPLACE_NAME, "Codex marketplace name is wrong", errors)
    require(claude_marketplace_name == MARKETPLACE_NAME, "Claude marketplace name is wrong", errors)
    require(
        codex_marketplace_name != NAME and claude_marketplace_name != NAME,
        "marketplace name must differ from plugin name",
        errors,
    )
    require(len(codex_plugins) == 1, "Codex marketplace must publish exactly one plugin", errors)
    if len(codex_plugins) == 1:
        require(codex_plugins[0].get("name") == NAME, "Codex marketplace plugin name is wrong", errors)
        codex_source = codex_plugins[0].get("source", {}).get("path")
        validate_marketplace_source(codex_source, "Codex", errors)

    claude_plugins = claude_market.get("plugins", [])
    require(len(claude_plugins) == 1, "Claude marketplace must publish exactly one plugin", errors)
    if len(claude_plugins) == 1:
        require(claude_plugins[0].get("name") == NAME, "Claude marketplace plugin name is wrong", errors)
        claude_source = claude_plugins[0].get("source")
        validate_marketplace_source(claude_source, "Claude", errors)
        require(claude_plugins[0].get("version") == version, "Claude marketplace version must match VERSION", errors)

    files = {
        path.relative_to(SKILL).as_posix()
        for path in SKILL.rglob("*")
        if path.is_file()
    } if SKILL.exists() else set()
    require(files == {"SKILL.md", "agents/openai.yaml"}, f"Skill package has unexpected files: {sorted(files)}", errors)

    skill_path = SKILL / "SKILL.md"
    skill_text = skill_path.read_text() if skill_path.exists() else ""
    require(len(skill_text.splitlines()) <= 30, "SKILL.md must be at most 30 lines", errors)
    require(len(skill_text.split()) <= 200, "SKILL.md must be at most 200 words", errors)
    for token in ("bootstrap", "adopt", "refresh", "govern", "HARNESS-MAINTENANCE"):
        require(token in skill_text, f"SKILL.md must include {token}", errors)
    for principle in ("thin prompts", "thick artifacts", "thin skills"):
        require(principle in skill_text.lower(), f"SKILL.md must include {principle}", errors)

    openai_path = SKILL / "agents" / "openai.yaml"
    openai_text = openai_path.read_text() if openai_path.exists() else ""
    require("$harness-template-sync" in openai_text, "OpenAI default prompt must invoke the Skill", errors)
    require("bootstrap, adopt, refresh, or govern" in openai_text, "OpenAI default prompt must expose all modes", errors)

    require((ROOT / "docs" / "CONTRACT.md").is_file(), "missing docs/CONTRACT.md authority", errors)
    require(not any(SKILL.glob("scripts/**/*")), "Skill must not bundle scripts", errors)
    require(not any(SKILL.glob("references/**/*")), "Skill must not bundle a playbook", errors)
    plugin_dirs = {
        path.name
        for path in (ROOT / "plugins").iterdir()
        if path.is_dir()
    } if (ROOT / "plugins").exists() else set()
    require(plugin_dirs == {NAME}, f"repository must publish only the independent {NAME} plugin", errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"release contract ok: {NAME} {version}")
    print(f"skill package ok: {len(skill_text.splitlines())} lines, {len(skill_text.split())} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
