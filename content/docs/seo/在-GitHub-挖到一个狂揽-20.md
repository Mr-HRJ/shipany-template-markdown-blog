---
title: '在 GitHub 挖到一个狂揽 20.1k Stars 的满分开源项目：claude-seo'
date: '2026-10-26'
---

真是不给传统 SEO 外包和天价工具留活路了……
刚在 GitHub 挖到一个狂揽 20.1k Stars 的满分开源项目：claude-seo(https://github.com/AgriciDaniel/claude-seo) （作者 AgriciDaniel）。它直接把 Claude Code 变成了一个由 19 个专家 Agent + 26 个子技能 组成的“全自动 SEO 特种部队”。
以前做一次深度的全站 SEO 审计，要么买每月几百刀的 Ahrefs/SEMrush，要么花几千刀找 Agency 等上两周。现在在终端里甩给它一个网址，15 分钟、0 成本，最多 17 个 AI Agent 会在本地并发执行：
• 传统基建全包：爬虫抓取、死链重定向、Core Web Vitals 性能、E-E-A-T 内容质量评估，甚至自带无头浏览器渲染 React/Next.js 页面，自动帮你写好修复版的 http://Schema.org 结构化代码。
• 降维打击的 GEO（AI 搜索优化）：现在的 SEO 早就变天了。它内置 /seo geo 和 /seo agentic 命令，专门检测你的网站有多大概率被 ChatGPT、Perplexity、Gemini 和 Google AI Overviews 引用，连最新的 llms.txt 和 WebMCP 智能体就绪度都能一键排查。
• 交付即落地：跑完不给你堆砌一堆看不懂的警告，而是直接生成按优先级排好的 Markdown / PDF 整改方案，连“改完怎么验证生效”都给你写得明明白白。作者自己的新站靠这套工具，前 12 周直接拿下 10.8K GSC 自然点击，移动端速度干到 99 分。
安装极其无脑（需 Claude Code 环境）：
1️⃣ /plugin marketplace add AgriciDaniel/claude-seo
2️⃣ /plugin install claude-seo@agricidaniel-claude-seo
3️⃣ /seo setup
装完直接一句 /seo audit 你的网址 就能看 AI 军团干活了。MIT 协议完全开源，数据全在本地。
