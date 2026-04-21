---
title: '创建一个claude skill 减少重复操作'
---

## 写在前面

如果你感觉麻烦，可以直接买Saas模板（内置了Skill一步到位），省去你这一步;
> Shipany AISaas模板，1小时快速上站，可扫码直接购买
> ![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/8eea25d4e67fee53.jpg)

> 这篇文章复盘了我在开发中如何用 Skill Creator 给 Claude Code 做一个可复用的“自动生成图片”技能，把原本需要我手动用 nano banana 生成图片的重复工作，变成 Claude Code 能自己完成的流程化能力。核心价值在于：**把高频、机械的素材生成工作从“人肉操作”变成“代码可调用的能力”**，尤其适合落地页、功能页这种需要大量配图的场景。文章同时记录了一个很现实的问题：如果你因为网络/权限原因无法在 claude.ai 打开 Skill Creator，也可以通过 GitHub 本地安装到 `.claude/skills/` 目录来正常使用，并在创建 Skill 时把 API 文档和调用规范提供给 Claude Code，确保它能写出正确的调用逻辑。

---


我在开发网页时有一个很常见的场景：

* 页面需要配图
* 我得自己去用 nano banana 生成图片
* 再下载、命名、放到项目里
* 最后把图片引用到页面组件里

这件事的问题不在于难，而在于**太耗时间**，尤其是：

* Landing page 经常要做多个版本
* feature 模块需要多张图
* 图片风格要统一
* 一次改版就是一轮重新生成

所以我想把它变成一个能力：
**让 Claude Code 在写页面时，自己生成配图并自动接入页面。**

Skill 就是最合适的载体。

---

# Skill Creator 的两种安装方式

正常情况下，创建 Skill 是“开关 + 对话式生成”就能完成的。

但我这次遇到一个现实情况：

* 我用的是拼车环境
* 禁止访问官方网页
* 在 claude.ai 里打开 Skill Creator 会报错

所以我走了本地安装的路线。

---

## 方式一：在 claude.ai 里启用 Skill Creator

常规路径是：

1. 进入 claude.ai
2. 点击头像
3. Settings
4. Capabilities
5. Skills
6. 打开 **Skill Creator**

然后你直接让 Claude Code 使用 Skill Creator 创建 Skill 就行了。

但如果你像我一样因为环境限制打不开，那就用方式二。

---

## 方式二：从 GitHub 下载 Skill Creator 手动安装

我的做法是：

1. 从 GitHub 把 Skill Creator 下载下来
2. 放到 Claude Code 的 skills 配置目录里

如果你不知道目录在哪，最省事的方式就是：

* 直接问 Claude Code：
  你的 skills 目录在哪？我应该把 skill creator 放哪里？

我自己的环境里，目录是：

* 用户主目录下的：`.claude/skills/`

也就是类似：

* `~/.claude/skills/`

把 Skill Creator 放进去之后，就可以正常创建 Skill 了。

---

# 用 Skill Creator 创建一个“生成图片”的 Skill

安装好之后，接下来就是创建 Skill 的关键环节。

## 1. 明确你要创建的 Skill 做什么

我的目标非常清晰：

* 创建一个生成图片的 Skill
* 需要调用我自己的 API 来生成图片

因为涉及调用 API，Claude Code 必须知道：

* 请求地址是什么
* 参数怎么传
* 返回格式是什么
* 图片如何下载/保存/命名

所以文档一定要给全。

---

## 2. 提供生成图片 API 的文档

我在创建 Skill 的描述里，直接给了文档路径（Windows为例）：

* `D:\code\mksaas-template\docs\nano-api.md`

核心原则是：

> 只要 Skill 需要调用外部服务，就必须把调用文档和示例给到它，否则它只能猜。

如果你还有其他相关依赖，比如鉴权方式、请求签名、headers、错误码，也要一并给到它。

---

## 3. 按 Skill Creator 的提问一步步选择

Skill Creator 会问你一些问题：

* Skill 的输入是什么
* 输出是什么
* 调用流程怎么组织
* 失败时怎么处理
* 图片保存到哪里
* 命名规则是什么

你只需要按你的需求选即可。

这一步不需要你“写代码”，主要是把边界讲清楚。

---

# 如何找到生成出来的 Skill

创建完成之后，生成的 Skill 会出现在同一个目录下：

* `.claude/skills/`

你会看到一个新文件夹/新文件，就是它生成的 Skill。

这一步非常重要，因为你后续：

* 想修改 prompt
* 想调整保存路径
* 想加默认风格模板
  都得回到这里改。

---

# 如何使用你新创建的 Skill

Skill 创建好之后，就可以在实际开发中直接用了。

我这次测试用的方式很简单：

我只给 Claude Code 一句话需求，让它：

* 新增一个页面
* 页面 feature 需要配图
* 图片通过 `nano-image-generator` skill 自动生成

示例需求是这样的（这里保留你原本的调用方式）：

* “帮我新增一个 photo to video landing page 页面，页面 feature 需要的图片使用 nano-image-generator skill 进行生成”

然后 Claude Code 就能自己完成：

* 生成页面结构
* 调用 Skill 生成图片
* 把图片放到项目中合适的位置
* 在页面中引用这些图片

从体验上看，这件事最大的价值在于：

**你不需要在“写页面”和“做素材”之间来回切换。**

---

# 这套流程最关键的注意点

## 1. Skill 不是魔法，文档决定上限

如果你不给 API 文档或示例：

* Skill 很容易写出“看起来对，但跑不通”的调用逻辑

所以一定要提供：

* 请求示例
* 返回示例
* 鉴权方式
* 错误处理策略

## 2. 让 Claude Code 先复述调用流程

为了避免“抽卡”，我建议在它真正生成 Skill 前：

* 让它先总结它理解的 API 调用流程
* 看看有没有理解偏差

这一步成本很低，但能减少后续返工。

---

# 核心结论

把这件事总结成一句话：

**Skill Creator 的价值，是把高频重复劳动做成可复用的工具能力，让 Claude Code 真正“自己干活”。**

对我这种经常做 Landing page、需要大量配图的开发流程来说：

* 以前：写页面 + 手动生成图 + 再回项目接入
* 现在：一句话需求，Claude Code 自己生成并插入图片

效率提升非常明显。
