# agent-sync

> One soul, many bodies — sync AI agent identity, memory, and knowledge across platforms.

## Why This Exists

MCP standardized tool calling. AGENTS.md is converging instruction formats. But your agent's **soul, memory, and knowledge** are still siloed per platform. Switch from Claude Code to Cursor, and your agent forgets who it is.

**agent-sync fixes this: define once, sync everywhere.**

Every platform does the same thing — tells your AI who it is, how to behave, what you prefer. But with different file names, different formats, different locations. agent-sync gives you one source of truth.

## Quick Start

```bash
# Install
pip install git+https://github.com/jasonjcwu/agent-sync.git

# Initialize in your project
agent-sync init ~/my-project

# Edit the YAML files with your agent's personality
# (see "Configuration" below)

# Sync to all detected platforms
agent-sync sync -a ~/my-project/universal-agent ~/my-project

# Preview changes first
agent-sync sync --dry-run
```

## Core Concepts

### Three Layers

agent-sync manages three independent layers of your agent's identity:

**1. Identity — who the agent is**

Layered, not copied:
- **Soul** (`soul.yaml`) — platform-agnostic meta-personality: boundaries, beliefs, temperament
- **Identity** (`identity.yaml`) — specific personality: name, values, communication style
- **User** (`user.yaml`) — who the AI serves: preferences, timezone, interests

One source of truth. Adapters translate to each platform's format.

**2. Memory — what the agent knows**

Three tiers by recency:
- **Hot** — observations from each conversation (auto-collected from claude-mem, OpenClaw logs)
- **Warm** (`memory/core.md`) — cross-session profile, compressed to ~100 lines
- **Cold** — long-term: directives, skills, knowledge base

**3. Directives — how the agent thinks**

Not "who I am" (that's Soul) but "how I think" — personal decision preferences and principles. Organized by domain in `directives/` with an index for routing.

### Directory Structure

```
universal-agent/
├── soul.yaml          # Meta-personality (all platforms)
├── identity.yaml      # Specific identity (adapts per platform)
├── user.yaml          # User profile (shared everywhere)
├── routing.yaml       # Task routing config
├── directives/        # Behavioral principles
│   └── INDEX.md       # Routing index
├── skills/            # Skill definitions
│   └── <name>/
│       └── SKILL.md
└── memory/
    └── core.md        # Warm memory (cross-session)
```

## Configuration

### soul.yaml — Meta-personality

```yaml
name: assistant
language: zh-CN
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
    - Say "I'd be happy to help!"
```

### identity.yaml — Specific identity

```yaml
name: Assistant
emoji: "🤖"
values:
  - name: craftsmanship
    principles: [do it right, test thoroughly, document well]
    icon: 🔨
traits:
  - Curious
  - Direct
development_goals:
  short_term: [master the codebase, learn user preferences]
```

### user.yaml — User profile

```yaml
name: Your Name
timezone: Asia/Shanghai
github: your-username
occupation: developer
interests:
  - AI/ML
  - Open source
preferences:
  - Use pnpm not npm
  - Chinese-English bilingual analysis
  - Feature branches, never push to main
```

### routing.yaml — Task routing

```yaml
platforms:
  openclaw:
    type: chat-assistant
    strengths: [daily chat, scheduled tasks, messaging]
  claude_code:
    type: coding-agent
    strengths: [complex coding, code review, refactoring]
  codex:
    type: research-agent
    strengths: [deep research, large-scale code generation]
  cursor:
    type: ide-agent
    strengths: [quick coding, real-time completion, UI development]
defaults:
  chat: openclaw
  coding: claude_code
  research: codex
  ide: cursor
```

## CLI Reference

```bash
# Setup
agent-sync init [path]              # Create universal-agent/ structure
agent-sync detect [path]            # Detect installed platforms
agent-sync status [path]            # Show sync status

# Sync
agent-sync sync [path]              # Sync to all detected platforms
agent-sync sync -t cursor           # Sync to specific platform only
agent-sync sync --dry-run           # Preview without writing

# Memory Pipeline
agent-sync memory today             # Show recent hot observations
agent-sync memory consolidate       # Hot → Warm: promote observations
agent-sync memory distill           # Warm → Cold: distill to directives
agent-sync memory distill --dry-run # Preview distillation candidates
agent-sync memory review            # Interactive: show all layers + skill candidates
agent-sync memory push              # Push memory to Git
agent-sync memory pull              # Pull latest from Git

# Skills
agent-sync skills scan              # List all skills in skills/
agent-sync skills discover          # Find skill candidates from warm memory
agent-sync skills discover --confirm  # Create skill scaffolds (needs confirmation)
agent-sync skills sync              # Sync skills summary to all platforms
```

## Memory Pipeline

```
Hot Memory (per conversation)
  claude-mem SQLite + OpenClaw daily logs
       ↓ agent-sync memory consolidate
       ↓ Reflector.collect_observations()
       ↓ _classify_entry() → insight / procedure / tool_pattern / preference
Warm Memory (cross-session)
  memory/core.md (~100 lines, compressed)
       ↓ agent-sync memory distill
       ↓ Reflector.distill_candidates() (confidence >= 2.0, occurrences >= 2)
Cold Memory (long-term)
  directives/   → behavioral principles
  skills/       → repeatable procedures
       ↓
  Obsidian/Notion → knowledge base (external brain)
```

**Classification** — every warm entry gets auto-classified:

| Category | Meaning | What happens next |
|----------|---------|-------------------|
| `insight` | Generic observation | May distill to directive |
| `procedure` | Repeatable workflow | → Skill candidate |
| `tool_pattern` | Tool usage pattern | → Skill candidate |
| `preference` | User habit/preference | Stays in warm memory |

**Skill discovery** — `procedure` and `tool_pattern` entries seen 2+ times become skill candidates. `agent-sync skills discover` lists them, `--confirm` creates scaffolds.

## Supported Platforms

| Platform | Status | Output Files |
|----------|--------|-------------|
| OpenClaw | ✅ | SOUL.md, IDENTITY.md, USER.md, MEMORY.md, SKILLS.md |
| Claude Code | ✅ | CLAUDE.md (project + global ~/.claude/CLAUDE.md) |
| Codex | ✅ | AGENTS.md |
| Cursor | ✅ | .cursor/rules/*.mdc |
| Windsurf | 🔜 | Planned |
| Copilot | 🔜 | Planned |

### What Gets Generated

**Cursor** (`.cursor/rules/*.mdc`):
- `soul.mdc` — alwaysApply: true
- `identity.mdc` — alwaysApply: true
- `user.mdc` — alwaysApply: true
- `directives/*.mdc` — alwaysApply: false (on-demand)
- `skills.mdc` — alwaysApply: false (on-demand)

**Claude Code**:
- Project `CLAUDE.md` — personality + directives + preferences
- Global `~/.claude/CLAUDE.md` — user preferences (all projects)

**Codex**:
- `AGENTS.md` — personality + behavioral rules

## Typical Workflow

```bash
# Day 1: Set up
agent-sync init ~/my-project
# Edit soul.yaml, identity.yaml, user.yaml
agent-sync sync -a ~/my-project/universal-agent ~/my-project

# Daily: Review what the agent learned
agent-sync memory today
agent-sync memory consolidate    # promote hot → warm
agent-sync memory review         # see all layers, find skill candidates

# Weekly: Distill long-term knowledge
agent-sync memory distill        # warm → cold (directives)
agent-sync skills discover       # find repeatable patterns → skills

# After changes: Sync
agent-sync sync                  # push updated identity to all platforms
agent-sync memory push           # push memory to Git
```

## Adding a New Adapter

To support a new platform, create a new adapter:

```python
# src/agent_sync/adapters/windsurf.py
from agent_sync.adapters.base import BaseAdapter, SyncResult, PullResult, AdapterStatus

class WindsurfAdapter(BaseAdapter):
    platform_name = "windsurf"
    platform_display = "Windsurf"

    def detect(self, project_path: Path) -> bool:
        return (project_path / ".windsurfrules").exists()

    def sync(self, agent, project_path, *, dry_run=False) -> SyncResult:
        # Read universal config → render → write platform-specific files
        ...

    def pull(self, agent, project_path) -> PullResult:
        # Read platform config → update universal config
        ...

    def status(self, project_path) -> AdapterStatus:
        ...
```

Then register it in `src/agent_sync/core/detector.py`:

```python
from agent_sync.adapters.windsurf import WindsurfAdapter

ADAPTERS = [
    OpenClawAdapter,
    ClaudeCodeAdapter,
    CodexAdapter,
    CursorAdapter,
    WindsurfAdapter,  # add here
]
```

See `src/agent_sync/adapters/cursor.py` for a complete reference implementation.

## Development

```bash
git clone https://github.com/jasonjcwu/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
pytest
```

## License

MIT
