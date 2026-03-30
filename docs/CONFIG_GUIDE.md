# agent-sync 配置指南

> 一次配置，多平台同步 — 让你的 AI agent 在所有平台保持一致人格和记忆

---

## 安装

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
```

验证安装：
```bash
agent-sync --version
agent-sync detect
```

---

## 快速开始

### 1. 初始化

```bash
agent-sync init ~/my-project
```

生成 `universal-agent/` 目录结构：

```
universal-agent/
├── soul.yaml          # 元人格：行为边界、核心信条
├── identity.yaml      # 具体人格：名字、价值观、沟通风格
├── user.yaml          # 用户画像：服务对象、偏好、时区
├── routing.yaml       # 任务路由
├── directives/        # 行为指令（按领域索引）
│   └── INDEX.md
├── skills/            # 技能定义（SKILL.md 格式）
└── memory/
    └── core.md        # 温记忆（跨会话核心画像）
```

### 2. 编辑配置

**soul.yaml** — 元人格（所有平台通用）：
```yaml
name: assistant
language: zh-CN
personality:
  - 真诚，不表演有用
  - 有观点，不谄媚
  - 先自己想办法，再问
boundaries:
  - 私人的事就留在私人里
  - 对外行动前，不确定就先问
communication:
  style: 简洁但彻底
  tone: 温暖真诚，有边界感
  do_not:
    - 说"好问题！"
    - 说"我很乐意帮忙！"
```

**identity.yaml** — 具体人格：
```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
development_goals: {}
```

**user.yaml** — 用户画像：
```yaml
name: 你的名字
timezone: Asia/Shanghai
github: your-username
preferences:
  - 用 pnpm 而非 npm
  - 中英双语分析
```

### 3. 同步到所有平台

```bash
# 同步到当前目录检测到的所有平台
agent-sync sync -a universal-agent/ .

# 预览变更（不写文件）
agent-sync sync --dry-run

# 只同步到特定平台
agent-sync sync -t cursor
agent-sync sync -t claude_code
```

---

## 支持的平台

### OpenClaw

同步生成：`SOUL.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, `SKILLS.md`

检测条件：项目中有 `SOUL.md` 或 `AGENTS.md`

### Claude Code

同步生成：
- 项目级 `CLAUDE.md`（人格 + 指令）
- 全局 `~/.claude/CLAUDE.md`（用户偏好）

检测条件：项目中有 `CLAUDE.md` 或 `.claude/` 目录

### Codex

同步生成：`AGENTS.md`

检测条件：项目中有 `AGENTS.md` 或 `.codex` 目录

### Cursor

同步生成 `.cursor/rules/` 目录下的 `.mdc` 文件：

| 文件 | 激活模式 | 内容 |
|------|----------|------|
| `soul.mdc` | alwaysApply | 人格 + 行为边界 |
| `identity.mdc` | alwaysApply | 身份 + 价值观 |
| `user.mdc` | alwaysApply | 用户上下文 + 偏好 |
| `directives/*.mdc` | 按需加载 | 行为指令 |
| `skills.mdc` | 按需加载 | 技能注册表 |

检测条件：项目中有 `.cursor/rules/` 或 `.cursorrules`

---

## 记忆系统

### 三层架构

```
热记忆（每次对话）
  claude-mem SQLite + OpenClaw 日志
  ↓ Reflector 自动采集
温记忆（跨会话）
  memory/core.md — 压缩到 ~100 行
  ↓ 自动分类: insight / procedure / tool_pattern / preference
冷记忆（长期知识）
  directives/ — 行为公理
  skills/ — 可复用技能
  Obsidian — 外挂大脑（公司外环境）
```

### 记忆源配置

默认从两个源采集：

```yaml
# universal-agent/memory.yaml（可选，有默认值）
sources:
  - type: claude-mem
    path: ~/.claude-mem/claude-mem.db
  - type: openclaw
    path: ../memory/  # universal-agent/ 同级的 memory/

gate:
  threshold: 1.5
```

### 安装 claude-mem（Claude Code 记忆收集）

在 Claude Code 中执行：

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

> 参考: [claude-mem](https://github.com/thedotmack/claude-mem)

---

## CLI 命令参考

### 同步命令

```bash
agent-sync init [path]              # 创建 universal-agent/ 目录
agent-sync detect [path]            # 检测已安装平台
agent-sync sync [path]              # 同步到所有平台
agent-sync sync -t cursor           # 只同步 Cursor
agent-sync sync --dry-run           # 预览不写入
agent-sync status [path]            # 各平台同步状态
```

### 记忆命令

```bash
agent-sync memory today             # 查看近期热记忆
agent-sync memory consolidate       # 热 → 温：提炼晋升
agent-sync memory distill           # 温 → 冷：蒸馏为指令
agent-sync memory distill --dry-run # 预览蒸馏候选
agent-sync memory review            # 交互式回顾（所有层 + skill 候选）
agent-sync memory push              # 推送记忆到 Git
agent-sync memory pull              # 从 Git 拉取最新记忆
```

### 技能命令

```bash
agent-sync skills scan              # 扫描 skills/ 目录
agent-sync skills discover          # 从温记忆发现 skill 候选
agent-sync skills discover --confirm # 确认后创建 skill 脚手架
agent-sync skills sync              # 同步 skills 到各平台
```

---

## 温记忆分类

Reflector 在晋升温记忆时自动分类：

| 分类 | 说明 | 下一步 |
|------|------|--------|
| `insight` | 通用观察和学习 | 可能蒸馏为 directive |
| `procedure` | 可重复流程和工作流 | → skill 候选 |
| `tool_pattern` | 工具/技术使用模式 | → skill 候选 |
| `preference` | 用户偏好和习惯 | 保留在温记忆 |

只有 `procedure` 和 `tool_pattern` 类型的条目才会被推荐为 skill 候选。

---

## 日常使用

```bash
# 同步人格到所有平台
agent-sync sync -a ~/agent-workspace/universal-agent

# 查看最近记忆
agent-sync memory today

# 提炼记忆（热 → 温）
agent-sync memory consolidate

# 蒸馏洞察（温 → 冷 → directives）
agent-sync memory distill

# 交互式回顾（推荐每天一次）
agent-sync memory review

# 推送到 Git
agent-sync memory push
```

---

## 自动化

### crontab（Linux/macOS）

```bash
# 每天凌晨 2 点提炼 + 蒸馏 + 推送
0 2 * * * agent-sync memory consolidate -a ~/agent-workspace/universal-agent && agent-sync memory distill -a ~/agent-workspace/universal-agent && cd ~/agent-workspace && git add . && git commit -m "auto memory sync $(date +\%Y-\%m-\%d)" && git push
```

---

## 多机器同步

将 `~/agent-workspace` 放在 Git 仓库，各机器克隆同一份配置：

```bash
git clone <你的仓库地址> ~/agent-workspace
cd ~/agent-workspace
agent-sync sync
```

---

## 从旧版迁移

如果你之前手动维护了 `.cursorrules` 或 `CLAUDE.md`：

1. `agent-sync init` 创建通用配置
2. 把旧文件里有价值的内容迁移到对应的 YAML 文件
3. `agent-sync sync` 重新生成各平台配置
4. 以后只改 YAML，不要改生成的文件（文件头有 `auto-generated` 标记）
