#!/usr/bin/env bash
# Pre-task hook: verifies that the spec is approved before implementing.
# Invoked by /impl command.
#
# Usage: ./.claude/hooks/pre-task.sh <spec-name> <task-id>

set -euo pipefail

SPEC_NAME="${1:?Spec name required}"
TASK_ID="${2:?Task ID required}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
SPEC_DIR="$REPO_ROOT/specs/$SPEC_NAME"

# 1. Spec exists
if [ ! -d "$SPEC_DIR" ]; then
    echo "✗ Spec '$SPEC_NAME' does not exist."
    echo "  Run /spec-init $SPEC_NAME first."
    exit 1
fi

# 2. Requirements approved
if ! grep -q "^\*\*Estado:\*\* Approved" "$SPEC_DIR/requirements.md" 2>/dev/null; then
    echo "✗ Requirements for '$SPEC_NAME' not approved."
    echo "  Approve requirements before /impl."
    exit 1
fi

# 3. Design approved
if [ ! -f "$SPEC_DIR/design.md" ] || ! grep -q "^\*\*Estado:\*\* Approved" "$SPEC_DIR/design.md"; then
    echo "✗ Design for '$SPEC_NAME' not approved."
    echo "  Run /spec-design first."
    exit 1
fi

# 4. Tasks approved
if [ ! -f "$SPEC_DIR/tasks.md" ] || ! grep -q "^\*\*Estado:\*\* Approved" "$SPEC_DIR/tasks.md"; then
    echo "✗ Tasks for '$SPEC_NAME' not approved."
    echo "  Run /spec-tasks first."
    exit 1
fi

# 5. Task ID exists in tasks.md
if ! grep -q "^### $TASK_ID:" "$SPEC_DIR/tasks.md"; then
    echo "✗ Task '$TASK_ID' not found in $SPEC_DIR/tasks.md"
    exit 1
fi

echo "✓ Pre-task checks passed for $SPEC_NAME/$TASK_ID"
