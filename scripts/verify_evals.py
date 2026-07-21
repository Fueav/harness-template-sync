#!/usr/bin/env python3
"""Validate Harness Template Sync eval fixtures and optional model results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
ACTIONS = {"preserve", "add", "merge", "relocate", "retire", "blocked"}
MODES = {"bootstrap", "adopt", "refresh", "govern"}


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def target_paths(case_id: str) -> set[str]:
    target = EVALS / "fixtures" / case_id / "target"
    return {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file() or path.is_symlink()
    }


def validate_fixture(case: dict, errors: list[str]) -> dict:
    case_id = case.get("id")
    mode = case.get("mode")
    if not isinstance(case_id, str) or not case_id:
        errors.append("case id must be non-empty")
        return {}
    if mode not in MODES:
        errors.append(f"{case_id}: invalid mode")
    expected_path = EVALS / "fixtures" / case_id / "expected.json"
    target = EVALS / "fixtures" / case_id / "target"
    if not expected_path.is_file() or not target.is_dir():
        errors.append(f"{case_id}: fixture must contain expected.json and target/")
        return {}
    expected = load(expected_path)
    if not isinstance(expected, dict):
        errors.append(f"{case_id}: expected contract must be an object")
        return {}
    if expected.get("case_id") != case_id or expected.get("mode") != mode:
        errors.append(f"{case_id}: expected identity disagrees with cases.json")
    if expected.get("decision") not in {"continue", "blocked"}:
        errors.append(f"{case_id}: expected decision is invalid")
    required = expected.get("required_actions")
    if not isinstance(required, dict) or any(
        not isinstance(path, str) or action not in ACTIONS
        for path, action in required.items()
    ):
        errors.append(f"{case_id}: required_actions is invalid")
        required = {}
    forbidden = expected.get("forbidden_actions", {})
    if not isinstance(forbidden, dict) or any(
        not isinstance(path, str)
        or not isinstance(actions, list)
        or any(action not in ACTIONS for action in actions)
        for path, actions in forbidden.items()
    ):
        errors.append(f"{case_id}: forbidden_actions is invalid")
    missing_ownership = target_paths(case_id) - set(required)
    if missing_ownership:
        errors.append(
            f"{case_id}: target paths lack required ownership decisions: "
            + ", ".join(sorted(missing_ownership))
        )
    return expected


def validate_results(
    cases: list[dict], expected_by_id: dict[str, dict], payload: object, errors: list[str]
) -> None:
    if not isinstance(payload, dict) or set(payload) != {"results"}:
        errors.append("result payload must contain only results")
        return
    results = payload.get("results")
    if not isinstance(results, list):
        errors.append("results must be an array")
        return
    by_id: dict[str, dict] = {}
    for result in results:
        if not isinstance(result, dict):
            errors.append("every result must be an object")
            continue
        case_id = result.get("case_id")
        if not isinstance(case_id, str) or case_id in by_id:
            errors.append("results contain an invalid or duplicate case_id")
            continue
        by_id[case_id] = result
    expected_ids = {case["id"] for case in cases}
    if set(by_id) != expected_ids:
        errors.append("results must cover every eval case exactly once")

    for case_id in sorted(expected_ids & set(by_id)):
        expected = expected_by_id[case_id]
        result = by_id[case_id]
        required_fields = {
            "case_id", "mode", "decision", "path_decisions", "blockers",
            "target_gates", "evidence",
        }
        if not required_fields.issubset(result):
            errors.append(f"{case_id}: result fields are incomplete")
            continue
        if result.get("mode") != expected.get("mode"):
            errors.append(f"{case_id}: mode does not match")
        if result.get("decision") != expected.get("decision"):
            errors.append(f"{case_id}: decision does not match")
        decisions = result.get("path_decisions")
        if not isinstance(decisions, list):
            errors.append(f"{case_id}: path_decisions must be an array")
            continue
        action_by_path: dict[str, str] = {}
        for item in decisions:
            if not isinstance(item, dict) or set(item) != {"path", "action"}:
                errors.append(f"{case_id}: path decision has invalid fields")
                continue
            path, action = item.get("path"), item.get("action")
            if not isinstance(path, str) or action not in ACTIONS or path in action_by_path:
                errors.append(f"{case_id}: path decision is invalid or duplicated")
                continue
            action_by_path[path] = action
        for path, action in expected.get("required_actions", {}).items():
            if action_by_path.get(path) != action:
                errors.append(f"{case_id}: {path} must be {action}")
        for path, forbidden in expected.get("forbidden_actions", {}).items():
            if action_by_path.get(path) in forbidden:
                errors.append(f"{case_id}: {path} uses forbidden action")
        blockers = result.get("blockers")
        if not isinstance(blockers, list) or any(not isinstance(item, str) for item in blockers):
            errors.append(f"{case_id}: blockers must be strings")
            blockers = []
        blocker_text = " ".join(blockers).lower()
        for phrase in expected.get("required_blockers", []):
            if not all(token in blocker_text for token in phrase.lower().split()):
                errors.append(f"{case_id}: missing blocker {phrase!r}")
        gates = result.get("target_gates")
        if not isinstance(gates, list) or any(not isinstance(item, str) for item in gates):
            errors.append(f"{case_id}: target_gates must be strings")
            gates = []
        for gate in expected.get("required_gates", []):
            if gate not in gates:
                errors.append(f"{case_id}: missing target gate {gate!r}")
        if "max_prompt_skill_line_delta" in expected:
            delta = result.get("prompt_skill_line_delta")
            if not isinstance(delta, int) or delta > expected["max_prompt_skill_line_delta"]:
                errors.append(f"{case_id}: prompt/Skill line budget exceeded")
        if not isinstance(result.get("evidence"), list) or not result["evidence"]:
            errors.append(f"{case_id}: evidence must be non-empty")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    manifest = load(EVALS / "cases.json")
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "cases"}:
        errors.append("cases.json has an invalid contract")
        cases: list[dict] = []
    else:
        cases = manifest.get("cases", [])
        if manifest.get("schema_version") != 1 or not isinstance(cases, list):
            errors.append("cases.json must use schema version 1 and a cases array")
            cases = []
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)):
        errors.append("case ids must be unique")
    expected_by_id = {
        case["id"]: validate_fixture(case, errors)
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }
    schema = load(EVALS / "result.schema.json")
    if not isinstance(schema, dict) or schema.get("type") != "object":
        errors.append("result schema is invalid")
    if args.results:
        validate_results(cases, expected_by_id, load(args.results), errors)
    for error in sorted(set(errors)):
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"eval contract ok: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
