"""Memory data models — hot, warm, cold layers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class MemorySource(BaseModel):
    """A hot memory source."""
    type: str = "claude-mem"
    path: str = ""


class PromotionGate(BaseModel):
    """Criteria for promoting hot → warm."""
    threshold: float = 1.5
    cross_project_weight: float = 0.8
    multi_occurrence_weight: float = 0.6
    clear_scenario_weight: float = 0.5


class MemoryConfig(BaseModel):
    """Configuration for the memory pipeline."""
    memory_path: str = "memory"
    sources: list[MemorySource] = Field(default_factory=list)
    gate: PromotionGate = Field(default_factory=PromotionGate)


class HotObservation(BaseModel):
    """A single observation from hot memory."""
    id: int = 0
    title: str = ""
    type: str = "discovery"
    project: str = ""
    narrative: str = ""
    facts: list[str] = Field(default_factory=list)
    created_at: str = ""
    created_at_epoch: int = 0
    source: str = ""
    date: str = ""
    session_id: str = ""


class WarmEntry(BaseModel):
    """A promoted entry in warm memory."""
    category: str = "insight"
    title: str = ""
    content: str = ""
    confidence: float = 0.0
    origin_date: str = ""
    source: str = ""
    occurrences: int = 1


class WarmMemory(BaseModel):
    """The warm memory store."""
    last_updated: str = ""
    gc_count: int = 0
    entries: list[WarmEntry] = Field(default_factory=list)
    path: Optional[Path] = None


def load_memory_config(agent_path: Path) -> MemoryConfig:
    """Load memory config from universal-agent/memory.yaml."""
    config_path = agent_path / "memory.yaml"
    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data, dict):
            return MemoryConfig(**data)
    return MemoryConfig(
        sources=[
            MemorySource(type="claude-mem", path="~/.claude-mem/claude-mem.db"),
            MemorySource(type="openclaw", path="~/Desktop/jasonbot/memory"),
        ],
    )
