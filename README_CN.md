# agent-sync

> 一个灵魂，多个身体 — 跨平台同步 AI 助手的身份、记忆和知识。

[English](README.md)

## 为什么需要这个

MCP 标准化了工具调用，AGENTS.md 正在统一指令格式。但 Agent 的**灵魂、记忆、知识**，每个平台还是各管各的。从 Claude Code 切到 Cursor，你的 AI 就失忆了。

**agent-sync：定义一次，到处运行。**

---

## 快速开始

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
cd ~/my-project
agent-sync init .
# 编辑 universal-agent/ 里的 YAML 文件
agent-sync sync --dry-run    # 先预览
agent-sync sync               # 正式同步到所有检测到的平台
```

### 配置文件

**soul.yaml** — AI 的性格和底线：
```yaml
name: assistant
language: zh-CN
personality:
  - 真诚，不表演有用
  - 有自己的观点，不当应声虫
  - 遇到问题先自己想办法
boundaries:
  - 私密信息不外泄
  - 对外操作先问确认
communication:
  style: 简洁但彻底
  tone: 温暖真诚
  do_not:
    - 说"好问题！"
    - 说"我很乐意帮忙！"
```

**user.yaml** — 你是谁：
```yaml
name: 你的名字
timezone: Asia/Shanghai
github: your-username
preferences:
  - 用 pnpm 不要 npm
  - 永远不要直接 push 到 main
```

**identity.yaml** — AI 身份：
```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
```

### 同步生成什么

| 平台 | 文件 |
|------|------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` + `directives/*.mdc` |
| Claude Code | `CLAUDE.md`（项目级）+ `~/.claude/CLAUDE.md`（全局） |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` + `MEMORY.md` |

---

## 核心概念

### 三层架构

**1. 身份 — AI 是谁**

一个源头定义，按平台适配。

- **Soul** (`soul.yaml`) — 元人格：行为边界、核心信条
- **Identity** (`identity.yaml`) — 具体人格：名字、价值观、沟通风格
- **User** (`user.yaml`) — 用户画像：偏好、时区、兴趣

**2. 记忆 — AI 知道什么**

| 层级 | 自动？ | 说明 |
|------|--------|------|
| 热记忆 | ✅ 自动 | 每次对话的观察 |
| 温记忆 | ✅ 自动 | 跨会话画像（~100行） |
| 冷记忆 | ⚠️ 需确认 | 指令 + 技能 |

> 热→温全自动。温→冷需要**你确认** — 没有你的同意，什么都不会被蒸馏。

**3. 指令 + 技能**

| 类型 | 位置 | 含义 |
|------|------|------|
| 指令 | `directives/` | 怎么**思考** — 价值观、决策偏好 |
| 技能 | `skills/` | 怎么**做** — 可复用流程、工具操作 |

### 目录结构

```
universal-agent/
├── soul.yaml          # 元人格
├── identity.yaml      # 具体人格
├── user.yaml          # 用户画像
├── routing.yaml       # 任务路由
├── directives/        # 怎么思考（需确认）
│   └── INDEX.md
├── skills/            # 怎么做（需确认）
│   └── <name>/SKILL.md
└── memory/
    └── core.md        # 温记忆（自动）
```

---

## 记忆系统

### 自动采集

agent-sync 从两个源采集记忆（至少配一个）。

**方式一：Claude Code + claude-mem**
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```
自动保存到 `~/.claude-mem/claude-mem.db`。

**方式二：OpenClaw（内置，无需插件）**

OpenClaw 每天自动写 `memory/YYYY-MM-DD.md`。agent-sync 直接读取 markdown 文件。

### 记忆管线

```
热记忆（自动）
  claude-mem SQLite + OpenClaw 日志
       ↓ memory consolidate（自动）
       ↓ 分类: insight / procedure / tool_pattern / preference
温记忆（自动）
  memory/core.md（~100行）
       ↓ memory distill / skills discover
       ↓ 列出候选 → 你确认
冷记忆（需确认）
  directives/ → 怎么思考
  skills/    → 怎么做
```

**分类说明：**

| 分类 | 含义 | 会发生什么 |
|------|------|-----------|
| `insight` | 通用观察 | 可能推荐蒸馏为指令 |
| `procedure` | 可重复流程 | → 技能候选 |
| `tool_pattern` | 工具使用模式 | → 技能候选 |
| `preference` | 用户偏好 | 留在温记忆 |

### 离线 & 内网

完全离线可用，不依赖云服务。

- **Git**：内网 GitLab CE / Gitea
- **知识库**：Obsidian 本地仓库
- **记忆**：只用 OpenClaw 源（markdown 文件）
- **全程无外部 API 调用**

```yaml
# memory.yaml — 离线/公司模式
sources:
  - type: openclaw
    path: ../memory/
```

冷知识输出：
- **公司内**：只沉淀到 `directives/`，不外传
- **个人**：可以绑 Obsidian 做外挂大脑

---

## CLI 参考

```bash
# 设置
agent-sync init [path]              # 创建目录
agent-sync detect [path]            # 检测平台
agent-sync status [path]            # 显示状态

# 同步
agent-sync sync [path]              # 同步所有平台
agent-sync sync -t cursor           # 只同步一个平台
agent-sync sync --dry-run           # 预览

# 记忆（自动层）
agent-sync memory today             # 近期热记忆
agent-sync memory consolidate       # 热→温（自动）

# 记忆（确认层）
agent-sync memory review            # 查看所有层+候选
agent-sync memory distill           # 温→指令（需确认）
agent-sync memory distill --dry-run # 预览候选
agent-sync skills discover          # 温→技能（需确认）
agent-sync skills discover --confirm # 自动创建脚手架

# 记忆同步
agent-sync memory push              # 推到 Git
agent-sync memory pull              # 从 Git 拉

# 技能
agent-sync skills scan              # 列出技能
agent-sync skills sync              # 同步到平台
```

---

## 典型工作流

```bash
# 第一天：设置
agent-sync init ~/my-project
# 编辑 YAML
agent-sync sync

# 每天（自动）
agent-sync memory consolidate

# 每天（5分钟回顾）
agent-sync memory review
# 候选看起来不错的话：
agent-sync memory distill
agent-sync skills discover

# 改了 YAML 后
agent-sync sync
```

---

## 支持平台

| 平台 | 状态 | 输出 |
|------|------|------|
| OpenClaw | ✅ | SOUL.md, IDENTITY.md, USER.md, MEMORY.md, SKILLS.md |
| Claude Code | ✅ | CLAUDE.md（项目+全局 ~/.claude/CLAUDE.md） |
| Codex | ✅ | AGENTS.md |
| Cursor | ✅ | .cursor/rules/*.mdc |
| Windsurf | 🔜 | 计划中 |
| Copilot | 🔜 | 计划中 |
| CatPaw | 🔜 | 计划中 |
| Trae | 🔜 | 计划中 |

---

## 添加新平台适配器

以 Trae 为例：

```python
# src/agent_sync/adapters/trae.py
from agent_sync.adapters.base import BaseAdapter, SyncResult, PullResult, AdapterStatus

class TraeAdapter(BaseAdapter):
    platform_name = "trae"
    platform_display = "Trae"

    def detect(self, project_path: Path) -> bool:
        return (project_path / ".trae").exists()

    def sync(self, agent, project_path, *, dry_run=False) -> SyncResult:
        ...  # 读取 YAML → 渲染模板 → 写入文件

    def pull(self, agent, project_path) -> PullResult:
        ...  # 读取平台配置 → 更新 universal

    def status(self, project_path) -> AdapterStatus:
        ...
```

在 `detector.py` 注册：`ADAPTERS = [..., TraeAdapter]`

完整参考见 `src/agent_sync/adapters/cursor.py`。

---

## 开发

```bash
git clone https://github.com/jasonjcwu/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
pytest
```

## License

MIT
