"""Tests for agent-sync schema loading."""

import tempfile
from pathlib import Path

import yaml
import pytest

from agent_sync.core.schema import Soul, UniversalAgent, load_universal_agent


def _write_yaml(path: Path, data: dict):
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))


def test_soul_defaults():
    soul = Soul()
    assert soul.name == "assistant"
    assert soul.language == "en"


def test_load_universal_agent():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        _write_yaml(base / "soul.yaml", {
            "name": "test-agent",
            "language": "zh-CN",
            "personality": ["be helpful"],
            "boundaries": ["stay safe"],
            "communication": {"style": "concise", "tone": "warm"},
        })
        _write_yaml(base / "identity.yaml", {"name": "Test", "emoji": "T"})
        _write_yaml(base / "user.yaml", {"name": "Alice", "timezone": "UTC"})

        agent = load_universal_agent(base)
        assert agent.soul.name == "test-agent"
        assert agent.soul.language == "zh-CN"
        assert agent.identity.name == "Test"
        assert agent.user.name == "Alice"


def test_load_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_universal_agent(Path("/nonexistent/path"))


def test_load_partial_config():
    """Should work with only soul.yaml."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        _write_yaml(base / "soul.yaml", {"name": "minimal"})

        agent = load_universal_agent(base)
        assert agent.soul.name == "minimal"
        assert agent.user.name == ""  # defaults
