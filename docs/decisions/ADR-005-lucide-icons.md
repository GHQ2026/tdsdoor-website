# ADR-005: 锁定 Lucide 作为全站唯一 SVG 图标库

## Status: Accepted (2026-08-28)

## Background

项目 P0 规则：禁止 emoji 作为功能图标，全项目必须锁定一套 SVG 图标库、统一描边风格、不混用。备选：Lucide、Feather、Tabler Icons。

## Decision

锁定 Lucide，经官方 Astro 集成包 @lucide/astro（^1.16.0）组件化引入，构建期内联为 SVG，零运行时 JS。

理由：
- Lucide 是 Feather 的社区延续：同为 24x24/2px 统一描边风格，与"浅色简约高级"设计系统匹配，但图标数量 1500+（Feather 约 280，不足以覆盖工业门企官网所需）。
- 官方提供 @lucide/astro 集成，按需引入、构建期优化，优于 Tabler（数量最多但风格松散、需自行处理引入）。
- 纯线性图标无文化歧义，中文排版适配无问题；维护活跃（lucide-icons 组织持续发版）。

## Consequences

- 正面：图标风格全站统一；树摇后体积可忽略；新增图标只需引入对应命名导出。
- 负面：锁定单一来源意味着个别特殊图形（如门体剖面示意图）不属于图标范畴，须由设计师出插图画作而非图标库强凑。
- 硬约束：任何页面/组件禁止引入其他图标来源、禁止以 emoji 充当功能图标（P0 规则，Phase 3 门禁检查项）。

## Related ADRs: ADR-001, ADR-007
