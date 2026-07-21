#!/usr/bin/env python3
"""Verify the Template to Sync to router contract composition."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(
    command: list[str], cwd: Path, env: dict[str, str] | None = None
) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def require_success(step: dict[str, object], label: str) -> None:
    if step["returncode"] != 0:
        raise RuntimeError(
            f"{label} failed\nstdout:\n{step['stdout']}\nstderr:\n{step['stderr']}"
        )


def git_revision(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--harnessctl-bin", type=Path, required=True)
    parser.add_argument("--hdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/cross-component.json")
    args = parser.parse_args()
    template = args.template.resolve()
    harnessctl = args.harnessctl_bin.resolve()
    hdf = args.hdf.resolve()
    summary: dict[str, object] = {
        "schema_version": 1,
        "components": {
            "template": git_revision(template),
            "template_sync": git_revision(ROOT),
            "harness_driven_development": git_revision(hdf),
        },
        "steps": {},
        "status": "failed",
    }
    try:
        compatibility = json.loads(
            (ROOT / "contracts/template-compatibility.json").read_text(encoding="utf-8")
        )["template_contracts"]
        scaffold_version = json.loads(
            (template / "harness/scaffold_manifest.json").read_text(encoding="utf-8")
        )["schema_version"]
        workflow_version = json.loads(
            (template / "docs/harness-workflows.json").read_text(encoding="utf-8")
        )["version"]
        if scaffold_version not in compatibility["scaffold_manifest"]:
            raise RuntimeError("Template scaffold manifest schema is unsupported")
        if workflow_version not in compatibility["workflow_registry"]:
            raise RuntimeError("Template workflow registry schema is unsupported")

        lock = json.loads((template / "harness/harness.lock").read_text(encoding="utf-8"))
        expected_version = lock["version"]
        version_step = run([str(harnessctl), "version"], ROOT)
        summary["steps"]["harnessctl_version"] = version_step
        require_success(version_step, "harnessctl version")
        if version_step["stdout"].strip() != f"harnessctl {expected_version}":
            raise RuntimeError("harnessctl binary does not match Template lock")

        registry_env = dict(os.environ)
        registry_env["HARNESSCTL_BIN"] = str(harnessctl)
        registry_env["VERIFY_COMPARE_REF"] = "origin/main"
        registry_step = run(
            [str(template / "scripts/check_spec_registry.sh")], template, registry_env
        )
        summary["steps"]["template_registry"] = registry_step
        require_success(registry_step, "Template registry")
        evidence = json.loads(
            (template / ".artifacts/change/spec_registry.json").read_text(encoding="utf-8")
        )
        expected_workflows = sorted(
            json.loads(
                (template / "docs/harness-workflows.json").read_text(encoding="utf-8")
            )["workflow_classes"]
        )
        if evidence.get("workflow_classes") != expected_workflows:
            raise RuntimeError("Template registry evidence disagrees with the manifest")

        sync_release = run([sys.executable, "scripts/verify_release.py"], ROOT)
        summary["steps"]["template_sync_release"] = sync_release
        require_success(sync_release, "Template Sync release contract")
        sync_evals = run([sys.executable, "scripts/verify_evals.py"], ROOT)
        summary["steps"]["template_sync_evals"] = sync_evals
        require_success(sync_evals, "Template Sync eval contract")

        hdf_release = run([sys.executable, "scripts/verify_release.py"], hdf)
        summary["steps"]["hdf_release"] = hdf_release
        require_success(hdf_release, "Harness Driven Development release contract")
        hdf_evals = run(
            [sys.executable, "scripts/verify_evals.py", "--repository", str(template)],
            hdf,
        )
        summary["steps"]["hdf_evals"] = hdf_evals
        require_success(hdf_evals, "Harness Driven Development eval contract")

        with tempfile.TemporaryDirectory() as temp_dir:
            disposable = Path(temp_dir) / "service"
            shutil.copytree(
                template,
                disposable,
                symlinks=True,
                ignore=shutil.ignore_patterns(".git", ".artifacts", ".tools"),
            )
            init_step = run(
                [
                    str(disposable / "scripts/init_project.sh"),
                    "--module", "example.com/conformance/service",
                    "--service", "conformance-service",
                    "--owner", "@conformance-team",
                ],
                disposable,
            )
            summary["steps"]["template_init"] = init_step
            require_success(init_step, "Template initialization")
            build_step = run(["go", "build", "./..."], disposable)
            summary["steps"]["initialized_build"] = build_step
            require_success(build_step, "Initialized Template build")
            test_step = run(["go", "test", "./..."], disposable)
            summary["steps"]["initialized_test"] = test_step
            require_success(test_step, "Initialized Template tests")
            init_env = dict(os.environ)
            init_env["HARNESSCTL_BIN"] = str(harnessctl)
            init_registry = run(
                [str(disposable / "scripts/check_spec_registry.sh")],
                disposable,
                init_env,
            )
            summary["steps"]["initialized_registry"] = init_registry
            require_success(init_registry, "Initialized Template registry")
            expected_links = {
                "CLAUDE.md": "AGENTS.md",
                ".claude/skills": "../.agents/skills",
            }
            for relative, target in expected_links.items():
                path = disposable / relative
                if not path.is_symlink() or os.readlink(path) != target:
                    raise RuntimeError(f"initialized Template symlink is invalid: {relative}")

        summary["status"] = "passed"
    except (OSError, KeyError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        summary["error"] = str(exc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if summary["status"] != "passed":
        print(f"FAIL: {summary.get('error', 'conformance failed')}", file=sys.stderr)
        return 1
    print(f"cross-component conformance passed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
