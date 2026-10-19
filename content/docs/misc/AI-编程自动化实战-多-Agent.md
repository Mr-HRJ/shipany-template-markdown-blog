---
title: 'AI 编程自动化实战：多 Agent 开发、Code Review、CI 自动修复与合并'
date: '2026-10-18'
---

AI 编程真正值得自动化的，不只是让 Agent 写代码，而是把开发、代码审查、问题修复、测试和合并串成一个可验证的闭环。

本文使用 Git Worktree 管理并行开发，通过多个 AI Agent 交叉 Review，使用 GitHub Actions 执行 CI，并在满足条件时自动修复或合并代码。

整个流程遵循一个原则：Agent 负责开发和分析，Code Review 负责识别真实风险，CI 负责验证，编排器负责调度，GitHub 负责最终合并门禁。

## 一、整体流程

```
创建 Feature 分支和 Worktree
          ↓
开发 Agent 实现功能
          ↓
运行本地检查
          ↓
多个模型独立 Code Review
          ↓
验证问题，修复成立的缺陷
          ↓
再次检查并推送代码
          ↓
创建 PR，触发 GitHub Actions
          ↓
       CI 是否通过？
        ↙         ↘
      失败          通过
       ↓             ↓
获取对应提交的日志   检查 PR 和合并条件
       ↓             ↓
判断是否允许修复     请求 GitHub 自动合并
       ↓             ↓
Agent 限次修复       确认 PR 已合并
       ↓
重新测试并推送
       ↓
达到重试上限 → 人工介入
```

这套流程分为五个部分：

| 部分       | 工具                      | 作用                 |
| -------- | ----------------------- | ------------------ |
| 并行开发     | Git Worktree            | 隔离 Feature 工作目录    |
| AI 开发与审查 | Codex CLI、Claude Code 等 | 开发、交叉 Review、修复    |
| 流程编排     | Node.js / TypeScript 脚本 | 管理状态、调用 Agent、控制重试 |
| 自动化测试    | GitHub Actions          | 执行统一 CI 检查         |
| 合并门禁     | GitHub 分支保护、自动合并        | 确保检查通过后才允许合并       |

建议先实现单个 Feature 的最小闭环，再扩展多个 Feature 并行开发。不要一开始就搭建复杂的多 Agent 调度系统。

## 二、准备项目环境

本文以 GitHub 上的 Node.js / TypeScript 项目为例。

### 2.1 安装并检查基础工具

确保已经安装 Git、Node.js、pnpm 和所需的 AI 编程 CLI。

安装 GitHub CLI：

```
brew install gh
```

登录并检查 GitHub 认证：

```
gh auth login
gh auth status
```

进入项目目录：

```
cd your-project

git status
git branch --show-current
git remote -v
```

`your-project` 需要替换为实际项目路径。

开始前，确保工作区没有未处理的修改，并确认本地 `main` 与远程仓库同步。

### 2.2 统一本地检查命令

在 `package.json` 中确认项目已经定义实际可用的检查命令，例如：

```
{
  "scripts": {
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "build": "your-project-build-command"
  }
}
```

其中 `your-project-build-command` 只是占位示例，必须替换为真实构建命令。项目没有使用某个工具时，不要照抄对应脚本。

先手动运行：

```
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

如果其中某项尚未配置，应先完善项目脚本，或在后续流程中明确跳过的原因。不要把不存在的测试命令当作已经通过的检查。

### 2.3 让 Agent 支持命令行调用

选择实际使用的 AI 编程工具，例如 Codex CLI 或 Claude Code，并确认：

- 已完成认证，能够正常调用模型。
- 支持非交互式任务执行，或者有可调用的 API。
- 能够指定工作目录和任务提示词。
- 能够获取退出码、执行输出及错误信息。
- 可以限制文件修改、命令执行和 Git 操作权限。

不同 CLI 的调用方式和权限参数并不通用。后续编排器需要针对所选工具单独实现适配器，不能假设一个命令可以调用所有模型。

## 三、使用 Git Worktree 并行开发

假设需要开发用户资料和支付两个功能。

先同步 `main`：

```
git switch main
git pull --ff-only origin main
```

创建用户资料功能的 Worktree：

```
git worktree add \
  -b feature/user-profile \
  ../project-user-profile \
  main
```

创建支付功能的 Worktree：

```
git worktree add \
  -b feature/payment \
  ../project-payment \
  main
```

检查目录：

```
git worktree list
```

现在可以分别在两个目录启动 Agent：

- `../project-user-profile`：开发用户资料功能。
- `../project-payment`：开发支付功能。

Worktree 可以让多个分支同时拥有独立的工作目录，不需要频繁切换分支。

但它不负责解决共享文件冲突、数据库迁移冲突、接口依赖和测试环境隔离。对于涉及同一文件或同一业务流程的任务，应先明确修改范围和接口约定。

另外，不要让多个 Agent 同时修改同一个 Worktree。每个 Feature 完成后，仍然必须经过 Review、测试和 PR 集成。

## 四、建立统一的 Code Review 准则

多模型 Review 的重点不是让模型尽可能多地找问题，而是用最少的人工时间发现真正会导致故障的缺陷，避免因为无效意见反复修改代码。

建议将以下规则保存到仓库的 `rule.md`，并在每次 Review 时作为固定审查规范传给 Reviewer。

### 4.1 Review 的目标和范围

Review 开始前，先对齐本次需求、PR 描述和实际代码变更。

必须回答三个问题：

1. 这次修改是否真正解决了需求？
2. 是否符合现有系统架构、调用链路和接口约定？
3. 是否会破坏其他功能或引入新的风险？

对于 Bug 修复，必须判断修改是否解决根因，而不是绕过症状。

不要追求逐行评论。重点检查可能造成真实故障的代码，纯风格偏好、命名偏好、格式问题以及“可以更优雅”的建议不作为 Review 意见。

### 4.2 每条意见必须有证据

每个问题必须提供：

- 严重级别。
- `文件:行号`。
- 触发条件或复现路径。
- 实际调用链路、接口契约、失败测试或其他证据。
- 可能造成的实际影响。

拿不准的问题，先检查调用链、运行类型检查或相关测试。仍然无法确认时，标记为“待确认”，不要直接认定为 Bug。

不能仅凭函数命名、代码风格或模型推测下结论。

### 4.3 统一问题分级

| 级别             | 定义                      | 处理方式                 |
| -------------- | ----------------------- | -------------------- |
| `Important`    | 会导致真实 Bug、安全、数据、权限或计费问题 | 必须处理，或明确证明问题不成立      |
| `Nit`          | 不影响主要功能的小问题             | 可选处理，每轮最多 3 条        |
| `Pre-existing` | 本次修改之前就存在的问题            | 单独列出，不归责本次修改，不要求本次修复 |

Review 输出必须按照严重程度排序。

开头先给出数量，例如：

`2 个 Important，1 个 Nit，1 个 Pre-existing`

如果没有需要处理的问题，直接写：

`没有需要修的。`

不要为了显得审查充分而硬凑意见。

### 4.4 根据风险决定审查深度

| 变更类型          | 审查要求                |
| ------------- | ------------------- |
| 文案、文档、纯样式调整   | 快速检查                |
| 通过现有开关控制的新功能  | 重点检查开关及相关调用路径       |
| 普通业务逻辑        | 检查边界条件、异常处理和回归风险    |
| 支付、计费、积分扣减    | 深审金额、幂等性、重复请求和数据一致性 |
| 登录、鉴权、权限控制    | 深审身份验证、资源归属和越权风险    |
| 数据库迁移         | 深审兼容性、数据完整性和回滚方案    |
| Webhook       | 深审签名验证、重放、重复事件和状态流转 |
| CI、部署、密钥及环境变量 | 深审权限边界、部署影响和敏感信息泄露  |

对支付、鉴权、数据库迁移、Webhook、CI 和部署等高风险变更，最终结论必须明确提示：

这块建议人工再看一眼。

### 4.5 安全问题必须单独检查

每次 Review 都要单独检查：

- API Route、Server Action 是否缺少身份验证或资源权限校验。
- 是否存在越权访问、敏感数据泄露。
- 是否存在 SQL、命令或其他类型的注入风险。
- 是否存在 SSRF 风险。
- 密钥是否泄露到前端代码、客户端构建产物或日志。
- 外部回调是否经过签名、来源和参数校验。
- 高风险操作是否具备必要的幂等性和权限限制。

不能因为功能测试通过，就认定安全检查也已经通过。

### 4.6 发现同一类问题，要一次检查全部位置

如果发现某类问题，应先判断它是否存在于其他调用点。

例如发现某个 API 缺少资源归属校验，就应搜索同类 API，列出本次变更涉及的全部问题位置，而不是只指出第一处。

但不要为了扩大 Review 范围而无限扫描无关的历史代码。

目标是让作者一次修复同类问题，避免下一轮又出现相同缺陷。

### 4.7 Review 必须收敛

同一项改动最多进行 3 轮 Review：

- 第 1 轮：审查本次完整变更及其必要上下文。
- 第 2 轮：只审新增的 diff，不重复第一轮已经提出的问题。
- 第 3 轮：继续只审新增的 diff，重点确认遗留的 Important 问题。

复审时，不要重新翻查第一轮就已存在、且没有被本次改动影响的老代码。此类问题如有必要，单独标记为 `Pre-existing`。

第 3 轮后仍有 `Important` 问题，就停止继续打补丁，建议退一步重新设计方案或交由人工处理。

同一类意见反复出现时，应考虑将规则沉淀到 `rule.md`、测试用例或 ESLint 等静态检查规则中，从源头减少问题。

### 4.8 修改完成前必须自证

开发 Agent 在说“完成”之前，必须运行与变更相关且可执行的检查，并以真实输出作为依据。

根据项目情况运行：

```
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

如果是 UI 改动，还应在可运行的环境中检查页面效果，必要时截图对照需求。

不能只根据 Agent 的文字说明判断检查通过。编排器应记录命令、退出码和关键输出。

对于高风险改动，应同时检查回滚方式：是否有功能开关、迁移是否可逆、是否可以通过独立提交恢复。最终结论用一句话说明回滚路径。

## 五、让多个 Agent 按统一准则执行 Review

将第四节的规则保存到 `rule.md`，并在项目中创建 `prompts/review.md`。

示例提示词：

请按照仓库中的 rule.md，对当前 Feature 相对目标基线的代码变更进行 Code Review。

开始前先阅读本次需求、PR 描述和相关代码，确认修改意图。

审查要求：

1. 判断是否解决了真实问题、是否符合现有系统约定、是否会破坏其他功能。
2. 优先发现真实 Bug、安全、数据一致性、权限和计费风险。
3. 每条意见必须包含严重级别、文件:行号、触发条件或复现路径，以及支持结论的证据。
4. 不确定的问题先检查调用链、类型检查和相关测试；仍无法确认的标记为待确认，不要作为已确认 Bug 报告。
5. 合并同类问题，列出本次变更涉及的全部问题位置。
6. 不报告纯风格、命名偏好、格式或个人审美类意见。Nit 每轮最多 3 条。
7. 区分 Important、Nit 和 Pre-existing，按严重程度排序。
8. 支付、计费、权限、数据库迁移、Webhook、CI、部署及密钥相关改动必须深审，并明确提示是否需要人工复核。
9. 本任务只进行审查，不修改代码。请遵守实际工具提供的只读权限。

输出开头先列问题数量。没有问题时直接输出“没有需要修的”。

最后给出简短结论，说明主要风险、尚未验证的事项及必要的人工复核建议。

建议让两个 Reviewer 独立运行，分别输出到：

```
review/
  reviewer-a.md
  reviewer-b.md
```

不要把 Agent A 的结论直接交给 Agent B 作为唯一审查依据，否则容易让第二个模型跟随第一个模型的判断。

编排器随后负责合并重复意见、校验必需字段，并把待验证问题交给验证步骤。

注意：提示词不能保证模型遵守规则，也不能证明问题真实成立。正式运行时，还要通过 CLI 权限限制、输出校验、测试和人工复核来控制风险。

## 六、验证问题并修复

两个 Reviewer 输出后，不要直接把所有意见交给开发 Agent 修改。

推荐执行以下步骤：

1. 汇总并去重。
2. 检查每条意见的文件、行号及相关代码。
3. 根据触发条件运行现有测试或构造复现用例。
4. 确认问题成立后，才安排修复。
5. 对不成立的问题记录排除依据。
6. 修复后运行相关检查，并再次 Review 新增的 diff。

例如 Reviewer 报告某个用户接口缺少权限校验，应先检查实际调用链，确认当前登录用户是否能访问其他用户的数据，再通过测试验证问题。

不能仅凭 Reviewer 的严重级别或多个模型的投票结果决定是否修复。

建议为每条问题记录以下字段：

```
{
  "severity": "Important",
  "file": "src/api/user.ts",
  "line": 42,
  "description": "缺少资源归属校验",
  "evidence": "接口未验证目标用户是否属于当前登录用户",
  "status": "pending",
  "verification": null,
  "fixCommit": null
}
```

这是内部数据结构示例，实际实现时应根据项目补充触发条件、测试结果、首次发现轮次和处理记录。

如果没有发现 `Important` 问题，可以进入后续检查和 PR 流程。若存在无法验证的高风险问题，应先阻止自动合并，而不是把“待确认”当成通过。

## 七、配置 GitHub Actions

在项目根目录创建 `.github/workflows/ci.yml`：

```
name: CI

on:
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:
  checks:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - name: Enable pnpm
        run: corepack enable

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Typecheck
        run: pnpm typecheck

      - name: Unit tests
        run: pnpm test

      - name: Build
        run: pnpm build
```

这是基础模板。正式使用前，应将 Node.js 版本调整为项目要求，声明正确的 pnpm 版本，并把示例 Action 版本替换为经过审查的固定 commit SHA。

如果项目测试依赖数据库、Redis、浏览器或第三方服务，需要在 CI 中配置对应环境。没有实际配置的 E2E 测试，不要直接加入一个看似完整的命令。

这里使用 `pull_request` 触发检查。若仓库需要对合并后的 `main` 再执行验证，可以单独增加工作流。

提交配置后，推送 Feature 分支并创建 PR。

```
git add .github/workflows/ci.yml
git commit -m "ci: add pull request checks"
git push -u origin feature/user-profile
```

如果还有其他实际修改，应根据 `git status` 确认提交范围，避免误提交环境变量、密钥或无关文件。

## 八、创建 PR 并准确获取 CI 结果

创建 PR：

```
gh pr create \
  --base main \
  --head feature/user-profile \
  --title "feat: add user profile" \
  --body "Implement user profile feature with tests."
```

查看 PR 信息：

```
gh pr view --json number,url,headRefOid
```

查看检查状态：

```
gh pr checks PR_NUMBER
```

`PR_NUMBER` 必须替换为真实的 PR 编号。

编排器不能只获取最近一次失败的工作流就启动修复。必须将 CI 运行记录与当前 PR 的最新提交 SHA 对齐。

例如：

```
gh run list \
  --branch feature/user-profile \
  --event pull_request \
  --limit 10 \
  --json databaseId,headSha,status,conclusion,event
```

从返回结果中筛选与 PR 当前 `headRefOid` 一致的运行记录，再等待对应的运行结束：

```
gh run watch RUN_ID --exit-status
```

获取失败日志：

```
gh run view RUN_ID --log-failed
```

`RUN_ID` 必须替换为真实运行 ID。

如果等待期间又有新提交，旧 CI 结果不能作为新提交的通过依据。调度器必须重新读取 PR 的最新 SHA，并确认对应检查已经完成。

## 九、CI 失败后的自动修复机制

CI 失败时，先判断错误是否适合自动修复，再决定是否启动开发 Agent。

| 失败情况             | 处理方式           |
| ---------------- | -------------- |
| Lint、类型检查、单元测试失败 | 分析失败代码和测试结果    |
| E2E 失败           | 检查断言、业务逻辑和测试环境 |
| 依赖安装失败           | 检查锁文件、版本及依赖源   |
| 数据库或第三方服务不可用     | 优先检查 CI 环境配置   |
| 权限错误、合并冲突        | 停止并交由人工处理      |
| 根因不明确或反复修复失败     | 停止自动修复         |

自动修复循环：

```
获取当前提交的失败日志
        ↓
判断是否允许自动修复
        ↓
Agent 分析并修改代码
        ↓
运行本地相关测试
        ↓
检查修改范围和 Git 状态
        ↓
提交并推送 Feature 分支
        ↓
等待新提交对应的 CI
        ↓
通过 → 进入合并流程
失败 → 判断是否继续重试
```

建议最多自动修复 3 次。重试次数必须由编排器持久记录，不能依赖 Agent 自己记忆。

每次修复都应记录提交 SHA、CI 运行 ID、失败日志、修改文件、测试结果和重试次数。

如果涉及数据库迁移、支付逻辑、权限模型或大规模架构调整，应停止自动修复并交由人工审核。

## 十、配置 main 分支保护和自动合并

进入 GitHub 仓库的 `Settings`，找到 `Rules → Rulesets`，为 `main` 配置分支保护。具体入口和可用选项以仓库当前界面为准。

建议至少设置：

- 必须通过 PR 合并，禁止直接推送到 `main`。
- 要求指定 CI 检查通过。
- 按团队要求配置审核人数和其他合并条件。
- 不允许普通 Agent 绕过分支保护。

启用仓库的自动合并功能后，执行：

```
gh pr merge PR_NUMBER --auto --squash
```

这会请求 GitHub 在所有必需条件满足后自动合并 PR。`--squash` 表示使用 Squash 合并策略，应根据项目实际策略调整。

需要特别注意：

- 请求自动合并成功，不代表 PR 已经合并。
- 编排器必须继续查询 PR 状态，直到确认合并成功或触发异常处理。
- 自动化账号必须具有所需权限，但不能因此获得不必要的管理员权限。
- 不得使用旧提交的 CI 结果为新提交放行。

对于支付、权限、数据库迁移等高风险变更，即使 CI 通过，也应保留必要的人工审批门禁。

## 十一、用 TypeScript 编排器串联所有步骤

前面的配置完成后，最后才是将步骤串起来。

建议创建 `scripts/orchestrator.ts`，统一管理：

1. 创建 Worktree。
2. 启动开发 Agent。
3. 运行本地检查。
4. 启动多个独立 Reviewer。
5. 验证问题并安排修复。
6. 推送代码并创建 PR。
7. 获取与当前提交 SHA 对应的 CI 结果。
8. CI 失败时执行限次修复。
9. CI 通过后请求自动合并。
10. 确认合并结果，记录状态并清理 Worktree。

建议至少定义以下任务状态：

| 状态              | 含义       |
| --------------- | -------- |
| `developing`    | 开发中      |
| `reviewing`     | Review 中 |
| `validating`    | 验证问题     |
| `waiting_ci`    | 等待 CI    |
| `repairing`     | 自动修复中    |
| `waiting_merge` | 等待合并     |
| `merged`        | 已确认合并    |
| `blocked`       | 需要人工介入   |

这些状态必须持久保存，并记录任务 ID、分支、PR 编号、提交 SHA、CI 运行 ID、Review 轮次和修复次数。

不同 AI CLI 应分别封装适配器，统一返回退出码、输出和执行状态；GitHub 操作也应独立封装，便于测试和替换实现。

需要明确：上述架构和命令可以作为实际实施基础，但完整的 `orchestrator.ts` 仍需结合所选 Agent CLI 编写。 不同 CLI 的参数、权限、输出格式并不一致，不能仅凭一个接口示例就认为所有工具已经打通。

第一版建议先实现单 Feature、两个 Reviewer、CI 状态查询和 GitHub 自动合并，再加入自动修复和多 Feature 并行。

## 十二、最终验收标准

整套自动化流程至少应通过以下验证：

- 两个 Feature 可以在独立 Worktree 中开发。
- 两个 Reviewer 能独立输出带文件、行号和证据的审查报告。
- Review 意见经过验证，不会直接把猜测当成 Bug。
- 修复完成后能够运行真实的本地检查。
- PR 触发 GitHub Actions，并能准确关联当前提交 SHA。
- CI 失败时能够获取对应日志，并按规则决定是否自动修复。
- 自动修复具有明确的重试上限和持久化状态。
- CI 通过后能够请求 GitHub 自动合并，并确认最终结果。
- 高风险变更、权限异常和无法确认的问题会停止自动化。
- Review 最多 3 轮，重复意见不会无限出现。

> 最终目标不是让 AI 无条件地修改和合并代码，而是让每一步都有明确的执行者、可验证的结果、有限的重试次数和可靠的退出机制。

只有当 Code Review、测试、权限控制和合并门禁真正连通后，多 Agent 编程才算从演示流程变成了可维护的工程自动化。
