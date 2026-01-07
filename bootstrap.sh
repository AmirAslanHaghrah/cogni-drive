#!/usr/bin/env bash
set -euo pipefail

./scripts/install_deps_rpi.sh

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
