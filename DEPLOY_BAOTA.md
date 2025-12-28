# 宝塔面板 (Baota Panel) 部署指南

本指南将协助您将 TK Tools 部署到使用宝塔面板管理的 Linux 服务器上。

由于本项目使用 Streamlit 框架，属于长连接应用，且依赖 Tesseract OCR 等系统库，建议按照以下步骤进行部署。

---

## 🛠️ 第一步：安装系统依赖

PDF 拆分功能依赖 `tesseract` (OCR) 和 `poppler` (PDF处理)。请在宝塔面板的 **终端** 中执行以下命令安装：

**如果是 CentOS 系统：**
```bash
yum install epel-release -y
yum install tesseract -y
# 如果 yum 找不到 tesseract，可能需要编译安装或寻找其他源，
# 或者简单的只安装 poppler-utils (某些 PDF 库依赖它)
yum install poppler-utils -y
# 验证安装
tesseract --version
```

**如果是 Ubuntu/Debian 系统：**
```bash
apt-get update
apt-get install tesseract-ocr poppler-utils -y
# 验证安装
tesseract --version
```

> ⚠️ **注意**：如果未安装 Tesseract，PDF 拆分功能可能会报错。

---

## 📂 第二步：上传项目代码

1.  在本地将项目文件夹打包为 `tk-tools.zip` (排除 `venv` 和 `__pycache__` 文件夹)。
2.  进入宝塔面板 -> **文件**。
3.  进入 `/www/wwwroot/` 目录。
4.  上传并解压 `tk-tools.zip`。
5.  最终路径应为：`/www/wwwroot/tk-tools`。

---

## 🐍 第三步：配置 Python 环境

推荐使用宝塔的 **Python项目管理器** (如果未安装，请在软件商店安装)，或者直接在终端手动创建虚拟环境（更灵活，推荐）。

**手动创建虚拟环境方法：**

1.  打开宝塔终端，进入项目目录：
    ```bash
    cd /www/wwwroot/tk-tools
    ```

2.  创建虚拟环境 (假设服务器已安装 Python 3)：
    ```bash
    # 检查 python 版本，需 3.9+
    python3 --version 
    
    # 创建 venv
    python3 -m venv venv
    ```

3.  激活环境并安装依赖：
    ```bash
    # 激活
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装项目依赖 (建议使用国内源)
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

4.  验证运行：
    ```bash
    # 试运行 (按 Ctrl+C 退出)
    streamlit run app.py
    ```

---

## ⚙️ 第四步：配置进程守护 (Supervisor)

为了让应用在后台持续运行，我们需要使用宝塔的 **Supervisor管理器**。

1.  在宝塔软件商店安装 **Supervisor管理器**。
2.  添加守护进程：
    *   **名称**：`tk-tools`
    *   **启动用户**：`root` (或您指定的 www 用户)
    *   **运行目录**：`/www/wwwroot/tk-tools`
    *   **启动命令**：
        ```bash
        /www/wwwroot/tk-tools/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
        ```
    *   **进程数量**：1
3.  点击确定，确保存状态为 **Running (运行中)**。

---

## 🌐 第五步：配置域名与反向代理 (Nginx)

为了通过域名访问（如 `tools.example.com`），需配置 Nginx 反向代理。

1.  **添加站点**：
    *   宝塔面板 -> **网站** -> **添加站点**。
    *   域名：填写您的域名。
    *   PHP版本：纯静态。

2.  **设置反向代理**：
    *   点击刚创建的网站设置 -> **反向代理** -> **添加反向代理**。
    *   **代理名称**：`streamlit`
    *   **目标URL**：`http://127.0.0.1:8501`
    *   **发送域名**：`$host`
    *   点击提交。

3.  **配置 WebSocket (关键)**：
    Streamlit 依赖 WebSocket，默认的反向代理配置可能不支持。
    *   点击反向代理列表中的 **"配置文件"**。
    *   确保配置文件中包含以下内容（如果没有，请手动替换或添加）：

    ```nginx
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    ```

---

## 🚨 常见问题排查 (Troubleshooting)

### 1. 🔴 出现 "WebSocket connection to 'wss://...' failed" 错误

**现象**：
*   浏览器控制台报错：`WebSocket connection to 'wss://your-domain.com/_stcore/stream' failed`。
*   页面右下角显示 "Please wait..." 且无法加载内容。

**原因**：
Nginx 反向代理未正确转发 WebSocket 协议，或者 SSL 证书配置导致协议降级失败。

**解决方案**：

1.  **修改反向代理配置文件**：
    *   在宝塔面板 -> 网站设置 -> 反向代理 -> 点击 **"配置文件"**。
    *   **完整替换**配置文件内容为下方的标准配置：

    ```nginx
    # 代理所有请求
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 关键：WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    
    # 强制针对 Streamlit 的 WebSocket 路径进行配置 (备用方案)
    location ^~ /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    ```

2.  **检查 Cloudflare 设置**（如果使用了 Cloudflare）：
    *   确保 SSL/TLS 模式设置为 **"Full"** 或 **"Full (Strict)"**，不要使用 "Flexible"。
    *   尝试关闭 **"Rocket Loader"**。

### 2. 🔴 上传 PDF 报错 "TesseractNotFoundError"
请检查第一步系统依赖是否安装成功，并在终端输入 `tesseract --version` 验证。

### 3. 🟡 跨域 (CORS) 或 XSRF 报错
已在 `.streamlit/config.toml` 中默认禁用了 CORS 和 XSRF 保护。如果仍有问题，请尝试重启服务：
```bash
supervisorctl restart tk-tools
```
