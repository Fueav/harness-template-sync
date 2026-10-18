#!/usr/bin/env bash
set -euo pipefail
scripts/run_checker_self_tests.sh
scripts/production_release_gate.sh
