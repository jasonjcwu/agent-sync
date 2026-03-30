# agent-sync Quick Start Guide

> Get a consistent AI assistant across all platforms in 5 minutes.

## What Is This

You taught your AI to use pnpm, write Chinese comments, and use feature branches in Claude Code. Switch to Cursor — it forgets everything.

**Define once, sync everywhere.**

---

## Step 1: Install

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
agent-sync --version
```

## Step 2: Init

```bash
cd ~/my-project
agent-sync init .
```

Creates `universal-agent/` with YAML templates.

## Step 3: Configure

### soul.yaml — AI's personality and boundaries

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
    - Say "I'd be happy to help!"
```

### user.yaml — who you are

```yaml
name: Your Name
timezone: Asia/Shanghai
github: your-username
preferences:
  - Use pnpm not npm
  - Code comments in English
  - Never push to main directly
```

### identity.yaml — AI identity

```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
```

## Step 4: Sync

```bash
agent-sync sync --dry-run    # Preview
agent-sync sync               # Do it
```

**What gets generated:**

| Platform | Files |
|----------|-------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` |
| Claude Code | `CLAUDE.md` + `~/.claude/CLAUDE.md` (global) |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` |

## Step 5: Setup Memory Collection

At least one memory source is needed.

### Option A: Claude Code + claude-mem

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

### Option B: OpenClaw (built-in, no plugin needed)

OpenClaw writes daily memory to `memory/YYYY-MM-DD.md` automatically. agent-sync reads these files directly.

Configure in `memory.yaml`:
```yaml
sources:
  - type: claude-mem
    path: ~/.claude-mem/claude-mem.db
  - type: openclaw
    path: ../memory/
```

## Step 6: Daily Use

```bash
agent-sync memory today          # See what agent learned
agent-sync memory consolidate    # Hot → Warm (auto)
agent-sync memory review         # Review all layers (recommended daily)
agent-sync memory distill        # Distill to directives (confirm)
agent-sync skills discover       # Find skill candidates (confirm)
agent-sync sync                  # Re-sync after config changes
```

---

## Multiple Machines

```bash
git clone <repo> ~/agent-config
agent-sync sync -a ~/agent-config/universal-agent ~/my-project
```

## FAQ

**Q: Will my CLAUDE.md edits be overwritten?**
A: Yes. Edit YAML source files only, not generated ones.

**Q: Sync to Cursor only?**
A: `agent-sync sync -t cursor`

**Q: How to see detected platforms?**
A: `agent-sync detect` or `agent-sync status`

**Q: Does it work offline?**
A: Fully offline. Use internal Git, local Obsidian vault, and openclaw-only memory source. No internet needed.

**Q: What are memory categories?**
A: `insight` = generic observation, `procedure` = repeatable workflow (→ skill candidate), `tool_pattern` = tool usage pattern (→ skill candidate), `preference` = user habit. Only procedure/tool_pattern seen 2+ times become skill candidates.

---

## Full Documentation

- [README.md](../README.md) — Architecture, CLI reference, adapter development
- [Architecture Spec (Chinese)](https://github.com/jasonjcwu/obsidian/blob/main/01_输出/跨平台AI人格与记忆架构设计.md)

## License

MIT
