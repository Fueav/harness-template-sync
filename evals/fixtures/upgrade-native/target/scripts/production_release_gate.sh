#!/usr/bin/env bash
set -euo pipefail
python3 -c 'import json; from pathlib import Path; x=json.loads(Path("product/order.json").read_text()); assert x["broker_order_id"] == "broker-7"'
printf "Broker order contract passed\n"
