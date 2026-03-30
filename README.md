# agent-sync

> One soul, many bodies — sync AI agent identity, memory, and knowledge across platforms.

[中文文档](README_CN.md)

## Why This Exists

MCP standardized tool calling. AGENTS.md is converging instruction formats. But your agent's **soul, memory, and knowledge** are still siloed per platform. Switch from Claude Code to Cursor, and your agent forgets who it is.

**agent-sync: define once, sync everywhere.**

---

## Quick Start

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
cd ~/my-project
agent-sync init .
# Edit YAML files in universal-agent/
agent-sync sync --dry-run    # Preview
agent-sync sync               # Sync to all detected platforms
```

### Configuration

**soul.yaml** — AI's personality:
```yaml
name: assistant
language: en
personality:
  - Be genuinely helpful, not performatively helpful
  - Have opinions
  - Try to figure things out before asking
boundaries:
  - Private things stay private
  - Ask before acting externally
communication:
  style: concise but thorough
  tone: warm and genuine
  do_not:
    - Say "Great question!"
```

**user.yaml** — who you are:
```yaml
name: Your Name
timezone: Asia/Shanghai
github: your-username
preferences:
  - Use pnpm not npm
  - Feature branches only
```

**identity.yaml** — AI identity:
```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
```

### What Gets Generated

| Platform | Files |
|----------|-------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` + `directives/*.mdc` |
| Claude Code | `CLAUDE.md` (project) + `~/.claude/CLAUDE.md` (global) |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` + `MEMORY.md` |

---

## Core Concepts

### Three Layers

**1. Identity — who the agent is**

One source of truth, adapted per platform.

- **Soul** (`soul.yaml`) — meta-personality (boundaries, beliefs, temperament)
- **Identity** (`identity.yaml`) — specific personality (name, values, communication style)
- **User** (`user.yaml`) — who the AI serves (preferences, timezone, interests)

**2. Memory — what the agent knows**

| Tier | Auto? | Description |
|------|-------|-------------|
| Hot | ✅ Auto | Per-conversation observations |
| Warm | ✅ Auto | Cross-session profile (~100 lines) |
| Cold | ⚠️ Confirm | directives + skills |

> Hot → Warm is fully automatic. Warm → Cold only happens with **your confirmation** — nothing gets promoted without you saying yes.

**3. Directives + Skills**

| Type | Location | Meaning |
|------|----------|---------|
| Directives | `directives/` | How to **think** — values, decision preferences |
| Skills | `skills/` | How to **act** — repeatable procedures, tool workflows |

### Directory Structure

```
universal-agent/
├── soul.yaml          # Meta-personality
├── identity.yaml      # Specific identity
├── user.yaml          # User profile
├── routing.yaml       # Task routing
├── directives/        # How to think (user-confirmed)
│   └── INDEX.md
├── skills/            # How to act (user-confirmed)
│   └── <name>/SKILL.md
└── memory/
    └── core.md        # Warm memory (auto)
```

---

## Memory System

### Auto-Collection

agent-sync reads from two sources (configure at least one).

**Source 1: Claude Code + claude-mem**
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```
Auto-saves to `~/.claude-mem/claude-mem.db`.

**Source 2: OpenClaw (built-in, no plugin needed)**

OpenClaw writes daily memory to `memory/YYYY-MM-DD.md` automatically. agent-sync reads these markdown files directly.

### Memory Pipeline

```
Hot (auto)
  claude-mem SQLite + OpenClaw daily/*.md
       ↓ memory consolidate (auto)
       ↓ classify: insight / procedure / tool_pattern / preference
Warm (auto)
  memory/core.md (~100 lines)
       ↓ memory distill / skills discover
       ↓ lists candidates → YOU confirm
Cold (user-confirmed)
  directives/ → how to think
  skills/    → how to act
```

**Classification:**

| Category | Meaning | What happens |
|----------|---------|-------------|
| `insight` | Generic observation | May suggest as directive candidate |
| `procedure` | Repeatable workflow | → Skill candidate |
| `tool_pattern` | Tool usage pattern | → Skill candidate |
| `preference` | User habit | Stays in warm memory |

### Air-Gapped / Corporate Network

Works fully offline. No cloud services needed.

- **Git**: Internal GitLab CE / Gitea
- **Knowledge**: Local Obsidian vault
- **Memory**: OpenClaw source only (markdown files)
- **No external API calls**

```yaml
# memory.yaml — offline/corporate mode
sources:
  - type: openclaw
    path: ../memory/
```

Cold knowledge output:
- **Corporate**: only `directives/` (stays internal)
- **Personal**: can bind Obsidian as external brain

---

## CLI Reference

```bash
# Setup
agent-sync init [path]              # Create structure
agent-sync detect [path]            # Detect platforms
agent-sync status [path]            # Show status

# Sync
agent-sync sync [path]              # Sync all platforms
agent-sync sync -t cursor           # Sync one platform
agent-sync sync --dry-run           # Preview

# Memory (auto tier)
agent-sync memory today             # Recent hot observations
agent-sync memory consolidate       # Hot → Warm (auto)

# Memory (confirmation tier)
agent-sync memory review            # See all layers + candidates
agent-sync memory distill           # Warm → directives (confirm)
agent-sync memory distill --dry-run # Preview candidates
agent-sync skills discover          # Warm → skills (confirm)
agent-sync skills discover --confirm # Auto-create scaffolds

# Memory sync
agent-sync memory push              # Push to Git
agent-sync memory pull              # Pull from Git

# Skills
agent-sync skills scan              # List all skills
agent-sync skills sync              # Sync to platforms
```

---

## Typical Workflow

```bash
# Day 1: Setup
agent-sync init ~/my-project
# Edit YAML files
agent-sync sync

# Daily (auto)
agent-sync memory consolidate

# Daily (5 min review)
agent-sync memory review
# If candidates look good:
agent-sync memory distill
agent-sync skills discover

# After any YAML change
agent-sync sync
```

---

## Supported Platforms

| Platform | Status | Output |
|----------|--------|--------|
| OpenClaw | ✅ | SOUL.md, IDENTITY.md, USER.md, MEMORY.md, SKILLS.md |
| Claude Code | ✅ | CLAUDE.md (project + global ~/.claude/CLAUDE.md) |
| Codex | ✅ | AGENTS.md |
| Cursor | ✅ | .cursor/rules/*.mdc |
| Windsurf | 🔜 | Planned |
| Copilot | 🔜 | Planned |
| CatPaw | 🔜 | Planned |
| Trae | 🔜 | Planned |

---

## Adding a New Adapter

Example: adding Trae support:

```python
# src/agent_sync/adapters/trae.py
from agent_sync.adapters.base import BaseAdapter, SyncResult, PullResult, AdapterStatus

class TraeAdapter(BaseAdapter):
    platform_name = "trae"
    platform_display = "Trae"

    def detect(self, project_path: Path) -> bool:
        return (project_path / ".trae").exists()

    def sync(self, agent, project_path, *, dry_run=False) -> SyncResult:
        ...  # Read YAML → render template → write files

    def pull(self, agent, project_path) -> PullResult:
        ...  # Read platform config → update universal

    def status(self, project_path) -> AdapterStatus:
        ...
```

Register in `detector.py`: `ADAPTERS = [..., TraeAdapter]`

See `src/agent_sync/adapters/cursor.py` for a complete reference.

---

## Development

```bash
git clone https://github.com/jasonjcwu/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
pytest
```

## License

MIT
