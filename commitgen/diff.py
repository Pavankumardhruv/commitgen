import subprocess
from dataclasses import dataclass


@dataclass
class DiffSummary:
    raw_diff: str
    staged_files: list[str]
    stats: str
    is_empty: bool


def get_staged_diff() -> DiffSummary:
    diff = _run("git diff --cached")
    stats = _run("git diff --cached --stat")
    files = _run("git diff --cached --name-only").strip().splitlines()

    return DiffSummary(
        raw_diff=diff,
        staged_files=[f for f in files if f],
        stats=stats,
        is_empty=not diff.strip(),
    )


def get_unstaged_diff() -> DiffSummary:
    diff = _run("git diff")
    stats = _run("git diff --stat")
    files = _run("git diff --name-only").strip().splitlines()

    return DiffSummary(
        raw_diff=diff,
        staged_files=[f for f in files if f],
        stats=stats,
        is_empty=not diff.strip(),
    )


def truncate_diff(diff: str, max_chars: int = 8000) -> str:
    if len(diff) <= max_chars:
        return diff
    return diff[:max_chars] + f"\n\n... (truncated, {len(diff) - max_chars} chars omitted)"


def _run(cmd: str) -> str:
    result = subprocess.run(
        cmd.split(),
        capture_output=True,
        text=True,
    )
    return result.stdout
