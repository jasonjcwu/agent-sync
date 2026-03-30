# agent-sync 快速上手指南

> 5 分钟，让你的 AI 助手在所有平台保持一致。

## 这是什么

你用 Claude Code 教会了 AI 用 pnpm、写中文注释、走 feature branch。切到 Cursor，这些全没了——你得重新写一遍 .cursorrules。

agent-sync 让你**只写一份配置，自动同步到所有平台**。

## 第一步：安装

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
```

验证：
```bash
agent-sync --version
```

## 第二步：初始化

进入你的项目目录：
```bash
cd ~/my-project
agent-sync init .
```

这会创建 `universal-agent/` 目录，里面有 4 个 YAML 文件等你填写。

## 第三步：填写配置

### soul.yaml — AI 的性格和底线

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

### user.yaml — 你是谁

```yaml
name: 你的名字
timezone: Asia/Shanghai
github: your-username
preferences:
  - 用 pnpm 不要 npm
  - 代码注释用中文
  - 永远不要直接 push 到 main
```

### identity.yaml — AI 的身份

```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
```

### routing.yaml — 平台分工（可选）

```yaml
platforms:
  claude_code:
    type: coding-agent
    strengths: [复杂编码, 代码审查]
  cursor:
    type: ide-agent
    strengths: [快速编码, 实时补全]
defaults:
  coding: claude_code
  ide: cursor
```

## 第四步：同步

```bash
# 先预览会生成什么文件
agent-sync sync --dry-run

# 确认没问题，正式同步
agent-sync sync
```

这会自动检测你的项目装了哪些平台（Cursor、Claude Code、Codex...），然后生成对应的配置文件。

**生成了什么：**

| 平台 | 文件 |
|------|------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` |
| Claude Code | `CLAUDE.md` + `~/.claude/CLAUDE.md`（全局） |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` |

## 第五步：日常使用

```bash
# 改了 soul.yaml？重新同步
agent-sync sync

# 看看 AI 最近学到了什么
agent-sync memory today

# 把观察提炼成记忆
agent-sync memory consolidate

# 查看所有层的记忆状态（推荐每天一次）
agent-sync memory review

# 发现可以沉淀为 skill 的重复操作
agent-sync skills discover
```

## 记忆系统（进阶）

agent-sync 有三层记忆，自动从你的对话中采集：

```
热记忆（每次对话的观察）
  ↓ agent-sync memory consolidate
温记忆（跨会话核心画像，~100行）
  ↓ 自动分类：insight / procedure / tool_pattern / preference
  ↓ agent-sync memory distill
冷记忆（长期知识：directives/ + skills/）
```

**需要 claude-mem 插件来自动采集 Claude Code 的对话：**

在 Claude Code 中执行：
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

## 多台电脑

把 `universal-agent/` 放 Git 仓库，每台电脑 clone 同一份配置：

```bash
git clone <repo> ~/agent-config
agent-sync sync -a ~/agent-config/universal-agent ~/my-project
```

## 常见问题

**Q: 我改了 CLAUDE.md，会被覆盖吗？**
A: 会。每次 `agent-sync sync` 都会重新生成。改 YAML 源文件，不要改生成的文件。

**Q: 只想同步到 Cursor 怎么办？**
A: `agent-sync sync -t cursor`

**Q: 我的项目没有 .cursor 目录能同步吗？**
A: `agent-sync detect` 查看检测到了哪些平台。只要项目里有对应平台的特征文件就会被检测到。

**Q: 记忆是怎么分类的？**
A: Reflector 自动分类——描述流程的归为 `procedure`（可能变成 skill），描述偏好的归为 `preference`，通用观察归为 `insight`。只有 `procedure` 和 `tool_pattern` 出现 2 次以上才会被推荐为 skill 候选。

## 完整文档

- [README.md](../README.md) — 完整架构、CLI 参考、适配器开发指南
- [跨平台AI人格与记忆架构设计](https://github.com/jasonjcwu/obsidian/blob/main/01_输出/跨平台AI人格与记忆架构设计.md) — 深度技术文章
