# agent-sync 快速上手 / Quick Start Guide

> 5 分钟，让你的 AI 助手在所有平台保持一致。
>
> Get a consistent AI assistant across all platforms in 5 minutes.

---

## 这是什么 / What Is This

你用 Claude Code 教会了 AI 用 pnpm、写中文注释、走 feature branch。切到 Cursor，这些全没了。

You taught your AI to use pnpm, write Chinese comments, and use feature branches in Claude Code. Switch to Cursor — it forgets everything.

agent-sync 让你**只写一份配置，自动同步到所有平台**。

**Define once, sync everywhere.**

---

## 第一步：安装 / Step 1: Install

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
```

验证 / Verify：
```bash
agent-sync --version
```

---

## 第二步：初始化 / Step 2: Init

```bash
cd ~/my-project
agent-sync init .
```

生成 `universal-agent/` 目录，里面有 4 个 YAML 模板。/ Creates `universal-agent/` with 4 YAML templates.

---

## 第三步：填配置 / Step 3: Configure

### soul.yaml — AI 的性格和底线 / AI's personality and boundaries

```yaml
name: assistant
language: zh-CN
personality:
  - 真诚，不表演有用        # Be genuinely helpful
  - 有自己的观点             # Have opinions
  - 遇到问题先自己想办法      # Try to figure things out first
boundaries:
  - 私密信息不外泄           # Private things stay private
  - 对外操作先问确认          # Ask before external actions
communication:
  style: 简洁但彻底          # concise but thorough
  tone: 温暖真诚             # warm and genuine
  do_not:
    - 说"好问题！"           # Don't say "Great question!"
    - 说"我很乐意帮忙！"     # Don't say "I'd be happy to help!"
```

### user.yaml — 你是谁 / Who you are

```yaml
name: 你的名字              # Your name
timezone: Asia/Shanghai
github: your-username
preferences:
  - 用 pnpm 不要 npm        # Use pnpm not npm
  - 代码注释用中文           # Code comments in Chinese
  - 永远不要直接 push main   # Never push to main directly
```

### identity.yaml — AI 身份 / AI identity

```yaml
name: Assistant
emoji: "🤖"
values: []      # Optional: add your values / 可选
traits: []      # Optional: add traits / 可选
```

### routing.yaml — 平台分工 / Platform routing (optional / 可选)

```yaml
platforms:
  claude_code:
    type: coding-agent
    strengths: [complex coding, code review]    # 复杂编码, 代码审查
  cursor:
    type: ide-agent
    strengths: [quick coding, real-time completion]  # 快速编码, 实时补全
defaults:
  coding: claude_code
  ide: cursor
```

---

## 第四步：同步 / Step 4: Sync

```bash
# 先预览会生成什么 / Preview what will be generated
agent-sync sync --dry-run

# 正式同步 / Do it
agent-sync sync
```

**生成了什么 / What gets generated：**

| Platform | Files |
|----------|-------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` |
| Claude Code | `CLAUDE.md` + `~/.claude/CLAUDE.md` (global) |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` |

---

## 第五步：设置记忆采集 / Step 5: Setup Memory Collection

agent-sync needs at least one memory source. / 至少配置一个记忆源。

### Option A: Claude Code + claude-mem

In Claude Code, run: / 在 Claude Code 中执行：

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

Observations auto-save to `~/.claude-mem/claude-mem.db`. / 观察自动保存到 SQLite。

### Option B: OpenClaw (built-in / 内置)

OpenClaw already writes daily memory to `memory/YYYY-MM-DD.md`. agent-sync reads these files automatically. No plugin needed.

OpenClaw 已经把每日记忆写到 `memory/YYYY-MM-DD.md`。agent-sync 自动读取，无需插件。

Make sure your `memory.yaml` points to the right path: / 确保 `memory.yaml` 路径正确：

```yaml
# universal-agent/memory.yaml (optional, has defaults / 可选，有默认值)
sources:
  - type: claude-mem
    path: ~/.claude-mem/claude-mem.db
  - type: openclaw
    path: ../memory/    # universal-agent/ 同级的 memory/ 目录
```

---

## 第六步：日常使用 / Step 6: Daily Use

```bash
# 看看 AI 最近学到了什么 / See what agent learned
agent-sync memory today

# 把观察提炼成记忆 / Promote hot → warm
agent-sync memory consolidate

# 查看所有层状态（推荐每天一次）/ Review all layers (recommended daily)
agent-sync memory review

# 蒸馏长期知识 / Distill to long-term directives
agent-sync memory distill

# 发现可沉淀的 skill / Find skill candidates
agent-sync skills discover

# 改了配置后重新同步 / Re-sync after config changes
agent-sync sync
```

---

## 多台电脑 / Multiple Machines

```bash
# Put universal-agent/ in a Git repo / 放 Git 仓库
git clone <repo> ~/agent-config
agent-sync sync -a ~/agent-config/universal-agent ~/my-project
```

---

## 常见问题 / FAQ

**Q: 我改了 CLAUDE.md，会被覆盖吗？/ Will my CLAUDE.md edits be overwritten?**
A: 会。只改 YAML 源文件，不要改生成的文件。/ Yes. Edit YAML source files only, not generated ones.

**Q: 只想同步到 Cursor？/ Sync to Cursor only?**
A: `agent-sync sync -t cursor`

**Q: 怎么看检测到了哪些平台？/ How to see detected platforms?**
A: `agent-sync detect` or `agent-sync status`

**Q: 记忆分类是什么意思？/ What are memory categories?**
A: `insight` = 通用观察, `procedure` = 可重复流程 → skill 候选, `tool_pattern` = 工具模式 → skill 候选, `preference` = 用户偏好。只有 procedure/tool_pattern 出现 2 次以上才推荐为 skill。

**Q: OpenClaw 的记忆怎么配置？/ How to configure OpenClaw memory?**
A: OpenClaw 内置记忆，每天自动写 `memory/YYYY-MM-DD.md`。agent-sync 自动读取。只需确保 `memory.yaml` 里 openclaw 的 path 指向正确的 memory 目录。

**Q: 公司内网/离线能用吗？/ Does it work offline?**
A: 完全可以。用内网 Git（GitLab CE/Gitea）同步，Obsidian 本地 vault 做知识库，memory 只配 openclaw 源。全程不需要外网。 / Fully offline. Use internal Git, local Obsidian vault, and openclaw-only memory source. No internet needed.

---

## 完整文档 / Full Documentation

- [README.md](../README.md) — Complete architecture, CLI reference, adapter development
- [Architecture Spec (中文)](https://github.com/jasonjcwu/obsidian/blob/main/01_输出/跨平台AI人格与记忆架构设计.md) — 深度技术文章

## License

MIT
