---
title: 'Cloudflare Workers vs Vercel vs Supabase：出海 SaaS 怎么选？成本、性能与部署对比'
date: '2026-11-02'
---

做出海 SaaS，除了选择 Next.js 还是 TanStack Start，还有一个绕不开的问题：项目到底部署在哪里？

Cloudflare、Vercel 和 Supabase 经常被放在一起比较，但它们并不是完全相同的产品：

- **Cloudflare**：提供计算、CDN、数据库、对象存储等基础设施，适合搭建全栈应用。
- **Vercel**：专注前端应用部署，尤其适合 Next.js 项目，开发和发布体验比较成熟。
- **Supabase**：提供托管 PostgreSQL、Auth、Storage、Realtime 等后端服务，可以搭配不同前端框架使用。

如果你是独立开发者，预算有限，又想尽快把 SaaS 推向海外市场，这三种方案都值得了解。

本文主要从定价、部署体验、性能、数据库、国内访问和迁移成本几个方面进行对比。

## 一、先看结论

| 需求 | 优先考虑 | 原因 |
|---|---|---|
| 尽量压低基础设施成本 | Cloudflare | 免费额度覆盖面较广 |
| 快速部署 Next.js 项目 | Vercel | Git 集成和部署体验成熟 |
| 快速搭建后端 | Supabase | PostgreSQL、Auth、Storage 等功能集成度高 |
| Cloudflare 全栈 SaaS | Cloudflare | Workers、D1、R2 可以组合使用 |
| 需要复杂关系型数据 | Supabase | 标准 PostgreSQL，生态成熟 |
| 实时协作、订阅功能 | Supabase | 提供 Realtime |
| 主要面向中国大陆用户 | 先做实际测试 | 三个平台都不能直接保证大陆访问稳定 |

简单来说：

**想控制成本，可以优先研究 Cloudflare；想快速上线 Next.js 项目，可以选择 Vercel；不想花太多时间开发后端，可以考虑 Supabase。**

## 二、三家平台的定价对比

先看最直接的成本。

### 1. Cloudflare Workers

Cloudflare 的特点是提供了比较丰富的免费额度，计算、数据库和对象存储可以分别使用。

| 服务 | 免费额度 / 主要规则 |
|---|---|
| Workers | 每天 10 万次请求，单次 CPU 时间 10ms |
| Workers Paid | $5/月起，包含每月 1000 万次请求额度 |
| D1 | 每天 500 万行读取、10 万行写入，5GB 存储 |
| R2 | 每月 10GB 存储免费额度，另有操作次数额度 |
| KV | 提供免费额度，超出后按使用量计费 |

Workers 免费版的 CPU 时间只有 10ms，需要注意：这是代码实际占用 CPU 的时间，不是整个请求的响应时间。

如果只是普通 API、用户认证、数据库查询等轻量业务，免费额度可能已经够用一段时间。

但如果有大量图片处理、复杂计算、长时间任务，就需要考虑其他服务或付费方案。

另外，R2 的出网流量费用是它很有吸引力的地方，尤其适合图片、视频等文件存储和分发场景。

参考：[Cloudflare Workers 定价](https://developers.cloudflare.com/workers/platform/pricing/)、[D1 定价](https://developers.cloudflare.com/d1/platform/pricing/)、[R2 定价](https://developers.cloudflare.com/r2/pricing/)。

### 2. Vercel

Vercel 的优势是开发体验，而不是最低成本。

| 套餐 | 价格 | 主要特点 |
|---|---:|---|
| Hobby | $0/月 | 适合个人项目和非商业用途 |
| Pro | $20/月起 | 面向商业项目，包含 $20 使用额度 |
| Enterprise | 定制 | 面向企业级需求 |

Pro 套餐按团队计费，额外成员会增加费用。部分资源超过套餐额度后，也可能产生额外费用。

需要注意的是，Vercel Hobby 并不是商业 SaaS 的免费生产环境替代方案。如果准备正式运营产品，应该把 Pro 等商业方案纳入预算。

它的优点很明显：

- GitHub 推送后自动构建和部署
- Preview 环境方便测试
- Next.js 集成完善
- CDN、日志、分析等功能比较齐全
- 不需要自己维护服务器

如果你主要精力放在产品开发和用户增长上，Vercel 可以节省不少部署维护时间。

参考：[Vercel 官方定价](https://vercel.com/pricing)。

### 3. Supabase

Supabase 采用项目和资源配额相结合的计费方式。

| 套餐 | 价格 | 主要特点 |
|---|---:|---|
| Free | $0/月 | 500MB 数据库、1GB 文件存储 |
| Pro | $25/月起 | 8GB 数据库、100GB 文件存储、250GB 出网流量 |
| Team | $599/月起 | 增加团队管理、安全和合规能力 |
| Enterprise | 定制 | 企业级服务 |

Supabase Free 还有一个需要注意的地方：项目连续一周低活跃时可能自动暂停，而且免费项目数量有限。

Pro 套餐则不会因为低活跃而暂停，适合正式运营的产品。

Supabase 的价值不只是数据库，还包括：

- PostgreSQL 数据库
- 用户认证 Auth
- 文件存储 Storage
- 实时订阅 Realtime
- Edge Functions
- 自动生成的 API

如果自己从头搭建这些功能，需要写不少后端代码。Supabase 把它们整合起来，可以明显缩短开发周期。

参考：[Supabase 官方定价](https://supabase.com/pricing)。

## 三、真实成本：一个 10k MAU SaaS 要花多少钱？

只看套餐价格很容易误判，实际成本还要结合请求量、数据库、存储和带宽。

假设有一个早期 SaaS：

- 月活用户：10,000 MAU
- API 请求：每天 5 万次
- 数据库：500MB
- 文件存储：20GB
- 月出网流量：100GB
- 不包含第三方 AI API、邮件、支付等费用

可以按下面的方式估算：

| 架构 | 基础设施成本 | 说明 |
|---|---:|---|
| Cloudflare Workers + D1 + R2 | 有机会从 $0 起步 | 需要分别核算免费额度和实际用量 |
| Vercel Pro + 外部数据库 | $20/月起 | 数据库、存储可能产生额外费用 |
| Supabase Pro + 独立前端部署 | $25/月起 | 前端托管费用另算 |
| Vercel Pro + Supabase Pro | $45/月起 | 两个平台的基础套餐费用 |

这里有几个容易忽略的问题：

**第一，Cloudflare 的免费额度不是所有资源都无限免费。**

例如 D1 有读取和写入额度，R2 有存储和操作次数限制。超过额度后需要按实际用量付费。

**第二，Vercel 不包含所有外部服务。**

如果数据库使用 Neon、Supabase 或其他服务，应该把对应费用一起计算。

**第三，Supabase Pro 的 $25 不是整个网站的托管费用。**

它主要覆盖 Supabase 后端服务，前端仍然需要部署在 Vercel、Cloudflare 或其他平台。

所以，不能简单地说 Cloudflare 一定是 $0，或者 Supabase 一定是 $25。

更准确的说法是：**早期业务如果请求量不大、资源使用合理，Cloudflare 有机会把基础设施费用压得很低；Supabase 和 Vercel 则用固定套餐换取更成熟的开发体验和服务能力。**

## 四、性能和冷启动：谁更快？

原始对比中经常会出现这样的数字：

| 平台 | 常见说法 |
|---|---|
| Cloudflare Workers | 冷启动低于 5ms |
| Vercel Edge | 50～150ms |
| Vercel Node.js | 300～800ms |
| Supabase Edge Functions | 50～200ms |

这些数字不能直接作为选型依据。

原因很简单：不同框架、运行时、部署区域、依赖数量、数据库位置和测试方式都会影响结果。P50、P95 也需要明确测试环境和请求样本，不能拿几个孤立数字做平台排名。

实际需要区分三个概念：

1. **启动时间**：运行环境启动和加载代码需要多久。
2. **网络延迟**：用户到计算节点、计算节点到数据库的网络耗时。
3. **业务响应时间**：包括鉴权、数据库查询、外部 API 和业务逻辑在内的完整耗时。

Cloudflare Workers 使用 V8 Isolate 运行模型，通常不需要传统服务器函数那样启动完整运行环境，因此启动开销比较低。

Vercel 使用不同的运行时和计算方式，Node.js 函数与 Edge Runtime 也不能混为一谈。

Supabase Edge Functions 使用 Deno 兼容运行时，支持在不同区域执行，但如果函数需要频繁访问数据库，数据库所在区域同样会影响整体响应时间。

**对 SaaS 来说，数据库和外部 API 的延迟，往往比框架本身的启动时间更值得关注。**

例如：

用户在东京，Worker 在东京，但 PostgreSQL 在美国。即使 Worker 启动很快，多次跨区域数据库查询仍然会拖慢整个接口。

所以不要只看冷启动，应该测试完整业务链路。

## 五、中国大陆访问：不能只看 CDN 节点

如果你的产品面向海外用户，这部分可能不是主要问题。

但如果你希望国内用户也能访问，就需要单独评估。

| 平台 | 需要关注的问题 |
|---|---|
| Cloudflare | 域名解析、线路、回源路径、节点调度 |
| Vercel | 部署区域、域名访问、跨境网络质量 |
| Supabase | 数据库和 API 所在区域、跨境连接稳定性 |

原文中给出的「Cloudflare 国内 P50 80～150ms」「Vercel 150～400ms」等数据，我不建议直接采用。

因为国内不同运营商、不同省份、不同时间段的访问结果可能差异很大。一个地区访问正常，不代表全国都稳定。

还有一点：Cloudflare 的全球 CDN 节点数量多，并不意味着所有节点都能为中国大陆用户提供相同的访问体验。

如果国内用户是核心客户，建议至少测试：

- 电信、联通、移动等不同运营商
- 不同地区的 DNS 解析结果
- 首页静态资源加载时间
- API 接口响应时间
- 数据库查询耗时
- 图片和文件上传下载速度

如果产品主要面向海外用户，国内访问表现就不应该成为唯一选型标准。

如果主要面向中国大陆市场，还需要额外考虑服务器部署、备案和相关合规要求，不能只靠换一个 CDN 解决所有问题。

## 六、数据库：三家的差异非常明显

这部分是选型时容易被忽略，但后期影响很大的地方。

| 维度 | Cloudflare D1 | Vercel | Supabase |
|---|---|---|---|
| 默认数据库 | D1 | 不自带通用关系型数据库 | PostgreSQL |
| 数据库类型 | SQLite | 需要外接 | PostgreSQL |
| 关系数据 | 支持 | 取决于外接数据库 | 支持 |
| 实时订阅 | 需要自行实现 | 需要外接服务 | 内置 Realtime |
| 文件存储 | R2 | Blob 或外接服务 | Storage |
| 用户认证 | 需要集成 | 需要集成 | 内置 Auth |
| 全文检索 | 支持 FTS5 | 取决于数据库 | PostgreSQL 全文检索 |

### Cloudflare D1

D1 基于 SQLite，适合轻量级 SaaS、用户数据、订单、配置和常规业务数据。

优点是与 Workers 集成方便，使用 Drizzle 等 ORM 也比较顺手。

但它和 PostgreSQL 不是一回事。如果业务依赖复杂 SQL、特定 PostgreSQL 扩展或大量复杂事务，就需要提前评估。

如果想继续使用 PostgreSQL，也可以通过 Hyperdrive 连接外部数据库。

### Vercel

Vercel 本身并不是数据库服务商。

你可以搭配 Neon、Supabase、PostgreSQL、Redis 等服务，根据业务需求选择。

这种方式灵活，但也意味着数据库、存储和部署可能分散在多个平台。

### Supabase

Supabase 最大的优势是标准 PostgreSQL。

如果业务涉及用户、订单、订阅、权限、团队、支付记录等关系型数据，PostgreSQL 是一个很成熟的选择。

再加上 Auth、Storage 和 Realtime，可以减少不少后端开发工作。

**我的建议：** 如果项目数据结构简单，希望尽可能使用 Cloudflare 原生服务，可以选择 D1；如果业务关系复杂，或者未来需要更多数据库能力，优先考虑 PostgreSQL。

## 七、平台锁定风险：以后迁移麻烦吗？

独立开发者还应该考虑一个问题：如果以后平台涨价、服务不稳定，或者项目规模变大，能不能迁走？

| 平台 | 锁定风险 | 迁移时需要注意 |
|---|---|---|
| Cloudflare | 中 | Workers API、D1、KV、Durable Objects 等平台能力 |
| Vercel | 中 | Next.js 特定能力、Vercel SDK 和部署配置 |
| Supabase | 相对较低 | PostgreSQL 数据可迁移，但 Auth、Storage、Realtime 需要替换 |

### Cloudflare

D1 基于 SQLite，数据迁移相对直观。

但如果大量使用 KV、Durable Objects、Queues 等平台专属能力，迁移时就需要重新设计对应功能。

### Vercel

如果只是部署标准 Next.js 应用，迁移到其他 Node.js 平台并不困难。

但如果大量使用 Vercel 特有的服务和 API，例如 Edge Config、Blob 等，就需要额外处理。

### Supabase

Supabase 使用标准 PostgreSQL，这是它的一个优势。

数据库可以通过 PostgreSQL 的备份和迁移工具进行迁移。

不过，Auth、Storage、Realtime 和自动生成 API 并不是单纯迁移数据库就能解决的，仍然需要替换对应服务。

我的建议是：**不要为了避免平台锁定而拒绝使用平台能力，但核心业务逻辑和数据结构尽量保持独立。**

例如，把数据库访问封装在 Repository 层，避免业务代码到处直接依赖某个平台的 SDK。

## 八、三种常见的 SaaS 部署架构

### 架构 A：纯 Cloudflare

```text
TanStack Start
      ↓
Cloudflare Workers
      ↓
   ┌──┴────┐
   ↓       ↓
  D1      R2
数据库   文件存储
   ↓
 KV / Queues
缓存 / 异步任务
```

**适合：** 独立开发者、轻量 SaaS、AI 工具站，以及希望控制基础设施成本的项目。

优点：

- 前后端可以部署在同一套基础设施中
- D1、R2、KV 等服务集成方便
- 免费额度比较丰富
- 不需要维护传统服务器

缺点：

- 需要理解 Workers 的运行时限制
- D1 不等于完整 PostgreSQL
- 部分第三方 Node.js 库需要适配
- 平台专属服务用得越多，迁移成本越高

### 架构 B：Vercel + 外部数据库

```text
Next.js
   ↓
Vercel
   ↓
Neon / Supabase / PostgreSQL
   ↓
S3 / Blob
```

**适合：** 已经熟悉 Next.js、需要成熟部署体验，或者依赖 Next.js 生态的项目。

优点：

- 部署流程简单
- Preview 环境方便
- Next.js 支持完善
- 数据库和存储可以独立选择

缺点：

- 需要分别管理多个服务
- 费用可能随着带宽和资源使用增长
- 数据库与计算区域需要合理规划

### 架构 C：Supabase + 前端托管平台

```text
Next.js / TanStack Start
          ↓
   Vercel / Cloudflare
          ↓
       Supabase
    ┌─────┼─────┐
    ↓     ↓     ↓
   DB    Auth  Storage
          ↓
       Realtime
```

**适合：** 需要快速开发用户系统、权限、文件管理和实时功能的 SaaS。

优点：

- PostgreSQL 能力成熟
- Auth、Storage、Realtime 集成度高
- 前端框架选择自由
- 不需要从零搭建完整后端

缺点：

- 正式运营通常需要考虑 Pro 套餐
- 前端与后端可能分布在不同区域
- 需要关注数据库连接数和资源使用量

## 九、独立开发者到底应该怎么选？

我会根据项目需求做决定，而不是单纯比较谁的免费额度更多。

| 你的需求 | 推荐方案 |
|---|---|
| 预算有限，想尽量降低月成本 | Cloudflare |
| 开发 Next.js 项目，追求快速部署 | Vercel |
| 需要标准 PostgreSQL | Supabase |
| 需要 Auth + Storage + Realtime | Supabase |
| AI 图片、视频生成 SaaS | Cloudflare + 外部 AI API |
| 多人协作、实时数据同步 | Supabase |
| 长时间任务、异步任务队列 | Cloudflare Queues / Durable Objects，或专门的任务平台 |
| 面向海外用户 | 根据目标用户区域选择部署位置 |
| 面向中国大陆用户 | 先做线路和合规测试，再确定架构 |

如果是我从零开发一个面向海外用户的轻量 SaaS，会优先考虑两种组合：

**方案一：TanStack Start + Cloudflare Workers + D1 + R2**

适合数据结构相对简单、希望控制成本，并且愿意使用 Cloudflare 原生服务的项目。

**方案二：Next.js + Vercel + Supabase**

适合需要 PostgreSQL、认证、文件存储和成熟生态，希望尽快完成产品开发的项目。

这两套方案都能做出完整的商业 SaaS，没必要为了追求某个平台的免费额度而牺牲开发效率。

## 写在最后

Cloudflare、Vercel 和 Supabase 并不是只能三选一。

实际项目中，完全可以组合使用：

- Cloudflare：DNS、CDN、R2 文件存储
- Vercel：Next.js 应用部署
- Supabase：PostgreSQL、Auth、Storage

但对于独立开发者来说，服务越多，配置、账单、故障排查和维护工作也越多。

如果一个项目早期只有几百个用户，没必要一开始就搭建复杂的分布式架构。

先选一套自己熟悉、成本可控的方案，把核心功能、支付和用户增长跑通。等业务真的遇到性能或成本瓶颈，再考虑拆分服务。

**技术架构是为产品服务的。能稳定上线、方便维护、成本可控，比单纯追求最低账单更重要。**
