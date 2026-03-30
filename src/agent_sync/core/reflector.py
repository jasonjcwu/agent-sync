"""Reflector — hot → warm memory promotion engine.

Read observations from claude-mem SQLite + OpenClaw daily memory files.
Identify patterns and promote to warm memory (core.md).

Promotion gate criteria (from context-infrastructure):
- cross_project: mentioned in 2+ projects
- multi_verified: type appears 2+ times across observations
- clear_scenario: has a concrete use case

GC rule: remove entries older than N days with no active references.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from agent_sync.core.memory_schema import (
    HotObservation,
    MemoryConfig,
    MemorySource,
    WarmEntry,
    WarmMemory,
)

# Type weights for promotion scoring
TYPE_WEIGHTS = {
    "bugfix": 1.5,
    "feature": 1.2,
    "change": 1.0,
    "refactor": 1.0,
    "discovery": 0.8,
}

TRIVIAL_RE = re.compile(
    r"(typo|minor fix|cosmetic|trailing whitespace|formatting)",
    re.IGNORECASE,
)


def _has_clear_scenario(narrative: str) -> bool:
    if not narrative:
        return False
    return not bool(TRIVIAL_RE.search(narrative.lower()))


def _parse_facts(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    try:
        facts = json.loads(f"[{raw}]")
        if isinstance(facts, list):
            return [str(f) for f in facts]
    except (json.JSONDecodeError, ValueError):
        pass
    return [f.strip().strip('"') for f in raw.split(",")]


def _parse_markdown_sections(content: str) -> list[tuple[str, str]]:
    """Parse markdown into (title, body) sections by ## headings."""
    sections: list[tuple[str, str]] = []
    title = ""
    body: list[str] = []
    for line in content.split("\n"):
        if line.startswith("## ") and not line.startswith("### "):
            if title:
                sections.append((title, "\n".join(body).strip()))
            title = line.lstrip("# ").strip()
            body = []
        else:
            body.append(line)
    if title:
        sections.append((title, "\n".join(body).strip()))
    return sections


# --- Warm memory file I/O ---

def load_warm(path: Path) -> WarmMemory:
    """Load warm memory from core.md file."""
    if not path.exists():
        return WarmMemory(path=path)
    content = path.read_text()
    entries: list[WarmEntry] = []
    in_entry = False
    lines_buf: list[str] = []
    for line in content.split("\n"):
        if line.startswith("## "):
            if in_entry and lines_buf:
                e = _parse_entry(lines_buf)
                if e:
                    entries.append(e)
            lines_buf = [line]
            in_entry = True
        elif in_entry:
            lines_buf.append(line)
    if in_entry and lines_buf:
        e = _parse_entry(lines_buf)
        if e:
            entries.append(e)
    return WarmMemory(
        last_updated=datetime.now().date().isoformat(),
        entries=entries,
        path=path,
    )


def _parse_entry(lines: list[str]) -> Optional[WarmEntry]:
    title = ""
    content_parts: list[str] = []
    meta: dict[str, str] = {}
    for line in lines:
        if line.startswith("## "):
            title = line.lstrip("# ").strip()
        elif line.startswith("- ") and ":" in line:
            kv = line.lstrip("- ").strip()
            k, _, v = kv.partition(": ")
            meta[k.strip()] = v.strip()
        else:
            content_parts.append(line)
    return WarmEntry(
        category=meta.get("category", "insight"),
        title=title,
        content="\n".join(content_parts).strip(),
        confidence=float(meta.get("confidence", "0.5")),
        origin_date=meta.get("origin_date", ""),
        source=meta.get("source", ""),
        occurrences=int(meta.get("occurrences", "1")),
    )


def write_warm(path: Path, warm: WarmMemory) -> None:
    """Write warm memory to markdown file."""
    lines = [
        "# Warm Memory — Core Profile",
        "# Auto-managed by agent-sync reflector.",
        "",
        f"last_updated: {warm.last_updated}",
        f"total_entries: {len(warm.entries)}",
        "",
    ]
    for entry in warm.entries:
        lines.append(f"## {entry.title}")
        lines.append(f"- category: {entry.category}")
        lines.append(f"- confidence: {entry.confidence:.2f}")
        if entry.origin_date:
            lines.append(f"- origin_date: {entry.origin_date}")
        if entry.source:
            lines.append(f"- source: {entry.source}")
        lines.append(f"- occurrences: {entry.occurrences}")
        lines.append("")
        if entry.content:
            lines.append(entry.content)
        lines.append("---")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


# --- Reflector ---

class Reflector:
    """Promote hot observations to warm memory."""

    def __init__(self, config: Optional[MemoryConfig] = None, agent_path: Optional[Path] = None):
        """Initialize reflector with optional config and agent workspace path.

        If no config provided, uses defaults:
        - claude-mem: ~/.claude-mem/claude-mem.db
        - openclaw: <agent_path>/../memory/  (relative to universal-agent/)
        """
        if config is not None:
            self.config = config
        elif agent_path is not None:
            from agent_sync.core.memory_schema import load_memory_config
            self.config = load_memory_config(agent_path)
        else:
            self.config = MemoryConfig(
                sources=[
                    MemorySource(type="claude-mem", path="~/.claude-mem/claude-mem.db"),
                ],
            )

    def collect_observations(self, days: int = 7) -> list[HotObservation]:
        """Collect from all sources."""
        observations: list[HotObservation] = []
        for src in self.config.sources:
            if src.type == "claude-mem":
                observations.extend(self._read_claude_mem(days, src))
            elif src.type == "openclaw":
                observations.extend(self._read_openclaw(days, src))
        # Deduplicate
        seen: set[str] = set()
        unique: list[HotObservation] = []
        for obs in observations:
            key = f"{obs.date}:{obs.title}"
            if key not in seen:
                seen.add(key)
                unique.append(obs)
        return sorted(unique, key=lambda x: x.created_at_epoch, reverse=True)

    def reflect(self, observations: list[HotObservation], threshold: float = 1.5) -> list[WarmEntry]:
        """Score and filter observations for promotion."""
        if not observations:
            return []
        # Count per title
        title_counts: dict[str, int] = {}
        for obs in observations:
            norm = obs.title.strip().lower()
            title_counts[norm] = title_counts.get(norm, 0) + 1
        # Count distinct projects
        projects: set[str] = set()
        for obs in observations:
            if obs.project:
                projects.add(obs.project.split("/")[0] if "/" in obs.project else obs.project)
        cross_project = len(projects) >= 2

        candidates: list[WarmEntry] = []
        for obs in observations:
            norm = obs.title.strip().lower()
            occurrences = title_counts.get(norm, 1)
            score = TYPE_WEIGHTS.get(obs.type, 0.8)
            if cross_project:
                score += 0.8
            if occurrences >= 2:
                score += 0.6
            if _has_clear_scenario(obs.narrative):
                score += 0.5
            if score >= threshold:
                candidates.append(WarmEntry(
                    category="insight",
                    title=obs.title,
                    content=obs.narrative or "\n".join(obs.facts),
                    confidence=round(score, 2),
                    origin_date=obs.date,
                    source=obs.source,
                    occurrences=occurrences,
                ))
        return sorted(candidates, key=lambda x: (-x.confidence, x.title))

    def promote(self, entries: list[WarmEntry], warm_path: Path) -> WarmMemory:
        """Merge promoted entries into warm memory."""
        warm = load_warm(warm_path)
        existing_titles = {e.title for e in warm.entries}
        added = [e for e in entries if e.title not in existing_titles]
        warm.entries.extend(added)
        if added:
            warm.last_updated = datetime.now().date().isoformat()
            write_warm(warm_path, warm)
        return warm

    def gc(self, warm_path: Path, max_age_days: int = 30) -> int:
        """Remove entries older than max_age_days."""
        warm = load_warm(warm_path)
        if not warm.entries:
            return 0
        cutoff = (datetime.now() - timedelta(days=max_age_days)).date().isoformat()
        surviving = [e for e in warm.entries if not (e.origin_date and e.origin_date < cutoff)]
        removed = len(warm.entries) - len(surviving)
        warm.entries = surviving
        if removed:
            warm.last_updated = datetime.now().date().isoformat()
            write_warm(warm_path, warm)
        return removed

    # --- Source readers ---

    def _read_claude_mem(self, days: int, source: MemorySource) -> list[HotObservation]:
        db_path = Path(source.path).expanduser()
        if not db_path.exists():
            return []
        cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
        conn = sqlite3.connect(str(db_path))
        try:
            # Detect available columns in observations table
            col_cur = conn.execute("PRAGMA table_info(observations)")
            available = {row[1] for row in col_cur.fetchall()}

            # Build query dynamically based on actual schema
            select_cols = []
            col_map = {
                "id": "id",
                "title": "title",
                "type": "type",
                "project": "project",
                "narrative": "narrative",
                "facts": "facts",
                "created_at": "created_at",
                "created_at_epoch": "created_at_epoch",
                "session_id": "session_id",
            }
            for alias, col in col_map.items():
                if col in available:
                    select_cols.append(col)

            if not select_cols:
                return []

            cols_str = ", ".join(select_cols)
            cur = conn.execute(
                f"SELECT {cols_str} FROM observations WHERE created_at_epoch >= ? "
                f"ORDER BY created_at_epoch DESC",
                (cutoff,),
            )
            results = []
            for row in cur.fetchall():
                row_dict = dict(zip(select_cols, row))
                results.append(HotObservation(
                    id=row_dict.get("id", 0),
                    title=row_dict.get("title") or "",
                    type=row_dict.get("type") or "discovery",
                    project=row_dict.get("project") or "",
                    narrative=row_dict.get("narrative") or "",
                    facts=_parse_facts(row_dict.get("facts")),
                    created_at=row_dict.get("created_at") or "",
                    created_at_epoch=row_dict.get("created_at_epoch") or 0,
                    source="claude-mem",
                    date=(row_dict.get("created_at") or "")[:10],
                    session_id=row_dict.get("session_id") or "",
                ))
        finally:
            conn.close()
        return results

    def _read_openclaw(self, days: int, source: MemorySource) -> list[HotObservation]:
        mem_dir = Path(source.path).expanduser()
        if not mem_dir.is_dir():
            return []
        results: list[HotObservation] = []
        for i in range(days):
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            for fpath in sorted(mem_dir.glob(f"{date_str}*.md")):
                content = fpath.read_text()
                for title, body in _parse_markdown_sections(content):
                    results.append(HotObservation(
                        title=title,
                        type="discovery",
                        source="openclaw",
                        narrative=body,
                        created_at=date_str,
                        created_at_epoch=int(date_str.replace("-", "") + "000000"),
                        project="openclaw",
                        date=date_str,
                    ))
        return results
