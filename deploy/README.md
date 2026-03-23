# OpenChamber Docker 部署指南

## 前置要求

- Docker 已安装并运行
- Docker Compose 已安装
- 足够的磁盘空间（约 2GB+）

## 快速开始

### Linux / macOS

```bash
cd deploy
chmod +x deploy.sh
./deploy.sh deploy
```

### Windows (PowerShell)

```powershell
cd deploy
.\deploy.ps1 deploy
```

部署完成后，访问 http://localhost:3000 即可使用 OpenChamber。

## 命令说明

| 命令 | 说明 |
|------|------|
| `deploy` | 完整部署（构建镜像并启动服务） |
| `build` | 构建 Docker 镜像 |
| `start` | 启动服务 |
| `stop` | 停止服务 |
| `restart` | 重启服务 |
| `logs` | 查看实时日志 |
| `status` | 查看服务状态 |
| `help` | 显示帮助信息 |

## 环境变量配置

在 `docker-compose.yml` 中可以配置以下环境变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `UI_PASSWORD` | 设置 UI 访问密码 | `your_secure_password` |
| `CF_TUNNEL` | 启用 Cloudflare Tunnel | `true` / `qr` / `password` |
| `OH_MY_OPENCODE` | 启用 oh-my-opencode | `true` |
| `OPENCODE_HOST` | 连接外部 OpenCode 服务器 | `http://172.17.0.1:4096` |
| `OPENCODE_SKIP_START` | 跳过启动 opencode | `true` |

### 配置示例

编辑 `docker-compose.yml`：

```yaml
services:
  openchamber:
    environment:
      UI_PASSWORD: your_secure_password_here
      CF_TUNNEL: true
      OH_MY_OPENCODE: true
```

## 目录结构

部署后会在项目根目录创建以下目录：

```
data/
├── openchamber/          # OpenChamber 配置目录
├── opencode/
│   ├── share/            # OpenCode 共享数据
│   ├── state/            # OpenCode 状态数据
│   └── config/           # OpenCode 配置
└── ssh/                  # SSH 密钥存储
workspaces/               # 工作空间目录
```

## 端口说明

- `3000`: OpenChamber Web UI 端口

如需修改端口，编辑 `docker-compose.yml` 中的 `ports` 配置：

```yaml
ports:
  - "8080:3000"  # 将服务映射到 8080 端口
```

## 常见问题

### 1. Docker 镜像构建失败

确保 Docker 有足够的内存（建议 4GB+）和磁盘空间。

### 2. 服务无法访问

- 检查 Docker 容器是否正常运行：`./deploy.sh status`
- 查看日志排查问题：`./deploy.sh logs`
- 确认端口未被其他服务占用

### 3. SSH 连接问题

SSH 密钥会在首次启动时自动生成，存储在 `data/ssh/` 目录。

### 4. 数据持久化

所有数据都挂载到 `data/` 和 `workspaces/` 目录，删除容器不会丢失数据。

## 生产环境建议

1. **设置密码保护**：配置 `UI_PASSWORD` 环境变量
2. **使用 HTTPS**：配合反向代理（如 Nginx、Caddy）启用 HTTPS
3. **定期备份**：备份 `data/` 目录
4. **资源限制**：在 `docker-compose.yml` 中添加资源限制

```yaml
services:
  openchamber:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并部署
./deploy.sh deploy
```
