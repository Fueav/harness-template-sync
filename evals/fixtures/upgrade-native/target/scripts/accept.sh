#!/usr/bin/env bash
set -euo pipefail
python3 -c 'import json; from pathlib import Path; x=json.loads(Path("product/order.json").read_text()); assert x["client_order_id"] == "client-2"; assert x["broker_order_id"] != x["client_order_id"]'
printf "Independent fixture acceptance passed\n"
