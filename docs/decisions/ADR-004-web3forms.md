# ADR-004: 使用 Web3Forms 作为联系表单邮件投递服务

## Status: Accepted (2026-08-28)

## Background

联系我们页需要询盘表单，提交后投递至 82257018@qq.com。站点为纯静态，无自建后端。备选：Formspree、自建 mailto/自建后端发信。

## Decision

选用 Web3Forms（免费层 250 封/月），表单以 fetch POST JSON 提交，Access Key 经构建期环境变量注入。

理由：
- 免费额度为 Formspree 的 5 倍（250 vs 50 封/月），企业官网询盘量级绰绰有余。
- 接入成本最低：注册取 key + 一个 fetch 调用；内置 botcheck/honeypot 反垃圾；免费含自动回执。
- mailto 在移动端与网页邮箱基本不可用，否决；自建后端发信违背静态优先与零服务器约束，否决。
- 密钥安全：key 不硬编码进仓库，构建时注入；前端暴露的 key 仅能向固定邮箱发信，风险可控。

## Consequences

- 正面：零服务器、零费用实现邮件通知；接入当日可完成。
- 负面：api.web3forms.com 为海外端点，国内提交存在偶发超时可能（风险 R2）。
- 预案：表单失败分支展示电话兜底；若月失败率超 5%，切换 EdgeOne Pages Function + 腾讯云 SES（国内链路，预计 +1 天）。

## Related ADRs: ADR-001, ADR-003
