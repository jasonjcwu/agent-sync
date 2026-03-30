# agent-sync 配置指南

> 一次配置，多平台同步 — 让你的 AI agent 在所有平台保持一致人格和记忆

---

## Part 1: OpenClaw 端（远程）

复制以下内容发送给 OpenClaw：

```
执行以下操作：

1. 提交当前 workspace 到 git, 如果没有请你叫我创建个 git 地址发给你：
 git add -A
 git commit -m "sync: workspace snapshot"
 git push

2. 确认 workspace 目录名，告诉我完整路径
```

---

## Part 2: ClaudeCode 端（本地）

复制以下内容发送给 ClaudeCode：

```
帮我配置 agent-sync 跨平台同步：

## 1. 安装 agent-sync

pip install git+https://github.com/jasonjcwu/agent-sync.git

## 2. 拉取远程 workspace

git clone <你的远程workspace仓库地址> ~/agent-workspace

（如果已存在则 cd ~/agent-workspace && git pull）

## 3. 初始化 universal-agent 配置

agent-sync init ~/agent-workspace

或如果已有配置，检查以下文件是否存在：
- universal-agent/soul.yaml（人格定义）
- universal-agent/user.yaml（用户画像）
- universal-agent/directives/axioms/（记忆结晶）

## 4. 同步人格（系统级 + 项目级）

# 同步到全局 ~/.claude/CLAUDE.md（所有项目共享）
agent-sync sync -a ~/agent-workspace/universal-agent ~/

# 或同步到特定项目
agent-sync sync -a ~/agent-workspace/universal-agent <项目目录>

## 5. 验证

agent-sync status
```

---

## 记忆系统

agent-sync 自动从以下源收集记忆：
- **ClaudeCode**: claude-mem 插件 → `~/.claude-mem/claude-mem.db`
- **OpenClaw**: `<agent-workspace>/memory/` 目录（相对路径，自动检测）

### 安装 claude-mem（ClaudeCode 记忆收集）

在 Claude Code 中执行：

```
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
```

重启 Claude Code 后生效。记忆会自动存储到 `~/.claude-mem/claude-mem.db`。

> 参考: [claude-mem](https://github.com/thedotmack/claude-mem)

### 自定义记忆源路径

如需自定义路径，在 `universal-agent/memory.yaml` 中配置：

```yaml
sources:
 - type: claude-mem
   path: ~/.claude-mem/claude-mem.db
 - type: openclaw
   path: /your/custom/path/to/memory

gate:
 threshold: 1.5
```

**默认行为**：
- openclaw 记忆路径默认为 `<agent-workspace>/memory/`
- 即 `universal-agent/` 同级的 `memory/` 目录

---

## 配置文件说明

### soul.yaml — AI 人格
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
```

### user.yaml — 用户画像
```yaml
name: 你的名字
timezone: Asia/Beijing
github: your-username
preferences:
 - 用 pnpm 而非 npm
 - 中英双语分析
```

### directives/axioms/ — 记忆结晶
```
directives/
├── INDEX.md # 索引
├── a01_*.md # AI 相关公理
├── t01_*.md # 技术决策公理
└── ...
```

---

## 日常使用

```bash
# 同步人格（全局 + 项目）
agent-sync sync -a ~/agent-workspace/universal-agent

# 查看最近记忆
agent-sync memory today -a ~/agent-workspace/universal-agent

# 提炼记忆（hot → warm）
agent-sync memory consolidate -a ~/agent-workspace/universal-agent

# 推送记忆到 git
cd ~/agent-workspace && git add . && git commit -m "memory sync" && git push
```

**同步范围**：
- `~/.claude/CLAUDE.md` — 全局人格和偏好，所有项目生效
- `<项目>/CLAUDE.md` — 项目特定配置（如需要）

---

## 自动化（定时任务）

### macOS/Linux — crontab

```bash
# 编辑定时任务
crontab -e

# 添加以下行（每天凌晨 2 点提炼记忆并推送）
0 2 * * * agent-sync memory consolidate -a ~/agent-workspace/universal-agent && cd ~/agent-workspace && git add . && git commit -m "auto memory sync" && git push
```

### macOS — launchd（推荐）

创建 `~/Library/LaunchAgents/com.user.agent-sync.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
 <key>Label</key>
 <string>com.user.agent-sync</string>
 <key>ProgramArguments</key>
 <array>
 <string>/usr/local/bin/agent-sync</string>
 <string>memory</string>
 <string>consolidate</string>
 <string>-a</string>
 <string>/Users/你的用户名/agent-workspace/universal-agent</string>
 </array>
 <key>StartCalendarInterval</key>
 <dict>
 <key>Hour</key>
 <integer>2</integer>
 <key>Minute</key>
 <integer>0</integer>
 </dict>
</dict>
</plist>
```

加载：
```bash
launchctl load ~/Library/LaunchAgents/com.user.agent-sync.plist
```

---

## 多机器同步

将 `~/agent-workspace` 放在 git 仓库或云盘，各机器克隆/同步同一份配置即可。
