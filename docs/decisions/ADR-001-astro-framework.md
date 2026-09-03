# ADR-001: 使用 Astro 6 作为站点框架

## Status: Accepted (2026-08-28)

## Background

官网硬约束为"静态优先"（SEO 与加载速度最优），同时需要结构化内容（产品/新闻/案例）支撑非技术用户经后台编辑。备选：纯手写 HTML/Python 模板（现有初版即此方案）、VitePress。

## Decision

选用 Astro 6（astro ^6.1.1，Node 22 本机运行）。

理由：
- 纯静态输出、默认零客户端 JS，Lighthouse SEO/性能近满分，满足静态优先约束。
- Content Collections + Zod 提供类型安全的内容建模，是 CMS 编辑与页面渲染之间的天然契约。
- Git-based CMS（Sveltia/Decap）对 Astro 有成熟集成路径，"用户零代码编辑"依赖此生态。
- 内置 sharp 图片管线，解决现有 7 张 2MB PNG 的性能问题。
- 现有 Python 模板方案被否定：无内容模型、维护靠人肉、CMS 无从接入；VitePress 定位文档站，不适合企业营销站。

## Consequences

- 正面：零服务器、零数据库，托管与维护成本最低；页面路由与内容集合天然支持后续扩展。
- 负面：任何"动态内容"需求都要走构建（内容变更后 1-3 分钟生效），不适合实时性场景（本项目无此需求）。
- 现有 site/ 目录产物仅作内容参考，全部重构。

## Related ADRs: ADR-002, ADR-003, ADR-007
