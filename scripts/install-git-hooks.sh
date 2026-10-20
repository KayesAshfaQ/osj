#!/bin/sh
# Opt-in installer for Justify Git hooks
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="${REPO_ROOT}/scripts/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Hooks directory not found at $HOOKS_DIR" >&2
    exit 1
fi

chmod +x "${HOOKS_DIR}/"*

git config core.hooksPath scripts/hooks
echo "✅ Git hooks installed: core.hooksPath set to scripts/hooks"
