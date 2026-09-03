# 安徽拓达昇门业官网 技术架构文档

- 项目：安徽拓达昇门业（合肥）企业官方网站
- 文档版本：v1.0（Phase 1 技术调研产出）
- 作者：架构师 高见远
- 状态：已定稿，供 Phase 2 设计与 Phase 3 开发执行
- 硬约束：静态优先（SEO 与加载速度最优）、浅色简约高级设计系统、非技术用户上线后可通过网页后台零代码编辑内容

---

## 0. 结论速览（一页看懂）

| 层 | 最终选型（锁定） | 版本锚定 | 成本 |
|----|------------------|----------|------|
| 站点框架 | Astro（静态生成 SSG） | astro ^6.1.1 | 免费开源 |
| 样式方案 | Tailwind CSS（配合设计系统令牌） | tailwindcss ^4.1 | 免费 |
| SVG 图标库 | Lucide（经 @lucide/astro 集成，全站唯一图标库） | @lucide/astro ^1.16.0 | 免费（ISC） |
| 内容管理后台 | Sveltia CMS（Git-based，自托管于 /admin） | @sveltia/cms 0.129.x（锁定次版本） | 免费（MIT） |
| 内容存储 | Markdown + JSON 文件（Git 仓库内，Astro Content Collections + Zod 校验） | — | 免费 |
| 表单邮件 | Web3Forms（提交转发至 82257018@qq.com） | 服务，无版本 | 免费 250 封/月 |
| 地图 | 腾讯位置服务 GL JS（用户自行申请 key） | gljs v1.exp | 免费配额 |
| 托管与部署 | 腾讯云 EdgeOne Pages（Git 集成自动构建） | 平台服务 | 免费额度 |
| CMS 登录认证 | sveltia-cms-auth OAuth Worker（部署于 Cloudflare Workers） | 社区项目，锁定发布版 | 免费额度 |
| 运行时 | Node.js LTS | v22.x（本机已装 22.22.2） | 免费 |

总计月度成本：0 元。年度成本：域名约 60–100 元/年（备案阶段才需要）。

> 版本锚定说明：npm 依赖在脚手架时由 `package-lock.json` 冻结精确版本；上表为约束区间。开发期一律按锁文件内实际版本编写代码，禁止按"通用印象"调用 API。

---

## 1. 选型对比矩阵

### 1.1 静态站框架（3 方案对比）

| 维度（权重） | Astro 6 | 纯手写 HTML / Python 模板 | VitePress |
|--------------|---------|--------------------------|----------|
| SEO 能力（高） | 每页产出纯静态 HTML，默认零客户端 JS，Lighthouse SEO/性能近满分 | 同样纯 HTML，但 meta/OG/sitemap 全靠手写易漏 | 面向文档站，主题结构不适合企业营销站 |
| 内容建模（高） | Content Collections + Zod：产品/新闻/案例有类型校验，内容文件与模板解耦 | 无内容模型，内容散落在 HTML 里，非技术用户无法编辑 | Markdown 优先，但集合/单例模型弱 |
| 后台 CMS 生态（高，决定性） | Sveltia/Decap 等 Git-based CMS 均有成熟 Astro 用法 | 需自研管理页，投入不成比例 | 可接 CMS 但案例少 |
| 本机环境（高） | Node 22 + npm，本机已具备；此前 pip 安装失败的教训不复发 | Python 3.13 可用，但纯模板方案维护靠人肉 | Node 可用 |
| 构建与部署（高） | EdgeOne Pages 官方明确支持 Astro 模板 | 需手动维护产物 | 支持，但定位文档站 |
| 图片管线（中） | 内置 sharp：构建期把现有 2MB PNG 压缩转 webp/avif 并生成多尺寸 | 无，需额外工具 | 一般 |
| 团队熟悉度/生态（中） | 2026 年内容型官网事实标准，文档完善 | — | — |

**结论：Astro 6。** 前期预研倾向成立，予以确认；现有 Python 模板产物（site/ 目录）仅作内容参考，全部按新设计系统重构，代码不迁移、内容人工抽取。

### 1.2 CMS 方案（3 方案对比，核心是"非技术用户编辑体验 + 部署约束"）

| 维度（权重） | A. Sveltia CMS（Git-based，Decap 的现代继任者） | B. 飞书多维表格当 headless 数据源（Astro 构建期拉取） | C. 本地 JSON + 简单管理页（自研） |
|--------------|-----------------------------------------------|------------------------------------------------------|-----------------------------------|
| 非技术用户编辑体验（高） | 浏览器打开 `网站/admin`，表单化编辑 + 图片上传 + 富文本，点"发布"即上线，全流程零代码、零 Git 感知 | 类 Excel 表格编辑，体验尚可，但换封面图需处理附件外链问题 | 自研界面质量不可控，维护成本最高 |
| 图片管理（高） | 上传图片自动提交进 Git 仓库并走构建管线压缩 | 飞书附件不可公开外链，图片方案是硬伤 | 需自建上传与存储 |
| 内容版本与安全（中高） | 每次编辑即 Git 提交，天然版本历史、可回滚 | 内容在第三方 SaaS，不在仓库 | 取决于实现 |
| 部署联动（中高） | 发布提交自动触发 EdgeOne Pages 重新构建 | 表格变更不触发构建，需额外飞书自动化调 Webhook，链路长且脆 | 需自研同步 |
| 实现成本（高） | 配置文件驱动（config.yml），约 1–2 天集成 | 需要飞书开放平台建应用、token 管理、自定义 Loader，3–5 天 | 5 天以上且长期维护 |
| 国内可用性（中） | 后端为 GitHub（存在访问波动风险，见第 8 节风险 R1） | 飞书国内可用性好 | 好 |

**结论：方案 A，Sveltia CMS。** 决定性理由：编辑体验、图片管理、发布联动三者同时满足，且配置与 Decap CMS 兼容（保留退路）。

**对前期"Decap CMS"倾向的裁决：修正。** Decap CMS 官方投入衰退、UI 陈旧、社区已大规模迁往 Sveltia（Sveltia 为其直接替代品，配置文件兼容，仅改一行 script 引用即可切换）。选 Sveltia，弃 Decap。

**部署约束可行性验证（重点）**：Decap/Sveltia 类 CMS 的后端是 Git 仓库（GitHub），无需自建服务器，与"静态托管 + EdgeOne Pages"完全兼容——CMS 在浏览器里通过 GitHub API 提交内容文件，EdgeOne Pages 检测到推送后自动重建站点。唯一前置条件：一个 GitHub 账号 + 一个 OAuth Worker（登录用），均为免费。**结论：可行，"用户可自行编辑"能落地。**

### 1.3 表单邮件方案（3 方案对比）

| 维度（权重） | Web3Forms | Formspree | 自建 mailto / 自建后端发信 |
|--------------|-----------|-----------|---------------------------|
| 免费额度（高） | 250 封/月，无限表单 | 50 封/月 | 无限额（但见右列） |
| 接入成本（高） | 注册取 Access Key，一个 fetch POST 完成 | 需建表单取 endpoint，免费版功能少 | mailto 在移动端/网页邮箱基本不可用，直接否决；自建后端违背静态优先与 MVP 原则 |
| 反垃圾（中高） | 内置 botcheck + Honeypot，免费含 hCaptcha | ML Formshield + reCAPTCHA | 无 |
| 提交记录（中） | 免费版 30 天历史，转发即删 | 免费版 30 天历史 | — |
| 国内连通性（中） | api.web3forms.com 为海外端点，国内访问总体可用但存在波动（风险 R2，有替代预案） | 同为海外端点 | — |

**结论：Web3Forms。** 企业官网询盘量级（每月数十封）下免费额度绰绰有余；附带honeypot 反垃圾与自动回执。备用预案见 8.2 节。

### 1.4 SVG 图标库（3 方案对比，全站锁定一套）

| 维度（权重） | Lucide | Feather | Tabler Icons |
|--------------|--------|---------|--------------|
| 图标数量与场景覆盖（高） | 1500+，含工业/工程/商务场景所需（门、齿轮、盾牌、电话、邮件、地图钉等） | 约 280，数量不足以覆盖全站 | 5000+，数量最多但风格略松散 |
| 统一描边风格（高） | 24x24 / 2px 描边，与"浅色简约高级"设计系统天然匹配 | 同源风格（Lucide 即 Feather 的社区延续） | 混合风格需筛选 |
| 维护活跃度（高） | lucide-icons 组织活跃维护，@lucide/astro 官方 Astro 集成（当前 1.16.0） | 事实停更 | 活跃 |
| 中文场景适配（中） | 纯线性图标无文化歧义，搭配中文排版间距正常 | 同左 | 同左 |
| 引入方式（中） | @lucide/astro 组件化按需引入，构建期内联 SVG，零运行时 JS | 需自行处理 | 需自行处理 |

**结论：Lucide，经 @lucide/astro 集成。全项目唯一图标库，禁止混用其他来源图标与任何 emoji 图标（P0 规则）。**

### 1.5 地图方案（含中国地图合规裁决）

合规红线（地图合规守则）：仅允许 腾讯位置服务、高德、百度地图、天地图。Google Maps、Mapbox、OpenStreetMap、Leaflet+OSM 瓦片等一律禁止。

| 维度（权重） | 腾讯位置服务 GL JS | 高德开放平台 JS API | 百度地图 JS API |
|--------------|--------------------|---------------------|-----------------|
| 合规资质（高） | 具备审图号，合规 | 合规 | 合规 |
| 与本项目栈协同（高） | 站点托管在腾讯 EdgeOne，账号体系统一，同为腾讯生态 | 独立账号体系 | 独立账号体系 |
| Web 端 JS API 免费配额（中高） | 个人/企业认证开发者有免费日调用量配额，企业官网展示场景远够用 | 同类配额，够用 | 同类配额，够用 |
| key 安全（中高） | 支持域名 Referer 白名单 | 支持 | 支持 |
| 文档与示例质量（中） | 官方 GL JS 文档完善 | 完善 | 完善 |

**结论：腾讯位置服务 GL JS。** 用户在 lbs.qq.com 注册并申请 Web 端（GL JS）key，配置域名白名单；坐标一律使用 GCJ-02。项目代码中不得内置任何真实 key（构建时以环境变量/占位符注入，见 7.3 节）。WorkBuddy 开发预览环境可用其 key 代理模式联调，生产环境使用用户自有 key。

### 1.6 托管部署（3 方案对比）

| 维度（权重） | 腾讯云 EdgeOne Pages | Cloudflare Pages | Vercel / Netlify |
|--------------|----------------------|------------------|------------------|
| 国内访客访问速度（高，决定性） | 备案域名可启用中国大陆节点（2300+ 节点），延迟 50–90ms；未备案走海外节点仍稳定 | 国内晚高峰波动大（实测 800ms+） | 国内访问差或不稳定 |
| 免费额度（高） | 长期免费：不限静态流量与请求，每月定额构建/函数/KV（控制台实时可见，企业官网量级足够） | 免费额度大 | 免费额度可用 |
| Git 自动构建（高） | 支持 GitHub / Gitee / Coding 仓库接入，推送自动部署 | 仅 GitHub/GitLab | 仅 GitHub/GitLab |
| 备案与域名（高） | 腾讯云体系内完成 ICP 备案 + 域名 + SSL 自动签发，链路最短 | 备案链路不顺 | 同左 |
| 静态 + 边缘函数（中） | 支持（本项目基本不需要，仅留作表单备用预案） | 支持 | 支持 |

**结论：腾讯云 EdgeOne Pages（国内站，edgeone.cloud.tencent.com）。** 决定性理由：目标访客为国内 B 端客户，备案后大陆节点速度优势是其他方案不可替代的；且与本地图（腾讯位置服务）形成统一腾讯生态。

---

## 2. 总体架构与站点结构

### 2.1 架构图

```
                    ┌─────────────────────────────────────────────┐
                    │                内容生产链路                   │
                    │                                             │
  用户（非技术） ──► │  浏览器打开 站点/admin（Sveltia CMS 自托管页） │
                    │        │ 登录：GitHub OAuth（Cloudflare      │
                    │        │       Workers 上的 sveltia-cms-auth）│
                    │        ▼                                     │
                    │  GitHub 私有仓库（内容 Markdown/JSON + 图片）  │
                    └────────┬────────────────────────────────────┘
                             │ push 触发自动构建
                    ┌────────▼────────────────────────────────────┐
                    │              构建与发布链路                   │
                    │  EdgeOne Pages CI：npm ci → astro build      │
                    │  （Astro 6 + Content Collections + sharp）    │
                    │        │ 产出纯静态 HTML/CSS/图片             │
                    │        ▼                                     │
                    │  EdgeOne 全球边缘网络（备案后启用大陆节点）      │
                    └────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────────┐
              ▼              ▼                  ▼
        站点访客（国内 B 端）  联系表单 POST      地图/瓦片请求
              │              │                  │
              │              ▼                  ▼
              │        Web3Forms API      腾讯位置服务 GL JS
              │              │                  │
              │              ▼                  │
              │      邮件投递 82257018@qq.com    │
              └──────────────────────────────────┘

  开发者链路（本机 Windows + Node 22）：astro dev 本地预览 → git push → 自动部署
```

要点：全站无自建服务器、无数据库、无运行时后端。唯一两处第三方运行时依赖：Web3Forms（表单）与腾讯位置服务（地图），均为可替换的外部端点。

### 2.2 页面路由表（站点地图）

| 路由 | 页面 | 数量 | 生成方式 |
|------|------|------|----------|
| `/` | 首页（Banner、主营产品、精选案例、公司简介、新闻速览、联系方式摘要） | 1 | 静态 |
| `/about/` | 关于我们（公司介绍、资质证书、厂区、发展历程） | 1 | 静态 |
| `/products/` | 产品总览（4 分类导航 + 全部产品卡片） | 1 | 静态 |
| `/products/[category]/` | 产品分类列表页 | 4 | getStaticPaths 按 categories 集合生成 |
| `/products/[category]/[slug]/` | 产品详情页 | 6（首批） | getStaticPaths 按 products 集合生成 |
| `/cases/` | 案例列表页 | 1 | 静态 |
| `/cases/[slug]/` | 案例详情页 | 按内容量 | getStaticPaths 按 cases 集合生成 |
| `/news/` | 新闻列表页（分页，每页 10 条） | 1+ | getStaticPaths 分页 |
| `/news/[slug]/` | 新闻详情页 | 按内容量 | getStaticPaths 按 news 集合生成 |
| `/contact/` | 联系我们（腾讯地图 + 询盘表单 + 联系信息） | 1 | 静态 |
| `/404` | 404 页 | 1 | 静态 |
| `/admin/` | Sveltia CMS 管理后台 | 1 | 纯静态 SPA（不索引，robots 禁抓） |

分类 slug 沿用现有内容命名（拼音/英文，SEO 友好且 URL 稳定）：
`electric-roller`（电动卷帘门）、`fireproof`（防火门类）、`retractable`（伸缩门类）、`smart-access`（智能通道类）。具体分类归属以 PM 的内容清单为准，此处为路由占位。

---

## 3. 内容数据模型（CMS 编辑的基础）

所有内容以文件形式存于 Git 仓库，由 `src/content.config.ts` 中 Zod Schema 做构建期强校验——**Schema 即前后端契约**（本项目无自研 REST API，OpenAPI 不适用；契约载体为：content.config.ts 的 Zod Schema、public/admin/config.yml 的 CMS 字段配置、6.1 节的表单提交契约）。

### 3.1 categories（产品分类，JSON 文件集合）

```jsonc
// src/content/categories/electric-roller.json
{
  "name": "电动卷帘门",          // 导航与列表页标题
  "description": "工业厂房与仓储出入口电动卷帘门系列",  // 列表页导语（<=120字）
  "cover": "/uploads/categories/electric-roller.jpg",
  "order": 1                     // 前台排序，数字小的在前
}
```

文件名即 slug（URL 段）。Zod：`name: z.string()`、`description: z.string().max(160)`、`cover: z.string()`、`order: z.number().int().default(99)`。

### 3.2 products（产品，Markdown 集合，正文为详情富文本）

```yaml
# src/content/products/pvc-fast-door.md
---
title: "PVC 快速卷帘门"
category: "electric-roller"       # 关联 categories id
summary: "高频次出入场景的高速隔离门，开启速度可达 2m/s"  # 卡片与 meta description（<=150字）
cover: "/uploads/products/pvc-fast-door/cover.jpg"
gallery:                          # 详情页图集（0-8 张）
  - "/uploads/products/pvc-fast-door/01.jpg"
specs:                            # 规格参数表（键值对，按序渲染）
  - { name: "开启速度", value: "0.8-2.0 m/s" }
  - { name: "门体材质", value: "工业基布 / 铝合金" }
features:                         # 核心卖点（3-6 条，列表页也取前 3 条）
  - "伺服电机驱动，运行平稳低噪"
order: 1
published: true                   # false 则构建时过滤，不产出页面
---
（正文：产品详情 Markdown，支持图片与表格）
```

### 3.3 cases（工程案例，Markdown 集合）

```yaml
---
title: "合肥某汽车零部件厂房快速门项目"
industry: "汽车制造"               # 行业标签
location: "安徽 合肥"             # 项目地点
products_used: ["pvc-fast-door"]  # 关联产品 id，可选
cover: "/uploads/cases/xxx/cover.jpg"
summary: "为该项目交付 12 樘快速卷帘门..."   # 列表卡片文案
date: 2026-03-15                  # 用于排序
---
（正文：项目背景、方案、实施效果）
```

### 3.4 news（新闻动态，Markdown 集合）

```yaml
---
title: "拓达昇门业参加 2026 合肥工业装备展"
date: 2026-04-01
cover: "/uploads/news/xxx.jpg"    # 可选
summary: "..."                    # 列表摘要（<=150字）
tags: ["展会", "公司动态"]
draft: false
---
（正文）
```

### 3.5 company（公司信息单例，单文件集合）

```jsonc
// src/content/company.json —— 全站复用：页头页脚、关于页、联系页、JSON-LD
{
  "name": "安徽拓达昇门业有限公司",
  "shortName": "拓达昇门业",
  "tagline": "工业门制造与安装服务",
  "phone": "0551-XXXXXXXX",        // 座机（占位，以 PM 清单为准）
  "mobile": "1XXXXXXXXXX",
  "email": "82257018@qq.com",
  "address": "安徽省合肥市XX区XX路XX号",
  "geo": { "lat": 31.820587, "lng": 117.227244 },  // GCJ-02 坐标（地图打点用，交付前现场核准）
  "icp": "",                       // 备案号（备案下来后回填，页脚展示）
  "about": { "intro": "...", "history": [...], "stats": [...] },
  "qualifications": [ { "name": "XXX 资质", "image": "/uploads/quals/01.jpg" } ]
}
```

### 3.6 媒体约定

- CMS 上传目录：`public/uploads/<集合>/<条目>/`，Sveltia 的 media_folder 指向 `public/uploads`。
- 图片入库前约定：单图不超过 500KB（CMS 端无自动压缩，需在文档中约束编辑者；原始 2MB PNG 由开发期统一经 sharp 管线压缩入库）。
- 构建期由 Astro `<Image>` 组件统一转 webp 并生成响应式尺寸，首屏大图懒加载。

---

## 4. 目录结构与代码组织约束

```
project_002_公司官方网站/
├── astro.config.mjs              # 只做装配：site URL、sitemap 集成、图片配置
├── package.json / package-lock.json
├── public/
│   ├── admin/
│   │   ├── index.html            # Sveltia CMS 挂载页
│   │   ├── config.yml            # CMS 集合配置（与 content.config.ts 字段一一对应）
│   │   └── sveltia-cms.js        # 自托管 bundle（不走海外 CDN，国内可用性）
│   ├── uploads/                  # CMS 上传媒体（入 Git）
│   └── favicon.svg
├── src/
│   ├── content.config.ts         # 全部内容集合 Zod Schema（单一契约源）
│   ├── content/
│   │   ├── categories/*.json
│   │   ├── products/*.md
│   │   ├── cases/*.md
│   │   ├── news/*.md
│   │   └── company.json
│   ├── layouts/
│   │   └── BaseLayout.astro      # HTML 骨架 + SEO 头部装配（<200 行）
│   ├── components/
│   │   ├── ui/                   # Button / SectionTitle / Card / Breadcrumb / Pagination
│   │   ├── nav/                  # Header（含移动端菜单）/ Footer
│   │   ├── home/                 # 首页各区块组件（一区块一文件）
│   │   ├── product/              # ProductCard / SpecTable / Gallery
│   │   ├── form/                 # ContactForm.astro + contact-form.ts（提交逻辑）
│   │   ├── map/                  # TencentMap.astro + tencent-map.ts（key 注入与打点）
│   │   └── seo/                  # SeoHead / JsonLd（Organization/Product/Article/Breadcrumb）
│   ├── pages/                    # 仅路由与数据组装，不写展示细节（见 2.2 路由表）
│   ├── scripts/                  # 少量原生 TS（表单、地图、移动菜单），零框架运行时
│   ├── styles/global.css         # Tailwind 入口 + 设计令牌（颜色/字体/间距来自设计系统）
│   └── utils/                    # 纯函数：日期格式化、分页切片、路径拼接
├── docs/
│   ├── ARCHITECTURE.md           # 本文档
│   └── decisions/ADR-00X-*.md    # 选型决策记录
└── site/                         # 旧版 Python 模板产物（只读参考，重构完成后归档删除）
```

硬规则（Phase 3 门禁，违反即退回）：

1. 单文件不超过 300 行（不含空行注释）；页面文件只做数据获取与组件组装。
2. 依赖方向：`pages → components/layouts → content/utils`；utils 只放纯函数。
3. 设计令牌（颜色、字体、间距、圆角、阴影）只定义在 `global.css` 的 Tailwind 主题层，组件内禁止散落魔法值。
4. 图标一律 `import { X } from '@lucide/astro'`，禁止引入其他图标来源，禁止 emoji 充当功能图标。
5. SEO 三件套（title/description/canonical/OG）与 JSON-LD 由 SeoHead/JsonLd 组件统一产出，页面只传参，禁止手写 head。

---

## 5. 集成方案细节

### 5.1 表单（Web3Forms）

- 端点：`POST https://api.web3forms.com/submit`，JSON body：`access_key`（构建期由环境变量 `WEB3FORMS_KEY` 注入，不硬编码进仓库）、`name`、`phone`、`email`（可选）、`company`（可选）、`message`、隐藏字段 `botcheck`（honeypot）。
- 交互：原生 `fetch` 异步提交，成功/失败均为行内提示，不跳页；提交按钮置防重复提交。
- 必填校验：姓名、电话（前端 pattern + 服务端 botcheck 双层）；电话做 `tel:` 链接直呼。
- 收件：82257018@qq.com（Web3Forms 后台绑定 Access Key 与邮箱，首封激活邮件需点击确认）。
- 失败路径（错误分支必须实现，禁止只写 happy path）：网络失败/非 2xx 时展示"提交失败，请直接致电"兜底文案 + 联系电话。

### 5.2 地图（腾讯位置服务 GL JS）

- 容器：联系页固定高度容器（`height` 必须显式，flex 布局下 0 高会导致白屏）。
- key：申请入口 lbs.qq.com 控制台，创建 Web 端（GL JS）key，域名白名单配置为正式域名 + 预览域名。代码中以 `data-site-key` 占位注入，构建/部署时替换，仓库内不得出现真实 key。
- 打点：`TMap.MultiMarker` 标注公司位置（company.geo 的 GCJ-02 坐标），地图懒加载（进入视口才加载 SDK，保障性能分）。
- 合规自检：仅使用腾讯官方底图与样式，不传 `mapStyleId`（避免白图），不自绘边界数据。

### 5.3 SEO 基础设施

- 每页：唯一 title（页面名 - 拓达昇门业）、meta description（取 summary）、canonical、OG 标签（og:title/og:description/og:image/og:type）、移动视口。
- JSON-LD：全站 `Organization`（含地址/电话，来自 company.json）；产品详情 `Product`；新闻详情 `Article`；面包屑 `BreadcrumbList`。
- `@astrojs/sitemap` 生成 sitemap-index.xml；robots.txt 放行全部页面、指向 sitemap、禁止 `/admin/`。
- 性能基线：首页 LCP < 2.5s（4G），总 JS < 50KB（原生 TS + 地图 SDK 懒加载），图片走 webp。

### 5.4 CMS（Sveltia）运行链路

1. 用户访问 `https://域名/admin/`（自托管 Sveltia bundle，无海外 CDN 依赖）。
2. 登录：GitHub OAuth，经部署在 Cloudflare Workers 的 sveltia-cms-auth Worker（免费额度 10 万请求/日，本项目用量可忽略）。
3. 编辑：按 config.yml 渲染表单（产品/新闻/案例/公司信息），图片直接上传进仓库。
4. 发布：保存即提交到 GitHub main 分支 → EdgeOne Pages 自动构建 → 约 1–3 分钟后线上生效。
5. 权限控制：仓库设为私有，仅公司持有的 GitHub 账号有写权限；EdgeOne Pages 构建凭据独立授权，最小化权限。

---

## 6. 部署与域名规划（临时预览 → 备案 → 绑定）

| 阶段 | 域名 | 加速区域 | 说明 |
|------|------|----------|------|
| 阶段 1 开发期 | 本机 `localhost:4321`（astro dev） | — | 每日开发预览，Windows 本机 Node 22 |
| 阶段 2 交付预览 | EdgeOne Pages 默认域名 `*.edgeone.app` | 全球（不含中国大陆节点） | 无需备案即可访问，供甲方验收；国内访问可用但延迟较高 |
| 阶段 3 备案 | 腾讯云注册域名（.com/.cn，约 60–100 元/年）→ 腾讯云 ICP 备案（免费，通常 2–4 周） | — | 备案期间站点继续走默认域名 |
| 阶段 4 正式上线 | 自定义域名绑定 EdgeOne Pages，加速区域切换"中国大陆" | 中国大陆 + 全球 | SSL 自动签发；备案号回填 company.json 页脚；地图 key 域名白名单更新 |

npm 网络注意：本机此前出现过 pip 网络受限。Node 侧规避方案：`npm config set registry https://registry.npmmirror.com` 使用国内镜像；Sveltia bundle 亦自托管不依赖 jsdelivr 等 CDN。

---

## 7. 风险与不可行警告

| # | 风险/不可行项 | 等级 | 影响 | 对策 |
|---|--------------|------|------|------|
| R1 | GitHub 国内访问波动，导致用户偶发打不开 /admin 或登录失败 | 高（CMS 编辑通道核心风险） | 用户无法自助编辑 | 三层缓解：(a) Sveltia bundle 与 OAuth Worker 均自托管/独立 Worker，规避 CDN 波动；(b) 提供第二编辑通道——通过本 AI 工作区直接改内容文件后推送，同样零代码；(c) 若 GitHub 长期不可用，退路见 R1-fallback |
| R1-fallback | 若 GitHub 通道被验证长期不可用：内容仓库迁 Gitee（EdgeOne Pages 国内站原生支持 Gitee），此时 Git-based CMS 无 Gitee 后端支持，编辑通道降级为"AI 助手维护"或升级飞书多维表格方案（成本 +3~5 天） | 中 | 编辑体验降级 | 决策点：上线后 2 周内实测 GitHub 编辑成功率，低于 80% 触发本预案 |
| R2 | Web3Forms 海外端点在国内提交偶发超时 | 中 | 询盘丢失 | 表单失败分支展示电话兜底；若月失败率 >5%，切换 EdgeOne Pages Function + 腾讯云 SES 邮件推送（国内链路，预计 +1 天开发，邮件费用极低） |
| R3 | 现有 7 张 PNG 每张约 2MB，直接上线拖垮性能 | 高（可控） | LCP 超标、SEO 扣分 | 开发期统一经 sharp 压缩为 webp（目标单图 <150KB）；CMS 上传约束 <500KB/张写入交付文档 |
| R4 | Sveltia CMS 处于 0.129.x beta（1.0 预计近期发布） | 低中 | 潜在 bug | 自托管锁定次版本不变更；配置兼容 Decap，极端情况可一行切回 Decap |
| R5 | 未备案前自定义域名无法启用大陆节点 | 必然发生（流程性） | 上线初期国内访问延迟 0.7–1.4s | 预览期用 *.edgeone.app；备案与开发并行启动，压缩空窗 |
| R6 | 地图 key 前端暴露被刷量 | 低 | 配额耗尽 | 域名 Referer 白名单；企业认证提升配额；展示型单点场景调用量极小 |
| R7 | 紫粉渐变、emoji 图标、AI 模板味文案（P0 规则） | 禁止项 | — | 架构已锁定 Lucide 单一图标库；设计系统约束交由设计师执行；文案由 PM 把关 |

明确不可行清单（不做）：

- WordPress / 动态 CMS / 自建数据库后台——违背静态优先与零服务器成本约束，否决。
- Decap CMS——维护停滞，被 Sveltia 完全替代，否决。
- mailto 表单——移动端与网页邮箱基本不可用，否决。
- Google Maps / Mapbox / OSM——不符合中国地图合规要求，否决。
- Notion / 海外 headless CMS 作内容源——国内访问不可靠且图片外链受限，否决。

---

## 8. 端到端验证步骤（Phase 3 完成定义）

1. `npm run build && npm run preview`：全站构建零报错，路由表 2.2 中所有页面返回 200。
2. Lighthouse（移动端）抽检首页/产品详情/新闻详情：SEO >= 95、性能 >= 90、无障碍 >= 90。
3. 内容校验：故意提交一份缺 `category` 的产品 md → 构建必须报错（验证 Zod 契约生效）。
4. 表单：本地填表提交 → 82257018@qq.com 收到邮件；断网状态提交 → 展示电话兜底文案（验证错误分支）。
5. CMS：浏览器打开 `/admin/` → GitHub 登录 → 修改一条新闻标题 → 发布 → 3 分钟内线上生效（验证完整内容生产闭环，这是本项目最关键验收项）。
6. 地图：联系页进入视口加载地图并正确打点公司位置（GCJ-02 坐标无偏移）。
7. 响应式：375px / 768px / 1440px 三档断点走查导航、卡片、表格、表单。
8. SEO 产物：`sitemap-index.xml` 可访问、robots.txt 禁 /admin/、首页 HTML 含 Organization JSON-LD。

---

## 9. 选型决策记录（ADR 索引）

| ADR | 决策 | 一句话理由 |
|-----|------|-----------|
| ADR-001 | Astro 6 作站点框架 | 静态优先 + 内容集合 + CMS 生态三项最优 |
| ADR-002 | Sveltia CMS 替代 Decap | Decap 停滞；Sveltia 配置兼容且活跃，保留退路 |
| ADR-003 | EdgeOne Pages 托管 | 备案后大陆节点速度无可替代，免费额度足够 |
| ADR-004 | Web3Forms 表单 | 免费额度大、接入成本最低，附国内链路备选 |
| ADR-005 | Lucide 图标库 | 统一描边、活跃维护、官方 Astro 集成 |
| ADR-006 | 腾讯位置服务地图 | 合规白名单内 + 与托管栈同生态 |
| ADR-007 | Tailwind CSS 4 | 设计令牌工程化落地，构建期裁剪零运行时 |
| ADR-008 | 内容即 Git 中的 Markdown/JSON | 版本化、可校验、CMS/SSG 通用底座 |

完整 ADR 见 `docs/decisions/` 目录（MADR 格式，每条一文件）。

---

## 10. 本次不做（Out of Scope）

- 多语言站点（中英双语）——MVP 不做，结构上预留集合按语言扩展的可能。
- 在线询价单管理后台/CRM 集成——询盘直接进邮箱，不做系统化管理。
- 站内搜索——页面量（约 20 页）不需要，导航分类覆盖。
- 产品 3D 展示/视频——图片静态展示为主。
- 深度数据分析——最多预留一个统计脚本挂载位（备案后决定是否接入）。
