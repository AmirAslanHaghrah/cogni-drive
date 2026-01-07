#!/usr/bin/env bash
set -euo pipefail

# Install system dependencies for Raspberry Pi OS (Debian-based)

if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get not found. This script is for Debian/Raspberry Pi OS."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_FILE="${SCRIPT_DIR}/apt-packages-rpi.txt"

echo "[1/3] Updating apt..."
sudo apt-get update

echo "[2/3] Installing apt packages from: ${PKG_FILE}"
# Remove comments/blank lines
PKGS=$(grep -vE '^\s*#|^\s*$' "${PKG_FILE}" | xargs)
sudo apt-get install -y ${PKGS}

echo "[3/3] Done."
