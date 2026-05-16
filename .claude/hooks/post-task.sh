#!/usr/bin/env bash
# Post-task hook: reminder to update impl-log and CHANGELOG after task completion.
# Invoked by /impl command after Review phase.
#
# Usage: ./.claude/hooks/post-task.sh <spec-name> <task-id>

set -euo pipefail

SPEC_NAME="${1:?Spec name required}"
TASK_ID="${2:?Task ID required}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
SPEC_DIR="$REPO_ROOT/specs/$SPEC_NAME"
IMPL_LOG="$SPEC_DIR/impl-log.md"
CHANGELOG="$REPO_ROOT/CHANGELOG.md"

# 1. impl-log has an entry for this task
if ! grep -q "$TASK_ID" "$IMPL_LOG" 2>/dev/null; then
    echo "✗ No entry for $TASK_ID in $IMPL_LOG"
    echo "  Add an entry describing the implementation before continuing."
    exit 1
fi

# 2. CHANGELOG was modified in the last commit
LAST_COMMIT_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)
if ! echo "$LAST_COMMIT_FILES" | grep -q "^CHANGELOG.md$"; then
    echo "⚠ CHANGELOG.md not modified in last commit."
    echo "  Consider adding an entry under [Unreleased]."
fi

# 3. Task marked as completed in tasks.md
TASKS_FILE="$SPEC_DIR/tasks.md"
if ! grep -A1 "^### $TASK_ID:" "$TASKS_FILE" | grep -q "\[x\]"; then
    echo "⚠ $TASK_ID not marked as completed in tasks.md"
fi

echo "✓ Post-task checks completed for $SPEC_NAME/$TASK_ID"
