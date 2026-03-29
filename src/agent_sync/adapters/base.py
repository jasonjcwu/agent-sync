"""Base adapter interface — all platform adapters implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from agent_sync.core.schema import UniversalAgent


@dataclass
class SyncResult:
    """Result of syncing to a platform."""

    platform: str
    files_written: list[Path] = field(default_factory=list)
    files_skipped: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


@dataclass
class PullResult:
    """Result of pulling from a platform."""

    platform: str
    fields_updated: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class AdapterStatus:
    """Status of a platform adapter."""

    platform: str
    installed: bool = False
    config_path: Optional[Path] = None
    last_sync: Optional[str] = None


class BaseAdapter(ABC):
    """All platform adapters inherit from this."""

    platform_name: str = ""
    platform_display: str = ""

    @abstractmethod
    def detect(self, project_path: Path) -> bool:
        """Detect if this platform is configured in the given project."""

    @abstractmethod
    def sync(
        self,
        agent: UniversalAgent,
        project_path: Path,
        *,
        dry_run: bool = False,
    ) -> SyncResult:
        """Sync universal config → platform-specific files."""

    @abstractmethod
    def pull(self, agent: UniversalAgent, project_path: Path) -> PullResult:
        """Pull platform-specific config back into universal format."""

    @abstractmethod
    def status(self, project_path: Path) -> AdapterStatus:
        """Report current sync status."""

    def get_template_dir(self) -> Path:
        """Return the directory containing Jinja2 templates for this adapter."""
        return Path(__file__).parent.parent / "templates" / self.platform_name
