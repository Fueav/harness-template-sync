#!/usr/bin/env python3
"""Regression tests for the Template Sync eval contract."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = (
    Path("plugins/harness-template-sync/skills/harness-template-sync/SKILL.md"),
    Path("plugins/harness-template-sync/skills/harness-template-sync/agents/openai.yaml"),
)


def skill_package_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SKILL_FILES:
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update((root / relative).read_bytes() + b"\0")
    return digest.hexdigest()


class EvalContractTests(unittest.TestCase):
    def run_validator(self, checkout: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/verify_evals.py", *args],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )

    def copy_checkout(self, temp_dir: str) -> Path:
        checkout = Path(temp_dir) / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return checkout

    def valid_results(self, checkout: Path) -> dict:
        cases = json.loads((checkout / "evals/cases.json").read_text())["cases"]
        results = []
        for case in cases:
            expected = json.loads(
                (checkout / "evals/fixtures" / case["id"] / "expected.json").read_text()
            )
            result = {
                "case_id": case["id"],
                "mode": case["mode"],
                "decision": expected["decision"],
                "path_decisions": [
                    {"path": path, "action": action[0] if isinstance(action, list) else action}
                    for path, action in expected["required_actions"].items()
                ],
                "blockers": ["Blocked by fixture state"] if expected["decision"] == "blocked" else [],
                "target_gates": expected.get("required_gates", []),
                "evidence": expected.get("required_evidence", ["fixture evidence"]),
            }
            if "max_prompt_skill_line_delta" in expected:
                result["prompt_skill_line_delta"] = expected["max_prompt_skill_line_delta"]
            observed = {"kind": "parent-verification", "case_id": case["id"],
                        "model_task": "unit-test synthetic input", "model_response": "synthetic validator fixture",
                        "target_unchanged": True, "protected_paths_unchanged": True, "verification_scope": "migration-structure",
                        "checks": [{"name": name, "returncode": 0, "argv": ["synthetic"], "stdout": "ok"}
                                   for name in ["migration-structure", *expected.get("required_gates", [])]]}
            artifact = checkout / "evals/evidence" / (case["id"] + ".json")
            artifact.parent.mkdir(exist_ok=True)
            artifact.write_text(json.dumps(observed) + "\n")
            result["execution"] = {"artifact": "evidence/" + artifact.name,
                                   "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}
            results.append(result)
        return {
            "schema_version": 1,
            "eval_contract_version": 3,
            "skill_package_sha256": skill_package_sha256(checkout),
            "results": results,
        }

    def test_accepts_fixture_contract_and_complete_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(self.valid_results(checkout)) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_changed_inputs_with_stale_execution_evidence(self) -> None:
        for relative in ("request.md", "expected.json", "target/product/order.json"):
            with self.subTest(input=relative), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                fixture = checkout / "evals/fixtures/upgrade-native" / relative
                fixture.write_text(fixture.read_text() + "\n")
                result = self.run_validator(checkout, "--results", "evals/results.json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("run input digest differs", result.stderr)

    def test_rejects_incomplete_or_extra_run_inputs(self) -> None:
        for action in ("remove", "add"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                run_path = checkout / "evals/run.json"
                run = json.loads(run_path.read_text())
                if action == "remove":
                    run["input_sha256"].pop(next(iter(run["input_sha256"])))
                else:
                    run["input_sha256"]["evals/fixtures/stale-case/request.md"] = "0" * 64
                run_path.write_text(json.dumps(run))
                result = self.run_validator(checkout, "--results", "evals/results.json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("run input set differs", result.stderr)

    def test_rejects_chmod_only_fixture_changes(self) -> None:
        for relative, mode in (("scripts/production_release_gate.sh", 0o644), ("product/order.json", 0o755)):
            with self.subTest(input=relative), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                fixture = checkout / "evals/fixtures/upgrade-native/target" / relative
                fixture.chmod(mode)
                result = self.run_validator(checkout, "--results", "evals/results.json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("run input mode differs", result.stderr)

    def test_rejects_same_content_fixture_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            fixture = checkout / "evals/fixtures/upgrade-native/target/scripts/production_release_gate.sh"
            original = Path(temp_dir) / "original.sh"
            shutil.copy2(fixture, original)
            fixture.unlink()
            fixture.symlink_to(original)
            result = self.run_validator(checkout, "--results", "evals/results.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run input must be a regular file", result.stderr)

    def test_requires_recorded_eval_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            (checkout / "evals/run.json").unlink()
            result = self.run_validator(checkout, "--results", "evals/results.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid eval run", result.stderr)

    def test_rejects_simulation_without_execution_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            del payload["results"][0]["execution"]
            path = checkout / "results.json"
            path.write_text(json.dumps(payload))
            result = self.run_validator(checkout, "--results", str(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing executed model evidence", result.stderr)

    def test_rejects_changed_execution_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            artifact = checkout / "evals" / payload["results"][0]["execution"]["artifact"]
            artifact.write_text(artifact.read_text() + " ")
            path = checkout / "results.json"
            path.write_text(json.dumps(payload))
            result = self.run_validator(checkout, "--results", str(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("artifact digest differs", result.stderr)

    def test_rejects_unsuccessful_parent_observations(self) -> None:
        for case_id, field, value, message in [
            ("upgrade-native", "checks", [], "missing successful parent check"),
            ("dirty-target-stop", "protected_paths_unchanged", False, "protected owner changes"),
        ]:
            with self.subTest(case_id=case_id), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                payload = self.valid_results(checkout)
                result = next(item for item in payload["results"] if item["case_id"] == case_id)
                artifact = checkout / "evals" / result["execution"]["artifact"]
                observed = json.loads(artifact.read_text())
                observed[field] = value
                artifact.write_text(json.dumps(observed))
                result["execution"]["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
                path = checkout / "results.json"
                path.write_text(json.dumps(payload))
                checked = self.run_validator(checkout, "--results", str(path))
                self.assertNotEqual(checked.returncode, 0)
                self.assertIn(message, checked.stderr)

    def test_exposes_only_delivery_intents(self) -> None:
        modes = {
            case["mode"]
            for case in json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        }
        self.assertTrue(modes and modes <= {"bootstrap", "upgrade"})

    def test_rejects_unknown_target_without_ownership_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            path = checkout / "evals/fixtures/upgrade-native/target/unknown.txt"
            path.write_text("unknown\n")
            result = self.run_validator(checkout)
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("lack required ownership decisions", output)

    def test_rejects_retiring_project_owned_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            target = next(
                item for item in payload["results"] if item["case_id"] == "upgrade-native"
            )
            next(
                item for item in target["path_decisions"]
                if item["path"] == "scripts/production_release_gate.sh"
            )["action"] = "retire"
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("scripts/production_release_gate.sh must be preserve", output)

    def test_rejects_missing_stop_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            target = next(
                item for item in payload["results"] if item["case_id"] == "dirty-target-stop"
            )
            target["blockers"] = []
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("missing blocker", output)

    def test_rejects_stale_skill_package_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            skill = checkout / "plugins/harness-template-sync/skills/harness-template-sync/SKILL.md"
            skill.write_text(skill.read_text() + "\n")
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("stale skill package digest", output)

    def test_rejects_reusing_an_old_eval_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            payload["eval_contract_version"] = 1
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale eval contract version", result.stderr)

    def test_requires_native_gate_even_after_retiring_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            target = next(item for item in payload["results"] if item["case_id"] == "upgrade-native")
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(payload) + "\n")
            self.assertEqual(self.run_validator(checkout, "--results", str(result_path)).returncode, 0)
            target["target_gates"] = []
            result_path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing target gate", result.stderr)


if __name__ == "__main__":
    unittest.main()
