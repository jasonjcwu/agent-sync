# agent-sync 快速上手指南

> 5 分钟，让你的 AI 助手在所有平台保持一致。

## 这是什么

你用 Claude Code 教会了 AI 用 pnpm、写中文注释、走 feature branch。切到 Cursor，这些全没了。

**定义一次，到处运行。**

---

## 第一步：安装

```bash
pip install git+https://github.com/jasonjcwu/agent-sync.git
agent-sync --version
```

## 第二步：初始化

```bash
cd ~/my-project
agent-sync init .
```

生成 `universal-agent/` 目录，里面有 YAML 模板。

## 第三步：填配置

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

### identity.yaml — AI 身份

```yaml
name: Assistant
emoji: "🤖"
values: []
traits: []
```

## 第四步：同步

```bash
agent-sync sync --dry-run    # 先预览
agent-sync sync               # 正式同步
```

**生成了什么：**

| 平台 | 文件 |
|------|------|
| Cursor | `.cursor/rules/soul.mdc` + `identity.mdc` + `user.mdc` |
| Claude Code | `CLAUDE.md` + `~/.claude/CLAUDE.md`（全局） |
| Codex | `AGENTS.md` |
| OpenClaw | `SOUL.md` + `IDENTITY.md` + `USER.md` |

## 第五步：设置记忆采集

至少配置一个记忆源。

### 方式 A：Claude Code + claude-mem

在 Claude Code 中执行：
```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

### 方式 B：OpenClaw（内置，无需插件）

OpenClaw 每天自动写 `memory/YYYY-MM-DD.md`。agent-sync 自动读取。

配置 `memory.yaml`：
```yaml
sources:
  - type: claude-mem
    path: ~/.claude-mem/claude-mem.db
  - type: openclaw
    path: ../memory/
```

## 第六步：日常使用

```bash
agent-sync memory today          # 看看 AI 最近学到了什么
agent-sync memory consolidate    # 热→温（自动）
agent-sync memory review         # 查看所有层状态（推荐每天一次）
agent-sync memory distill        # 蒸馏长期知识（需确认）
agent-sync skills discover       # 发现可沉淀的 skill（需确认）
agent-sync sync                  # 改了配置后重新同步
```

---

## 多台电脑

```bash
git clone <仓库地址> ~/agent-config
agent-sync sync -a ~/agent-config/universal-agent ~/my-project
```

## 常见问题

**Q: 我改了 CLAUDE.md，会被覆盖吗？**
A: 会。只改 YAML 源文件，不要改生成的文件。

**Q: 只想同步到 Cursor？**
A: `agent-sync sync -t cursor`

**Q: 怎么看检测到了哪些平台？**
A: `agent-sync detect` 或 `agent-sync status`

**Q: 公司内网/离线能用吗？**
A: 完全可以。用内网 Git（GitLab CE/Gitea）同步，Obsidian 本地 vault 做知识库，memory 只配 openclaw 源。全程不需要外网。

**Q: 记忆分类是什么意思？**
A: `insight` = 通用观察, `procedure` = 可重复流程 → skill 候选, `tool_pattern` = 工具模式 → skill 候选, `preference` = 用户偏好。只有 procedure/tool_pattern 出现 2 次以上才推荐为 skill。

---

## 完整文档

- [README.md](../README.md) — 完整架构、CLI 参考、适配器开发
- [英文版快速上手](CONFIG_GUIDE_EN.md)
- [跨平台AI人格与记忆架构设计](https://github.com/jasonjcwu/obsidian/blob/main/01_输出/跨平台AI人格与记忆架构设计.md) — 深度技术文章

## License

MIT
