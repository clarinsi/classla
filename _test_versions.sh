#!/bin/bash
set -e  # Stop on any error

for py in 3.8 3.9 3.10 3.11 3.12 3.13 3.14; do
    echo "=== Testing Python $py ==="
    uv venv -p $py .venv-$py --clear
    source .venv-$py/bin/activate
    uv pip install -e ".[dev]"
    cd tests_classla
    pytest -vv
    deactivate
    cd ..
    rm -rf .venv-$py
done