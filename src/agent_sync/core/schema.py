"""Universal data models for agent identity, memory, and directives."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


# --- Identity Layer ---


class CommunicationStyle(BaseModel):
    style: str = ""
    tone: str = ""
    do_not: list[str] = Field(default_factory=list)


class Soul(BaseModel):
    """Meta-personality: behavioral boundaries, core beliefs, temperament.
    Platform-agnostic. Applies to all AI agents."""

    name: str = "assistant"
    language: str = "en"
    personality: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    communication: CommunicationStyle = Field(default_factory=lambda: CommunicationStyle())


class ValueRef(BaseModel):
    name: str
    principles: list[str] = Field(default_factory=list)
    icon: str = ""


class Identity(BaseModel):
    """Specific personality: name, communication style, values.
    Can be tweaked per platform, core stays the same."""

    name: str = ""
    emoji: str = ""
    values: list[ValueRef] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)
    development_goals: dict[str, list[str]] = Field(default_factory=dict)


class User(BaseModel):
    """User profile: who the AI serves, preferences, timezone.
    Shared across all platforms."""

    name: str = ""
    timezone: str = "UTC"
    github: str = ""
    occupation: str = ""
    interests: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)


# --- Directives Layer ---


class DirectiveEntry(BaseModel):
    """A single directive in the INDEX."""

    id: str
    title: str
    summary: str
    domain: str = ""
    file: str = ""
    keywords: list[str] = Field(default_factory=list)


class DirectiveIndex(BaseModel):
    """Routing index for directives."""

    directives: list[DirectiveEntry] = Field(default_factory=list)
    keyword_map: dict[str, list[str]] = Field(default_factory=dict)


# --- Routing Layer ---


class PlatformConfig(BaseModel):
    type: str = ""
    strengths: list[str] = Field(default_factory=list)


class Routing(BaseModel):
    platforms: dict[str, PlatformConfig] = Field(default_factory=dict)
    defaults: dict[str, str] = Field(default_factory=dict)
    knowledge: dict[str, str] = Field(default_factory=dict)


# --- Aggregate ---


class UniversalAgent(BaseModel):
    """The complete universal agent configuration."""

    soul: Soul = Field(default_factory=Soul)
    identity: Identity = Field(default_factory=Identity)
    user: User = Field(default_factory=User)
    routing: Routing = Field(default_factory=Routing)
    directives: DirectiveIndex = Field(default_factory=DirectiveIndex)

    # Paths (not serialized)
    base_path: Optional[Path] = None

    model_config = {"arbitrary_types_allowed": True}


# --- File Loading ---


class DirectiveFile(BaseModel):
    """A loaded directive .md file from the directives/ directory."""
    filename: str
    content: str


class SkillEntry(BaseModel):
    """A loaded skill from the skills/ directory."""
    name: str
    path: str
    description: str = ""
    content: str = ""


def load_directives(agent_path: Path) -> list[DirectiveFile]:
    """Recursively scan directives/ directory and load all .md files."""
    directives_dir = agent_path / "directives"
    if not directives_dir.is_dir():
        return []

    entries: list[DirectiveFile] = []
    for md_file in sorted(directives_dir.rglob("*.md")):
        rel = md_file.relative_to(directives_dir)
        entries.append(DirectiveFile(
            filename=str(rel),
            content=md_file.read_text(),
        ))
    return entries


def load_skills(agent_path: Path) -> list[SkillEntry]:
    """Recursively scan skills/ directory and load all SKILL.md files."""
    skills_dir = agent_path / "skills"
    if not skills_dir.is_dir():
        return []

    entries: list[SkillEntry] = []
    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        rel = skill_file.relative_to(skills_dir)
        skill_name = str(rel.parent) if str(rel.parent) != "." else rel.stem
        content = skill_file.read_text()

        # Extract description from first non-empty, non-heading line
        description = ""
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                description = stripped[:120]
                break

        entries.append(SkillEntry(
            name=skill_name,
            path=str(rel),
            description=description,
            content=content,
        ))
    return entries


# --- I/O ---


def load_universal_agent(path: Path) -> UniversalAgent:
    """Load a universal-agent directory into a UniversalAgent model."""

    base = Path(path)
    if not base.is_dir():
        raise FileNotFoundError(f"Universal agent directory not found: {base}")

    soul_data = _load_yaml(base / "soul.yaml")
    identity_data = _load_yaml(base / "identity.yaml")
    user_data = _load_yaml(base / "user.yaml")
    routing_data = _load_yaml(base / "routing.yaml")

    ua = UniversalAgent(
        soul=Soul(**soul_data) if soul_data else Soul(),
        identity=Identity(**identity_data) if identity_data else Identity(),
        user=User(**user_data) if user_data else User(),
        routing=Routing(**routing_data) if routing_data else Routing(),
        base_path=base,
    )

    return ua


def _load_yaml(path: Path) -> dict | None:
    """Load a YAML file, return None if it doesn't exist."""
    if not path.exists():
        return None
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else None
