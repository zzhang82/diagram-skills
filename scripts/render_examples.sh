#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m diagram_studio.cli render-examples "$@"
