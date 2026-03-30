"""Platform detector — find which agent platforms are installed."""

from __future__ import annotations

from pathlib import Path

from agent_sync.adapters.base import AdapterStatus, BaseAdapter
from agent_sync.adapters.claude_code import ClaudeCodeAdapter
from agent_sync.adapters.codex import CodexAdapter
from agent_sync.adapters.cursor import CursorAdapter
from agent_sync.adapters.openclaw import OpenClawAdapter

# Registry of all adapters
ADAPTERS: list[type[BaseAdapter]] = [
    OpenClawAdapter,
    ClaudeCodeAdapter,
    CodexAdapter,
    CursorAdapter,
]


class Detector:
    """Detect which agent platforms are configured in a project."""

    def __init__(self, project_path: Path | None = None):
        self.project_path = project_path or Path.cwd()

    def detect_all(self) -> list[AdapterStatus]:
        """Return status for all known adapters."""
        return [adapter_cls().status(self.project_path) for adapter_cls in ADAPTERS]

    def detect_installed(self) -> list[AdapterStatus]:
        """Return status only for installed platforms."""
        return [s for s in self.detect_all() if s.installed]

    def get_adapter(self, platform: str) -> BaseAdapter | None:
        """Get adapter instance by platform name."""
        for adapter_cls in ADAPTERS:
            if adapter_cls.platform_name == platform:
                return adapter_cls()
        return None

    def get_adapters_for_platforms(self, platforms: list[str]) -> list[BaseAdapter]:
        """Get adapter instances for given platform names."""
        adapters = []
        for name in platforms:
            adapter = self.get_adapter(name)
            if adapter:
                adapters.append(adapter)
        return adapters
