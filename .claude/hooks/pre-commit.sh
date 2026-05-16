#!/usr/bin/env bash
# Pre-commit hook for tempify
# Runs before every commit. Fails fast if checks don't pass.
#
# To install:  ln -s ../../.claude/hooks/pre-commit.sh .git/hooks/pre-commit
# Or:          pip install pre-commit && pre-commit install

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "→ ruff format check"
ruff format --check src/ tests/

echo "→ ruff lint"
ruff check src/ tests/

echo "→ mypy strict"
mypy --strict src/

echo "→ pytest (fast tests only, marker 'not slow')"
pytest -m "not slow" --no-cov -q

echo "✓ All pre-commit checks passed"
