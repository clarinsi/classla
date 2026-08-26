#!/bin/bash
set -e  # Stop on any error

for py in 3.8 3.9 3.10 3.10.20 3.11 3.12 3.13 3.14; do
    echo "=== Testing Python $py ==="
    uv venv -p $py .venv-$py --clear
    source .venv-$py/bin/activate

    # Normalize "3.10.20" to "3.10" so both full and short
    # version strings match the cases below.
    py_majmin="$(printf '%s' "$py" | cut -d. -f1-2)"

    # Use the lowest torch version that has wheels for this Python.
    case "$py_majmin" in
        3.8|3.9|3.10|3.11) TORCH_MIN="1.13.0" ;;
        3.12) TORCH_MIN="2.2.0" ;;
        3.13) TORCH_MIN="2.5.0" ;;
        3.14) TORCH_MIN="2.9.0" ;;
        *) echo "Unknown Python version: $py"; exit 1 ;;
    esac

    uv pip install -e ".[dev]" "torch==$TORCH_MIN"
    cd tests_classla
    pytest . -xvv
    deactivate
    cd ..
    rm -rf .venv-$py

    uv venv -p $py .venv-$py --clear
    source .venv-$py/bin/activate
    uv pip install -e ".[dev]"
    cd tests_classla
    pytest . -xvv
    deactivate
    cd ..
    rm -rf .venv-$py
done