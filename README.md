# agent-sync

> One soul, many bodies — sync AI agent identity, memory, and knowledge across platforms.
>
> 一个灵魂，多个身体 — 跨平台同步 AI 助手的身份、记忆和知识。

## Why This Exists / 为什么需要这个

MCP standardized tool calling. AGENTS.md is converging instruction formats. But your agent's **soul, memory, and knowledge** are still siloed per platform. Switch from Claude Code to Cursor, and your agent forgets who it is.

MCP 标准化了工具调用，AGENTS.md 正在统一指令格式。但 Agent 的**灵魂、记忆、知识**，每个平台还是各管各的。从 Claude Code 切到 Cursor，你的 AI 就失忆了。

**agent-sync: define once, sync everywhere. / 定义一次，到处运行。**

---

## Quick Start / 快速开始

### Step 1: Install / 安装

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
agent-sync --version
```

### Step 2: Init / 初始化

```bash
cd ~/my-project
agent-sync init .
```

Creates `universal-agent/` with YAML templates. / 生成目录和模板配置。

### Step 3: Configure / 填配置

**soul.yaml** — AI's personality / AI 的性格：
```yaml
name: assistant
language: zh-CN
personality:
  - Be genuinely helpful, not performatively helpful  # 真诚，不表演有用
  - Have opinions                                      # 有观点
  - Try to figure things out before asking             # 先试再问
boundaries:
  - Private things stay private                        # 私密信息不外泄
  - Ask before acting externally                       # 对外操作先确认
communication:
  style: concise but thorough
  tone: warm and genuine
  do_not:
    - Say "Great question!"      # 不要说"好问题！"
```

**user.yaml** — who you are / 你是谁：
```yaml
name: Your Name
timezone: Asia/Shanghai
github: your-username
preferences:
  - Use pnpm not npm              # 用 pnpm 不要 npm
  - Feature branches only         # 只用 feature 分支
```

**identity.yaml** — AI identity / AI 身份：
```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
```

### Step 4: Sync / 同步

```bash
agent-sync sync --dry-run    # Preview / 先预览
agent-sync sync               # Do it / 正式同步
```

**What gets generated / 生成了什么：**

| Platform | Files |
|----------|-------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` + `directives/*.mdc` |
| Claude Code | `CLAUDE.md` (project) + `~/.claude/CLAUDE.md` (global) |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` + `MEMORY.md` |

---

## Core Concepts / 核心概念

### Three Layers / 三层架构

**1. Identity — who the agent is / 身份**

One source of truth, adapted per platform. / 一个源头，按平台适配。

- **Soul** (`soul.yaml`) — meta-personality / 元人格
- **Identity** (`identity.yaml`) — specific personality / 具体人格
- **User** (`user.yaml`) — who the AI serves / 用户画像

**2. Memory — what the agent knows / 记忆**

| Tier | Auto? | Description |
|------|-------|-------------|
| Hot 热记忆 | ✅ 自动 | Per-conversation observations / 每次对话的观察 |
| Warm 温记忆 | ✅ 自动 | Cross-session profile (~100 lines) / 跨会话画像 |
| Cold 冷记忆 | ⚠️ 需确认 | directives + skills / 长期知识和技能 |

> **Important / 重要：** Hot → Warm is fully automatic. Warm → Cold (distill to directives / discover skills) only happens with your confirmation — nothing gets promoted without you saying yes.
>
> 热→温全自动。温→冷需要你确认 — 没有你的同意，什么都不会被蒸馏。

**3. Directives + Skills / 指令+技能**

| Type | Location | Meaning |
|------|----------|---------|
| Directives 指令 | `directives/` | How to **think** — values, decision preferences / 怎么**思考** |
| Skills 技能 | `skills/` | How to **act** — repeatable procedures, tool workflows / 怎么**做** |

### Directory Structure / 目录结构

```
universal-agent/
├── soul.yaml          # Meta-personality / 元人格
├── identity.yaml      # Specific identity / 具体人格
├── user.yaml          # User profile / 用户画像
├── routing.yaml       # Task routing / 任务路由
├── directives/        # How to think (user-confirmed) / 怎么思考（需确认）
│   └── INDEX.md
├── skills/            # How to act (user-confirmed) / 怎么做（需确认）
│   └── <name>/SKILL.md
└── memory/
    └── core.md        # Warm memory (auto) / 温记忆（自动）
```

---

## Memory System / 记忆系统

### Auto-Collection / 自动采集

agent-sync reads from two sources (configure at least one). / 从两个源采集（至少配一个）。

**Source 1: Claude Code + claude-mem**
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```
Auto-saves to `~/.claude-mem/claude-mem.db`. / 自动保存到 SQLite。

**Source 2: OpenClaw (built-in / 内置，无需插件)**

OpenClaw writes daily memory to `memory/YYYY-MM-DD.md` automatically. agent-sync reads these markdown files. No plugin needed.
OpenClaw 已内置记忆沉淀，每天写 markdown 文件。agent-sync 自动读取，无需插件。

### Memory Pipeline / 记忆管线

```
Hot (auto / 自动)
  claude-mem SQLite + OpenClaw daily/*.md
       ↓ memory consolidate (auto / 自动)
       ↓ classify: insight / procedure / tool_pattern / preference
Warm (auto / 自动)
  memory/core.md (~100 lines)
       ↓ memory distill / skills discover
       ↓ lists candidates → YOU confirm / 列出候选 → 你确认
Cold (user-confirmed / 需要你确认)
  directives/ → how to think / 怎么思考
  skills/    → how to act / 怎么做
```

**Classification / 分类：**

| Category | Meaning | What happens |
|----------|---------|-------------|
| `insight` | Generic observation / 通用观察 | May suggest as directive candidate / 可能推荐蒸馏为指令 |
| `procedure` | Repeatable workflow / 可重复流程 | → Skill candidate / 技能候选 |
| `tool_pattern` | Tool usage pattern / 工具使用模式 | → Skill candidate / 技能候选 |
| `preference` | User habit / 用户偏好 | Stays in warm / 留在温记忆 |

### Air-Gapped / Corporate Network / 离线 & 内网

Works fully offline. No cloud services needed. / 完全离线可用，不依赖云服务。

- **Git**: Internal GitLab CE / Gitea / 内网 Git
- **Knowledge**: Local Obsidian vault / 本地 Obsidian
- **Memory**: OpenClaw source only (markdown files) / 只用 OpenClaw 源
- **No external API calls** / 全程无外部 API

```yaml
# memory.yaml — offline/corporate / 离线/公司模式
sources:
  - type: openclaw
    path: ../memory/
```

Cold knowledge output / 冷知识输出：
- **Corporate / 公司内**: only `directives/` / 只沉淀为指令，不外传
- **Personal / 个人**: can bind Obsidian / 可以绑 Obsidian 做外挂大脑

---

## CLI Reference / CLI 参考

```bash
# Setup / 设置
agent-sync init [path]              # Create structure / 创建目录
agent-sync detect [path]            # Detect platforms / 检测平台
agent-sync status [path]            # Show status / 显示状态

# Sync / 同步
agent-sync sync [path]              # Sync all / 同步所有平台
agent-sync sync -t cursor           # Sync one platform / 只同步一个
agent-sync sync --dry-run           # Preview / 预览

# Memory (auto tier) / 记忆（自动层）
agent-sync memory today             # Recent hot obs / 近期热记忆
agent-sync memory consolidate       # Hot → Warm (auto) / 热→温（自动）

# Memory (confirmation tier) / 记忆（确认层）
agent-sync memory review            # See all layers + candidates / 查看所有层+候选
agent-sync memory distill           # Warm → directives (confirm) / 温→指令（需确认）
agent-sync memory distill --dry-run # Preview candidates / 预览候选
agent-sync skills discover          # Warm → skills (confirm) / 温→技能（需确认）
agent-sync skills discover --confirm # Auto-create scaffolds / 自动创建脚手架

# Memory sync / 记忆同步
agent-sync memory push              # Push to Git / 推到 Git
agent-sync memory pull              # Pull from Git / 从 Git 拉

# Skills / 技能
agent-sync skills scan              # List all skills / 列出技能
agent-sync skills sync              # Sync to platforms / 同步到平台
```

---

## Typical Workflow / 典型工作流

```bash
# Day 1: Setup / 第一天：设置
agent-sync init ~/my-project
# Edit YAML files / 编辑 YAML
agent-sync sync

# Daily (auto) / 每天（自动）
agent-sync memory consolidate       # hot → warm, runs automatically

# Daily (5 min review) / 每天（5分钟回顾）
agent-sync memory review            # see what's new, any candidates?
# If candidates look good: / 如果候选看起来不错：
agent-sync memory distill           # confirm → directives
agent-sync skills discover          # confirm → skills

# After any YAML change / 改了 YAML 后
agent-sync sync
```

---

## Supported Platforms / 支持平台

| Platform | Status | Output / 输出 |
|----------|--------|-------------|
| OpenClaw | ✅ | SOUL.md, IDENTITY.md, USER.md, MEMORY.md, SKILLS.md |
| Claude Code | ✅ | CLAUDE.md (project + global ~/.claude/CLAUDE.md) |
| Codex | ✅ | AGENTS.md |
| Cursor | ✅ | .cursor/rules/*.mdc |
| Windsurf | 🔜 | Planned / 计划中 |
| Copilot | 🔜 | Planned / 计划中 |
| CatPaw | 🔜 | Planned / 计划中 |
| Trae | 🔜 | Planned / 计划中 |

---

## Adding a New Adapter / 添加新平台

Example: adding Trae support / 以 Trae 为例：

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

## Development / 开发

```bash
git clone https://github.com/jasonjcwu/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
pytest
```

## License

MIT
