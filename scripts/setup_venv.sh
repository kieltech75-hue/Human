#!/usr/bin/env bash
# Cross-platform POSIX-friendly script to create a venv and install requirements
# Usage: ./scripts/setup_venv.sh [venv_dir]
set -euo pipefail
VENV_DIR=${1:-.venv}

echo "Creating virtualenv at ${VENV_DIR}"
python -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r requirements.txt

echo "Virtualenv created. Activate with: source ${VENV_DIR}/bin/activate"
