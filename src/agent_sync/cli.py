"""agent-sync CLI — One soul, many bodies."""

from __future__ import annotations

from datetime import datetime
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

# --- Memory subcommands ---

memory_app = typer.Typer(help="Memory pipeline: collect, reflect, promote.")
app.add_typer(memory_app, name="memory")


@memory_app.command("today")
def memory_today(
    agent_path: Path = typer.Option(Path("universal-agent"), "--agent", "-a"),
    days: int = typer.Option(7, "--days", "-d", help="How many days to look back"),
):
    """Show recent hot observations from all sources."""
    from agent_sync.core.memory_schema import load_memory_config
    from agent_sync.core.reflector import Reflector

    config = load_memory_config(agent_path)
    reflector = Reflector(config)
    observations = reflector.collect_observations(days=days)

    if not observations:
        console.print("[yellow]No observations found.[/yellow]")
        raise typer.Exit()

    from rich.table import Table

    table = Table(title=f"Hot Observations (last {days} days)")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Type", width=10)
    table.add_column("Source", width=12)
    table.add_column("Title", style="bold")

    for obs in observations[:50]:
        table.add_row(obs.date, obs.type, obs.source, obs.title[:80])

    console.print(table)
    console.print(f"[dim]Showing {min(len(observations), 50)} of {len(observations)}[/dim]")


@memory_app.command("consolidate")
def memory_consolidate(
    agent_path: Path = typer.Option(Path("universal-agent"), "--agent", "-a"),
    days: int = typer.Option(7, "--days", "-d"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    gc_days: int = typer.Option(30, "--gc-days", help="Remove warm entries older than N days"),
):
    """Run reflector: promote hot → warm, then GC stale entries."""
    from agent_sync.core.memory_schema import load_memory_config
    from agent_sync.core.reflector import Reflector

    config = load_memory_config(agent_path)
    reflector = Reflector(config)

    # Collect
    observations = reflector.collect_observations(days=days)
    console.print(f"Collected [bold]{len(observations)}[/bold] observations")

    # Reflect
    candidates = reflector.reflect(observations)
    console.print(f"Identified [bold]{len(candidates)}[/bold] promotion candidates")

    if candidates:
        for entry in candidates:
            console.print(f"  [green]+[/green] {entry.title} (confidence: {entry.confidence:.2f})")

    if dry_run:
        console.print("\n[dim](dry run — no files written)[/dim]")
        raise typer.Exit()

    # Promote
    warm_path = agent_path / "memory" / "core.md"
    if candidates:
        warm = reflector.promote(candidates, warm_path)
        console.print(f"[green]Promoted {len(warm.entries)} entries to {warm_path}[/green]")

    # GC
    if warm_path.exists():
        removed = reflector.gc(warm_path, max_age_days=gc_days)
        if removed:
            console.print(f"[yellow]GC removed {removed} stale entries[/yellow]")
        else:
            console.print("[dim]No stale entries to GC[/dim]")


@memory_app.command("push")
def memory_push(
    agent_path: Path = typer.Option(Path("universal-agent"), "--agent", "-a"),
):
    """Push memory to Git remote."""
    import subprocess

    memory_dir = agent_path / "memory"
    if not memory_dir.exists():
        console.print("[yellow]No memory directory found.[/yellow]")
        raise typer.Exit(1)

    subprocess.run(["git", "add", str(memory_dir)], cwd=agent_path, check=True)
    subprocess.run(["git", "commit", "-m", f"memory sync {datetime.now().strftime('%Y-%m-%d')}"], cwd=agent_path, check=True)
    subprocess.run(["git", "push"], cwd=agent_path, check=True)
    console.print("[green]Memory pushed to remote.[/green]")


@memory_app.command("pull")
def memory_pull(
    agent_path: Path = typer.Option(Path("universal-agent"), "--agent", "-a"),
):
    """Pull latest memory from Git remote."""
    import subprocess

    subprocess.run(["git", "pull"], cwd=agent_path, check=True)
    console.print("[green]Memory pulled from remote.[/green]")
