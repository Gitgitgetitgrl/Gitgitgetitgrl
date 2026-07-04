#!/usr/bin/env bash
# Set up the KDP automation project: create a Python venv and install deps.
# Gen (the Image Generation Agent) is authorized to run this to bootstrap a run.
#   bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
echo "==> Creating virtual environment (.venv)"
$PY -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing dependencies"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "==> Creating standard work folders"
mkdir -p work assets

echo
echo "==> Setup complete. Activate with:  source .venv/bin/activate"
echo "    Sanity check:  pytest validation/test_validate.py -q"
