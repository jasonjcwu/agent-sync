"""Codex adapter — AGENTS.md."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from agent_sync.adapters.base import AdapterStatus, BaseAdapter, PullResult, SyncResult
from agent_sync.core.schema import UniversalAgent

AGENTS_MD = "AGENTS.md"


class CodexAdapter(BaseAdapter):
    platform_name = "codex"
    platform_display = "OpenAI Codex"

    def detect(self, project_path: Path) -> bool:
        return (project_path / AGENTS_MD).exists() or (project_path / ".codex").exists()

    def sync(
        self,
        agent: UniversalAgent,
        project_path: Path,
        *,
        dry_run: bool = False,
    ) -> SyncResult:
        result = SyncResult(platform=self.platform_name, dry_run=dry_run)
        env = self._get_jinja_env()

        content = self._render_agents_md(env, agent)
        target = project_path / AGENTS_MD
        result.files_written.append(self._write_managed(target, content, dry_run))

        return result

    def pull(self, agent: UniversalAgent, project_path: Path) -> PullResult:
        result = PullResult(platform=self.platform_name)
        agents_md = project_path / AGENTS_MD
        if agents_md.exists():
            result.fields_updated = ["agents_md_read"]
        return result

    def status(self, project_path: Path) -> AdapterStatus:
        exists = (project_path / AGENTS_MD).exists()
        return AdapterStatus(
            platform=self.platform_name,
            installed=exists,
            config_path=(project_path / AGENTS_MD) if exists else None,
        )

    def _render_agents_md(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("AGENTS.md.j2")
        return tmpl.render(agent=agent)

    def _get_jinja_env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(str(self.get_template_dir())),
            keep_trailing_newline=True,
        )
