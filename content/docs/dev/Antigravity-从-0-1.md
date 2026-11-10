---
title: 'Antigravity 从 0 ~ 1 完整保姆级教程'
date: '2026-11-10'
updated: '2026-11-10'
---

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/c79304c5fd3a390d.jpg)

这篇文章只想教会你所有Antigravity的技巧👇：安装、购买、配置、使用场景、remote agent 完整保姆级教程一网打尽

最近 Antigravity 的更新频率真的有点猛。从 10 月底到 11 月初这短短一周多，接连上了侧边栏内置浏览器、PDF 阅读器、长对话轮次跳转、插件市场的 Notion/Figma 官方插件，这两天连语音模式和云端运行的 Remote Agents 也开始灰度了

很多人装好 Antigravity 之后，还停留在拿它当个普通聊天框问问题，或者刚登上去碰到地区限制、额度莫名其妙烧光就直接卸载了，其实非常亏。我这段时间高频用下来，给 Antigravity 的定位很明确，它就是我手头最顺手的「干杂活的料」

它什么活都能干，核心看你怎么排兵布阵。像我平时在本地知识库写文章、找素材，再用 Notion MCP 同步，或者让子 Agent 跑页面检查、查跨文件 bug，这类调用工具极多、特别吃上下文的杂活，我全丢给 Antigravity 搭 Gemini 3.8 Flash 去跑，不仅速度快，算下来成本也低得离谱

现在连 Obsidian 也有了新玩法：Claudian 这个插件已经支持 agy，可以直接把本地 CLI 拉进笔记库里跑，这下写稿真不用来回切窗口了。这篇长文不整虚的，直接从最前面的网络登录避坑开始，一路讲到我日常怎么用它干活、怎么用 Notion MCP 和 Claudian、怎么选 /boost 和 /teamwork、怎么用手机远程切实例，以及怎么把额度花在刀刃上

## 一、上手前先避坑：入口选择、节点与便宜订阅

如果你刚准备装，或者之前卸了想重装，先把下面这三件事搞对，后面会省很多事

### 1️⃣ 选哪个入口？不用全装

Antigravity 现在有桌面端 App、终端 CLI 和主流 IDE 扩展，本地是一套 Google 账号凭证互通的
新手或平时看文档、跑多任务多，直接下桌面端 App 就行。最近几次大更新，比如侧边栏内置浏览器、PDF 阅读、Markdown 渲染预览、插件市场面板，都在 App 里体验最完整
桌面端下载地址

https://antigravity.google/download/

装完在终端输入 agy 就能跑了！

macOS / Linux：curl -fsSL https://antigravity.google/cli/install.sh | bash
Windows PowerShell：irm https://antigravity.google/cli/install.ps1 | iex

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/5ecf1ab4962b184e.jpg)

安装过程就不啰嗦了，装完打开 App 点 New Project，绑一个你本地真实的文件夹。一个项目还可以关联多个本地文件夹，适合几个 Git 仓库同时开发的场景

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/d4c421b76a38fb02.jpg)

### 打开 App 来收悉一下😁

第一次打开看到全英文界面不用慌，左边导航栏管项目（Projects）、定时任务（Automations）和插件规则（Customizations）；中间底部输入框敲 @ 引用文件、敲 / 调命令，左下角切模型并查看额度（View Usage 里的 Weekly limit 和 5h limit 就是你的周额度和 5 小时刷新池）

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/594f5637e37b8526.jpg)

真正容易踩坑的是这三个设置，动手前先看一眼：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/3c932725d5ea4355.jpg)

1. 选对工作目录与 Git Worktree：输入框上方点项目名就能切目录，涉及改文件时千万看清当前绑的是哪个文件夹。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/93706a912a942747.jpg)

如果项目名旁边显示 Git 分支（比如 master），点开会看到 Work in a New Worktree——强烈建议善用这个功能，它会拉一个独立的 Git 工作树让 Agent 折腾，主工作区保持干净，跑完检查没问题再合并不迟。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/166cd4e26d0b708d.jpg)

2. 新手先锁死 Request Review：输入框右下角是命令执行模式。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/24b1fc7205660aa6.jpg)

Request Review 是每条终端命令都要你点头；Turbo 则是无限制直接跑。刚上手先老老实实用 Request Review，看清它准备干嘛再放行。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/2bab709f07ff52b5.jpg)

3. 顺手把 Browser Subagent 开了：去左下角 Settings → General，除了能细调文件/终端/MCP 权限（Tool Permissions）和计划审阅策略（Plan Review Policy），拉到底部能看到 Browser Subagent。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/7694d42264d733fd.jpg)

装好 Chrome 后把这里的 JS 执行和网页操作权限放开，后面在对话框敲 /browser 就能直接调浏览器子 Agent 干活，我的建议是浏览器相关权限可以全开

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/4182ef7a54a4466e.jpg)

接着打开保持在底部面板，这样叉掉页面还能继续跑任务

英文看着还是累的话，GitHub 上也有第三方汉化项目 Antigravity-Hans，同时支持 App 和 IDE：

https://github.com/yuexps/Antigravity-Hans

### 2️⃣ IP 节点与地区限制怎么破？

很多人第一步就卡在“当前地区未开放”或者担心封号，说一下我的实测经验：

节点首选纯净的美国节点：我实测下来，美国的纯净节点是可以同时稳用 Antigravity 和 Gemini 的；其次是日区，其他地区的 IP 体验都不太好

坚决别碰“万人骑”机场节点：最近大家聊的封号问题，只要你用的不是那种几百人共用的脏 IP，其实没那么严重

可以去这里自查一下 ：

https://ipqs.1ms.dog/zh-cn/

卡地区限制怎么办：如果登录时弹“当前地区未开放”，直接切一下干净 IP，清空一下浏览器缓存，然后强制刷新页面、多重新登录几次就能过去了

### 3️⃣ 订阅怎么弄？

如果你现在想新上车或者续费，目前主流是走学生优惠延期或低价区订阅。推特上已经有小伙伴把具体步骤和踩坑点写得很细了，直接看下面这几篇教程就行，我就不重复造轮子了

学生优惠领过的账号 8.99 美元再领一年，有步骤有截图：

https://x.com/bitpanda88/status/2111976287665557558

学生认证新套餐 8.99 美元最长拿 4 年 Google AI Pro，还送 YouTube Premium：

https://x.com/xmglab/status/2112084948891148798

走土耳其区合规低价订阅，月付约 30 元可续 4 年：

https://x.com/mjjwiki/status/2115449169737548181

学生优惠延期全流程 9 张截图，带踩坑反例：

https://x.com/dajuxaibot/status/2112001003189112858

8.99 美元再领一年的领取步骤，没领过学生优惠的不适用：

https://x.com/duola_eth/status/2111981733059219629

## 二、我的主力用法：Obsidian + Notion，专治耗额度杂活

为什么我说 Antigravity 是“干杂活的料”？看我每天都在跑的这套写作流就知道了

我平时会写很多推文和长文，本地有一个 Obsidian 知识库用来存草稿和资料。我日常就是把 Antigravity 挂在这个本地库上，跟 Agent 一起找素材、理框架、改草稿，写完之后再把重要的文章同步到 Notion 数据库里

用过 Notion MCP 的兄弟应该都知道，这玩意儿其实是个额度黑洞——它同步一篇文章要连续调好几次工具，还会往上下文里塞一大堆 JSON 结构，如果拿按量计费的 API 或者额度金贵的模型去跑，看着都肉疼

所以这种活我全交给 Antigravity：

在 Antigravity 里配好 Notion MCP（10 月 29 号更新的 v2.28.2 还在插件市场里直接上了 Notion、Figma、Canva 的官方合作插件，接入更省事了！）

模型直接锁死 Gemini 3.8 Flash

让它自己在后台调工具、改属性、同步页面，吐字极快，额度还完全不心疼，这就是我说的「杂活」，这种就交给 antigravity ！

### Notion MCP 怎么连接？跟着做就行

这一步其实不复杂，不用自己手写一堆配置。先点左边的 Customizations，在 Marketplace 搜 Notion，找到 Notion 插件后点右边的 +，按提示开始连接

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/a272ff74fa32de82.jpg)

接下来浏览器会打开登录和授权页面，登录自己的 Notion，按页面提示选择并授权需要访问的内容。完成后页面会给你一段要复制的内容；我这次的界面显示的是授权码，点 Copy to Clipboard 复制，然后回到 Antigravity，把它粘贴到连接流程提示的输入框里完成授权

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f973cb8fa86aa82d.jpg)

连接后打开 Notion 插件详情里的 Accounts，看到 Notion 账户显示 CONNECTED，就说明账号已经连上了

想确认 Agent 能不能用，再让它列出你刚才授权的 Notion 页面，看看返回的结果对不对。连接成功只说明账户接上了，具体能读写哪些页面，还要看你在 Notion 里给了哪些访问权限

项目里的文件夹和自定义内容也可以在设置里看：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/1170002009a30bc9.jpg)

图里的 Folders 是当前项目关联的文件夹，Add Folder 可以继续添加；Customizations 下面能看到 Rules、Skills 和 MCP Tools 的 token 占用与明细。这里的 Rules 是给 Agent 的规则，Skills 是可复用的工作流程，MCP Tools 是通过 MCP 接进来的工具。图中也提示，超过预算时，大规则可能被替换成路径指针，大型自定义内容可能被自动排除，所以东西装多了也可以回来看看

再加上最近几个版本把 PDF 阅读器、Markdown 代码块预览和长对话轮次跳转都补齐了，现在直接在 App 里读长资料、整理本地笔记，顺手程度比刚出来那会儿高了不止一个档次

### 不想来回切窗口？用 Claudian 把 agy 拉进 Obsidian

最近 Obsidian 插件 Claudian 也支持 Antigravity CLI 了。你的笔记仓库直接就是 Agent 的工作目录，我在 Obsidian 里找素材、理框架、改当前文章，都不用先把这段任务搬到 Antigravity App 里再绑目录，写稿顺滑很多
这里要注意先装 CLI 再装插件。Claudian 读取的是本机的 agy CLI，不是你刚装好的桌面 App，所以只装 Obsidian 插件还不够

1️⃣ 先回到第一章装好并登录 agy CLI，在终端跑一次 agy，确保你的账号能正常用
2️⃣ 去 Obsidian 的设置里打开「第三方插件 → 社区插件 → 浏览」，搜 Claudian。认准作者 Yishen Tu，不要装成下面的 Claudian Plus 或 Oh My Claudian，它们是另外的插件。点安装，再启用

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/ac4b8dd2d69abba0.jpg)

3️⃣ 打开 Claudian 的设置，切到「提供商」，选择 Antigravity，把右边的开关打开。插件会自动检测本机 CLI，和可用模型列表

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/0f8bb2efae33f64c.jpg)

4️⃣ 从左侧图标或命令面板打开 Claudian，模型选 Gemini 3.8 Flash，思考档按需选，就可以对着当前笔记和整个库干活了。要它帮你找资料和列出待引用的笔记，就 @ 提到笔记或文件夹；要它改当前一段，先选中文字再下指令，非常方便！

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f03062aa0d15b7d8.jpg)

插件地址

https://github.com/YishenTu/claudian

（平时在 Obsidian 里写长文、烦透了来回切窗口的兄弟，装完基本就回不去了）

## 三、复杂活怎么派：为什么我狂用 /boost，劝退 /teamwork

当你真的拿它改项目、查难 bug 的时候，光在输入框里干聊是不够的，核心要学会敲 / 调工作流

很多人分不清 /boost 和 /teamwork，这俩我都深度跑过，直接给结论：日常遇到难活，闭眼用 `/boost` 就够了，别轻易开 `/teamwork` 烧额度

### 1️⃣ /boost：真正好用的多 Agent 协同

之前有人以为 /boost 只是让同一个 Agent 换几个角度说话，其实不是。它的底层是由一个统筹的 Orchestrator 把任务拆开，派给专门负责调查和实现的子 Agent，在隔离的 worktree 里跑完、交叉验证，最后才把结果汇总给你（我之前发过实测对比图）

遇到偶发 bug、或者跨好几个文件摸不清调用关系的时候，我最喜欢这样给它下指令：

/boost 调查 [具体问题或报错]
先阅读相关代码，梳理完整调用路径和可能原因
不要修改代码
给出支持结论的文件位置、还没排除的疑点和验证方式

先加一句“不要修改代码”，让多 Agent 把根因查明白，你看过觉得靠谱了再让它动手，基本不会出现几个 Agent 一起瞎改把仓库搞炸的情况

这里顺带分享一个底层冷知识：Antigravity 的 Subagent 跑完任务之后，默认是进入

idle（常驻待命）

状态，而不是直接销毁（killed）。这意味着你接着追问一个相关问题时，它可以带着刚才读代码的上下文继续干活，不用从零重读一遍仓库（详见我之前拆过的 Subagent 生命周期帖：

https://x.com/chasen_liao/status/2110928117019902267

）

### 2️⃣ /teamwork：为什么我实测后很少开了？

/teamwork 是一个比 /boost 周期更长的工作流，会拉起更多的 Subagent 组队干活

但问题在于：它收敛真的太慢了。我之前实测过，拿 Pro 账号 5 个小时的刷新额度去跑，居然跑不完一个任务——因为它在里面会起非常多的验证和对抗检测，来回扯皮消耗巨量 Token

如果你非要用 /teamwork（比如做超大规模的跨目录迁移），我的建议只有一条：模型必须切到 Gemini 3.8 Flash，而且要在提示词里明确加上 `keep it small`，强制它精简 Subagent 团队和验证流程。但话说回来，既然都要手动阉割它的团队规模了，那还有什么必要开 teamwork 呢？直接用 /boost 反而干净利落

## 四、前端验收与插件：/browser + 现代 Web 规范

写前端或者改页面的时候，最烦的就是代码看着没报错，打开浏览器一看按钮歪了、手机窄屏全乱了

这时候直接敲 /browser：

它会调起一个沙箱 Chrome 浏览器子 Agent，自己去打开本地端口、点按钮、切桌面/手机宽度，还能截图回来给你对比

尤其当你丢了一张参考图让它照着写、第一版做出来差点意思的时候，直接让 /browser 打开本地页面截图，指出哪块间距或配色不对，让它边看边改，配 Gemini 3.8 Flash 又快又准

而且 v2.28 之后 App 右侧还多了个侧边栏内置浏览器，平时边改代码边在侧边栏看实时效果，连窗口都不用切。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/cf52e21cd11ed558.jpg)

另外，如果觉得 AI 写出来的网页总是有一股几年前的老旧味，去左边 Customizations → Marketplace 插件市场里搜 Chrome Modern Web Guidance 装上（顺带一提，这里还能直接一键接入 Google Docs、Sheets、Drive 等全家桶）。这个插件会把现代 Web 的新规范塞进上下文，治 AI 写过时 CSS 非常管用。

## 五、出门在外怎么控制：Remote Control vs 云端 Remote Agents

除了坐在电脑前用，Antigravity 现在有两个很容易混、但极其好用的远程功能：

### 1️⃣ Remote Control（远程控制我自己的电脑/服务器）

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/c5a24175efddd81e.jpg)

这是我现在每天都在用的功能。只要我的电脑或服务器开着机、连着网，我人在外面用手机浏览器就能直接进 Remote Control 页面

https://antigravity.google/docs/remote-control/

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/301575f49ffcfd9e.jpg)

顶部可以直接下拉切换我已经连上的多个实例，下面就能看到对应的项目和正在跑的会话。在外面突然想到有个杂活要跑，或者想看一眼家里的 Agent 跑完没，掏出手机切一下实例就能接着发指令，体验非常丝滑。这个 UI 跟桌面端基本致，操作逻辑不用重新学，挺好的

### 2️⃣ Remote Agents（已经上线的云端运行）

现在 Remote Agents 已经在 Antigravity 上线了。它跟 Remote Control 不一样，任务直接跑在 Google 管理的云端环境，你把活派出去之后，哪怕关掉浏览器、把电脑合上休眠，它在云端照样继续跑，随时换个浏览器还能回来看进度。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/568aaf61185ebaee.jpg)

项目资源也不只是绑 GitHub。点项目名下的 New Remote Project，或者 Remote 里 Connect GitHub，能直接选自己的仓库；Create Project 里点 Add Resource，还能接 Google Drive，或者把自己现成的文件直接传上去，不是所有活都得围着代码仓库转

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/9ec455d83e4d9829.jpg)

## 六、模型、额度池与权限：怎么配才不踩坑？

最后把大家最关心的模型选型、省额度习惯和权限设置集中理一下：

### 1️⃣ 模型怎么选？Flash 主力，4 留着攻坚

经常有小伙伴在评论区问：日常到底开 Argon 还是 3.8 Flash？

我的配方很固定：90% 的时间锁死 Gemini 3.8 Flash

现在虽然有 Gemini 4 Argon，但 Gemini 4 的额度给得真的很低，偶尔拿它来跑难一点的任务

但像我们平时写推文、找素材、跑 Notion MCP、用 /browser 验页面，甚至开 /boost 跑多 Agent，Gemini 3.8 Flash 的速度和额度宽松度完胜（如果你用 Pi，也可以用我之前分享过的 pi-antigravity 插件 把 3.8 Flash 接进 Pi 里白嫖流式输出

https://x.com/chasen_liao/status/2095340963954901201?a=RpxJfRwRgkuP8IhTFrE&s=20

）

### 2️⃣ 额度池铁律：两池分开看，别拿 Opus 跑多 Agent

打开模型菜单里的 View Usage 看自己账号的实际额度。我的界面里分别显示了 Gemini Models、Claude and GPT models，以及单独列出的 Gemini 4 Argon 周额度；每组能看到哪些周期、什么时候重置，以账户页面为准

最容易把号跑空的操作，就是顶着 Claude Opus 去开 /teamwork 或 /boost。多个子 Agent 同时调 Opus，几分钟就能把你的 Claude 池直接抽干。记住一句话：多 Agent 协同和工具调用多的杂活，一律切回 Gemini 3.8 Flash

### 3️⃣ 权限档别乱开 Turbo

前面提过输入框右下角的 Turbo 模式会放开完整文件系统访问和不受限制的终端命令。日常嫌确认烦想提速之前，先去 Settings 里把工具权限和网络规则摸透。千万别把 Turbo 当成单纯的“加速档”，也别指望光靠提示词就能约束住高风险的删改操作。

https://antigravity.google/docs/permissions/

## 七、日常什么场景敲哪个命令？

1️⃣ 需求还没想清楚，怕它瞎改
先敲 /plan，再用 /grill-me 让它追问边界条件、列好修改计划，确认后再动手
2️⃣ 目标和验收标准都很明确
敲 /goal，写清交付物和要跑的测试，让它自己闭环跑完
3️⃣ 遇到难 bug，跨多文件摸不清链路
敲 /boost，加一句「先调查不要改代码」。开头的例子已经给了完整指令，比 /teamwork 收敛快得多
4️⃣ 前端写完要看效果、对比参考图
敲 /browser，配 Gemini 3.8 Flash，让它自己点页面、截窄屏图验收
5️⃣ 主任务正在跑，突然想顺嘴问个问题
敲 /btw 旁支提问，完全不会打断当前正在干活的主任务
6️⃣ 同一个错误纠正了它两三次
收工前敲 /learn，把刚才的教训沉淀成持久规则或 Skill
7️⃣ 每天或每周固定要跑的整理杂活
敲 /schedule，适合定时汇总目录变化或日常巡检
8️⃣ 终端里觉得思考太慢或太浅
CLI 下敲 /effort 调节思考档位，日常 Medium 起步，难题再切 High

https://antigravity.google/docs/getting-started/

https://antigravity.google/docs/changelog

https://antigravity.google/docs/boost/

https://antigravity.google/docs/remote-control/

https://antigravity.google/docs/remote-agents/
