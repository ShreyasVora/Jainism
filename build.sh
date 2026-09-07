#!/usr/bin/env bash
#
# Build script for Jainism prayer documents.
# Converts markdown files in 'src/' to standalone HTML in 'build/' using pandoc.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
BUILD_DIR="${SCRIPT_DIR}/build"

# Verify pandoc is available in PATH
if ! command -v pandoc &> /dev/null; then
    echo "Error: 'pandoc' was not found in PATH." >&2
    echo "Please ensure pandoc is installed and accessible." >&2
    exit 1
fi

# Verify src directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Source directory '$SRC_DIR' does not exist." >&2
    exit 1
fi

# Ensure build directory exists
mkdir -p "$BUILD_DIR"

count=0

# Process all markdown files in src/ (including subdirectories if present)
while IFS= read -r -d '' md_file; do
    rel_path="${md_file#"$SRC_DIR"/}"
    rel_dir="$(dirname "$rel_path")"
    base_name="$(basename "$rel_path" .md)"

    if [ "$rel_dir" = "." ]; then
        target_file="$BUILD_DIR/${base_name}.html"
    else
        target_dir="$BUILD_DIR/$rel_dir"
        mkdir -p "$target_dir"
        target_file="$target_dir/${base_name}.html"
    fi

    echo "Building: src/$rel_path -> build/${target_file#"$BUILD_DIR"/}"
    pandoc --standalone "$md_file" -o "$target_file" "$@"
    count=$((count + 1))
done < <(find "$SRC_DIR" -type f -name "*.md" -print0 | sort -z)

if [ "$count" -eq 0 ]; then
    echo "No markdown files found in $SRC_DIR."
else
    echo "Successfully generated $count HTML file(s) in $BUILD_DIR."
fi
