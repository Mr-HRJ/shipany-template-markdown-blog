---
title: '开源的第一个SEO&GEO系统：GEOFlow'
---

> 做内容站、搞 SEO 流量的，这个开源项目能帮你省掉大量重复劳动。

GEOFlow —— 一套完整的 AI 内容生产流水线，从素材管理到 AI 生成到审核发布，全链路自动化。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f08c1614c9fb6ddb.jpg)

https://github.com/yaojingang/GEOFlow

> 1、GEOFlow系统可用于官网GEO频道部署、独立资讯站、以及独立官网甚至多站点部署，实现自动化+智能化的自运营；
2、对SEO&GEO进行了工作流层面的规范，前端相关页面做了相关的GEO代码规范，系统后台完成相关配置后，系统自动完成内容与发布的管理；
3、配套skill，通过skill可以与CLI及各种skill打通，实现更智能、便捷的管理，也可以接入多个AI工作台，比如codex、牛马AI、CodePilot等

我觉得它解决了一个真实痛点：

手动用 ChatGPT 写文章，一篇一篇复制粘贴，再手动排版、加 SEO 标签、上传发布——一天能搞几篇？10 篇顶天了。

GEOFlow 的做法是把这件事变成工厂模式：

1. 后台配好 AI 模型（兼容 OpenAI 接口，DeepSeek、GPT 都能接）
2. 录入素材：标题库、关键词库、图片库、提示词模板
3. 创建批量任务，设定调度规则
4. 系统自动排队生成，失败自动重试
5. 文章进入审核流程，确认后一键发布
6. 前台页面自动带 SEO 元信息、Open Graph、结构化数据

你要做的就是配一次，然后看着它跑。

Docker Compose 一键部署，还带 CLI 工具，可以用命令行批量操作。

Apache 2.0 开源，免费用。

https://github.com/yaojingang/GEOFlow
