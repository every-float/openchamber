from fastapi import FastAPI, Request, Response, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import os, json, secrets, subprocess, httpx
from filelock import FileLock

app = FastAPI()

""" 
发正式的时候，需要修改的地方：
    1. PUBLIC_IP 改为服务器 IP "192.168.140.26"
    2. BASE_DATA_DIR 改为服务器openchamber+opencode数据目录绝对路径（"/opt/open_data"）
    3. OPENCODE_DIR 改为服务器openchamber项目绝对路径（"/root/openchamber"）
"""

# ==========================================
# ⚙️ 智水云工 - 核心配置区
# ==========================================
# PUBLIC_IP = "172.29.237.124"
# BASE_DATA_DIR = "../../open_data"
# OPENCODE_DIR = "./"
PUBLIC_IP = "192.168.140.26"
BASE_DATA_DIR = "/opt/open_data"
OPENCODE_DIR = "/root/openchamber"


# 注册中心与网关配置
NACOS_ADDR = f"{PUBLIC_IP}:8848"      # Nacos 在 Docker 网络内的地址
GATEWAY_PORT = 52082                   # 网关统一入口端口
GATEWAY_URL = f"http://{PUBLIC_IP}:{GATEWAY_PORT}"

# 钉钉凭证
DING_APP_KEY = "dingqrubk8ptq9n3bgdj" # 填入之前验证成功的 Key
DING_APP_SECRET = "iN489Ilp-MybuTcPS7cygLzl00T8qQYYwLCpTUnV6uPXWaJVvFVzhMWQMSIyrud2" # 填入之前验证成功的 Secret
# ALLOWED_CORP_ID = "ding25f472b3c8d2bb51f2c783f7214b6d69"
ALLOWED_CORP_ID = "ding71bd0c66f9094aaa35c2f4657eb6378f"
REDIRECT_URI = f"http://{PUBLIC_IP}:9000/callback"

# openchamber 镜像
IMAGE_NAME = "openchamber"
IMAGE_TAG = "latest"
IMAGE_FILE = f"{OPENCODE_DIR}/images/openchamber-latest.tar"

# ==========================================

DB_FILE = "users.json"
LOCK_FILE = "users.json.lock"

os.makedirs(BASE_DATA_DIR, exist_ok=True)
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump({}, f)

# 确保openchamber专属网络存在
os.system("docker network create openchamber_net > /dev/null 2>&1")

def load_image(image_name, image_tag, file_path):
    if not os.path.exists(file_path): return False
    images = subprocess.getoutput(f"docker images -q {image_name}:{image_tag}")
    if images.strip(): return True
    return os.system(f"docker load -i {file_path} > /dev/null 2>&1") == 0

def read_users():
    with FileLock(LOCK_FILE, timeout=5):
        with open(DB_FILE, "r") as f: return json.load(f)

def write_users(data):
    with FileLock(LOCK_FILE, timeout=5):
        with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

# ==========================================
# 🎨 品牌 UI 渲染引擎 (已对齐 OpenCode 极简视觉规范)
# ==========================================
def render_page(title: str, content: str, msg: str = "", is_error: bool = True):
    alert_html = ""
    if msg:
        bg_color = "#fef2f2" if is_error else "#f0fdf4"
        text_color = "#991b1b" if is_error else "#166534"
        border_color = "#fee2e2" if is_error else "#dcfce3"
        alert_html = f'<div class="alert" style="background: {bg_color}; color: {text_color}; border: 1px solid {border_color};">{msg}</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            /* 提取自 OpenCode 的调色板 */
            :root {{ 
                --bg-canvas: #fafafa; 
                --bg-panel: #ffffff; 
                --text-main: #171717; 
                --text-muted: #888888; 
                --border-light: #e5e7eb;
                --btn-hover: #f3f4f6;
            }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background: var(--bg-canvas); 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh; 
                margin: 0; 
                color: var(--text-main);
            }}
            /* 扁平化卡片，去除非必要阴影，使用极细边框 */
            .card {{ 
                background: var(--bg-panel); 
                padding: 40px 32px; 
                border-radius: 8px; 
                border: 1px solid var(--border-light); 
                box-shadow: 0 1px 3px rgba(0,0,0,0.02); 
                width: 100%; 
                max-width: 340px; 
                box-sizing: border-box; 
                text-align: center;
            }}
            .brand-icon {{ margin-bottom: 20px; color: var(--text-main); display: flex; justify-content: center; }}
            .brand-icon svg {{ width: 28px; height: 28px; stroke-width: 1.5; }}
            h2 {{ font-size: 18px; font-weight: 500; margin: 0 0 8px 0; letter-spacing: -0.01em; }}
            .sub {{ font-size: 13px; color: var(--text-muted); margin-bottom: 32px; line-height: 1.5; }}
            
            /* 对齐 OpenCode 顶部工具栏按钮风格 */
            .btn-ding {{ 
                background: var(--bg-panel); 
                color: #374151; 
                padding: 10px 16px; 
                border-radius: 6px; 
                text-decoration: none; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                gap: 8px; 
                font-weight: 500; 
                font-size: 13px; 
                border: 1px solid var(--border-light);
                transition: all 0.2s ease;
                cursor: pointer;
            }}
            .btn-ding:hover {{ background: var(--btn-hover); border-color: #d1d5db; }}
            
            /* 极简灰调加载动画 */
            .spinner {{ 
                width: 20px; height: 20px; 
                border: 2px solid var(--border-light); 
                border-top: 2px solid var(--text-muted); 
                border-radius: 50%; 
                animation: spin 0.8s linear infinite; 
                margin: 0 auto 16px auto; 
            }}
            @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
            
            .alert {{ padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 24px; text-align: left; }}
        </style>
    </head>
    <body><div class="card">{alert_html}{content}</div></body>
    </html>
    """

# ==========================================
# 🚪 钉钉认证与回调逻辑
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def login_page(error: str = "", msg: str = ""):
    ding_auth_url = (
        f"https://login.dingtalk.com/oauth2/auth?"
        f"client_id={DING_APP_KEY}&"
        f"response_type=code&"
        f"scope=openid%20corpid&"
        f"redirect_uri={REDIRECT_URI}&"
        f"prompt=consent"
    )
    # UI 内容适配：使用更细致的图标和文案排版
    content = f"""
        <div class="brand-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
        </div>
        <h2>山脉AI水利：智水云工</h2>
        <p class="sub">垂直水利行业，实现数智创新<br>请验证您的企业身份</p>
        <a href="{ding_auth_url}" class="btn-ding">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg>
            钉钉一键登录
        </a>
    """
    return render_page("登录 - 智水云工", content, error if error else msg, True if error else False)

@app.get("/callback")
async def callback(code: str = Query(None)):
    if not code: return RedirectResponse(url="/?error=授权已取消")
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://api.dingtalk.com/v1.0/oauth2/userAccessToken",
            json={
                "clientId": DING_APP_KEY,
                "clientSecret": DING_APP_SECRET,
                "code": code,
                "grantType": "authorization_code"
            }
        )
        print(f"token_resp.json(): {token_resp.json()}")

        corp_id = token_resp.json().get("corpId")
        print(f"corp_id: {corp_id}")
        print(f"ALLOWED_CORP_ID: {ALLOWED_CORP_ID}")
        if not corp_id:
            return render_page("访问受限", "<h2>企业核验失败</h2><p class='sub'>未能获取企业ID，请检查钉钉后台权限配置。</p><a href='/' class='btn-ding'>返回首页</a>")
        elif corp_id != ALLOWED_CORP_ID:
            return render_page("访问受限", f"<h2>企业核验失败</h2><p class='sub'>当前账号(企业ID:{corp_id})未在许可白名单内。</p><a href='/' class='btn-ding'>返回首页</a>")

        access_token = token_resp.json().get("accessToken")
        if not access_token:
            err_msg = token_resp.json().get("message", "令牌校验失败")
            return render_page("认证失败", f"<h2>登录异常</h2><p class='sub'>{err_msg}</p><a href='/' class='btn-ding'>返回重试</a>")

        user_resp = await client.get(
            "https://api.dingtalk.com/v1.0/contact/users/me",
            headers={"x-acs-dingtalk-access-token": access_token}
        )
        user_info = user_resp.json()
        print(f"user_info: {user_info}")
        union_id = user_info.get("unionId")
        user_name = user_info.get("nick")
        # corp_id = user_info.get("corpId")
        print(f"union_id: {union_id}")
        print(f"user_name: {user_name}")
        if not union_id:
            return render_page("访问受限", "<h2>权限不足</h2><p class='sub'>未能获取身份标识，请检查钉钉后台权限配置。</p><a href='/' class='btn-ding'>返回首页</a>")

        users = read_users()
        if union_id not in users:
            display_name = user_name if user_name else "工程师"
            users[union_id] = {
                "name": display_name,
                "container_token": secrets.token_urlsafe(16)
            }
            write_users(users)

        response = RedirectResponse(url="/start_openchamber", status_code=303)
        response.set_cookie(key="session_user", value=union_id, httponly=True)
        response.set_cookie(key="auth_token", value=users[union_id]["container_token"], httponly=True)
        return response

# ==========================================
# 🚀 环境启动逻辑 (含 Session 持久化)
# ==========================================
@app.get("/start_openchamber", response_class=HTMLResponse)
async def start_openchamber(session_user: str = Cookie(None)):
    if not session_user: return RedirectResponse(url="/", status_code=303)

    users = read_users()
    u_data = users[session_user]
    token, name = u_data["container_token"], u_data.get("name", "工程师")
    u_home = f"{BASE_DATA_DIR}/{session_user}"

    # 动态服务名（前缀+用户唯一标识）
    session_user_lower = session_user.lower()
    service_name = f"openchamber-user-{session_user_lower}"

    for folder in ["config", "share", "workspace", "proxy"]:
        os.makedirs(os.path.join(u_home, folder), exist_ok=True)
        os.system(f"chmod -R 777 {os.path.join(u_home, folder)}")

    # # 测试代码：如果session_user为 EW9N0hsjiSIVTRO05dtckBQiEiE ，先停止并移除该容器
    # if session_user == "EW9N0hsjiSIVTRO05dtckBQiEiE" and "Up" in subprocess.getoutput(f"docker ps -a --filter name=openchamber_{session_user} --format '{{{{.Status}}}}'"):
    #     os.system(f"docker stop openchamber_{session_user} > /dev/null 2>&1")
    #     os.system(f"docker rm -f openchamber_{session_user} > /dev/null 2>&1")
    #     # 还有nginx容器 proxy_{session_user}
    #     os.system(f"docker stop proxy_{session_user} > /dev/null 2>&1")
    #     os.system(f"docker rm -f proxy_{session_user} > /dev/null 2>&1")
    # # 测试代码

    # 1. 启动容器，并注入 Nacos 注册信息
    backend_running = subprocess.getoutput(f"docker ps -a --filter name=openchamber_{session_user} --format '{{{{.Status}}}}'")
    if "Up" not in backend_running:
        if not load_image(IMAGE_NAME, IMAGE_TAG, IMAGE_FILE):
            return render_page(
                "系统错误",
                f"<h2>镜像加载失败</h2><p class='sub'>请检查镜像文件: {IMAGE_FILE}</p><a href='/' class='btn-ding'>返回重试</a>"
            )
        os.system(f"docker rm -f openchamber_{session_user} > /dev/null 2>&1")

        docker_cmd = (
            f'docker run -d --name openchamber_{session_user} --network openchamber_net '
            f'-v "{u_home}/data/openchamber:/home/openchamber/.config/openchamber" '
            f'-v "{u_home}/data/opencode/share:/home/openchamber/.local/share/opencode" '
            f'-v "{u_home}/data/opencode/state:/home/openchamber/.local/state/opencode" '
            f'-v "{u_home}/data/opencode/config:/home/openchamber/.config/opencode" '
            f'-v "{u_home}/data/ssh:/home/openchamber/.ssh" '
            f'-v "{u_home}/workspace:/home/openchamber/workspaces" '
            f'-e SERVICE_NAME={service_name} '  # 告知后端自己的服务名
            f'-e REGISTRY_ADDR={NACOS_ADDR} '   # 告知 Nacos 地址
            f'-e PUBLIC_IP={PUBLIC_IP} '        # 告知容器内的公网 IP
            f'-e AUTH_TOKEN={token} '
            f'{IMAGE_NAME}:{IMAGE_TAG}'
        )
        print(f"🔄 启动容器: {docker_cmd}")
        os.system(docker_cmd)

    # 2. 跳转到网关入口
    # 网关会自动根据路径中的 session_user 转发到对应的后端服务
    target_url = f"{GATEWAY_URL}/{service_name}/"
    content = f"""
        <div class="spinner"></div>
        <h2 style="margin-bottom: 4px;">环境准备就绪</h2>
        <p class="sub">正在进入专属工作空间...</p>
        <script>
            setTimeout(function() {{ window.location.href = "{target_url}"; }}, 10000);
        </script>
    """
    return render_page("加载中...", content, "", False)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)