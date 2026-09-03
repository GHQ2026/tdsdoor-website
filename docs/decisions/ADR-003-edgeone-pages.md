# ADR-003: 使用腾讯云 EdgeOne Pages 作为托管与部署平台

## Status: Accepted (2026-08-28)

## Background

站点交付后需静态托管；访客主要是国内 B 端客户；用户无域名、后续才备案。备选：Cloudflare Pages、Vercel/Netlify。

## Decision

选用腾讯云 EdgeOne Pages（国内站），以 Git 仓库（GitHub，备选 Gitee）为构建源，推送 main 分支自动部署。

理由：
- 目标访客在国内：EdgeOne 备案域名可启用中国大陆节点（2300+ 节点，实测 50-90ms），Cloudflare 晚高峰波动大（实测 800ms+），Vercel 国内访问差——对本项目这是决定性差异。
- 免费额度：不限静态流量与请求、每月定额构建次数（企业官网量级远够用），MVP 阶段零成本。
- 与 ICP 备案、域名、SSL、腾讯位置服务形成同一腾讯云账号体系，交付链路最短。
- 支持 GitHub/Gitee/Coding 接入，与 ADR-002 的 CMS 链路闭环。

## Consequences

- 正面：备案前可用平台默认域名（*.edgeone.app，全球加速）先行交付验收；备案后一键切大陆节点。
- 负面：未备案期间国内访问延迟 0.7-1.4s（流程性风险 R5，备案与开发并行缓解）；平台较新，文档与生态弱于 Cloudflare/Vercel。
- 预案：构建产物是纯静态目录，可随时 CLI 直传或迁移至任意静态托管，无锁定。

## Related ADRs: ADR-001, ADR-002, ADR-006
