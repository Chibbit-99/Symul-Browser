#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$REPO_ROOT"

if [[ ! -d .git || ! -f main.py || ! -f requirements.txt ]]; then
    echo "Error: this is not a valid Symul Browser Git checkout." >&2
    exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
    echo "Symul's virtual environment is missing. Run bash install.sh first." >&2
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: the checkout has local changes. Commit or stash them before updating." >&2
    git status --short >&2
    exit 1
fi

echo "Fetching updates..."
git fetch --prune
BRANCH="$(git symbolic-ref --quiet --short HEAD)" || {
    echo "Error: detached HEAD. Check out a branch before updating." >&2
    exit 1
}
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
if [[ -z "$UPSTREAM" ]]; then
    echo "Error: branch '$BRANCH' has no upstream configured." >&2
    echo "Set its upstream before running the updater." >&2
    exit 1
fi

if ! git merge --ff-only "$UPSTREAM"; then
    echo "Update stopped: Git could not fast-forward safely." >&2
    echo "Commit/stash local changes or resolve branch divergence, then retry." >&2
    exit 1
fi

echo "Refreshing Python dependencies..."
.venv/bin/python -m pip install -r requirements.txt
echo
echo "Symul Browser is up to date. Restart it if it was open."
