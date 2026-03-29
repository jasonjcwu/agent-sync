"""agent-sync CLI — One soul, many bodies."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from agent_sync import __version__
from agent_sync.core.detector import Detector
from agent_sync.core.schema import UniversalAgent, load_universal_agent
from agent_sync.core.syncer import Syncer

app = typer.Typer(
    name="agent-sync",
    help="One soul, many bodies — sync AI agent identity across platforms.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"agent-sync {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True),
):
    """One soul, many bodies — sync AI agent identity across platforms."""


@app.command()
def init(
    path: Path = typer.Argument(Path.cwd(), help="Directory to initialize"),
):
    """Create a universal-agent/ directory structure."""
    agent_dir = path / "universal-agent"
    if agent_dir.exists():
        console.print(f"[yellow]Already exists:[/yellow] {agent_dir}")
        raise typer.Exit(1)

    agent_dir.mkdir(parents=True)

    # Create example configs
    (agent_dir / "soul.yaml").write_text(_DEFAULT_SOUL)
    (agent_dir / "identity.yaml").write_text(_DEFAULT_IDENTITY)
    (agent_dir / "user.yaml").write_text(_DEFAULT_USER)
    (agent_dir / "routing.yaml").write_text(_DEFAULT_ROUTING)

    directives_dir = agent_dir / "directives"
    directives_dir.mkdir()
    (directives_dir / "INDEX.md").write_text(_DEFAULT_INDEX)

    console.print(f"[green]Created[/green] {agent_dir}")
    console.print("Edit the YAML files, then run [bold]agent-sync sync[/bold]")


@app.command()
def detect(
    project_path: Path = typer.Argument(Path.cwd(), help="Project directory to scan"),
):
    """Detect which agent platforms are configured."""
    detector = Detector(project_path)
    installed = detector.detect_installed()

    if not installed:
        console.print("[yellow]No agent platforms detected.[/yellow]")
        raise typer.Exit()

    console.print(f"[bold]Detected {len(installed)} platform(s):[/bold]")
    for status in installed:
        console.print(f"  [green]*[/green] {status.platform} — {status.config_path}")


@app.command()
def sync(
    agent_path: Path = typer.Option(
        Path("universal-agent"), "--agent", "-a", help="Path to universal-agent/ directory"
    ),
    project_path: Path = typer.Argument(Path.cwd(), help="Target project directory"),
    target: Optional[list[str]] = typer.Option(None, "--target", "-t", help="Specific platform(s)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing"),
):
    """Sync universal config to platform-specific files."""
    if not agent_path.exists():
        console.print(f"[red]Not found:[/red] {agent_path}")
        console.print("Run [bold]agent-sync init[/bold] first.")
        raise typer.Exit(1)

    syncer = Syncer(agent_path, project_path)
    targets = list(target) if target else None
    results = syncer.sync(targets=targets, dry_run=dry_run)

    if not results:
        raise typer.Exit(1)

    total_written = sum(len(r.files_written) for r in results)
    total_errors = sum(len(r.errors) for r in results)
    console.print(f"\n[bold]Done:[/bold] {total_written} files written, {total_errors} errors")


@app.command()
def status(
    project_path: Path = typer.Argument(Path.cwd(), help="Project directory"),
):
    """Show sync status for all platforms."""
    detector = Detector(project_path)
    statuses = detector.detect_all()

    from rich.table import Table

    table = Table(title="agent-sync status")
    table.add_column("Platform", style="bold")
    table.add_column("Installed")
    table.add_column("Config Path")

    for s in statuses:
        installed = "[green]yes[/green]" if s.installed else "[dim]no[/dim]"
        path = str(s.config_path) if s.config_path else "—"
        table.add_row(s.platform, installed, path)

    console.print(table)


# --- Default templates ---

_DEFAULT_SOUL = """\
name: assistant
language: en
personality:
  - Be genuinely helpful, not performatively helpful
  - Have opinions — you're not a search engine
  - Try to figure things out before asking
boundaries:
  - Private things stay private. No exceptions.
  - Ask before acting externally
  - You are a guest in someone's life
communication:
  style: concise but thorough
  tone: warm and genuine
  do_not:
    - Say "Great question!" or "I'd be happy to help!"
"""

_DEFAULT_IDENTITY = """\
name: Assistant
emoji: "\U0001f916"
values: []
traits: []
development_goals: {}
"""

_DEFAULT_USER = """\
name: ""
timezone: UTC
github: ""
occupation: ""
interests: []
preferences: []
"""

_DEFAULT_ROUTING = """\
platforms:
  openclaw:
    type: chat-assistant
    strengths: [daily chat, scheduled tasks, messaging]
  claude_code:
    type: coding-agent
    strengths: [complex coding, code review, refactoring]
  codex:
    type: research-agent
    strengths: [deep research, large-scale code generation]
defaults:
  chat: openclaw
  coding: claude_code
  research: codex
"""

_DEFAULT_INDEX = """\
# Directives Index

<!-- Add your directives here with format: -->
<!-- | ID | Title | Summary | Domain | Keywords | -->
"""
