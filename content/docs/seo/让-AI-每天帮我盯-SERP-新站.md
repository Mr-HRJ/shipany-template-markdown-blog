---
title: '让 AI 每天帮我盯 SERP，新站一冒头当天就知道'
date: '2026-11-18'
---

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/0e54068e051dd7be.jpg)

之前我看关键词排名，都是偶尔人工去搜一下。排名变了反应不及时，常常过了很久才突然发现，自己做的词有个新站已经做上去了。

前段时间看到 joker 老师分享的 serp 监控（下图），现在我换了个做法：用 AI 的定时任务帮我盯 SERP，自己的词每天看，大词每周看。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/2e3c0a80c1654a0b.jpg)

排在前面的页面，就是 Google 认为最符合用户搜索意图的内容，所以 SERP 的变化，其实就是 Google 的风向标。

大家平时可能更关注自己做的词，最近又有谁新冒了出来，AI Overview 引用了谁，看看冒出来的对手做了什么操作，是不是个机会点，自己可以超过他。

我把要盯的词分成两类：

- 自己网站在做的词：每天看，有新站冒上来、自己掉了、AI Overview 变了，当天就能知道
- 大词：暂时排不上，每周看一次，看 Google 的风向，也看看 AI Overview 喜欢引用什么样的页面

## 接入三方的 SERP API

数据这块我用的是 @Glasserai，它可以让 Claude Code 这类 AI 用一个 API key 调 Google 搜索结果、Ahrefs 这些付费数据，按次付费，不用一家家去开订阅，而支持 SEO 相关的 API 也非常多。

在 glasser.ai 注册后，按官网的 Setup 把它接到 Claude Code 上，然后直接用自然语言告诉 AI 要做什么就可以了，定时也是交给 Claude Code 来跑。

## 盯自己做的词

自己的词每天跑一次：

```
每天 9 点，查【你在做的词，用顿号隔开】。列出我的排名、SERP 模块（AI Overview、视频、Reddit）、AI Overview 引用了哪些网站、有没有引用我，以及和昨天相比新进前 10 的网站，每行附来源链接，出一份日报。
```

日报我会看：自己有没有掉出前 10，有没有新站冒上来，AI Overview 有没有换了引用的网站。第一次运行没有昨天的数据，可以让它先用最近一次的历史 SERP 快照来比。

## 盯大词，看风向

比如我选了 AI 视频和图片方向的大词，prompt 如下，就给我创建好定时任务了：

```
每周一 9 点，查这 5 个大词在 Google 美国站的前 10：ai video generator、image to video、text to video、ai photo editor、ai headshot generator。列出 SERP 模块、AI Overview 引用了哪些网站，以及和上周相比新进和掉出前 10 的网站，每行附来源链接，出一份周报。
```

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/e0893bddfc6fbc78.jpg)

每个词跑出的结果有个详细链接，一个词只花费 $0.002，还是可以花挺久的。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/828440bd3173a83d.jpg)

不过我发现现在风向标暂时还看不太出来，变化不大，需要接下来持续观察，可能才会有一些发现。

## 最后

大家如果有关注的方向或者搜索词，定期看看对应的搜索结果，感觉是个不错的方式，尤其是那种变化的数据。
