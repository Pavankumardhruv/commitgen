import stat
from pathlib import Path

HOOK_SCRIPT = """#!/bin/sh
# commitgen: auto-generate commit message from staged diff
# To disable: remove this file or run `commitgen unhook`

COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="$2"

# Only run for regular commits (not merge, amend, etc.)
if [ -n "$COMMIT_SOURCE" ]; then
    exit 0
fi

# Check if commitgen is installed
if ! command -v commitgen >/dev/null 2>&1; then
    echo "commitgen: not installed, skipping auto-generation"
    exit 0
fi

# Generate message and write to commit message file
MSG=$(commitgen --commit-msg-only 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$MSG" ]; then
    echo "$MSG" > "$COMMIT_MSG_FILE"
fi
"""


def install_hook() -> str:
    hooks_dir = _find_hooks_dir()
    hook_path = hooks_dir / "prepare-commit-msg"

    if hook_path.exists():
        content = hook_path.read_text()
        if "commitgen" in content:
            return "Hook already installed."
        raise FileExistsError(
            f"A prepare-commit-msg hook already exists at {hook_path}. "
            "Remove it first or add commitgen manually."
        )

    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(HOOK_SCRIPT)
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    return f"Hook installed at {hook_path}"


def uninstall_hook() -> str:
    hooks_dir = _find_hooks_dir()
    hook_path = hooks_dir / "prepare-commit-msg"

    if not hook_path.exists():
        return "No hook to remove."

    content = hook_path.read_text()
    if "commitgen" not in content:
        return "Existing hook was not installed by commitgen. Skipping."

    hook_path.unlink()
    return "Hook removed."


def _find_hooks_dir() -> Path:
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Not in a git repository.")

    return Path(result.stdout.strip()) / "hooks"
