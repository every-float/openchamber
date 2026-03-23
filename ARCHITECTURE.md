# OpenChamber 项目架构文档

## 项目概述

OpenChamber 是一个为 [OpenCode](https://opencode.ai) 提供丰富图形界面的多平台应用。支持桌面应用（macOS）、Web/PWA、VS Code 扩展等多种运行时环境，让用户可以在不同设备上无缝使用 AI 编程助手。

### 核心特性

- **跨设备连续性**：从终端 TUI 开始，在平板/手机上继续，再回到终端 - 同一会话
- **远程访问**：通过浏览器从任何地方使用 OpenCode
- **多运行时支持**：桌面应用、Web 应用、VS Code 扩展

---

## 项目结构

```
openchamber/
├── packages/                    # Monorepo 工作区
│   ├── web/                     # Web 版本 + CLI
│   ├── ui/                      # 共享 UI 组件库
│   ├── desktop/                 # Tauri 桌面应用
│   └── vscode/                  # VS Code 扩展
├── docs/                        # 文档和资源
├── .github/                     # GitHub 配置和工作流
├── .opencode/                   # OpenCode 技能配置
└── scripts/                     # 构建和开发脚本
```

---

## 技术栈

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.1.1 | UI 框架 |
| TypeScript | 5.8.3 | 类型安全 |
| Tailwind CSS | 4.0.0 | 样式系统 |
| Vite | 7.1.2 | 构建工具 |
| Zustand | 5.0.8 | 状态管理 |

### UI 组件库

| 库 | 用途 |
|-----|------|
| Radix UI | 无障碍基础组件（Dialog, Dropdown, Select 等） |
| CodeMirror | 代码编辑器 |
| @pierre/diffs | Diff 查看器 |
| react-syntax-highlighter | 代码高亮 |
| beautiful-mermaid | Mermaid 图表渲染 |
| @remixicon/react | 图标库 |

### 桌面应用

| 技术 | 版本 | 用途 |
|------|------|------|
| Tauri | 2.9.4 | 桌面应用框架 |
| Rust | - | 后端逻辑 |
| tauri-plugin-updater | 2.x | 自动更新 |
| tauri-plugin-shell | 2.3.3 | Shell 集成 |

### 后端/服务端

| 技术 | 用途 |
|------|------|
| Express | Web 服务器 |
| WebSocket (ws) | 实时通信 |
| node-pty / bun-pty | 终端模拟 |
| simple-git | Git 操作 |
| @octokit/rest | GitHub API |

### 工具链

| 工具 | 版本 | 用途 |
|------|------|------|
| Bun | 1.3.5 | 包管理器 + 运行时 |
| ESLint | 9.33.0 | 代码检查 |
| esbuild | 0.24.2 | 快速打包 |

---

## 包详解

### 1. @openchamber/web

Web 版本和 CLI 入口，提供独立运行的 Web 服务器。

```
packages/web/
├── src/                    # 前端源码
│   ├── api/               # API 客户端
│   │   ├── files.ts       # 文件操作 API
│   │   ├── git.ts         # Git API
│   │   ├── github.ts      # GitHub 集成
│   │   ├── terminal.ts    # 终端 API
│   │   └── ...
│   ├── main.tsx           # 入口文件
│   └── sw.ts              # Service Worker (PWA)
├── server/                 # 后端服务
│   ├── index.js           # 服务器入口
│   └── lib/               # 服务端库
│       ├── opencode/      # OpenCode 集成
│       ├── git/           # Git 服务
│       ├── github/        # GitHub 认证和操作
│       ├── terminal/      # 终端服务
│       ├── tunnels/       # 隧道服务 (Cloudflare)
│       ├── quota/         # 配额追踪
│       ├── skills-catalog/# 技能目录
│       └── tts/           # 文本转语音
├── bin/                    # CLI 入口
│   └── cli.js
└── public/                 # 静态资源
```

**主要功能：**
- 提供 HTTP/WebSocket 服务器
- OpenCode CLI 包装和生命周期管理
- Cloudflare 隧道集成
- PWA 支持
- 多种 AI 提供商配额追踪

### 2. @openchamber/ui

共享 UI 组件库，被所有平台复用。

```
packages/ui/
├── src/
│   ├── components/         # React 组件
│   │   ├── chat/          # 聊天界面组件
│   │   │   ├── message/   # 消息渲染
│   │   │   ├── hooks/     # 聊天相关 Hooks
│   │   │   └── lib/       # 聊天工具库
│   │   ├── views/         # 主要视图
│   │   │   ├── ChatView.tsx
│   │   │   ├── DiffView.tsx
│   │   │   ├── GitView.tsx
│   │   │   ├── FilesView.tsx
│   │   │   ├── TerminalView.tsx
│   │   │   └── PlanView.tsx
│   │   ├── layout/        # 布局组件
│   │   ├── session/       # 会话管理
│   │   ├── sections/      # 设置页面
│   │   ├── terminal/      # 终端组件
│   │   ├── voice/         # 语音功能
│   │   └── ui/            # 基础 UI 组件
│   ├── stores/            # Zustand 状态存储
│   │   ├── sessionStore.ts
│   │   ├── messageStore.ts
│   │   ├── contextStore.ts
│   │   ├── useGitStore.ts
│   │   └── ...
│   ├── hooks/             # 自定义 Hooks
│   ├── lib/               # 工具库
│   │   ├── theme/         # 主题系统
│   │   ├── voice/         # 语音服务
│   │   ├── worktrees/     # Worktree 管理
│   │   └── ...
│   ├── contexts/          # React Context
│   └── types/             # TypeScript 类型
└── package.json
```

**核心组件分类：**

| 分类 | 组件 | 说明 |
|------|------|------|
| 聊天 | ChatContainer, ChatInput, MessageList | 核心聊天界面 |
| 消息 | AssistantTextPart, ToolPart, DiffPreview | 消息内容渲染 |
| 视图 | ChatView, DiffView, GitView, FilesView | 主要功能视图 |
| 布局 | MainLayout, Sidebar, NavRail, Header | 应用布局 |
| 终端 | TerminalViewport | 集成终端 |
| Git | GitView, CommitInput, PullRequestSection | Git 工作流 |
| 语音 | VoiceProvider, BrowserVoiceButton | 语音输入/输出 |

### 3. @openchamber/desktop

基于 Tauri 的桌面应用（目前支持 macOS）。

```
packages/desktop/
├── src-tauri/              # Tauri/Rust 后端
│   ├── src/
│   │   ├── main.rs        # 主入口
│   │   └── remote_ssh.rs  # SSH 远程连接
│   ├── icons/             # 应用图标
│   ├── Cargo.toml         # Rust 依赖
│   └── tauri.conf.json    # Tauri 配置
├── scripts/                # 构建脚本
│   ├── build-sidecar.mjs  # Sidecar 构建
│   └── desktop-dev.mjs    # 开发脚本
└── package.json
```

**主要功能：**
- 原生 macOS 菜单集成
- 多窗口支持
- SSH 远程实例连接
- 自动更新
- "Open In" 快捷方式（Finder, Terminal, 编辑器）

### 4. openchamber (VS Code 扩展)

VS Code 编辑器扩展。

```
packages/vscode/
├── src/
│   ├── extension.ts            # 扩展入口
│   ├── ChatViewProvider.ts     # 侧边栏聊天视图
│   ├── AgentManagerPanelProvider.ts  # Agent 管理器
│   ├── SessionEditorPanelProvider.ts # 会话编辑器
│   ├── opencode.ts             # OpenCode 集成
│   ├── githubAuth.ts           # GitHub 认证
│   ├── theme.ts                # 主题映射
│   └── ...
├── webview/                    # Webview 前端
└── package.json               # 扩展配置
```

**主要功能：**
- 侧边栏聊天面板
- Agent Manager（多模型并行运行）
- 右键菜单操作（添加上下文、解释、改进代码）
- 编辑器内 Diff 查看
- 主题自动映射

---

## 核心架构

### 状态管理

使用 Zustand 进行状态管理，主要 Store 包括：

```
┌─────────────────────────────────────────────────────────────┐
│                        Zustand Stores                        │
├─────────────────────────────────────────────────────────────┤
│  sessionStore      - 会话状态、当前会话、会话列表           │
│  messageStore      - 消息数据、流式消息处理                 │
│  contextStore      - 上下文文件、Token 统计                 │
│  useGitStore       - Git 状态、分支、变更                   │
│  useProjectsStore  - 项目列表、项目配置                     │
│  useConfigStore    - 应用配置                               │
│  useTerminalStore  - 终端会话                               │
│  useQuotaStore     - AI 提供商配额                          │
│  useAgentsStore    - Agent 状态                             │
│  useMcpStore       - MCP 服务器配置                         │
│  useUIStore        - UI 状态（侧边栏、面板等）              │
└─────────────────────────────────────────────────────────────┘
```

### API 架构

```
┌──────────────┐     HTTP/WS      ┌──────────────┐     IPC      ┌──────────────┐
│   Frontend   │ ◄──────────────► │   Server     │ ◄──────────► │  OpenCode    │
│   (React)    │                  │  (Express)   │              │    CLI       │
└──────────────┘                  └──────────────┘              └──────────────┘
       │                                 │
       │                                 │
       ▼                                 ▼
┌──────────────┐                  ┌──────────────┐
│   Zustand    │                  │   Services   │
│   Stores     │                  │              │
└──────────────┘                  │ - Git        │
                                  │ - GitHub     │
                                  │ - Terminal   │
                                  │ - Tunnels    │
                                  │ - TTS        │
                                  │ - Quota      │
                                  └──────────────┘
```

### 主题系统

支持 18+ 内置主题，支持自定义主题：

```
packages/ui/src/lib/theme/
├── themes/                 # 内置主题 JSON
│   ├── flexoki-dark.json
│   ├── flexoki-light.json
│   ├── catppuccin-dark.json
│   ├── catppuccin-light.json
│   └── ...
├── cssGenerator.ts        # CSS 变量生成
├── syntaxThemeGenerator.ts # 语法高亮主题
└── vscode/adapter.ts      # VS Code 主题适配
```

### 终端架构

使用 Ghostty-web 渲染终端，通过 WebSocket 传输数据：

```
┌──────────────────┐    WebSocket    ┌──────────────────┐
│  TerminalViewport │ ◄─────────────► │  Terminal Service │
│   (Ghostty-web)  │                 │   (node-pty)      │
└──────────────────┘                 └──────────────────┘
```

### 隧道服务

支持 Cloudflare 隧道进行远程访问：

```
packages/web/server/lib/tunnels/
├── providers/
│   └── cloudflare.js     # Cloudflare 隧道实现
├── registry.js           # 隧道注册表
└── types.js              # 类型定义
```

**隧道模式：**
- `quick` - 临时隧道，自动生成 URL
- `managed-remote` - 托管远程隧道，自定义域名
- `managed-local` - 本地配置隧道

---

## 数据流

### 消息流

```
用户输入
    │
    ▼
┌─────────────┐
│ ChatInput   │
└─────────────┘
    │
    ▼
┌─────────────┐     POST /api/chat      ┌─────────────┐
│ messageStore│ ───────────────────────►│   Server    │
└─────────────┘                         └─────────────┘
    │                                         │
    │ SSE Stream                               │
    │◄─────────────────────────────────────────┤
    │                                         │
    ▼                                         ▼
┌─────────────┐                         ┌─────────────┐
│ MessageList │                         │  OpenCode   │
│   渲染      │                         │    CLI      │
└─────────────┘                         └─────────────┘
```

### Git 工作流

```
┌──────────────┐
│  useGitStore │
└──────────────┘
       │
       │ HTTP API
       ▼
┌──────────────────────────────────────┐
│           Git Service                 │
│  (packages/web/server/lib/git/)      │
├──────────────────────────────────────┤
│  - credentials.js   - 身份凭证管理    │
│  - identity-storage.js - 身份存储    │
│  - service.js       - Git 操作       │
└──────────────────────────────────────┘
       │
       │ simple-git
       ▼
┌──────────────┐
│  Git Repository │
└──────────────┘
```

---

## 构建和开发

### 开发命令

```bash
# 安装依赖
bun install

# 开发模式（Web + UI 热重载）
bun run dev

# 仅开发 Web
bun run dev:web

# 开发桌面应用
bun run desktop:dev

# 开发 VS Code 扩展
bun run vscode:dev

# 构建
bun run build           # 构建所有包
bun run build:web       # 构建 Web
bun run build:ui        # 构建 UI
bun run build:desktop   # 构建桌面应用

# 类型检查
bun run type-check

# 代码检查
bun run lint
```

### 发布流程

```bash
# 准备发布
bun run release:prepare

# 版本升级
bun run version:bump
```

---

## 配置文件

| 文件 | 用途 |
|------|------|
| `package.json` | Monorepo 根配置 |
| `bun.lock` | Bun 锁文件 |
| `tsconfig.json` | TypeScript 配置 |
| `eslint.config.js` | ESLint 配置 |
| `components.json` | shadcn/ui 组件配置 |
| `docker-compose.yml` | Docker 部署配置 |
| `Dockerfile` | Docker 镜像构建 |

---

## 部署选项

### 1. CLI 安装

```bash
curl -fsSL https://raw.githubusercontent.com/btriapitsyn/openchamber/main/scripts/install.sh | bash
openchamber --ui-password secret --daemon
```

### 2. Docker

```bash
docker compose up -d
```

### 3. 桌面应用

从 [GitHub Releases](https://github.com/btriapitsyn/openchamber/releases) 下载。

### 4. VS Code 扩展

从 [Marketplace](https://marketplace.visualstudio.com/items?itemName=fedaykindev.openchamber) 安装。

---

## 扩展性

### 自定义主题

在 `~/.config/openchamber/themes/` 目录放置 JSON 主题文件，支持热重载。

### Skills 系统

支持自定义技能，位于 `~/.config/openchamber/skills/`。

### MCP 集成

支持 Model Context Protocol 服务器集成。

---

## 安全考虑

- UI 密码保护
- Cloudflare 隧道一次性连接令牌
- GitHub OAuth 设备流程
- SSH 密钥管理

---

## 许可证

MIT License

---

## 相关链接

- [GitHub 仓库](https://github.com/btriapitsyn/openchamber)
- [OpenCode](https://opencode.ai)
- [Discord 社区](https://discord.gg/ZYRSdnwwKA)
