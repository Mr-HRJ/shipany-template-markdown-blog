---
title: '你只需要这一篇 SEO/GEO 文章，把它交给你的 AI'
date: '2026-11-16'
---

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/80ca1964ce5cc8be.jpg)

我让 Claude 读了 66 篇 SEO/GEO 文章、48 个技能和 14 个 GitHub 仓库。
下面就是你唯一需要的那份实操手册。
时间紧？文末有一段提示词。把它和这篇文章一起贴进你的 AI，让它直接跑审计。

我的信息流每周都在说：SEO 已死，GEO 才是新淘金热。
我正在推出一款产品（@SpaceCutAI，一个 AI 视频编辑器）。
我要的是真相，不是炒作。

于是我把自己在 X 上收藏的 66 篇 SEO 和 GEO 文章、一套供 AI 智能体使用的 48 个免费「SEO skills」，再加上另外 13 个星标从 2,000 到 27,000 的 GitHub 仓库，全部交给 Claude 阅读、整理，并在我自己的网站上跑了基础检查。

## 没人告诉你的 4 件事

1. 大约 90% 的建议，其实就是那十来条老话。其中大多数还是经典 SEO。
2. 那些醒目的大数字，几乎都没有数据支撑。至少有两篇文章，标题里的「AI mentions（AI 提及）」其实是 Google Search Console 里的展示次数。文章自己在更后面写了这一点。
3. 大家口口相传的阈值（「排名第 8 到第 15」「5 条内链」「DR 20」）只是经验法则。靠谱的来源会这么说；其余的则把它们写成事实。
4. GitHub 星标并不能说明建议是否仍然有效。有一个 11,000 星的仓库，把 ChatGPT 的爬虫都搞错了。下文还会细说。

这并不等于这些建议是坏的。它只是意味着：你不必再为它们付费，而且你应该自己核实。

## 1. 基础

Google 和 AI 引擎必须能读到你。

- 打开页面源代码。如果标题和正文不在原始 HTML 里，不执行 JavaScript 的爬虫看到的就是空白页。
- 读你的 robots.txt。GPTBot、ClaudeBot 和 Google-Extended 用于训练。OAI-SearchBot、Claude-SearchBot、PerplexityBot 和 Bingbot 为实时回答提供数据。把第二组拦掉，你就会从 AI 搜索里消失。
- 要读线上的那个文件，而不是项目里的那份。Cloudflare 可能在文件顶部自行加一段规则，也可以用一个开关拦截 AI 机器人。
- 测试一下：`curl -A "OAI-SearchBot" -s -o /dev/null -w "%{http_code}" https://yoursite.com/`。只要不是 200，就有问题。
- 加上一份只包含可收录页面的 sitemap、每个页面的 canonical 标签，以及结构化数据（Organization、WebSite，以及 Product 或 SoftwareApplication）。在你还没有真实评价之前，不要加评价星级。

上线前，我让 Claude 在自己的网站上跑了这些检查。Cloudflare 没有往我的 robots.txt 里加任何东西。但我没有 sitemap，没有 canonical 标签，没有结构化数据，而且 www 地址也没有重定向到主域名。

我还以为站点已经准备好了。

## 2. Bing 回来了

配置好 Bing Webmaster Tools。从 Google Search Console 导入，提交 sitemap，打开 IndexNow。十分钟就够。

Copilot 跑在 Bing 上，ChatGPT 的搜索也一度倚重它。Bing 还有一份 AI Performance 报告：列出 AI 回答引用了你网站的那些查询。这是目前最接近免费、第一方引用数据的东西。

## 3. 为决策做页面，而不是为关键词做页面

真正会被引用、也真正能转化的页面，是人们在做出选择前会读的那些：

X vs Y、X 的替代方案、适合某一类人的最佳 X、X 的定价。

规则如下，数字来自那些 skills：

- 先在 Google 上搜这个查询。如果前 10 里有 6 个或更多是同一类型的页面，你就该做这种类型。如果全是博客，而你卖的是产品，就跳过。
- 当两个关键词的前 10 结果有 4 个或更多重叠时，它们应该放在同一页。
- 在开头 40 到 80 个词里给出答案，并点出你的产品名称。AI 引擎提取的是段落，不是整页。
- 「最佳」榜单应有 5 到 8 个选项。3 个是广告，25 个是目录。
- 每个价格都来自厂商自己的页面，并标注「核对于」和日期。每个选项都要写一个真正的缺点，包括你自己的产品。
- 不要在自己做的榜单里把自家产品排第一。
- 补上前 10 结果都没有的一样东西：你自己的数据、你自己的测试、你自己的截图。把方法展示出来。

## 4. GEO：真正新鲜的部分

- 助手每回答一个问题，大约会跑十次隐藏搜索。打开 ChatGPT 或 Claude 里的「正在搜索」步骤，你就能看到它们。每一次搜索，都对应一个你需要的页面，或一个你需要出现的网站。
- 大多数引用流向第三方：「最佳」榜单、YouTube、评测站点。在某家厂商的数据集里（44,070 条引用，10 个品牌），85% 指向第三方页面，指向品牌自己网站的不足 4%。但那些自己网站也被引用的品牌，被点名的次数要高得多。两者你都需要。
- 答案会变。这些文章引用的一项研究说，ChatGPT 会在一周之内替换掉大部分来源。单次测试说明不了什么。
- AI 会把关于你的事实搞错。写一份标注日期的事实清单（价格、套餐、平台），去问这些引擎，再把每条错误陈述追溯到它来自的页面。在那里修正。只有连续两个月不再出现，才算修好。
- 如果你卖软件，用手机搜一下你的「best X」查询。如果 Google 弹出一排视频，那就去做视频。先做长视频，从 00:00 开始分章节，字幕要亲手校对。

## 5. 免费地衡量它

眼下先别买付费可见度追踪工具。

- 写出 15 到 30 个真实的买家问题。问题来自你的收件箱、销售通话和评价，而不是想象。
- 每个问题在每个引擎上至少跑两遍，并且处于登出状态：ChatGPT、Claude、Perplexity、Gemini。
- 记录谁被点名、哪些 URL 被引用。被引用和被推荐是两个不同的数字。
- 每月 AI 访问大约不到 100 次时，汇报计数，不要汇报百分比。
- 在注册时加上「你是怎么知道我们的？」。有一位创始人把它和自己的分析数据对比：推荐来源把注册量记在 Google 头上的数字，是客户自己说的 3.4 倍。

免费工具栈：Google Search Console、Bing Webmaster Tools、Ahrefs Webmaster Tools、Screaming Frog（500 个 URL）。

## 6. 外链与提及

值得花时间的：

- 上线平台和软件目录。到处用同一个名字、同一句一句话介绍、同一款 logo。做 20 到 30 个，不是 300 个。
- 未加链接的提及。搜索 `"your brand" -site:yoursite.com`，然后去要链接。
- 点了你的竞争对手、却没点你的「最佳」榜单。用 120 到 180 词的邮件投稿，带上证据。一周后再跟一次，然后停止。
- 写一篇关于你正在使用的某款工具的客户故事。厂商会给这类内容加链接。
- 在 Reddit 和 Quora 上以你本人身份出现，并做好披露。每个 subreddit 每周最多一条提及你公司的回答。

会让你吃亏的：

- 互换外链和积分网络。那些推销它们的文章自己也承认，Google 把这叫链接垃圾。
- 付费的 Reddit 和 Quora「任务」、假账号、你自己写的评价。
- 在一整站群里发 1,500 篇 AI 文章。
- 城市 × 服务的模板页。

## 7. 如果让 AI 智能体做你的 SEO

- 数字必须来自工具，绝不能来自模型。测试一下：让它按点击量列出你的前 5 个页面，再和 Search Console 对照。
- 三档权限。
  允许：读取数据、撰写草稿。
  需要批准：发布、改标题。
  绝不自行处理：删除页面、改 robots.txt 或 canonical。
  你先看 diff。
- 把「绝不」写进 hook，而不是写进提示词。
- 每次部署前给关键页面做快照，部署后再对比。会在无声中毁掉一个站点的四种改动：页面变成 noindex、canonical 指向别处、200 变成 404、robots.txt 屏蔽一切。
- 每份草稿上线前都要打分。我读过的最好的 skill，会在 8 个方面按 5 分制打分，总分 40 分里达到 32 分才算通过，且没有任何一项低于 3 分。

## 8. 新域名？先放慢节奏

- 每周新增 1 到 4 个页面。作者们在具体数字上有分歧，在方向上没有。
- 等 2 到 3 个月再判断一次改动的效果。
- 大多数 Search Console 打法（striking distance、标题测试、页面精简）需要你现在还没有的数据。留到第三个月再用。

## 这 49 篇文章背后的两款工具

我读过的内容，大部分出自两家公司：

Distribb（@borjafat）和 ChatSEO（@NicholasDulait 与 @VengeonsP）。

这两款我都还没用过。

下面是它们自己网站上的说法，阅读日期是 2026 年 11 月 10 日。

如果我这次让 Claude 读到的有误，请告诉我们；也请告诉我们，你们的产品在上述能力之外最能补上的是什么——我已经快要订阅了！

这本手册里的所有事情，都可以手工完成。这些工具售卖的，是三件手工做起来很慢、或几乎做不到的事。

- 关键词数据。大规模搜索量是要花钱的。ChatSEO 从 DataForSEO 拉取实时搜索量、外链和竞争对手数据，并放在你的 Search Console（只读）旁边。这样你就不用自己去 Google 每一个查询，也能做第 3 节的事。
- 每天追踪 AI 回答。第 5 节如果纯手工，是 30 个问题、4 个引擎、每个跑两遍。Distribb 会追踪 ChatGPT、Gemini、Perplexity 和 Google 的 AI 回答何时引用了你。
- 写作与发布。两者都会写文章并推送到你的 CMS：ChatSEO 支持 WordPress、Shopify 和 Webflow；Distribb 在这些之外还支持 Wix、Ghost、Notion 和 Framer。

两者都通过 MCP 服务器接入你的 AI 智能体：

Distribb 的所有套餐都有；ChatSEO 从 Pro 套餐起提供。

ChatSEO 还会抓取你的网站，并给出一份按优先级排列的修复清单。

价格：ChatSEO 起步价每月 29 欧元（带 MCP 为 49 欧元），有 7 天试用。Distribb 每月 97 美元，有 3 天试用。

新域名上我会先不做的 2 件事。

Distribb 有一个一键打开的外链交换（「每月自动交换 3 到 5 条链接」），而且它的套餐每月会写 30 篇文章。第 6 节和第 8 节解释了原因。

什么时候该付钱：等基础做完、并且你已经清楚自己要做哪些页面之后。在那之前不要。

## 14 个仓库，整理排序

对任何 SEO skill 的一个快速测试：问它，是哪一个机器人决定你能否出现在 ChatGPT 搜索里。OpenAI 自己的文档说是 OAI-SearchBot。GPTBot 用于训练。

值得安装的：

- RomeoSEO/seo-skills（48 个 skill，MIT）。方法最清楚，文件里也不夹带售卖。https://github.com/RomeoSEO/seo-skills
- AgriciDaniel/claude-seo（2.78 万星，26 个 skill）。在技术检查、结构化数据和 AI 爬虫上最精确，背后有真正的脚本。它能答对上面那个机器人问题，并且写着「只给实际测量到的打分。」使用它的页面、技术和 schema 命令。但要知道，它会在大型报告之后加上指向付费社区的链接。https://github.com/AgriciDaniel/claude-seo

等你有数据之后再值得用的：

- AminForou/mcp-gsc（2,200 星）。把 Claude 接到你的 Search Console。默认只读，跑在你自己的机器上，免费。https://github.com/AminForou/mcp-gsc
- every-app/open-seo（2.71 万星）。Semrush 和 Ahrefs 的开源替代。里面最精彩的一句是：「搜索量不是访问量。」需要付费数据。https://github.com/every-app/open-seo
- nowork-studio/notfair-plugin（4,100 星，45 个 skill）。一套不依赖 Search Console 数据也能做的扎实页面审计。它会经过他们的托管服务器运行，并且仍然把 FAQ 标记评为「缺失则影响很大」，而 Google 削减 FAQ 富结果、只留给少数站点，已经是好几年前的事了。https://github.com/nowork-studio/notfair-plugin

只取一个点子，其余丢掉：

- zubair-trabzada/geo-seo-claude（1.16 万星）。保留它的 Cloudflare 检查：读取你线上的 robots.txt，看 Cloudflare 有没有加封锁。其余的丢掉。它的爬虫说明里写着，如果你拦截 GPTBot，你的内容「将不会出现在 ChatGPT Search 结果中」，这与 OpenAI 的文档相矛盾。它的 SaaS 清单里仍然列着 HowTo 标记，而 Google 在 2023 年就已经不再展示它。而且它的安装方式是从 main 分支 curl 后直接打进 bash，所以先把脚本读一遍。https://github.com/zubair-trabzada/geo-seo-claude
- TheCraigHewitt/seomachine（7,600 星）。一套博客写作流水线。保留那些上下文文件（品牌语气、功能、风格指南）。丢掉「1-2% 关键词密度」这种目标，并删掉那句要求写带名字的小故事、「即便是虚构的也可以」的说明。https://github.com/TheCraigHewitt/seomachine
- Ryze-AI-Adgent/open-seo-mcp-skills（9,100 星）。有一条很好的规则：「永远不要编造搜索量。」但这些 skill 很短，而且你的数据会经过他们的托管连接器。https://github.com/Ryze-AI-Adgent/open-seo-mcp-skills
- i365dev/awesome-seo（2,900 星）。一份不过时、也不夹带厂商的阅读清单。最好的提示是：Cloudflare 的 Bot Fight Mode 可能挑战合法爬虫，所以上线后要检查安全事件。https://github.com/i365dev/awesome-seo

还有一件事。这些仓库里有 3 个会给你的网站打一个百分制分数。

这些权重从未对照过真实排名或真实引用。

读结论。别理会那个数字。

## 我会先用的 10 个 skill

全部来自 RomeoSEO：

1. technical-seo-audit: https://github.com/RomeoSEO/seo-skills/tree/main/skills/technical-seo-audit
2. schema-markup: https://github.com/RomeoSEO/seo-skills/tree/main/skills/schema-markup
3. ai-agent-readiness: https://github.com/RomeoSEO/seo-skills/tree/main/skills/ai-agent-readiness
4. xml-sitemap-check: https://github.com/RomeoSEO/seo-skills/tree/main/skills/xml-sitemap-check
5. seo-change-monitor: https://github.com/RomeoSEO/seo-skills/tree/main/skills/seo-change-monitor
6. comparison-page-writer: https://github.com/RomeoSEO/seo-skills/tree/main/skills/comparison-page-writer
7. ai-prompt-research: https://github.com/RomeoSEO/seo-skills/tree/main/skills/ai-prompt-research
8. ai-brand-facts: https://github.com/RomeoSEO/seo-skills/tree/main/skills/ai-brand-facts
9. seo-content-qa: https://github.com/RomeoSEO/seo-skills/tree/main/skills/seo-content-qa
10. ai-traffic-analytics: https://github.com/RomeoSEO/seo-skills/tree/main/skills/ai-traffic-analytics

其余的先跳过，等真正需要再用。其中十来个是面向商店、本地商家和站点迁移的。还有几个需要数月的 Search Console 数据，新站点并没有。

## 顺序

- 第 0 周：打好基础、配置 Bing，并先跑一轮买家问题。
- 上线：Search Console、sitemap、目录站。
- 第 1 个月：每周一个决策页，每个决策页配一条视频。
- 第 3 个月：打开 Search Console，开始优化。

我正在把这一切用到 SpaceCut 上，从零开始：新域名，没有外链，没有历史。

数字无论好坏，我都会公布。

## 把这段交给你的 AI

你不必手工做完这些。复制下面的提示词，填好三行，然后把这整篇文章贴在它下面。

它最适合能打开你网站项目的智能体（Claude Code、Cursor、Codex）。普通聊天助手可以跑审计、写草稿，但不能动手修改。

```
把下面这份实操手册应用到我的网站上。
网站：[你的网址]
产品：[一句话]
竞争对手：[2 或 3 个名字]

按这个顺序工作。每一步结束后停下来，把你发现的结果给我看。

1. 只做审计。什么都不要改。抓取我线上的 robots.txt、首页的原始 HTML、我的 sitemap 以及我的 www 地址。对第 1 节里的每一点，给出通过或失败，并附上证据：那一行或状态码。
2. 列出修复项，从小的开始。每一项写明：文件、改动，以及你将如何检查它是否生效。
3. 每一次改动前等我确认。凡是会动到 robots.txt、canonical、重定向或 noindex 的，先给我看 diff。绝不删除任何页面。
4. 每次改动之后，再跑一遍检查，并把结果给我看。
5. 列出只有我本人能做的事项（Search Console、Bing Webmaster Tools、目录站、外联、视频），并排好顺序。
6. 为我的产品起草 20 个买家问题。把你猜的那些标出来，方便我换成真实的问题。
7. 按第 3 节提议 5 个决策页。每一个写明：查询词、眼下前 10 结果长什么样，以及我的页面会多出来的那一样东西。在我选定之前，不要写任何页面。

规则：
- 数字必须来自工具或你抓取到的页面，绝不能来自记忆。如果某件事你无法核对，就写「未核对」。
- 永远不要编造搜索量。
- 不要加评价星级，不要加 FAQ 标记，不要加 HowTo 标记。
- 未经先给我看文件，不得从本文安装任何 skill 或仓库。
```

## 资料与致谢

卖工具并不等于一个人是错的，过时的一句话也不等于一个仓库没有用。这本手册里的每一个想法，都来自下面这些人——他们做了研究，并无偿分享出来。谢谢。

- @borjafat：决策页、信息增益、内链、把数据统计页当作吸引外链的磁石。
- @VengeonsP：助手会跑的那些隐藏搜索、免费工具栈、「你是怎么知道我们的」这一核对方法。
- @NicholasDulait：用搜索结果测试关键词、智能体的权限分级与 hook。
- @denohawari：Bing、robots.txt 和原始 HTML 检查清单。
- @alexteillet：引用数据集，以及始终给出样本量的规则。
- @ChadSE0：完整的技术审计提示词。
- @louisfoweraker：每周提示词追踪，以及应拒绝的事项清单。
- @samigrows：如何给外链潜在对象打分。
- @JulianGoldieSEO：新功能上线当天就要有的页面。
- @Affiseo_：长尾页面，以及用 Bing 获取 ChatGPT 流量。
- @eptwts：最早把 GEO 讲清楚的文章之一。
- @bloggersarvesh：20 条提示词的本地 SEO 工具包。

以及 GitHub 上的：RomeoSEO、AgriciDaniel、AminForou、every-app、nowork-studio、zubair-trabzada、TheCraigHewitt、Ryze-AI-Adgent、i365dev、aFarkas、garmeeh、goenning、yaojingang 和 marcobiedermann.
