#!/usr/bin/env bash
# Opens the restore chooser; --restore-latest is available for explicit CLI restore.
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$repo/setup/installer/app.py" "$@"
