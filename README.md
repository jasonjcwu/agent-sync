# agent-sync

> One soul, many bodies — sync AI agent identity, memory, and knowledge across platforms.

## The Problem

Every AI agent platform has its own config format:

| Platform | Config File |
|----------|-------------|
| OpenClaw | SOUL.md, IDENTITY.md, USER.md |
| Claude Code | CLAUDE.md |
| Codex | AGENTS.md |
| Cursor | .cursor/rules/*.mdc |
| Windsurf | .windsurf/rules/*.md |
| Copilot | .github/copilot-instructions.md |

Same intent, different syntax. Switch tools and your agent forgets who it is.

## The Solution

Define your agent's identity once in `universal-agent/`, then sync everywhere:

```bash
agent-sync init
agent-sync sync
```

## Quick Start

```bash
pip install agent-sync
agent-sync init ~/my-project
# Edit universal-agent/soul.yaml with your agent's personality
agent-sync sync -a universal-agent/ ~/my-project
```

## Universal Agent Structure

```
universal-agent/
├── soul.yaml        # Meta-personality: boundaries, beliefs, temperament
├── identity.yaml    # Specific identity: name, values, traits
├── user.yaml        # User profile: who the AI serves
├── routing.yaml     # Task routing across platforms
└── directives/      # Behavioral directives (indexed)
    └── INDEX.md
```

## CLI Commands

```bash
agent-sync init [path]          # Create universal-agent/ structure
agent-sync detect [path]        # Detect installed platforms
agent-sync sync [path]          # Sync to all platforms
agent-sync status [path]        # Show sync status
agent-sync sync --dry-run       # Preview without writing
agent-sync sync -t codex        # Sync to specific platform
```

## Architecture

Three layers:

1. **Identity** — Soul → Identity → User (platform-agnostic to platform-specific)
2. **Memory** — Hot (observations) → Warm (core.md) → Cold (knowledge base)
3. **Directives** — Behavioral principles organized by domain with index routing

Each platform has an **adapter** that translates the universal format into native config.

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| OpenClaw | ✅ | Full support (SOUL + IDENTITY + USER + MEMORY) |
| Claude Code | ✅ | CLAUDE.md (project + global) |
| Codex | ✅ | AGENTS.md |
| Cursor | 🔜 | Planned |
| Windsurf | 🔜 | Planned |
| Copilot | 🔜 | Planned |

## License

MIT
