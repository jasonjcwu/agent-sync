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
```

Verify / 验证：
```bash
agent-sync --version
```

### Step 2: Initialize / 初始化

```bash
cd ~/my-project
agent-sync init .
```

This creates `universal-agent/` with template configs. / 生成 `universal-agent/` 目录和模板配置。

### Step 3: Edit Configs / 编辑配置

Edit the YAML files (see [Configuration](#configuration--配置) below). / 编辑 YAML 文件（见下方配置说明）。

### Step 4: Sync / 同步

```bash
# Preview first / 先预览
agent-sync sync --dry-run

# Sync to all detected platforms / 同步到所有检测到的平台
agent-sync sync
```

### Step 5: Daily Use / 日常使用

```bash
agent-sync memory review     # Review what agent learned / 查看 AI 学到了什么
agent-sync sync              # Re-sync after config changes / 改了配置后重新同步
```

---

## Core Concepts / 核心概念

### Three Layers / 三层架构

**1. Identity — who the agent is / 身份 — AI 是谁**

Layered, not copied. One source of truth, adapted per platform.
分层定义，不是复制。一个源头，按平台适配。

- **Soul** (`soul.yaml`) — platform-agnostic meta-personality / 平台无关的元人格
- **Identity** (`identity.yaml`) — specific personality / 具体人格
- **User** (`user.yaml`) — who the AI serves / 用户画像

**2. Memory — what the agent knows / 记忆 — AI 知道什么**

| Tier | Location | Description |
|------|----------|-------------|
| Hot 热记忆 | claude-mem / OpenClaw logs | Per-conversation observations / 每次对话的观察 |
| Warm 温记忆 | `memory/core.md` | Cross-session profile (~100 lines) / 跨会话画像 |
| Cold 冷记忆 | `directives/` + `skills/` | Long-term knowledge / 长期知识 |

**3. Directives + Skills — how the agent thinks and acts / 指令+技能 — AI 怎么思考和行动**

Two types of long-term knowledge / 两种长期知识：

| Type | Location | Description |
|------|----------|-------------|
| Directives 指令 | `directives/` | How to think — values, decision preferences / 怎么思考 — 价值观、决策偏好 |
| Skills 技能 | `skills/` | How to act — repeatable procedures, tool workflows / 怎么做 — 可复用流程、工具操作 |

Both are organized with index routing (INDEX.md). Agent loads on demand.
两种都按领域组织，带路由索引，按需加载。

### Directory Structure / 目录结构

```
universal-agent/
├── soul.yaml          # Meta-personality / 元人格
├── identity.yaml      # Specific identity / 具体人格
├── user.yaml          # User profile / 用户画像
├── routing.yaml       # Task routing / 任务路由
├── directives/        # Behavioral principles / 行为指令
│   └── INDEX.md
├── skills/            # Skill definitions / 技能定义
│   └── <name>/SKILL.md
└── memory/
    └── core.md        # Warm memory / 温记忆
```

---

## Configuration / 配置

### soul.yaml — Meta-personality / 元人格

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
  style: concise but thorough    # 简洁但彻底
  tone: warm and genuine         # 温暖真诚
  do_not:
    - Say "Great question!"      # 不要说"好问题！"
    - Say "I'd be happy to help!" # 不要说"我很乐意帮忙！"
```

### user.yaml — User profile / 用户画像

```yaml
name: Your Name
timezone: Asia/Shanghai
github: your-username
occupation: developer
interests:
  - AI/ML
  - Open source
preferences:
  - Use pnpm not npm              # 用 pnpm 不要 npm
  - Chinese-English bilingual     # 中英双语
  - Feature branches only         # 只用 feature 分支
```

### identity.yaml — Specific identity / 具体人格

```yaml
name: Assistant
emoji: "🤖"
values:
  - name: craftsmanship
    principles: [do it right, test thoroughly, document well]
traits:
  - Curious
  - Direct
development_goals:
  short_term: [master the codebase]
```

### routing.yaml — Task routing / 任务路由

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
    strengths: [quick coding, real-time completion]
defaults:
  chat: openclaw
  coding: claude_code
  research: codex
  ide: cursor
```

---

## Memory Auto-Collection / 记忆自动采集

agent-sync reads from two memory sources. You need to set up at least one.
agent-sync 从两个源采集记忆。至少配置一个。

### Source 1: Claude Code (claude-mem)

Install the claude-mem plugin in Claude Code:
在 Claude Code 中安装 claude-mem 插件：

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

This auto-saves observations to `~/.claude-mem/claude-mem.db`. agent-sync reads this SQLite database automatically.
自动保存观察到 `~/.claude-mem/claude-mem.db`。agent-sync 自动读取。

> Reference: [claude-mem](https://github.com/thedotmack/claude-mem)

### Source 2: OpenClaw (built-in)

OpenClaw already writes daily memory to `<workspace>/memory/YYYY-MM-DD.md`. No extra plugin needed — just make sure the path is configured:
OpenClaw 已内置记忆沉淀，每天写入 `<workspace>/memory/YYYY-MM-DD.md`。无需额外插件 — 只需确保路径配置正确：

```yaml
# universal-agent/memory.yaml (optional, has defaults / 可选，有默认值)
sources:
  - type: claude-mem
    path: ~/.claude-mem/claude-mem.db
  - type: openclaw
    path: ../memory/    # relative to universal-agent/ / universal-agent/ 同级的 memory/
```

**How OpenClaw auto-collection works / OpenClaw 自动采集原理：**

OpenClaw's AGENTS.md instructs the agent to write daily notes to `memory/YYYY-MM-DD.md`. agent-sync's Reflector reads these markdown files, parses sections by `##` headings, and treats each section as a hot observation. No plugin or API needed — it's just markdown files in a directory.

OpenClaw 的 AGENTS.md 会指示 AI 将每日笔记写入 `memory/YYYY-MM-DD.md`。agent-sync 的 Reflector 读取这些 markdown 文件，按 `##` 标题解析段落，每段作为一个热记忆观察。无需插件或 API — 就是目录里的 markdown 文件。

### Air-Gapped / Corporate Network / 离线 & 内网环境

agent-sync works fully offline. No cloud services required.
agent-sync 完全支持离线使用，不依赖任何云服务。

- **Git sync**: Use internal GitLab CE, Gitea, or any self-hosted Git / 用内网 GitLab CE、Gitea 或任何自建 Git
- **Knowledge base**: Obsidian local vault, no internet needed / Obsidian 本地仓库，不需要联网
- **Memory**: Only OpenClaw source (markdown files), skip claude-mem / 只用 OpenClaw 记忆源（markdown 文件），跳过 claude-mem
- **No external API calls** at any point / 全程无外部 API 调用

Config for air-gapped setup / 离线配置：
```yaml
# memory.yaml — corporate/offline mode / 公司/离线模式
sources:
  - type: openclaw
    path: ../memory/    # local markdown files / 本地 markdown 文件
```

Cold knowledge output / 冷知识输出：
- **Corporate / 公司内**: only `directives/` (stays internal, no Obsidian) / 只沉淀为指令，不外传
- **Personal / 个人**: can bind Obsidian as external brain / 可以绑 Obsidian 做外挂大脑

### Memory Pipeline / 记忆管线

```
Hot (auto-collected / 自动采集)
  claude-mem SQLite + OpenClaw daily/*.md
       ↓ memory consolidate → Reflector.classify()
       ↓ 分类: insight / procedure / tool_pattern / preference
Warm (cross-session / 跨会话)
  memory/core.md (~100 lines)
       ↓ memory distill → confidence >= 2.0, occurrences >= 2
Cold (long-term / 长期)
  directives/ → behavioral principles / 行为公理
  skills/    → repeatable procedures / 可复用技能
       ↓
  Obsidian/Notion → knowledge base (external brain / 外挂大脑)
```

**Classification / 分类：**

| Category | Meaning | Next step |
|----------|---------|-----------|
| `insight` | Generic observation / 通用观察 | May distill to directive / 可能蒸馏为指令 |
| `procedure` | Repeatable workflow / 可重复流程 | → Skill candidate / 技能候选 |
| `tool_pattern` | Tool usage pattern / 工具使用模式 | → Skill candidate / 技能候选 |
| `preference` | User habit / 用户习惯 | Stays in warm / 留在温记忆 |

---

## CLI Reference / CLI 参考

```bash
# Setup / 设置
agent-sync init [path]              # Create universal-agent/ / 创建目录
agent-sync detect [path]            # Detect platforms / 检测平台
agent-sync status [path]            # Show status / 显示状态

# Sync / 同步
agent-sync sync [path]              # Sync all / 同步所有
agent-sync sync -t cursor           # Sync specific / 同步指定平台
agent-sync sync --dry-run           # Preview / 预览

# Memory / 记忆
agent-sync memory today             # Recent hot obs / 近期热记忆
agent-sync memory consolidate       # Hot → Warm / 热→温
agent-sync memory distill           # Warm → Cold / 温→冷
agent-sync memory distill --dry-run # Preview candidates / 预览候选
agent-sync memory review            # Interactive review / 交互式回顾
agent-sync memory push              # Push to Git / 推到 Git
agent-sync memory pull              # Pull from Git / 从 Git 拉

# Skills / 技能
agent-sync skills scan              # List skills / 列出技能
agent-sync skills discover          # Find candidates / 发现候选
agent-sync skills discover --confirm  # Create scaffolds / 创建脚手架
agent-sync skills sync              # Sync to platforms / 同步到平台
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

---

## Adding a New Adapter / 添加新平台适配器

```python
# src/agent_sync/adapters/windsurf.py
from agent_sync.adapters.base import BaseAdapter, SyncResult, PullResult, AdapterStatus

class WindsurfAdapter(BaseAdapter):
    platform_name = "windsurf"
    platform_display = "Windsurf"

    def detect(self, project_path: Path) -> bool:
        return (project_path / ".windsurfrules").exists()

    def sync(self, agent, project_path, *, dry_run=False) -> SyncResult:
        ...  # Read YAML → render template → write files

    def pull(self, agent, project_path) -> PullResult:
        ...  # Read platform config → update universal

    def status(self, project_path) -> AdapterStatus:
        ...
```

Register in `detector.py`:
在 `detector.py` 注册：

```python
from agent_sync.adapters.windsurf import WindsurfAdapter
ADAPTERS = [..., WindsurfAdapter]
```

See `src/agent_sync/adapters/cursor.py` for a complete reference.
完整参考见 `src/agent_sync/adapters/cursor.py`。

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
