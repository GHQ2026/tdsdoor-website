# 集成契约文档：安徽拓达昇门业官网（零构建静态站）

- 文档版本：v1.0
- 适用项目：安徽拓达昇门业科技有限公司官方网站（初版，零构建静态 HTML/CSS）
- 文档角色：集成契约（Integration Contract）
- 作者：后端工程师 贝洛奇
- 状态：供前端实现与后续运维 / 用户接入时作为权威配置依据
- 关联文档：`ARCHITECTURE.md`（技术架构）、`SPEC.md`（功能契约）、`UIUX.md`（设计系统）

---

## 0. 文档用途与范围

本期官网是**零构建静态站**：直接由浏览器运行的 HTML / CSS，没有传统后端服务、没有数据库、没有运行时 API 服务器。全站唯一的"外部运行时依赖"只有两处，本契约把它们固化成可复制的配置：

1. **联系表单** —— 借助 Web3Forms 把用户提交的内容以邮件形式投递到 `82257018@qq.com`，无需自建邮件服务。
2. **地图嵌入** —— 借助腾讯位置服务 GL JS 在联系页展示公司位置（中国地图合规白名单内），禁止 Google Maps / Mapbox / OpenStreetMap 直接嵌国内底图。

此外，静态站的可发现性依赖 **SEO 基础设施**（robots / sitemap / JSON-LD / 每页 meta），这部分也在本文给出可直接落盘的文件内容。

本文档与前端现有占位实现的对应关系：
- 前端已在联系页写好**表单占位**与**电话直拨兜底**，本文给出接入真实 Web3Forms 的字段契约与代码。
- 前端已在联系页写好**地图占位区块**，本文给出接入真实腾讯地图 key 的嵌入代码。
- 前端已按设计系统（蓝 `#0B4F8C` / 橙 `#E8922A`）实现视觉，本文不涉及配色（禁止紫粉渐变，遵循 P0 规则）。

> 禁止项（P0 规则，全文遵守）：文档内不使用 emoji 充当图标描述（改用文字如"电话图标"）；不给出紫粉渐变配色建议；不使用 Lorem ipsum 类空洞占位文案，占位内容一律标注"示例，可在后台替换"。

---

## 1. 联系表单（Web3Forms 方案）

### 1.1 申请 access_key 步骤

1. 打开 https://web3forms.com ，在首页输入框填入接收邮箱 `82257018@qq.com`，点击"Get Access Key"（免费）。
2. 系统会向该邮箱发送一封**激活邮件**，点击邮件中的确认链接完成 Access Key 激活（首封激活前投递不生效）。
3. 激活后，注册邮箱会收到包含 `access_key`（一段 32 位十六进制字符串）的欢迎邮件。复制该值。
4. 登录 https://web3forms.com/dashboard ，在 Access Key 设置里确认：
   - 收件邮箱为 `82257018@qq.com`；
   - 免费版额度为 **250 封 / 月**（企业官网询盘量级足够）；
   - 已开启 botcheck / Honeypot 反垃圾（默认开启）。
5. 将 `access_key` 替换到前端表单隐藏域 `name="access_key"` 的值中（详见 1.2）。

> 说明：Web3Forms 的 `access_key` 本就设计为**前端可见**（写入表单隐藏域），这是其正常工作方式，无需担心泄露；但建议接入后保持代码仓库私有，避免被他人冒用你的额度。

### 1.2 完整 HTML 表单代码（含 AJAX 提交与失败兜底）

下方的代码是接入真实服务的**权威实现**，可直接复制到联系页表单区块。它做了三件事：
- 通过 `fetch` 异步 POST 到 `https://api.web3forms.com/submit`，不跳页；
- honeypot（`botcheck` 复选框，默认隐藏且必须保持未勾选）拦截机器人；
- 成功 / 失败均为行内提示；**网络失败或非 2xx 时展示电话直拨兜底**（与页面已有兜底一致）。

```html
<!-- ========== 联系表单：Web3Forms 接入 ========== -->
<style>
  .hidden-botcheck { position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0; }
  .form-status { margin-top: 12px; font-size: 14px; }
  .form-status.ok { color: #0B4F8C; }
  .form-status.err { color: #C0392B; }
</style>

<form id="contact-form" novalidate>
  <!-- 投递密钥：替换为 1.1 申请的 access_key -->
  <input type="hidden" name="access_key" value="YOUR_WEB3FORMS_ACCESS_KEY">
  <!-- 邮件主题与发件人名 -->
  <input type="hidden" name="subject" value="拓达昇门业官网 - 新咨询">
  <input type="hidden" name="from_name" value="拓达昇门业官网">
  <!-- honeypot：必须保持未勾选，机器人常会误填 -->
  <input type="checkbox" name="botcheck" class="hidden-botcheck" tabindex="-1" autocomplete="off">

  <div class="field">
    <label for="cf-name">姓名 <span aria-hidden="true">*</span></label>
    <input type="text" id="cf-name" name="name" required maxlength="40" placeholder="请输入您的称呼">
  </div>

  <div class="field">
    <label for="cf-company">公司</label>
    <input type="text" id="cf-company" name="company" maxlength="60" placeholder="公司名称（选填）">
  </div>

  <div class="field">
    <label for="cf-phone">电话 <span aria-hidden="true">*</span></label>
    <input type="tel" id="cf-phone" name="phone" required pattern="[0-9+\- ]{6,20}"
           placeholder="如 136 7551 2533" autocomplete="tel">
  </div>

  <div class="field">
    <label for="cf-message">需求 <span aria-hidden="true">*</span></label>
    <textarea id="cf-message" name="message" required maxlength="1000" rows="4"
              placeholder="请描述您的门型需求、数量、使用场景等"></textarea>
  </div>

  <button type="submit" id="cf-submit">提交咨询</button>
  <p id="form-status" class="form-status" role="status" aria-live="polite"></p>
</form>

<script>
  (function () {
    var form = document.getElementById('contact-form');
    var status = document.getElementById('form-status');
    var btn = document.getElementById('cf-submit');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      status.textContent = '';
      status.className = 'form-status';

      // 前端必填校验（与服务端 botcheck 双层）
      if (!form.name.value.trim() || !form.phone.value.trim() || !form.message.value.trim()) {
        status.textContent = '请填写姓名、电话与需求后再提交。';
        status.className = 'form-status err';
        return;
      }

      var data = new FormData(form);
      btn.disabled = true;
      btn.textContent = '提交中…';

      // 超时兜底：8 秒未响应即视为失败，引导电话直拨
      var controller = new AbortController();
      var timer = setTimeout(function () { controller.abort(); }, 8000);

      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        body: data,
        headers: { 'Accept': 'application/json' },
        signal: controller.signal
      })
        .then(function (res) { return res.json(); })
        .then(function (json) {
          clearTimeout(timer);
          if (json.success) {
            status.textContent = '提交成功，我们会尽快与您联系。';
            status.className = 'form-status ok';
            form.reset();
          } else {
            throw new Error(json.message || '投递失败');
          }
        })
        .catch(function () {
          clearTimeout(timer);
          // 失败兜底：电话直拨提示（与页面已有兜底一致）
          status.innerHTML = '提交失败，请直接拨打 136 7551 2533 或发邮件至 82257018@qq.com。';
          status.className = 'form-status err';
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = '提交咨询';
        });
    });
  })();
</script>
```

### 1.3 字段契约表（前后端一致）

| 字段名 | 类型 | 必填 | 说明 | 校验 |
|--------|------|------|------|------|
| `access_key` | hidden | 是 | Web3Forms 密钥，替换占位 | 非空 |
| `subject` | hidden | 是 | 收件箱邮件主题 | 固定值 |
| `from_name` | hidden | 是 | 发件人名 | 固定值 |
| `botcheck` | checkbox(hidden) | 逻辑必空 | honeypot 反垃圾 | 必须未勾选 |
| `name` | text | 是 | 姓名 | 非空，≤40 字 |
| `company` | text | 否 | 公司 | ≤60 字 |
| `phone` | tel | 是 | 电话 | `pattern [0-9+\- ]{6,20}` |
| `message` | textarea | 是 | 需求 | 非空，≤1000 字 |

### 1.4 失败兜底说明

- 触发条件：网络不可达、Web3Forms 海外端点偶发超时（见风险 R2）、返回非 success。
- 兜底行为：`catch` 分支展示"提交失败，请直接拨打 136 7551 2533 或发邮件至 82257018@qq.com"，并保留电话图标直拨入口（页面已实现 `tel:13675512533` 链接）。
- 兜底文案严禁写成空洞占位，必须使用上述真实电话与邮箱。

### 1.5 月失败率 > 5% 的升级方案（仅简述，本期不实现）

当线上统计发现 Web3Forms 投递月失败率超过 5%（如海外端点国内抖动加剧），切换到**国内链路**：

- 用 **EdgeOne Pages Function**（边缘函数）承接表单 POST，函数内调用 **腾讯云 SES** 发送邮件至 `82257018@qq.com`；
- 腾讯云 SES 为国内端点，投递成功率与速度显著优于海外 Web3Forms；
- 预计工作量约 +1 天：编写 Function（Node/TS，接收表单 body、做同样的前端字段校验与 honeypot 过滤、调 SES SendMail）、在 EdgeOne 控制台配置函数路由、绑定 SES 发信域名与 `82257018@qq.com` 收件；
- 邮件资费极低，企业官网量级可忽略。
- 触发决策点：上线后观测 1 个月，失败率 > 5% 即启动本预案（详见风险表 R2）。

---

## 2. 地图嵌入（腾讯位置服务 GL JS）

### 2.1 申请 key 步骤

1. 注册并登录腾讯位置服务开发者控制台：https://lbs.qq.com 。
2. 进入"应用管理 → 我的应用 → 创建应用"，应用名称填"拓达昇门业官网"，类型选"Web 端（GL JS）"。
3. 创建后获得 `key`（形如 `XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX`）。
4. **域名白名单（必做）**：在 key 设置里配置"域名白名单（referer）"，至少加入：
   - 临时预览域名：`*.edgeone.app`（或具体分配的 `xxx.edgeone.app`）；
   - 备案后的正式域名：`你的域名`（如 `tuodasheng.com` 或 `拓达昇.cn`）。
   - 未配置白名单或白名单不匹配时，JS API 会拒绝加载（白屏），这是最常见接入故障。
5. 将 `key` 替换到嵌入代码的 `YOUR_TENCENT_MAP_KEY` 占位。

### 2.2 GCJ-02 坐标获取方法（合肥 蜀山区 湖光路1299号）

中国公开地图必须使用 **GCJ-02** 坐标系（俗称"火星坐标"），不要用 WGS-84（GPS 直出）或 BD-09，否则点位会偏移。获取公司坐标有两种方法：

**方法 A：地址解析 API（推荐，可脚本化）**

```
GET https://apis.map.qq.com/ws/geocoder/v1/
    ?address=安徽省合肥市蜀山区经济开发区湖光路1299号
    &key=YOUR_TENCENT_MAP_KEY
```

返回示例（节选）：

```json
{
  "status": 0,
  "result": {
    "location": { "lat": 31.820587, "lng": 117.227244 },
    "title": "湖光路1299号"
  }
}
```

取 `result.location` 的 `lat` / `lng` 即为公司位置的 GCJ-02 坐标，填入 2.3 的 `MAP_CENTER`。

**方法 B：手动查**

在 https://lbs.qq.com 的"地图工具 → 坐标拾取器"中搜索"安徽省合肥市蜀山区经济开发区湖光路1299号"，鼠标落点读取经纬度（确认坐标系为 GCJ-02）。

> 坐标占位说明：本文及架构文档暂用 `lat 31.820587, lng 117.227244` 作为初始占位，**上线前必须**用上述方法 A 实测核实后替换，确保 marker 精准落在公司门口而非道路中央。

### 2.3 完整嵌入代码片段（懒加载 + marker + infoWindow）

下方代码满足架构要求：容器显式高度（避免 flex 0 高白屏）、key 占位注入、进入视口才加载 SDK（性能分友好）、`TMap.MultiMarker` 标注、`TMap.InfoWindow` 展示地址电话、不打自定义 `mapStyleId`（避免白图）。

```html
<!-- ========== 地图：腾讯位置服务 GL JS 接入 ========== -->
<div id="company-map" style="width:100%; height:420px;"></div>

<script>
  // 公司 GCJ-02 坐标（务必用 2.2 地址解析 API 核实后替换）
  var MAP_CENTER = { lat: 31.820587, lng: 117.227244 };
  var MAP_KEY = 'YOUR_TENCENT_MAP_KEY'; // 替换为 2.1 申请的 key

  function initCompanyMap() {
    if (!window.TMap) { return; }
    var center = new TMap.LatLng(MAP_CENTER.lat, MAP_CENTER.lng);
    var map = new TMap.Map('company-map', {
      center: center,
      zoom: 15,
      // 不传 mapStyleId，使用官方默认底图（合规）
    });

    // marker 标注公司位置
    new TMap.MultiMarker({
      map: map,
      geometries: [{ id: 'company', position: center }],
    });

    // infoWindow 显示地址与电话
    var info = new TMap.InfoWindow({
      map: map,
      position: center,
      offset: { x: 0, y: -32 },
      content:
        '<div style="padding:10px 12px;font-size:13px;line-height:1.6;">' +
        '<strong style="font-size:14px;">安徽拓达昇门业科技有限公司</strong><br>' +
        '安徽省合肥市蜀山区经济开发区湖光路1299号<br>' +
        '电话：136 7551 2533　邮箱：82257018@qq.com' +
        '</div>',
    });
    info.open();
  }

  // 懒加载：容器进入视口才加载 SDK
  function loadMapSDK() {
    var s = document.createElement('script');
    s.src = 'https://map.qq.com/api/gljs?v=1.exp&key=' + encodeURIComponent(MAP_KEY) + '&callback=initCompanyMap';
    s.onerror = function () {
      document.getElementById('company-map').innerHTML =
        '<div style="padding:24px;text-align:center;color:#5F6B7A;">' +
        '地图加载失败，请直接拨打 136 7551 2533 或搜索"安徽拓达昇门业科技有限公司"。</div>';
    };
    document.head.appendChild(s);
  }

  if ('IntersectionObserver' in window) {
    var el = document.getElementById('company-map');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { loadMapSDK(); io.disconnect(); }
      });
    }, { threshold: 0.2 });
    io.observe(el);
  } else {
    loadMapSDK();
  }
</script>
```

> 合规自检（铁律）：仅使用腾讯官方底图与默认样式；**不自绘**任何国界 / 省界 / 边界数据；不引入 Google Maps / Mapbox / OSM 瓦片；key 必须配置域名白名单。

### 2.4 备选方案：腾讯地图 URI（"在地图中查看"按钮）

若暂不想接入 JS API（如 key 尚未申请），可用**腾讯地图 URI 方案**做一个"在地图中查看"按钮，点击后跳转到腾讯地图 App / 网页并定位公司。该方案零 key 暴露风险，仅需 `referer`（你的应用名 / 域名）。

```
https://apis.map.qq.com/uri/v1/marker
  ?marker=coord:31.820587,117.227244;title:安徽拓达昇门业科技有限公司;addr:安徽省合肥市蜀山区经济开发区湖光路1299号
  &referer=YOUR_MAP_REFERER
```

对应按钮代码：

```html
<a class="map-view-btn" target="_blank" rel="noopener"
   href="https://apis.map.qq.com/uri/v1/marker?marker=coord:31.820587,117.227244;title:安徽拓达昇门业科技有限公司;addr:安徽省合肥市蜀山区经济开发区湖光路1299号&referer=YOUR_MAP_REFERER">
  在地图中查看公司位置
</a>
```

`YOUR_MAP_REFERER` 填你在腾讯位置服务控制台登记的应用名（与 key 同应用）。

---

## 3. SEO 基础设施

以下文件内容直接落盘到站点根目录（`/`，即 `site/` 或构建产物根）。占位域名统一用 `https://yoursite.edgeone.app`，上线后全局替换为正式域名。

### 3.1 robots.txt

```
User-agent: *
Allow: /

# 后台管理页不索引（ hardening 阶段接入 Sveltia CMS 后生效）
Disallow: /admin/

Sitemap: https://yoursite.edgeone.app/sitemap.xml
```

### 3.2 sitemap.xml（全站 8 类页面 URL 模板）

> 说明：以下为 8 类页面的代表 URL。 hardening 阶段若改为 Astro，应由 `@astrojs/sitemap` 自动生成 `sitemap-index.xml`，此处模板用于当前零构建静态站手工维护。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://yoursite.edgeone.app/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/about.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/products/index.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/products/electric-roller.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/products/pvc-fast-door.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/cases/index.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/news/index.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://yoursite.edgeone.app/contact.html</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

> 8 类页面对应：首页、关于我们、产品中心、产品分类（示例）、产品详情（示例）、案例、新闻、联系我们。产品分类 / 详情随内容增加需补充 `<url>` 条目。

### 3.3 JSON-LD 结构化数据

**Organization（全站通用，建议放在每个页面的 `<head>`）**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "安徽拓达昇门业科技有限公司",
  "url": "https://yoursite.edgeone.app/",
  "logo": "https://yoursite.edgeone.app/logo.png",
  "email": "82257018@qq.com",
  "telephone": "+86 136 7551 2533",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "经济开发区湖光路1299号",
    "addressLocality": "合肥市",
    "addressRegion": "安徽省",
    "addressCountry": "CN"
  }
}
</script>
```

**Product（各产品详情页建议，取产品字段填充）**

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "PVC 快速卷帘门",
  "image": "https://yoursite.edgeone.app/uploads/products/pvc-fast-door/cover.jpg",
  "description": "高频次出入场景的高速隔离门，开启速度可达 2m/s",
  "brand": { "@type": "Brand", "name": "拓达昇门业" },
  "offers": {
    "@type": "Offer",
    "priceCurrency": "CNY",
    "availability": "https://schema.org/InStock",
    "url": "https://yoursite.edgeone.app/products/pvc-fast-door.html"
  }
}
</script>
```

> 价格若为非标定制（多数工业门），可省略 `offers` 或标注"询价"，避免误导。Product 的 `name` / `image` / `description` 应与产品详情页正文、meta description 保持一致，形成单一事实源。

### 3.4 每页 meta 规范模板（title / description / OG 三件套）

每页 `<head>` 统一输出以下字段（以首页、产品详情页为例，其余页面同构替换）：

**首页**

```html
<title>安徽拓达昇门业科技有限公司 - 工业门制造与安装</title>
<meta name="description" content="拓达昇门业专注工业门制造与安装，提供电动卷帘门、防火门、伸缩门、智能通道等门类产品与工程方案，服务安徽及全国制造企业。">
<link rel="canonical" href="https://yoursite.edgeone.app/">

<meta property="og:type" content="website">
<meta property="og:title" content="安徽拓达昇门业科技有限公司 - 工业门制造与安装">
<meta property="og:description" content="工业门制造与安装，电动卷帘门、防火门、伸缩门、智能通道产品与方案。">
<meta property="og:url" content="https://yoursite.edgeone.app/">
<meta property="og:image" content="https://yoursite.edgeone.app/og-cover.jpg">
<meta name="twitter:card" content="summary_large_image">
```

**产品详情页（示例：PVC 快速卷帘门）**

```html
<title>PVC 快速卷帘门 - 拓达昇门业</title>
<meta name="description" content="PVC 快速卷帘门：高频次出入场景的高速隔离门，开启速度可达 2m/s，伺服电机驱动运行平稳低噪。">
<link rel="canonical" href="https://yoursite.edgeone.app/products/pvc-fast-door.html">

<meta property="og:type" content="product">
<meta property="og:title" content="PVC 快速卷帘门 - 拓达昇门业">
<meta property="og:description" content="高频次出入场景的高速隔离门，开启速度可达 2m/s。">
<meta property="og:url" content="https://yoursite.edgeone.app/products/pvc-fast-door.html">
<meta property="og:image" content="https://yoursite.edgeone.app/uploads/products/pvc-fast-door/cover.jpg">
<meta name="twitter:card" content="summary_large_image">
```

**meta 规范约束（全站）**

- `title` 格式统一为"页面名 - 拓达昇门业"，长度 ≤ 60 字符；
- `description` 取该页 summary，长度 50–160 字符，不用空洞占位；
- `og:image` 建议尺寸 1200×630，`twitter:card` 统一 `summary_large_image`；
- `canonical` 与 `og:url` 必须一致且为正式域名（上线后替换占位）。

---

## 4. 部署与域名（结合架构师 R5 风险）

### 4.1 阶段表

| 阶段 | 域名 | 加速区域 | 说明 |
|------|------|----------|------|
| 阶段 1 开发期 | 本机 `localhost`（静态服务器） | — | 每日开发预览 |
| 阶段 2 交付预览 | EdgeOne Pages 默认域名 `*.edgeone.app` | 全球（不含中国大陆节点） | 无需备案即可访问，供甲方验收；国内访问可用但延迟较高（对应风险 R5） |
| 阶段 3 备案 | 腾讯云注册域名（.com / .cn，约 60–100 元/年）→ 腾讯云 ICP 备案（免费，通常 2–4 周） | — | **备案与开发并行启动**，压缩空窗；备案期间站点继续走默认域名 |
| 阶段 4 正式上线 | 自定义域名绑定 EdgeOne Pages，加速区域切换"中国大陆" | 中国大陆 + 全球 | SSL 自动签发；备案号回填页脚；地图 key 域名白名单更新为正式域名 |

> **R5 风险应对（必然发生，流程性）**：未备案前自定义域名无法启用大陆节点，上线初期国内访问延迟约 0.7–1.4s。对策：预览期用 `*.edgeone.app` 交付验收；ICP 备案与开发并行启动，把空窗压到最短；备案完成即刻切正式域名 + 大陆节点。

### 4.2 EdgeOne Pages 接入（静态托管 + 自动构建）

- 平台：腾讯云 EdgeOne Pages（国内站 edgeone.cloud.tencent.com），免费额度足够企业官网量级。
- Git 集成：将站点源码（当前 `site/` 或后续 Astro 工程）推送到 GitHub / Gitee 仓库，在 EdgeOne Pages 控制台"新建项目 → 关联仓库 → 选择分支"，即开启**推送自动构建**。
- 构建产物：零构建静态站直接以 `site/` 或根目录作为输出；hardening 阶段若用 Astro，构建命令 `npm run build`、输出目录 `dist/`。
- 生效时延：CMS / 内容提交（GitHub）→ EdgeOne 检测推送 → 重新构建，约 **1–3 分钟**后线上生效。
- 域名与 SSL：阶段 4 在控制台"自定义域名"绑定正式域名，SSL 证书自动签发续期。

---

## 5. 风险与待办（checklist）

### 5.1 用户 / 运维需逐项补齐的待办

- [ ] 申请 Web3Forms `access_key` 并替换前端表单占位 `YOUR_WEB3FORMS_ACCESS_KEY`（见 1.1、1.2）
- [ ] 申请腾讯位置服务 key 并接入地图（见 2.1、2.3），配置域名白名单
- [ ] 用地址解析 API 核实公司 GCJ-02 坐标，替换 `MAP_CENTER` 占位（见 2.2）
- [ ] 注册域名 + 提交腾讯云 ICP 备案（与开发并行，见 4.1）
- [ ] 申请 GitHub / Gitee 仓库（hardening 阶段 CMS 后台用，见 4.2）
- [ ] 提供真实案例 / 新闻 / 资质内容替换占位（标注"示例，可在后台替换"的区块）
- [ ] 上线后观测 1 个月表单投递失败率，> 5% 启动 EdgeOne Function + 腾讯云 SES 预案（见 1.5）

### 5.2 占位符总表（接入时全局替换）

| 占位符 | 含义 | 获取方式 |
|--------|------|----------|
| `YOUR_WEB3FORMS_ACCESS_KEY` | 表单投递密钥 | web3forms.com 注册（免费 250 封/月） |
| `YOUR_TENCENT_MAP_KEY` | 腾讯地图 JS API key | lbs.qq.com 申请 Web 端(GL JS) key |
| `YOUR_MAP_REFERER` | 地图 URI 方案应用名 | 同 key 所在应用名 |
| `MAP_CENTER` (lat/lng) | 公司 GCJ-02 坐标 | 地址解析 API 核实（见 2.2） |
| `https://yoursite.edgeone.app` | 临时预览域名 | EdgeOne Pages 默认分配 |
| 正式自定义域名 | 备案后绑定 | 腾讯云注册 + ICP 备案 |
| `/logo.png` `/og-cover.jpg` | 站点 logo 与分享图 | 设计交付物 |

### 5.3 集成风险研判（后端视角）

| 编号 | 风险 | 等级 | 影响 | 对策 |
|------|------|------|------|------|
| R2 | Web3Forms 海外端点国内偶发超时 | 中 | 询盘丢失 | 表单失败分支展示电话兜底（1.4）；月失败率 >5% 切 EdgeOne Function + 腾讯云 SES（1.5） |
| R5 | 未备案前无法启用大陆节点 | 必然（流程性） | 初期国内访问延迟 0.7–1.4s | 预览用 `*.edgeone.app`；备案与开发并行（4.1） |
| R6 | 地图 key 前端暴露被刷量 | 低 | 配额耗尽 | 域名 Referer 白名单；展示型单点调用量极小（2.1） |
| 地图合规 | 误用非白名单地图源 | 禁止项 | 合规风险 / 白图 | 仅腾讯位置服务；不自绘边界；不引 OSM/Google/Mapbox（2.3 合规自检） |
| 坐标偏移 | 用错坐标系（WGS-84 / BD-09） | 中 | marker 偏离 | 一律 GCJ-02，地址解析 API 取数（2.2） |
| SEO 漏配 | 漏 meta / sitemap / JSON-LD | 中 | 收录差 | 每页按 3.4 模板输出；sitemap 随内容增补（3.2） |

> 后端结论：本期无自建后端，集成风险集中在"两个外部端点（Web3Forms / 腾讯地图）的可用性与合规"以及"备案流程时序"。两处外部依赖均为可替换端点，且已分别准备国内链路预案（R2）与合规白名单约束（地图合规），整体可控。最关键的时序风险 R5 通过"备案与开发并行"消解，建议用户**立即启动备案**以免成为上线瓶颈。

---

_文档结束。本契约为前端实现与运维 / 用户接入的权威依据；如外部服务（Web3Forms / 腾讯位置服务）政策或 API 变更，以各平台官方文档为准并同步更新本文。_
