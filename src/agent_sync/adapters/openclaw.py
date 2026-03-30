"""OpenClaw adapter — SOUL.md, IDENTITY.md, USER.md, MEMORY.md."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from agent_sync.adapters.base import AdapterStatus, BaseAdapter, PullResult, SyncResult
from agent_sync.core.schema import UniversalAgent, load_directives, load_skills


class OpenClawAdapter(BaseAdapter):
    platform_name = "openclaw"
    platform_display = "OpenClaw"

    def detect(self, project_path: Path) -> bool:
        return (project_path / "SOUL.md").exists() or (project_path / "AGENTS.md").exists()

    def sync(
        self,
        agent: UniversalAgent,
        project_path: Path,
        *,
        dry_run: bool = False,
    ) -> SyncResult:
        result = SyncResult(platform=self.platform_name, dry_run=dry_run)
        env = self._get_jinja_env()

        # SOUL.md
        soul_content = self._render_soul(env, agent)
        target = project_path / "SOUL.md"
        result.files_written.append(self._write_managed(target, soul_content, dry_run))

        # IDENTITY.md
        identity_content = self._render_identity(env, agent)
        target = project_path / "IDENTITY.md"
        result.files_written.append(self._write_managed(target, identity_content, dry_run))

        # USER.md
        user_content = self._render_user(env, agent)
        target = project_path / "USER.md"
        result.files_written.append(self._write_managed(target, user_content, dry_run))

        # MEMORY.md (warm memory — only write if not exists)
        target = project_path / "MEMORY.md"
        if not target.exists():
            memory_content = self._render_memory(env, agent)
            result.files_written.append(self._write_managed(target, memory_content, dry_run))
        else:
            result.files_skipped.append(target)

        # SKILLS.md (summary of all skills)
        if agent.base_path:
            skills = load_skills(agent.base_path)
            if skills:
                target = project_path / "SKILLS.md"
                skills_content = self._render_skills(skills)
                result.files_written.append(self._write_managed(target, skills_content, dry_run))

        return result

    def pull(self, agent: UniversalAgent, project_path: Path) -> PullResult:
        """OpenClaw is the source of truth for soul/identity/user — pulling is identity-preserving."""
        return PullResult(platform=self.platform_name, fields_updated=[])

    def status(self, project_path: Path) -> AdapterStatus:
        installed = self.detect(project_path)
        return AdapterStatus(
            platform=self.platform_name,
            installed=installed,
            config_path=project_path if installed else None,
        )

    # --- Renderers ---

    def _render_soul(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("SOUL.md.j2")
        directives = load_directives(agent.base_path) if agent.base_path else []
        return tmpl.render(soul=agent.soul, directives=directives)

    def _render_identity(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("IDENTITY.md.j2")
        return tmpl.render(identity=agent.identity)

    def _render_user(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("USER.md.j2")
        return tmpl.render(user=agent.user)

    def _render_memory(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("MEMORY.md.j2")
        return tmpl.render(user=agent.user)

    def _render_skills(self, skills) -> str:
        """Render a skills summary as markdown."""
        lines = ["# Skills Registry", "", f"Total skills: {len(skills)}", ""]
        for s in skills:
            lines.append(f"## {s.name}")
            if s.description:
                lines.append(f"> {s.description}")
            lines.append(f"- Path: `{s.path}`")
            lines.append("")
        return "\n".join(lines)

    # --- Helpers ---

    def _get_jinja_env(self) -> Environment:
        return Environment(
            loader=FileSystemLoader(str(self.get_template_dir())),
            keep_trailing_newline=True,
        )
