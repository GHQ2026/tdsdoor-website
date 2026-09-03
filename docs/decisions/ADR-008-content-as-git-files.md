# ADR-008: 内容以 Git 仓库中的 Markdown/JSON 文件为唯一数据源

## Status: Accepted (2026-08-28)

## Background

站点需要产品（6 详情 + 4 分类）、案例、新闻、公司信息四类内容，且要求非技术用户可经网页后台编辑。需确定内容存储与校验机制。

## Decision

内容全部以 Markdown（正文型）+ JSON（结构型）文件存于 Git 仓库 src/content/，由 Astro Content Collections + Zod Schema（src/content.config.ts）做构建期强校验；CMS（Sveltia）编辑的即是这批文件；本项目无自研 REST API，故不产出 openapi.yaml，契约载体为：content.config.ts 的 Zod Schema、public/admin/config.yml 的字段配置、ARCHITECTURE.md 5.1 节的表单提交契约。

理由：
- 单一数据源：CMS、构建、页面渲染共享同一批文件，无同步问题。
- 构建期校验：缺字段/类型错的内容直接构建失败，不会带病上线（沉默错误前置拦截）。
- Markdown 承载富文本正文，JSON 承载结构化字段（规格参数、坐标、联系方式），各得其所。
- 版本化天然成立：每次编辑是一次 Git 提交，可回滚、可审计。

## Consequences

- 正面：零数据库、零内容同步服务；Zod Schema 即前后端契约，字段结构变更在构建期暴露影响面。
- 负面：CMS config.yml 与 content.config.ts 需保持字段一致（两处维护，已约定一一对应并在 Phase 3 检查项中列出）；单集合内容量上万后构建变慢（本项目量级 <100 条，无影响）。
- 约束：所有集合字段定义见 ARCHITECTURE.md 第 3 节，新增字段必须先改 Schema 再改 CMS 配置（规格即契约：先改规格再改代码）。

## Related ADRs: ADR-001, ADR-002
