"""Cursor adapter — .cursor/rules/*.mdc files."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from agent_sync.adapters.base import AdapterStatus, BaseAdapter, PullResult, SyncResult
from agent_sync.core.schema import UniversalAgent, load_directives, load_skills

CURSOR_RULES_DIR = ".cursor/rules"


class CursorAdapter(BaseAdapter):
    platform_name = "cursor"
    platform_display = "Cursor"

    def detect(self, project_path: Path) -> bool:
        return (
            (project_path / ".cursorrules").exists()
            or (project_path / CURSOR_RULES_DIR).exists()
            or (project_path / ".cursor").exists()
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
        rules_dir = project_path / CURSOR_RULES_DIR

        # Soul + boundaries → always-apply rule
        soul_content = self._render_soul_mdc(env, agent)
        target = rules_dir / "soul.mdc"
        result.files_written.append(self._write(target, soul_content, dry_run))

        # Identity + communication → always-apply rule
        identity_content = self._render_identity_mdc(env, agent)
        target = rules_dir / "identity.mdc"
        result.files_written.append(self._write(target, identity_content, dry_run))

        # User preferences → always-apply rule
        user_content = self._render_user_mdc(env, agent)
        target = rules_dir / "user.mdc"
        result.files_written.append(self._write(target, user_content, dry_run))

        # Directives → agent-requested rules (loaded on demand)
        directives = load_directives(agent.base_path) if agent.base_path else []
        for d in directives:
            directive_content = self._render_directive_mdc(d)
            safe_name = d.filename.replace("/", "-").replace(".md", ".mdc")
            target = rules_dir / "directives" / safe_name
            result.files_written.append(self._write(target, directive_content, dry_run))

        # Skills summary → agent-requested
        skills = load_skills(agent.base_path) if agent.base_path else []
        if skills:
            skills_content = self._render_skills_mdc(skills)
            target = rules_dir / "skills.mdc"
            result.files_written.append(self._write(target, skills_content, dry_run))

        return result

    def pull(self, agent: UniversalAgent, project_path: Path) -> PullResult:
        result = PullResult(platform=self.platform_name)
        rules_dir = project_path / CURSOR_RULES_DIR
        if rules_dir.exists():
            result.fields_updated = ["cursor_rules_read"]
        return result

    def status(self, project_path: Path) -> AdapterStatus:
        has_rules = (project_path / CURSOR_RULES_DIR).exists()
        has_legacy = (project_path / ".cursorrules").exists()
        return AdapterStatus(
            platform=self.platform_name,
            installed=has_rules or has_legacy,
            config_path=(project_path / CURSOR_RULES_DIR) if has_rules else (project_path / ".cursorrules") if has_legacy else None,
        )

    # --- Renderers ---

    def _render_soul_mdc(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("soul.mdc.j2")
        return tmpl.render(soul=agent.soul)

    def _render_identity_mdc(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("identity.mdc.j2")
        return tmpl.render(identity=agent.identity, soul=agent.soul)

    def _render_user_mdc(self, env: Environment, agent: UniversalAgent) -> str:
        tmpl = env.get_template("user.mdc.j2")
        return tmpl.render(user=agent.user)

    def _render_directive_mdc(self, directive) -> str:
        """Render a directive as a Cursor .mdc rule."""
        lines = [
            "---",
            "description: " + directive.filename.replace(".md", ""),
            "globs: ",
            "alwaysApply: false",
            "---",
            "",
            directive.content,
        ]
        return "\n".join(lines)

    def _render_skills_mdc(self, skills) -> str:
        """Render skills summary as a Cursor .mdc rule."""
        lines = [
            "---",
            "description: Available skills and tools",
            "globs: ",
            "alwaysApply: false",
            "---",
            "",
            "# Skills Registry",
            "",
            f"Total: {len(skills)}",
            "",
        ]
        for s in skills:
            lines.append(f"## {s.name}")
            if s.description:
                lines.append(f"> {s.description}")
            lines.append(f"Path: `{s.path}`")
            lines.append("")
        return "\n".join(lines)

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
