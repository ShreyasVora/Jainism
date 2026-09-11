#!/usr/bin/env bash
#
# Build script for Jainism prayer documents.
# Converts markdown files in 'src/' to standalone, print-friendly HTML
# (and plain-text downloads) in 'build/' using build.py. No external
# dependencies required -- just Python 3.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${SCRIPT_DIR}/build.py"
