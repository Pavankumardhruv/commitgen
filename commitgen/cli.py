import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from commitgen.diff import get_staged_diff, get_unstaged_diff
from commitgen.generate import generate_message

console = Console()


def main():
    args = sys.argv[1:]

    if "hook" in args:
        from commitgen.hook import install_hook
        console.print(install_hook())
        return

    if "unhook" in args:
        from commitgen.hook import uninstall_hook
        console.print(uninstall_hook())
        return

    commit_msg_only = "--commit-msg-only" in args
    use_local = "--local" in args
    auto_commit = "--commit" in args or "-c" in args
    backend = "ollama" if use_local else "claude"

    diff = get_staged_diff()

    if diff.is_empty:
        unstaged = get_unstaged_diff()
        if not unstaged.is_empty:
            console.print("[yellow]No staged changes.[/yellow] Stage files first:")
            console.print("  [dim]git add <files>[/dim]")
            console.print(f"  [dim]({len(unstaged.staged_files)} unstaged files detected)[/dim]")
        else:
            console.print("[dim]No changes to commit.[/dim]")
        sys.exit(1)

    console.print(f"[bold]Analyzing {len(diff.staged_files)} staged file(s)...[/bold]\n")
    for f in diff.staged_files:
        console.print(f"  [dim]•[/dim] {f}")
    console.print()

    with console.status(f"Generating commit message ({backend})..."):
        message = generate_message(diff, backend=backend)

    if commit_msg_only:
        print(message)
        return

    panel = Panel(
        Text(message),
        title="[bold green]Suggested commit message[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)

    if auto_commit:
        _do_commit(message)
        return

    console.print("\n[bold]Actions:[/bold]")
    console.print("  [green]y[/green] — commit with this message")
    console.print("  [yellow]e[/yellow] — edit in $EDITOR then commit")
    console.print("  [red]n[/red] — cancel")

    try:
        choice = console.input("\n[bold]→ [/bold]").strip().lower()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled.[/dim]")
        sys.exit(0)

    if choice == "y":
        _do_commit(message)
    elif choice == "e":
        _edit_and_commit(message)
    else:
        console.print("[dim]Cancelled.[/dim]")


def _do_commit(message: str):
    result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        console.print(f"\n[bold green]Committed.[/bold green]")
        console.print(f"[dim]{result.stdout.strip()}[/dim]")
    else:
        console.print(f"\n[red]Commit failed:[/red] {result.stderr.strip()}")
        sys.exit(1)


def _edit_and_commit(message: str):
    import os
    import tempfile

    editor = os.environ.get("EDITOR", "vim")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(message)
        tmpfile = f.name

    subprocess.run([editor, tmpfile])

    with open(tmpfile) as f:
        edited = f.read().strip()

    os.unlink(tmpfile)

    if not edited:
        console.print("[dim]Empty message — cancelled.[/dim]")
        sys.exit(0)

    _do_commit(edited)


if __name__ == "__main__":
    main()
