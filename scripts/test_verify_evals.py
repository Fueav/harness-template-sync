#!/usr/bin/env python3
"""Regression tests for the Template Sync eval contract."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
                    {"path": path, "action": action}
                    for path, action in expected["required_actions"].items()
                ],
                "blockers": expected.get("required_blockers", []),
                "target_gates": expected.get("required_gates", []),
                "evidence": ["fixture evidence"],
            }
            if "max_prompt_skill_line_delta" in expected:
                result["prompt_skill_line_delta"] = expected["max_prompt_skill_line_delta"]
            results.append(result)
        return {"results": results}

    def test_accepts_fixture_contract_and_complete_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(self.valid_results(checkout)) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_unknown_target_without_ownership_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            path = checkout / "evals/fixtures/adopt-mature/target/unknown.txt"
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
                item for item in payload["results"] if item["case_id"] == "refresh-custom-gates"
            )
            next(
                item for item in target["path_decisions"]
                if item["path"] == "scripts/gates/custom_check.sh"
            )["action"] = "retire"
            result_path = checkout / "results.json"
            result_path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(result_path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("scripts/gates/custom_check.sh must be preserve", output)

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


if __name__ == "__main__":
    unittest.main()
