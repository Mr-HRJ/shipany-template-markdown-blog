---
title: '创建claude code命令，减少重复操作'
---

> 这篇文章系统整理了我在多个项目中复用 Claude Code 的一个高效技巧：**把高频使用的提示词封装成可调用的个人命令**。通过在本地创建简单的 Markdown 文件，就可以把 SEO 检查、代码检查、基于关键词生成内容等重复性工作，变成“随时可调用”的标准化指令。整个过程只需要三步，不涉及复杂配置，但能显著降低重复输入成本，并让 AI 协作更加工程化。

---

在不同项目中，我经常会让 Claude Code 做一些**高度重复的事情**，比如：

* SEO 检查页面质量
* 代码规范和潜在问题检查
* 根据关键词生成 SEO 内容

如果每次都重新输入一大段提示词，会出现几个问题：

* 浪费时间
* 容易前后不一致
* 提示词版本不好维护

所以我后来干脆把这些固定流程，**封装成“个人命令”**，在任何项目里都能直接调用。

---

# 核心思路是什么

本质非常简单：

* 每一个命令
* 就是一个独立的 `.md` 文件
* 文件名就是命令名
* 文件内容就是你固定使用的提示词

当你调用命令时：

* 把动态内容作为参数传进去
* 由 `$ARGUMENTS` 接收

这就相当于给 Claude Code 做了一层“快捷指令”。

---

# 创建 Claude Code 命令的完整三步流程

整个过程，我自己总结下来就是三步，没有任何隐藏操作。

---

## 一、找到 .claude 目录并创建 commands 文件夹

第一步是找到 Claude Code 的配置路径。

* `.claude` 目录一般在**用户路径**下
* 每个人系统位置可能略有不同

在这个目录中：

1. 新建一个 `commands` 文件夹

这个文件夹，专门用来存放你的自定义命令。

---

## 二、创建命令对应的 Markdown 文件

接下来，在 `commands` 目录中：

1. 新建一个 `.md` 文件
2. 文件名就是你要使用的命令名

举个我自己的例子：

* 我做了一个 SEO 检查命令
* 文件名就叫：`seo-check.md`

后续在项目中调用时，用的就是这个名字。

---

## 三、在 md 文件中编写提示词内容

`.md` 文件里写的，就是你希望 Claude 每次执行的完整指令。

### 一个完整的示例

下面是我在 `seo-check.md` 里实际写的内容结构：

* 明确角色
* 明确任务
* 明确分析维度
* 明确输出形式

  
// 例如：
```
You are an SEO expert. Check the SEO quality of the following page:
Page: $ARGUMENTS
Please analyze from the following aspects:
1. Title tag quality and keyword usage
2. Meta description clarity and length
3. Heading structure (H1/H2/H3)
4. Internal linking opportunities
5. Image alt text usage
6. Content quality and keyword density
7. Page load speed and mobile friendliness
8. Overall recommendations for improvement
Provide a clear, structured report.
```

同时，关键点在这里：

**用 `$ARGUMENTS` 来接收调用时传入的参数。**

---

### 使用 $ARGUMENTS 的意义

`$ARGUMENTS` 的作用是：

* 在调用命令时
* 把不同的输入内容传进来
* 而不需要改动命令本身

在 SEO 检查这个场景里：

* `$ARGUMENTS` 接收的就是页面内容或页面 URL

这样同一个命令：

* 可以反复用在不同页面
* 不需要复制、修改提示词

---

# 如何调用自定义命令

调用方式本身非常简单。

核心规则只有一句话：

**用文件名作为命令名即可调用。**

比如：

* 你创建了 `seo-check.md`
* 那么在任何项目中
* 直接用 `seo-check` 这个命令

再配合传入的参数，就能让 Claude 按你预设的流程执行。

---

# 这种方式适合用在什么场景

从我的实际使用来看，特别适合下面几类任务：

* SEO 审查类流程
* 代码检查和代码 Review
* 内容生成模板
* 固定结构的分析报告
* 项目初始化时的通用指令

只要你发现：

* 自己在反复输入“几乎一样的话”
* 那就非常值得把它抽成一个命令

---

# 核心结论

总结下来，这套方法的价值非常明确：

* **把重复沟通变成一次性配置**
* **把随意对话升级为标准流程**
* **让 AI 使用方式更接近工程化工具**

它本质不是“高级玩法”，而是一个**节省时间、降低出错概率的小技巧**。

当你开始把常用提示词沉淀成命令之后，
你会明显感觉到：
**AI 不再只是聊天对象，而是一个可复用的生产力组件。**
