"""Sync orchestrator — coordinate syncing across platforms."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from agent_sync.adapters.base import SyncResult
from agent_sync.core.detector import Detector
from agent_sync.core.schema import UniversalAgent, load_universal_agent

console = Console()


class Syncer:
    """Orchestrate sync between universal config and platforms."""

    def __init__(self, agent_path: Path, project_path: Path | None = None):
        self.agent = load_universal_agent(agent_path)
        self.project_path = project_path or Path.cwd()
        self.detector = Detector(self.project_path)

    def sync(
        self,
        *,
        targets: list[str] | None = None,
        dry_run: bool = False,
    ) -> list[SyncResult]:
        """Sync universal config to target platforms."""
        if targets:
            adapters = self.detector.get_adapters_for_platforms(targets)
        else:
            # Sync to all detected platforms
            installed = self.detector.detect_installed()
            adapters = []
            for status in installed:
                adapter = self.detector.get_adapter(status.platform)
                if adapter:
                    adapters.append(adapter)

        if not adapters:
            console.print("[yellow]No platforms detected. Use --target to specify.[/yellow]")
            return []

        results = []
        for adapter in adapters:
            console.print(f"Syncing to [bold]{adapter.platform_display}[/bold]...")
            result = adapter.sync(self.agent, self.project_path, dry_run=dry_run)
            results.append(result)
            self._print_result(result)

        return results

    def _print_result(self, result: SyncResult) -> None:
        prefix = "[dim](dry run)[/dim] " if result.dry_run else ""
        if result.ok:
            console.print(f"  {prefix}[green]OK[/green] — {len(result.files_written)} files written")
            for f in result.files_written:
                console.print(f"    [dim]{f}[/dim]")
            if result.files_skipped:
                for f in result.files_skipped:
                    console.print(f"    [yellow]skipped[/yellow] {f}")
        else:
            console.print(f"  {prefix}[red]FAILED[/red]")
            for err in result.errors:
                console.print(f"    [red]{err}[/red]")

    def print_status(self) -> None:
        """Print a status table of all platforms."""
        table = Table(title="agent-sync status")
        table.add_column("Platform", style="bold")
        table.add_column("Installed")
        table.add_column("Config Path")

        for status in self.detector.detect_all():
            installed = "[green]yes[/green]" if status.installed else "[dim]no[/dim]"
            path = str(status.config_path) if status.config_path else "—"
            table.add_row(status.platform, installed, path)

        console.print(table)
