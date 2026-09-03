# ADR-002: 使用 Sveltia CMS 作为内容管理后台（替代 Decap CMS）

## Status: Accepted (2026-08-28)

## Background

硬约束：用户是非技术人员，上线后要能在网页后台零代码编辑新闻/产品/案例。前期倾向 Decap CMS（Git-based），需要验证其维护状态与部署可行性。

## Decision

选用 Sveltia CMS（@sveltia/cms 0.129.x，自托管 bundle 于 /admin），后端为 GitHub 私有仓库，登录经 Cloudflare Workers 上的 sveltia-cms-auth OAuth Worker。

理由：
- Decap CMS（原 Netlify CMS）官方投入衰退、UI 陈旧、社区大规模外迁，长期支持存疑，不选。
- Sveltia 是 Decap 的直接继任者：配置文件（config.yml）完全兼容，修掉了前者数百个已知问题，编辑体验现代、内置图片上传、活跃发版（2026 年已至 0.129.x，1.0 在路上）。
- Git-based 模式与 EdgeOne Pages 部署链路天然兼容：CMS 提交 → GitHub → 自动构建 → 上线，无需任何自建服务器。
- 对比飞书多维表格方案：飞书附件无公开外链（图片管理硬伤）、变更不触发构建、集成成本 3-5 天；对比自研管理页：维护成本不成比例，均不选。
- 已验证可行性：CMS 全程运行在浏览器（调 GitHub API），静态托管无冲突；唯一外部依赖是 GitHub 与 OAuth Worker，均为免费。

## Consequences

- 正面：用户编辑体验接近轻量 WordPress；内容变更天然有 Git 版本历史可回滚；图片随仓库走构建管线。
- 负面：GitHub 国内访问存在波动（核心风险 R1，已列三层缓解与 Gitee 降级预案）；Sveltia 处于 beta，自托管需锁定版本。
- 退路：配置兼容 Decap，极端情况改一行 script 引用即可切回。

## Related ADRs: ADR-001, ADR-003
