---
title: '别再把 Google Antigravity 当编辑器了：保姆级实战手册（附全套命令与提示词）'
date: '2026-11-22'
---

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/67fc4669d048fd8d.jpg)

这篇只解决一个问题：把你脑子里“Antigravity = 免费送 Gemini 3 Pro 的编辑器”的旧印象洗掉，按最新版从安装汉化、模型省额度、/swarm 蜂群到视频反推和深度长文写作，一次全跑通。
很多人对 Google Antigravity（反重力）的印象，还停留在 2025 年 11 月。
那会儿谷歌发了一个基于 VS Code 的 AI 编辑器，免费送 Gemini 3 Pro，大家一窝蜂去薅羊毛。
一年过去，它早就不是当年那个东西了。
现在独立的桌面 Antigravity App 成了主力，编辑器退居为可选项之一。
模型全换成了 Gemini 4 家族，多 Agent 协作长出了 /swarm 和 /teamwork。界面还专门给写作和研究人群做了一套「知识工作」布局。
网上大量教程还在讲旧版的 Planning / Fast 模式和 Gemini 3 Pro。
照着旧教程做，菜单找不到，按钮对不上，额度烧得莫名其妙。
打开编辑器。开个聊天框。一问一答。
这不是现在的 Antigravity。现在的它，是一台独立的桌面 AI 指挥中心。
来看几组已经落地的数字：
官方基准测试（Terminal-Bench 4.1）：用 Orchestrator 编排模式跑任务，成功率接近单用旗舰模型 Carbon，但平均少用 24% 额度、快 19%。
谷歌内部：每月有超过 10 万人在用 Gemini 4 Argon，数万名非工程岗位员工（销售、财务、法务、产品、设计、市场）每周在用知识工作布局写文档和做分析。
社区实测：有博主用它一次逆向 7 条抖音和 X 爆款视频分镜；有作者用 Gemini 4 Argon 在 CLI 里写出 12 章、17.3 万字书稿再换模型审三轮。
把 Antigravity 当编辑器，你只用了它两成能力。
把它当一台带参谋部、工兵连和外部工具接口的 AI 指挥中心，写代码、拆视频、写长文才能真正串起来。
读完这篇你会知道：
现在的 6 种产品形态怎么选，以及安装、账号地区、权限和汉化怎么避坑
Gemini 4 四兄弟和 Orchestrator 怎么配，才能少花 24% 额度还更快
忘掉旧版模式后，该用哪几个斜杠命令实现从“手把手”到“合盖自动跑”
/boost、/swarm、/teamwork 怎么选，外加 4 段直接能改着用的蜂群提示词
怎么用 Gemini 原生看片能力反推爆款视频提示词，以及 3 条外部出片通道
怎么切到知识工作布局写深度长文，用“先建事实库 + 换模型审稿”压住幻觉和 AI 味
这套工具能做什么、绝对不能做什么，外加 8 个高频报错速查
下面正式开始。
## Part 1：先认清现状——装对入口、切对布局、避开首日 3 个坑

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/c879b6d61ca8513f.jpg)

很多人第一步就装错了。
以前只有编辑器可装；现在官方把同一套 Agent 底座拆成了 6 种入口，共用同一个账号和登录态。
看清再下，别一股脑全装：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/1e1ac40b70419a68.jpg)

版本号核对自官方更新日志与 Second Talent 11 月 17 日实测记录。App 顶栏自带 Open IDE 按钮，拿不准就先装 Antigravity App。
首日避坑 1：账号与地区。
需要年满 18 岁的个人 Google 账号且绑定受支持地区。公司或学校的 Google Workspace 账号不享受套餐和更高速率限制，管理员关掉权限后会直接卡在 Sorry, this account is ineligible to use Antigravity.。
社区实测（博主 Leaf）：遇到「所在国家/地区不可用」分两层——底层绑定地区靠代理改不掉，要去 Google 的[国家/地区关联更正表单](https://policies.google.com/country-association-form)如实申请（他提交后不到半天通过）；改好后某天再报错，多半是代理节点被识别成香港，换节点刷新即可。
首日避坑 2：系统门槛与 Windows 拦截。
App 要求 Windows 10 64 位+ / macOS 13+ / Linux glibc 2.28+；Windows 版安装包约 189 MB，按用户安装，一般不用管理员权限。若额外装 IDE（安装包 199.6 MB、解压约 922 MB），首次启动还会二次下载 Agent 后端，进度条走完前别关窗口；Win11 开启 Smart App Control 时可能拦截 sqlite3.node 和 iselevated.node，先验签再看是否影响使用，不要一上来关掉整机安全防护。
首日避坑 3：布局与搬家。
v2.30.0+ 首次登录会让你选工作类型：选 Knowledge Work / Science / Design / Other 进入知识工作布局（隐藏 diff 和终端，进度折叠成大白话，但底层能力 100% 相同）；选 Software Engineering 进入软件工程布局，还能一键把 Claude Code、Codex、Cursor、Gemini CLI 的 MCP、Skills 和规则搬过来。随时可在 Settings > General > Interface Layout 秒切。
装机验签、装 CLI、装社区汉化的命令直接放这里，按需复制：
```
# 1) Windows 下载 App 后建议先在 PowerShell 验签（确认 Status: Valid 且 CN=Google LLC）
Get-AuthenticodeSignature .\Antigravity-x64.exe | Format-List Status, SignerCertificate

# 2) 安装 CLI（agy）—— macOS / Linux
curl -fsSL https://antigravity.google/cli/install.sh | bash

#    Windows PowerShell
irm https://antigravity.google/cli/install.ps1 | iex

# 3) 社区动态汉化（仅当你确实需要中文界面；非官方工具，更新可能滞后于 App）
#    工具 A：yuexps/Antigravity-Hans（零改动动态注入，可保留英文模型/权限名）
antigravity-hans --app        # 动态汉化 App
antigravity-hans --ide        # 动态汉化 IDE
antigravity-hans --stop       # 随时停止还原
#    工具 B：qqxpee/antigravity2-cn（注入 app.asar，标注适配 App v2.33.0+，覆盖菜单与 Swarm 面板）
```

顺手说一句汉化的实话：IDE 基于 VS Code，直接装官方 Chinese (Simplified) Language Pack 最稳。
App 目前没在官方文档里看到内置简体中文，上面两款都是第三方社区工具。
因为 App 几乎每周发版，汉化一旦滞后或出界面异常，先还原回英文原版再排查问题。
进门最后一件事：先把消息框里的 4 档权限预设看懂（v2.30.0+ 个人账号切换只对当前对话生效）：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/8b5edaa1ac5d51eb.jpg)

批准文件或目录权限时，可以直接在弹窗里把单个文件路径改宽成整个目录，这一轮就不会反复弹窗打断你。
装对 App、选对布局、守住 Default 权限，你才算真正进了指挥中心的大门。
门进了，下一个最容易交学费的地方就是模型和额度——很多人刚充完会员，两天就把一周额度烧穿了。
## Part 2：模型与思考档位——怎么选才能省 24% 额度还快 19%

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/3fa6105198c6c95b.jpg)

拿旗舰模型干所有杂活，是新手烧光额度最快的方式。
以前大家只认“最强模型”；现在 Antigravity 把 Gemini 4 拆成了四个定位分明的兄弟，外加一个杀手级开关——Orchestrator。
先看清账号套餐和模型阵容：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/72897bee90fe263c.jpg)

注：Pro 档的 Argon / Neon / Orchestrator 需付费或符合条件设备试用，Hydrogen 与 Claude 5.5 仅限非试用付费 Pro；企业版 Orchestrator 固定 Carbon(High) + Hydrogen(High)。免费用户旧模型下线后（文档写 11/30，定价页脚注写 11/18）主力仅剩 Gemini 3.8 Flash。
思考档位怎么调：
多数 Gemini 模型有 Low / Medium（默认） / High 三档；Neon 和 Hydrogen 多一档 Extra（CLI 写作 xhigh）。档位越高越耗额度也越慢。注意一个细节：Agent 正在干活时切模型，本轮仍按旧模型跑完，下一轮才生效。
为什么 Orchestrator 是日常首选：
它不是“根据第一句话猜难度”的傻瓜路由器，而是在任务中途来回交接。每条消息先由规划模型（默认 Neon，Ultra 可换 Carbon）只读探索、写计划；再交给执行模型（默认 Hydrogen）改文件、跑测试。一旦执行模型卡壳（同一验证连续失败两次、接口行为不符、遇到未覆盖的设计选择），它会自动把接力棒交回规划模型修计划。官方数据：Terminal-Bench 4.1 上成功率接近单用 Carbon，少耗 24% 额度、快 19%。
直接按下面这张图选，基本不踩坑：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/a6080f3b12dd6d74.jpg)

CLI 里指定 Orchestrator 或看账号可用模型，直接敲这两行：
```
agy models                                              # 列出当前账号所有可用模型 ID
agy --model "Orchestrator (Neon)"                       # 用 Neon 规划 + Hydrogen 执行
agy --model gemini-4-neon-xhigh                         # 单独上 Neon Extra 档攻硬骨头
```

额度怎么算、别乱装插件：
Pro / Ultra 按每 5 小时刷新 + 每周上限计费，免费版按周刷新；额度看 Agent 实际工作量而不是对话条数，目前不支持 BYOK（自带 API Key）提限。App 的 Settings 和 CLI 的 /usage、/credits 都能直接查余额。社区有 Antigravity Cockpit 这类状态栏监控扩展，但有知乎用户反馈装监控插件后触发过风控（属个例）——尤其是带多账号切换、自动唤醒、自动预热功能的插件，可能碰服务条款，自己掂量清楚再用。
日常把 Orchestrator 当默认，硬骨头再单开 High/Extra，杂活丢给 Hydrogen——光这一条，每周就能多干四分之一的活。
模型和额度管住了，下一步该把指挥中心的“快捷键和命令面板”真正用起来。
## Part 3：斜杠指令与五档放手——忘掉旧模式，从一问一答到合盖自动跑

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/5e7d6f59aaaa4f6f.jpg)

别再到处找旧教程里的 Planning 模式和 Fast 模式了，2026 年的 Antigravity 早就改用模型选择 + 斜杠命令来控制节奏。
在输入框敲一个 /，所有工作模式都在里面。你不需要背几十个命令，先吃透这 4 组高频命令就够打全场：
```
── 先商量再动手 ──
  /plan                 先读仓库、澄清需求、出可审阅计划再改代码
  /grill-me             一次只问你一个问题并给推荐答案，可叠加：/plan /grill-me <任务>

── 放手跑与自动化 ──
  /goal <目标>          不停下来求确认，一直干到验收标准通过为止
  /schedule "<cron>"    在当前对话里定时唤醒 Agent（一次性或 cron 周期）
  /automation           建周期性后台任务，在 Automations 页统一管理
  /browser              把 UI 检查、截图、网页操作交给浏览器子 Agent

── 防打断与控上下文 ──
  /btw                  在侧边栏开只读旁支标签页追问，不污染主对话（答完可一键插回主对话）
                        终端选中输出按 Cmd+E（Win 为 Ctrl+E）也能直接发起 /btw
  /compact <保留要求>    把长对话压成检查点，保住关键结论腾出上下文

── 越用越顺手 ──
  /learn                把本次会话里你纠正过的偏好，提案成永久规则或 Skill（批准才写入）
  /plugin               管理官方 Marketplace 插件（Cloudflare/Tavily/SonarQube/MCP Apps 等）
  /agy-customizations   不会写 Rules/Skills/MCP 时直接叫它按官方规范帮你配
```

把它们按“你放手的程度”排开，正好是一条 5 档进阶梯子：
第 1 档 · 直接对话：小任务直接发，边看边调。
第 2 档 · 先规划再干：上 /plan /grill-me，把模糊需求逼清楚，在计划里逐条批注后再放行。
第 3 档 · 目标驱动：上 /goal，把“怎样算做完”（跑通哪条测试、产出什么文件）写死，让它闭环跑完。
第 4 档 · 定时常驻：上 /schedule 或 /automation，把周报、晨检、巡检交给后台。
第 5 档 · 离电脑也跑：付费会员开 Remote Agents（云端绑 GitHub 或 Google Drive，合上电脑继续跑，手机打开 https://antigravity.google.com/remote 随时看进度），或用 v2.33.0+ 的 SSH 远程主机直接连 Linux 服务器；空消息框还能开语音模式（基于 Gemini Live，0.75x～2x 语速）动口不动手。
四条最常用的实战命令，直接拿去套：
```
# 1) 复杂需求开工前，先让它把坑问透再写计划
/plan /grill-me 给 [模块名] 增加 [功能]，约束是 [边界条件]。先把模糊点问清楚，再出实现计划。

# 2) 工作日早 9 点自动巡检分支和待审 PR（官方示例）
/schedule "0 9 * * 1-5" Run git fetch, prune stale local branches, and summarize pending PR reviews.

# 3) 对话变长变笨前，带要求压缩上下文
/compact 保留架构结论和已修改文件清单，丢弃前期试错日志，接下来补集成测试。

# 4) 刚纠正过一个习惯，趁热固化成永久规则
/learn 把刚才“所有数据库迁移前必须先备份、禁止直接 drop”的要求沉淀为项目规则。
```

CLI 无头模式避坑：
用 agy -p "提示词" 跑自动化脚本时，没人点权限确认，需要权限的工具会被直接拒绝并吐出 no output produced（且提示词必须跟在 -p 后，不能写裸参数）。正确做法是在 ~/.gemini/antigravity-cli/settings.json 的 permissions.allow 里放行具体命令（如 command(git status)）；--dangerously-skip-permissions 只留给用完就删的沙箱目录。
一个不会 /learn 和 /compact 的 Agent，每天都在从零认识你；用熟这几条命令，它才开始长记性。
单兵已经很顺手了。但如果一个任务大到单兵要干两小时，或者难到单模型自己钻牛角尖，就该拉一支小队进场了。
## Part 4：/swarm 蜂群与 /teamwork——难用 boost，大用 swarm，长用 teamwork

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/28066bafd255cbdf.jpg)

多 Agent 不是越热闹越好，选错模式只会白烧额度。
Antigravity 把多 Agent 分成了四个工种，外加一个脚本编排。
记住这一句选型口诀就行：难用 /boost，大用 /swarm，长用 /teamwork，固定重复流程用 /run-workflow。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/156cc1b43d0f342c.jpg)

重点讲全套餐都能用的 /swarm（蜂群）。v2.31.0 刚上线头几天就有数万个 swarm 被跑起来，它的设计非常像一个真实工程小组：
协调者（coordinator）：你当前对话变身总指挥，不写业务代码，只拆活、派活、向你汇报——所以 worker 干活时它随时能回你。
具名 worker + 独立 worktree：每个 worker 只管自己那块文件，上下文干净，可在各自独立 git worktree 里改代码不撞车；没活干时休眠，不消耗 token。
独立把关的 @verifier + 沉默监工 @monitor：通常每 2～4 个 worker 配一个 @verifier 审 diff、跑测试、打回返工；所有交流公开留在共享留言板（Board）上，侧边栏切 Board / Members / Graph（CLI 按 Alt+S 或 /swarm board）能回放谁 @ 了谁。
最值钱的一个隐藏技巧：在提示词里明确要求 @verifier 使用和 worker 不同的模型。
同一个模型审自己写的东西，盲区基本重叠。换一个模型来挑刺，抓 bug 和查幻觉的准确率会明显高一截（写代码和写长文都通用）。
这 4 段官方风格的 /swarm 提示词，把文件名换成你的就能跑：
```
# 1) 多文件并行改造 + 补测试
/swarm 给 src/routes/users.ts、src/routes/orders.ts、src/routes/products.ts 三个 API handler 加输入校验。每个 handler 一个 worker，在各自旁边补测试，全部完成后让 verifier 运行 npm test。

# 2) 跨模型把关（防同模型盲区）
/swarm 给 pkg/httpclient 的 HTTP 客户端和 pkg/webhooks 的 webhook 发送器加指数退避重试。让 verifier 使用和 worker 不同的模型，检查竞态条件并运行 go test -race ./...

# 3) 多路只读排查性能瓶颈
/swarm 查清我们的 CLI 为什么要 4 秒才能启动。安排三个只读 worker 分别调查模块导入、配置加载和插件发现，最后在留言板上汇总成一份按优先级排序的修复清单。

# 4) 批量修红测，且禁删断言
/swarm 在整个仓库跑 pytest，按包对失败测试分组，每个出问题的包分配一个 worker 修复，不许删断言，最后让 verifier 重跑全量测试。
```

开蜂群前先看一眼额度警告：
官方博客说得很直白：哪怕有零 token 空闲等待，并行多 Agent 烧额度的速度依然远快于普通对话。先拿 2～3 个文件的小任务测一次掉血速度，心里有数再开大群；而且某个 worker 额度用完暂停后，哪怕 5 小时额度刷新了也不会自动重启，必须给它发消息、在留言板发帖或给它切模型才会继续。活干完记得让协调者移除闲置 worker。
写清楚“做成什么”和“怎么验收”，把拆活交给协调者，把挑刺交给不同模型的 verifier——这才是蜂群该有的用法。
代码和工程讲完了，但 2026 年的 Antigravity 最让人惊喜的，其实是它跳出代码圈的两个高频副业场景：视频反推和深度长文。
## Part 5：视频反推工作流——让 Gemini 原生看片，拆出能复刻的分镜提示词

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/43c51048236bfea9.jpg)

很多创作者拿 GPT 或 Claude 拆爆款视频，总觉得写出来的提示词“神似形不似”。
社区博主的观察一针见血（以下为社区实测与观察，非官方技术文档）：抽帧看图会丢掉动作衔接、推拉速度和节奏卡点。
而 Gemini 4 能原生看视频，直接读出「0–2 秒近景从左往右极速横移跟拍」「第 8 秒火焰横斩、白衣后空翻躲开」这种带时间轴和机位方向的硬细节。
再加上 v2.33.0 侧边栏支持直接播放最大 200 MB 音视频，下载、看片、写文件、调外部 CLI 可以在一个对话里串成一条线。
先泼一盆必须泼的冷水：截至 2026 年 11 月，Antigravity 不能直接生成视频。
生图靠内置 Nano Banana 2，但没有内置视频生成，也接不进谷歌自家视频模型。它的位置是大脑 + 调度台：负责看片反推、写提示词、调外部工具出片、抽帧验收。
结合博主 Leaf（逆向 7 条抖音/X 爆款视频）与黑粉科技（11 月 18 日全自动出片闭环）的社区实测，整条流水线有 5 条铁律：
铁律 1：先定目标模型，别套死模板。 纪实风反推的是“随手拍+现场光+去 AI 味”，二次元打斗反推的是逐秒分镜加作画术语，一套万能模板会把风格全磨平。
铁律 2：单段不超过 15 秒，写动作不写形容词。 Leaf 实测直接生 25 秒，模型会吞掉一半镜头再把剩下的拉成慢动作；别写“打得很激烈”，写成时间 + 机位 + 动作方向 + 碰撞接触，音效单独写清并注明“无背景音乐、无台词”。
铁律 3：追问“原文提示词”必须交证据文件。 Leaf 让 Agent 查原作者有没有公开提示词，它先报“3 条拿到了 100% 原文”，一要本地证据截图，实际只有 1 条。眼见为实，别轻信口头汇报。
铁律 4：锁画风先垫图，多人换角按服装认人。 纯文字复刻二次元容易退化成廉价 TV 动画，先用生图出一张设定图垫进去就稳得多；多人同框写“穿黑袖白衬衫那位换成角色 A”，别写“左边第一个”，交叉走位才不会串脸。
铁律 5：先出 360p 小样 + 6 帧对照验收。 黑粉科技实测 Google Flow 一条 15 秒视频 360p 扣 20 点、720p 扣 60 点；先出低清让 Agent 从原片和成片各抽 6 帧拼图对照，动作构图过关再花大钱渲染高清；超过 30 秒用 ffmpeg 抽前段尾帧做后段首帧续接。
两段直接能发给 Antigravity 的反推提示词（单条版 + 批量版）：
```
# 单条视频反推提示词
请下载并完整观看这条视频：[视频链接或本地路径]
我要把它拿到 [目标视频模型，例如 Seedance 2.5] 里复刻。请按以下要求输出：
1. 先逐段拆解：时间段、景别、机位与运镜方向、主体动作及方向、接触或碰撞、光线与色调、环境音效；
2. 再写一版可以直接粘贴的生成提示词。单段不超过 15 秒，超过的按镜头切成多段；
3. 动作一律用「时间 + 机位 + 动作方向 + 接触」描述，不用「很激烈」「很唯美」这类形容词；
4. 音效写清楚，注明「无背景音乐、无台词」；
5. 不要套用固定模板，根据这条视频本身的风格决定提示词的写法；
6. 如果你声称找到了原作者公开的提示词，必须把证据截图或网页保存到本地，并告诉我文件路径。
所有产出保存到 ./reverse/[视频名]/ 目录下。
```

```
# 批量反推总清单提示词
./refs/ 目录下有 [N] 条参考视频。请逐条按上面的方法反推提示词，
然后写一份总任务清单 tasks.md，每条写明：参考视频路径、对应提示词文件、目标模型、成片保存路径。
每次发起任何会产生扣费的外部生成请求前，必须先估算费用并等我确认。
完成后先给我看清单，我确认后再继续。
```

黑粉科技实测跑通的 3 条外部出片通道对比（社区实测数据，具体价格和额度以官方页面为准）：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/67554c068236094c.jpg)

合规与断流提醒： 反推学的是镜头语言，直接商用复刻他人作品或真人换脸有版权和肖像权风险，务必先确认授权。另外社区观察到又下载又生成的长任务大约跑 1 小时容易报 The stream was interrupted（疑似登录 token 过期），进度都在本地文件里，断了直接让它接着跑就行。
让 Gemini 看懂镜头，让外部模型去出片，用 360p 小样和 6 帧对照把废片拦在花钱之前。
视频之外，另一个被严重低估的非代码战场，是写深度长文和整本书。
## Part 6：深度长文与书稿工作流——切到知识工作布局，搭一条“去 AI 味”流水线

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/21250b35a2cc46e3.jpg)

拿网页聊天框写一万字以上长文，基本都会越写越散、前后吃设定。
谷歌内部每周有数万名非工程员工在用 Antigravity 写文档和做研究。
原因就四个：素材全在本地文件夹里、文风规则持久化生效、多 Agent 写审分离、改动可以逐条批注（不用二选一全部接受或拒绝）。
动手前先做两步准备：
准备 1：切到知识工作布局。 Settings > General > Interface Layout 选 Knowledge Work，隐藏代码 diff 和终端，专注文档、产物和链接，底层 Agent 能力一分不减。
准备 2：选对写作模型，并且提前防住它的“过度自信”。
社区实测（AI 编程实验室 · 鲁工）：他把写作任务全切到 Gemini 4 Argon 压测一周，在 CLI 里先整理 2 万字史料汇编，再写出 12 章、17.3 万字《姜维传》书稿，评价它在长篇文字驾驭上很强（免费用户可选 Gemini 3.8 Flash）。
但他同时爆出一个致命坑：Argon 极其自信，一旦超出输入材料范围，它不会说“不知道”，而是用笃定的学术口吻编出像模像样的假出处——一审时审稿模型就抓出它把裴松之注错标成了《晋书》。（注：文中提到的 Argon 输出上限数字未经官方确认；官方文档明确标注的是 Neon 最高 512K 上下文。）
所以，靠谱的深度长文流水线绝对不能一上来就让模型直接写正文。先把项目目录搭成这样：
```
我的长文项目/
├── 00-brief.md          # 选题、读者、目标字数、核心观点
├── 01-sources/          # 原始资料：PDF、网页存档、访谈记录
├── 02-notes/            # 事实库：带精确出处的资料汇编（facts.md）
├── 03-outline.md        # 大纲：每章要点、调用的资料、预计字数
├── 04-chapters/         # 逐章正文：ch01.md、ch02.md……
├── 05-reviews/          # 换模型审稿意见（不直接改正文）
└── style-guide.md       # 文风要求 + 你自己满意的范文片段 + 禁用表达
```

把这 4 段流水线提示词按顺序喂给它，事实可溯源、AI 味也能压下去一大截：
```
# ① 用 /plan /grill-me 定选题和大纲
/plan /grill-me 我要写一篇 [字数] 的深度文章，主题是 [主题]，读者是 [读者画像]。
资料在 ./01-sources/。请一次只问我一个问题，把立意、结构和取舍问清楚，
然后在 03-outline.md 里写出大纲：每章标题、要回答的问题、要用到的资料、预计字数。

# ② 先建带出处的事实库（先汇编，再动笔）
请通读 ./01-sources/ 里的全部材料，整理成 02-notes/facts.md。
每条事实后面标注出处（文件名 + 页码或段落）。材料里没有的内容不要补充，
材料之间有矛盾的地方单独列出来。

# ③ 逐章写正文（锁死事实来源，缺料强制占位）
按 03-outline.md 写第 [N] 章，存到 04-chapters/ch0[N].md。要求：
- 遵守 style-guide.md，并模仿里面附带的范文节奏；
- 所有事实只能来自 02-notes/facts.md，引用时保留出处标记；
- 资料不够支撑的地方，用【待补：……】标出来，绝对不要自己编；
- 写完后在文末列出本章用到的出处清单。

# ④ 用 /swarm 换模型审稿（只挑错，不改原文）
/swarm 审阅 04-chapters/ 下的全部章节。每章分配一个只读 worker，
逐条核对引用是否能在 02-notes/facts.md 和 01-sources/ 中找到原文，
并检查是否出现 style-guide.md 里禁止的 AI 腔表达。
verifier 使用和 worker 不同的模型复核。所有问题汇总到 05-reviews/round1.md，不要直接改正文。
```

压住 AI 味的 4 个实操细节（参考鲁工实测）：
1. AI 写长文最爱复发的四个毛病：高频单句甩“不是 A 而是 B”、满篇破折号插播解释、硬凑工整三四个小标题、结尾莫名拔高升华。
2. 只写二十条禁用规则还不够，一定要在 style-guide.md 里贴一段你自己满意的范文，让它照着范文的语感写。
3. 改稿时每揪出一个毛病，顺手敲 /learn 沉淀成永久规则；长对话记得带要求 /compact。
4. 论文、书稿和公开发表的深度文，审稿模型过完之后，人工至少核一轮出处并通改一遍。
先建事实库锁死底线，再分章写作稳住质量，最后换模型只查出处和文风——这三步把长文从“碰运气抽卡”变成了可复现的工程。
## 高频踩坑速查

把最常遇到的 8 个报错压缩成一张对照图，出问题直接照着排：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/bb8049072165b69b.jpg)

## 诚实契约：能做什么，不能做什么

这一段建议截图存好。工具吹得再神，边界必须讲在明面上。
现在的 Google Antigravity（v2.34.0）能做到：
用同一套底座打通桌面 App、独立 IDE、CLI（agy）、主流编辑器扩展和云端 Remote Agents
用 Orchestrator 把规划和执行拆分给不同模型，在保证接近旗舰质量的同时省额度、提速度
在本地项目里持久沉淀 Rules、Skills、MCP 和 /learn 规则，跨对话越用越顺手
用 /swarm 和 /teamwork 在独立 worktree 和共享留言板上跑多 Agent 并行协作与跨模型复核
凭借 Gemini 原生视频理解能力拆解爆款分镜、调度外部工具完成出片和 6 帧对照验收
切到知识工作布局，用本地文件夹 + 事实库 + 换模型审稿跑通万字长文与书稿生产
它现在明确不能做到（或者有硬坑）：
不能直接生成视频：内置生图是 Nano Banana 2，但没有内置视频生成，也接不进谷歌自家视频模型，必须接外部 API / Flow / 视频 CLI
不能靠免费账号白嫖 Gemini 4：免费用户无权用 Gemini 4 家族、Orchestrator 和 Claude 5.5，且旧模型（Claude 4.6 / GPT-OSS-120b）下线后只剩 Gemini 3.8 Flash
不能让 Workspace 账号享受个人套餐权益：学校/公司账号不支持更高额度，也不支持知识工作布局与 Auto 权限
不能无限免费开蜂群：多 Agent 烧额度远快于单对话，worker 额度耗尽暂停后刷新也不会自动续跑
不能自带 API Key（BYOK）提速或提限：Pro / Ultra 超额只能等刷新或买 AI credits
不能盲信模型的事实与出处：社区实测 Argon 超出资料范围会自信编造假出处，视频反推追问原文也可能虚报数量——必须留证据文件、换模型复核并人工把关
不能指望官方一键简体中文 App 或长任务永不断流：App 汉化目前靠滞后的第三方社区工具；1 小时以上的超长任务可能因 token 过期中断，需要续跑
把局限写清楚，前面那些能力才站得住。
## 写在最后

回过头看，一年前大家都在盯着“免费的 AI 编辑器”。
可真正拉开效率差距的，从来不是你多装了一个编辑器，而是你有没有把零散的聊天窗口，升级成一台有编排、有规则、有独立审稿人、还能定时和离机运转的 AI 指挥中心。
一个底座，六种入口。
一个总指挥，一群按文件分工的工兵。
大模型做规划和挑刺，小模型跑脏活累活。
本地文件存记忆，/learn 把每一次纠错变成永久资产。
别等把所有文档背完再动手。
今天先装好 Antigravity App，挑一个手头真实的任务，按 Default 权限跑一遍，亲自感受一次 Orchestrator 和 /swarm 的区别。
所以，你现在还在把 Antigravity 当普通 AI 编辑器一问一答，还是已经搭起自己的 Orchestrator + 蜂群工作流了？
