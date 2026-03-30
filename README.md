# agent-sync

> One soul, many bodies — sync AI agent identity, memory, and knowledge across platforms.

MCP standardized tool calling. AGENTS.md is converging instruction formats. But your agent's **soul, memory, and knowledge** are still siloed per platform. Switch from Claude Code to Cursor, and your agent forgets who it is.

agent-sync fixes this: **define once, sync everywhere.**

## The Problem

Every AI agent platform has its own config format:

| Platform | Identity | Memory | Tools |
|----------|----------|--------|-------|
| OpenClaw | SOUL.md + IDENTITY.md | MEMORY.md | Skills/ |
| Claude Code | CLAUDE.md | Auto Memory | MCP |
| Codex | AGENTS.md | — | MCP |
| Cursor | .cursor/rules/*.mdc | Cascade Memory | MCP |
| Windsurf | .windsurfrules | Cascade Memories | MCP |
| Copilot | copilot-instructions.md | Agentic Memory | MCP |

Same intent, different syntax. Same agent, different personality on each platform.

## Quick Start

```bash
pip install agent-sync
agent-sync init ~/my-project
# Edit the YAML files in universal-agent/
agent-sync sync -a universal-agent/ ~/my-project
```

## Universal Agent Structure

```
universal-agent/
├── soul.yaml          # Meta-personality: boundaries, beliefs, temperament
├── identity.yaml      # Specific identity: name, values, communication style
├── user.yaml          # User profile: who the AI serves, preferences, timezone
├── routing.yaml       # Task routing across platforms
├── memory/
│   ├── core.md        # Warm memory: core profile (~100 lines)
│   └── daily/         # Hot memory: daily observations
├── directives/        # Behavioral principles (indexed by domain)
│   └── INDEX.md
└── skills/            # Skill definitions (SKILL.md format)
```

## Architecture: Three Layers

### 1. Identity — Soul → Identity → User

Identity is layered, not copied. Define once at the source, adapt per platform:

- **Soul** — platform-agnostic meta-personality (boundaries, beliefs, temperament)
- **Identity** — specific personality (name, values, communication style)
- **User** — who the AI serves (shared across all platforms)

Adapters translate: "你不是用户的代言人" in SOUL.md becomes a behavioral constraint in CLAUDE.md, a guardrail in .cursorrules — same meaning, different expression.

### 2. Memory — Hot → Warm → Cold

Three tiers by recency and density:

- **Hot** (per conversation) — auto-collected observations, logs, decisions
- **Warm** (cross-session) — core profile + key preferences + risk alerts, compressed to ~100 lines
- **Cold** (long-term) — Obsidian / Notion / knowledge base articles

Why three tiers? Conversation memory gets lost. File memory grows unbounded. Warm memory exists to **compress core info to a size any platform can load instantly**.

### 3. Directives — Behavioral Principles

Not "who I am" (that's Soul), but "how I think" — personal decision preferences and cognitive沉淀. Organized by domain with a routing index (INDEX.md) for on-demand retrieval.

### Bonus: Skill Discovery

The Reflector automatically identifies repeatable procedures from warm memory:

```
claude-mem observations (hot)
       ↓ Reflector.collect_observations()
Warm memory core.md (auto-classified: insight / procedure / tool_pattern / preference)
       ↓ category = procedure or tool_pattern + seen >= 2x
       ↓ agent-sync skills discover
  List candidates → user confirms → scaffold created in skills/
```

## CLI Reference

```bash
# Setup
agent-sync init [path]              # Create universal-agent/ structure
agent-sync detect [path]            # Detect installed platforms
agent-sync status [path]            # Show sync status

# Sync
agent-sync sync [path]              # Sync to all detected platforms
agent-sync sync -t cursor           # Sync to specific platform
agent-sync sync --dry-run           # Preview without writing

# Memory Pipeline
agent-sync memory today             # Show recent hot observations
agent-sync memory consolidate       # Hot → Warm: promote observations
agent-sync memory distill           # Warm → Cold: distill to directives
agent-sync memory review            # Interactive: show all layers + skill candidates
agent-sync memory push              # Push memory to Git
agent-sync memory pull              # Pull latest from Git

# Skills
agent-sync skills scan              # List all skills in skills/
agent-sync skills discover          # Find skill candidates from warm memory
agent-sync skills discover --confirm  # Create skill scaffolds (with confirmation)
agent-sync skills sync              # Sync skills to all platforms
```

## Supported Platforms

| Platform | Status | Output |
|----------|--------|--------|
| OpenClaw | ✅ | SOUL.md, IDENTITY.md, USER.md, MEMORY.md, SKILLS.md |
| Claude Code | ✅ | CLAUDE.md (project + global ~/.claude/CLAUDE.md) |
| Codex | ✅ | AGENTS.md |
| Cursor | ✅ | .cursor/rules/*.mdc (soul, identity, user, directives, skills) |
| Windsurf | 🔜 | Planned |
| Copilot | 🔜 | Planned |

### Cursor Adapter Details

The Cursor adapter generates `.cursor/rules/*.mdc` files with proper frontmatter:

- `soul.mdc` — alwaysApply: true (personality + boundaries)
- `identity.mdc` — alwaysApply: true (name + values + traits)
- `user.mdc` — alwaysApply: true (user context + preferences)
- `directives/*.mdc` — alwaysApply: false (loaded on demand)
- `skills.mdc` — alwaysApply: false (skill registry)

## Memory Pipeline

```
Observer (L1)         Reflector (L2)              Writer (L3)
Auto-collect          Classify + Promote           Output
─────────────         ──────────────────           ──────

claude-mem SQLite  →  _classify_entry()  →         directives/
OpenClaw daily/    →  reflect()          →         skills/
                   →  promote()          →         memory/core.md
                   →  gc()               →
                   →  distill()          →
                   →  discover_skill_candidates() →
```

**Classification categories:**
- `insight` — generic observations and learnings
- `procedure` — repeatable workflows and processes → skill candidates
- `tool_pattern` — tool/technology usage patterns → skill candidates
- `preference` — user preferences and habits

**Promotion gates** (hot → warm): cross-project + multi-verified + clear scenario
**Distillation** (warm → cold): confidence >= 2.0, occurrences >= 2, meaningful content
**GC rule**: remove entries older than 30 days with no active references

## Development

```bash
git clone https://github.com/jasonjcwu/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
pytest
```

## License

MIT
