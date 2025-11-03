#!/bin/bash -eo pipefail
set -x

PY_MINOR=$(python -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MINOR" -lt 11 ]; then
  echo "Not checking abi3audit for Python $PY_MINOR < 3.11"
  exit 0
fi
abi3audit --strict --report --verbose "$1"
