"""
Terminal renderer: displays schema diffs with rich formatting.
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from .differ import SchemaDiff, FieldChange

console = Console()


def _kind_badge(change: FieldChange) -> Text:
    if change.kind == "added":
        return Text("+ ADDED", style="bold green")
    elif change.kind == "removed":
        return Text("- REMOVED", style="bold red")
    elif change.kind == "type_changed":
        return Text("~ CHANGED", style="bold yellow")
    else:
        return Text("  ok", style="dim")


def render_diff(diff: SchemaDiff, show_unchanged: bool = False) -> None:
    if not diff.has_changes and not show_unchanged:
        console.print(f"  [dim]✓ {diff.file}[/dim] — [green]no schema changes[/green]")
        return

    title = f"[bold cyan]{diff.file}[/bold cyan]"
    if diff.has_changes:
        parts = []
        if diff.added:
            parts.append(f"[green]+{len(diff.added)} added[/green]")
        if diff.removed:
            parts.append(f"[red]-{len(diff.removed)} removed[/red]")
        if diff.type_changed:
            parts.append(f"[yellow]~{len(diff.type_changed)} changed[/yellow]")
        title += "  " + "  ".join(parts)

    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
        expand=False,
        min_width=60,
    )
    table.add_column("Status", width=12)
    table.add_column("Field", style="bold")
    table.add_column("Before", style="dim")
    table.add_column("After")

    all_changes = diff.added + diff.removed + diff.type_changed
    if show_unchanged:
        all_changes += diff.unchanged

    # Sort: changed first, then alpha
    def sort_key(c: FieldChange) -> tuple:
        order = {"added": 0, "removed": 1, "type_changed": 2, "unchanged": 3}
        return (order.get(c.kind, 9), c.field)

    for change in sorted(all_changes, key=sort_key):
        badge = _kind_badge(change)
        before = change.old_type or "—"
        after = change.new_type or "—"
        if change.kind == "added":
            after_text = Text(after, style="green")
        elif change.kind == "removed":
            after_text = Text(after, style="red")
        elif change.kind == "type_changed":
            after_text = Text(after, style="yellow")
        else:
            after_text = Text(after, style="dim")
        table.add_row(badge, change.field, before, after_text)

    console.print(table)
    console.print()


def render_summary(diffs: list[SchemaDiff]) -> None:
    changed = [d for d in diffs if d.has_changes]
    clean = [d for d in diffs if not d.has_changes]

    console.rule("[bold]Schema Shift Report[/bold]")
    console.print(f"  [bold]{len(diffs)}[/bold] file(s) scanned  •  "
                  f"[bold yellow]{len(changed)}[/bold yellow] with drift  •  "
                  f"[bold green]{len(clean)}[/bold green] clean\n")
