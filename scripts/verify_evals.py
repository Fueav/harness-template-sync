#!/usr/bin/env python3
"""Validate Harness Template Sync eval fixtures and optional model results."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
ACTIONS = {"preserve", "add", "merge", "relocate", "retire", "regenerate", "blocked"}
MODES = {"bootstrap", "upgrade"}
EVAL_CONTRACT_VERSION = 3
SKILL_FILES = (
    Path("plugins/harness-template-sync/skills/harness-template-sync/SKILL.md"),
    Path("plugins/harness-template-sync/skills/harness-template-sync/agents/openai.yaml"),
)


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def skill_package_sha256(root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for relative in SKILL_FILES:
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update((root / relative).read_bytes() + b"\0")
    return digest.hexdigest()


def target_paths(case_id: str) -> set[str]:
    target = EVALS / "fixtures" / case_id / "target"
    return {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file() or path.is_symlink()
    }


def accepted_actions(value: object) -> list[str]:
    return value if isinstance(value, list) else [value]


def validate_run(cases: list[dict], errors: list[str]) -> None:
    try:
        run = load(EVALS / "run.json")
        if not isinstance(run, dict) or run.get("schema_version") != 1:
            raise ValueError("invalid run contract")
        if run.get("eval_contract_version") != EVAL_CONTRACT_VERSION:
            raise ValueError("stale run eval contract version")
        if run.get("skill_package_sha256") != skill_package_sha256():
            raise ValueError("stale run skill package digest")
        recorded = run.get("input_sha256")
        if not isinstance(recorded, dict):
            raise ValueError("run input digests must be an object")
        current = {
            path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for case in cases
            for path in (EVALS / "fixtures" / case["id"]).rglob("*")
            if path.is_file()
        }
        if set(recorded) != set(current):
            raise ValueError("run input set differs from current case fixtures")
        changed = [path for path, digest in current.items() if recorded[path] != digest]
        if changed:
            raise ValueError("run input digest differs: " + ", ".join(sorted(changed)))
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f"invalid eval run: {error}")


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
        not isinstance(path, str)
        or not accepted_actions(action)
        or any(not isinstance(item, str) or item not in ACTIONS for item in accepted_actions(action))
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
    expected_fields = {"schema_version", "eval_contract_version", "skill_package_sha256", "results"}
    if not isinstance(payload, dict) or set(payload) != expected_fields:
        errors.append("result payload has an invalid contract")
        return
    if payload.get("schema_version") != 1:
        errors.append("result payload has an invalid schema version")
    if payload.get("eval_contract_version") != EVAL_CONTRACT_VERSION:
        errors.append("result payload has a stale eval contract version")
    if payload.get("skill_package_sha256") != skill_package_sha256():
        errors.append("result payload has a stale skill package digest")
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
            if action_by_path.get(path) not in accepted_actions(action):
                errors.append(f"{case_id}: {path} must be {action}")
        for path, forbidden in expected.get("forbidden_actions", {}).items():
            if action_by_path.get(path) in forbidden:
                errors.append(f"{case_id}: {path} uses forbidden action")
        blockers = result.get("blockers")
        if not isinstance(blockers, list) or any(not isinstance(item, str) for item in blockers):
            errors.append(f"{case_id}: blockers must be strings")
            blockers = []
        if result.get("decision") == "blocked" and not blockers:
            errors.append(f"{case_id}: missing blocker for blocked delivery")
        gates = result.get("target_gates")
        if not isinstance(gates, list) or any(not isinstance(item, str) for item in gates):
            errors.append(f"{case_id}: target_gates must be strings")
            gates = []
        for gate in expected.get("required_gates", []):
            if gate not in gates:
                errors.append(f"{case_id}: missing target gate {gate!r}")
        for gate in expected.get("forbidden_gates", []):
            if gate in gates:
                errors.append(f"{case_id}: forbidden target gate {gate!r}")
        if "max_prompt_skill_line_delta" in expected:
            delta = result.get("prompt_skill_line_delta")
            if not isinstance(delta, int) or delta > expected["max_prompt_skill_line_delta"]:
                errors.append(f"{case_id}: prompt/Skill line budget exceeded")
        execution = result.get("execution")
        if not isinstance(execution, dict) or set(execution) != {"artifact", "sha256"}:
            errors.append(f"{case_id}: missing executed model evidence")
        else:
            artifact = EVALS / str(execution["artifact"])
            try:
                if not artifact.resolve().is_relative_to((EVALS / "evidence").resolve()):
                    raise ValueError("artifact must stay inside evals/evidence")
                raw = artifact.read_bytes()
                if hashlib.sha256(raw).hexdigest() != execution["sha256"]:
                    raise ValueError("execution artifact digest differs")
                observed = json.loads(raw)
                if observed.get("case_id") != case_id or observed.get("kind") != "parent-verification":
                    raise ValueError("wrong execution artifact identity")
                if not observed.get("model_task") or not observed.get("model_response"):
                    raise ValueError("missing executed model task or response")
                if result["decision"] == "continue":
                    checks = observed.get("checks", [])
                    for command in ("migration-structure", *expected.get("required_gates", [])):
                        if not any(c.get("name") == command and c.get("returncode") == 0
                                   and c.get("argv") and "stdout" in c for c in checks):
                            raise ValueError(f"missing successful parent check {command}")
                    if observed.get("verification_scope") != "migration-structure":
                        raise ValueError("source verification is not product acceptance")
                elif expected.get("protected_paths"):
                    if observed.get("protected_paths_unchanged") is not True:
                        raise ValueError("protected owner changes were not checked unchanged")
                elif observed.get("target_unchanged") is not True:
                    raise ValueError("blocked target was not independently checked unchanged")
            except (OSError, ValueError, TypeError, AttributeError) as error:
                errors.append(f"{case_id}: invalid executed model evidence: {error}")
        evidence = result.get("evidence")
        if (
            not isinstance(evidence, list)
            or not evidence
            or any(not isinstance(item, str) for item in evidence)
        ):
            errors.append(f"{case_id}: evidence must be non-empty")
            evidence = []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    manifest = load(EVALS / "cases.json")
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "eval_contract_version", "cases"}:
        errors.append("cases.json has an invalid contract")
        cases: list[dict] = []
    else:
        cases = manifest.get("cases", [])
        if manifest.get("schema_version") != 1 or not isinstance(cases, list):
            errors.append("cases.json must use schema version 1 and a cases array")
            cases = []
        if manifest.get("eval_contract_version") != EVAL_CONTRACT_VERSION:
            errors.append("cases.json has a stale eval contract version")
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
        validate_run(cases, errors)
        try:
            results = load(args.results)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot load eval results: {error}")
            results = {}
        validate_results(cases, expected_by_id, results, errors)
    for error in sorted(set(errors)):
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"eval contract ok: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
