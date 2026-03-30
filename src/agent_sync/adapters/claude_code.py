"""Claude Code adapter — CLAUDE.md."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from agent_sync.adapters.base import AdapterStatus, BaseAdapter, PullResult, SyncResult
from agent_sync.core.schema import UniversalAgent, load_directives

GLOBAL_CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
PROJECT_CLAUDE_MD = "CLAUDE.md"


class ClaudeCodeAdapter(BaseAdapter):
    platform_name = "claude_code"
    platform_display = "Claude Code"

    def detect(self, project_path: Path) -> bool:
        return (
            (project_path / PROJECT_CLAUDE_MD).exists()
            or (project_path / ".claude" / "settings.json").exists()
            or GLOBAL_CLAUDE_MD.exists()
        )

    def sync(
        self,
        agent: UniversalAgent,
        project_path: Path,
        *,
        dry_run: bool = False,
    ) -> SyncResult:
        result = SyncResult(platform=self.platform_name, dry_run=dry_run)
        env = self._get_jinja_env()

        # Project-level CLAUDE.md
        content = self._render_claude_md(env, agent)
        target = project_path / PROJECT_CLAUDE_MD
        result.files_written.append(self._write(target, content, dry_run))

        # Global ~/.claude/CLAUDE.md (user preferences)
        global_content = self._render_global_claude_md(env, agent)
        result.files_written.append(self._write(GLOBAL_CLAUDE_MD, global_content, dry_run))

        return result

    def pull(self, agent: UniversalAgent, project_path: Path) -> PullResult:
        """Read existing CLAUDE.md back into universal fields."""
        result = PullResult(platform=self.platform_name)
        claude_md = project_path / PROJECT_CLAUDE_MD
        if claude_md.exists():
            # TODO: parse CLAUDE.md back to extract preferences
            result.fields_updated = ["claudemd_read"]
        return result

    def status(self, project_path: Path) -> AdapterStatus:
        has_project = (project_path / PROJECT_CLAUDE_MD).exists()
        has_global = GLOBAL_CLAUDE_MD.exists()
        return AdapterStatus(
            platform=self.platform_name,
            installed=has_project or has_global,
            config_path=(project_path / PROJECT_CLAUDE_MD) if has_project else GLOBAL_CLAUDE_MD if has_global else None,
        )

    def _render_claude_md(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("CLAUDE.md.j2")
        directives = load_directives(agent.base_path) if agent.base_path else []
        return tmpl.render(agent=agent, directives=directives)

    def _render_global_claude_md(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("CLAUDE.global.md.j2")
        directives = load_directives(agent.base_path) if agent.base_path else []
        return tmpl.render(agent=agent, directives=directives)

    def _get_jinja_env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(str(self.get_template_dir())),
            keep_trailing_newline=True,
        )

    @staticmethod
    def _write(path: Path, content: str, dry_run: bool) -> Path:
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return path
