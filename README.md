# 安徽拓达昇门业官网

静态站点源码仓库。零框架、零依赖构建（Python 标准库），内容层与展示层分离。

正式域名：**https://www.tdsdoor.com**

---

## 目录结构

| 路径 | 说明 |
|------|------|
| `src/build.py` | 构建脚本，读取内容层生成全站 HTML |
| `src/tools/gate_check.py` | 质量门禁（11 项检查：emoji / 硬编码色值 / 图片引用 / 布局等） |
| `content/content.json` | **内容层**，全站文字与产品数据的唯一来源 |
| `content/og-cover.jpg` | 社交分享封面（1200×630） |
| `site/` | 构建产物（18 页），同时提交进仓库，便于任何平台直接静态托管 |
| `site/admin/` | Sveltia CMS 网页后台（浏览器改内容） |
| `cms/sveltia-auth-worker.js` | 后台登录鉴权用的 Cloudflare Worker 源码 |
| `admin/server.py` | 本机后台（可选，双击 `启动后台.bat` 使用） |
| `.github/workflows/` | GitHub Actions：推送即自动构建 + 部署 |

---

## 本地使用

```bash
python src/build.py          # 生成全站到 site/
python src/tools/gate_check.py   # 跑质量门禁
```

> **重要**：修改任何产品图 / 新闻 / 案例，必须同时改 `content/content.json` 和 `src/build.py`。
> `content.json` 存在时优先级更高，只改 `build.py` 不生效。

---

## 后台改内容（两种方式）

### 方式一：Sveltia 网页后台（推荐，任何设备）

访问 `https://www.tdsdoor.com/admin/`，用 GitHub 账号登录，即可在线改新闻 / 产品 / 案例 / 图片。
保存后自动提交到本仓库 → 触发自动构建 → 全站更新。

前置配置（一次性）：
1. GitHub 注册 OAuth App（Settings → Developer settings → OAuth Apps → New OAuth App）
   - Homepage URL：`https://www.tdsdoor.com`
   - Authorization callback URL：`https://<你的Worker域名>/callback`
2. 部署 `cms/sveltia-auth-worker.js` 到 Cloudflare Worker，配置环境变量：
   - `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` / `ADMIN_URL`
3. 把 `site/admin/config.yml` 里的 `base_url` 改成实际 Worker 域名

### 方式二：GitHub 网页直接编辑（零配置，随时可用）

打开 `content/content.json` → 点右上角铅笔图标 → 改完点 Commit changes。
推送后自动触发构建和部署，约 1 分钟生效。

---

## 部署平台

### GitHub Pages（已配置，自动）
Settings → Pages → Source 选 **GitHub Actions**。推送 main 分支即自动构建部署。

### EdgeOne Pages（国内访问快，推荐正式使用）
控制台新建项目 → 导入本仓库 → 构建配置：
- 构建命令：`pip install Pillow && python src/build.py`
- 输出目录：`site`
- Node/Python 环境：Python 3.11

之后每次推送自动重新部署。

---

## 上线 checklist

- [ ] 域名 `tdsdoor.com` DNS 解析指向托管平台
- [ ] ICP 备案完成，回填页脚备案号（当前为 `皖ICP备XXXXXXXX号` 占位）
- [ ] Web3Forms `access_key` 替换（当前占位，表单不会真发邮件）
- [ ] 百度 / 搜狗 / 360 / 神马站长平台提交站点 + sitemap.xml
- [ ] 资质证书真实图片替换
