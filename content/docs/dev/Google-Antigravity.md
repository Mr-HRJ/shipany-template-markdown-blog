---
title: 'Google Antigravity 最全使用攻略：从订阅、反代、插件、模型，到白嫖 40 美元 API'
date: '2026-11-17'
---

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/beb3c51a037793b6.jpg)

这篇文章只解决一个问题：怎么每个月花不到 300 块钱（美区原价不到四折），稳稳拿下 Google Antigravity 的 Gemini 4 与满血 Claude 5.5 双独立额度池，并把注册、改区、订阅、装插件和防封路上的暗坑一次填平。

很多人以为用上 Antigravity 就是充个会员、下个安装包的事，真自己动手跑一遍就会发现，装客户端反而是最简单的一步。电脑注册 Gmail 强制弹二维码让你给 96831/244444 发国际短信死循环、中国区老号登进去直接弹 ineligible 拒之门外、土区 Google AI Ultra 5x不知道怎么订阅、好不容易登进客户端又卡在 Eligibility check failed 二次验证，甚至付完钱账号还锁在 Starter Quota 免费档、开着代理照样无限转圈，随手切个节点或挂个反代就直接吃 403 封禁。

上面这些坑我这阵子全实打实踩了一遍，也把每个卡点亲测能跑通的解法记了下来，你在折腾 Antigravity 时会碰到的绝大部分问题，基本都能在这篇里直接翻到答案，改区申请话术也放在文里了，复制就能直接用。

## 目录

- 为什么 Google AI Ultra 5x 爆火
- 校验逻辑与账号准备：新号注册·转区·节点自检
- 低价订阅实操：SEAGM 买土区苹果礼品卡
- 客户端安装与三款必装插件
- 模型选择：Orchestrator 与双额度池分工
- 反代与防封指南：Magpie 三种接入方案
- 手机远控访问：防休眠保活·扫码监工
- 每月 40 美元赠金：AI Studio 绑定与领取
- 疑难杂症：二次验证·锁额度·TUN 模式

## 01｜为什么 Google AI Ultra 5x爆火

开搞之前先算一笔明白账。很多朋友一听 Google AI Ultra 动辄百来美元一个月就劝退，其实走土耳其区苹果 App Store 内购通道，价格直接打到美区原价四折以内。

先看四个常见档位的对比：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/a74aab18d8d57bd0.jpg)

每月两百八十多块钱(以实际显示价格为准)的Google AI Ultra 5x，到底能拿回什么？核心回报实打实落在四件事上：

- 双独立额度池（最值钱的回本点）：一个订阅同时解锁谷歌自家的 Gemini 4 Carbon / Argon 系列和 满血 Claude 5.5 Sonnet / Opus，而且后台把 Gemini 和 Claude 的额度独立计算。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/1f98b45b256ef6a4.jpg)

- 20 TB 云空间与完整个人版 YouTube Premium：附带 Gmail、Drive、Photos 共用的 20 TB Google One 空间，以及去广告、后台播放、离线下载全齐的完整个人版 YouTube Premium（区别于阉割的 Lite 版）。
- 6 人 Google 家庭组共享：主号可以把最多 5 位家庭成员（共 6 个账号）拉进家庭组共享 20 TB 云盘，注意所有家庭成员共享你的AI Token额度池。
- Google Flow: 生成视频 10000 积分，每月 720p能生成一小时
- Google Flow Music: 生成音乐 30000 积分，每月可以生成 6000 首歌
- Google Colab 1000 计算单元，能用 96G显存的云机器 110 小时
- 每月可以领 $40 的Gemini API调用额度: 可以理解成codex pro订阅每月送的API额度，可以在第三方Agent，像Cursor、DSH里使用apikey调用Gemini API

## 02｜Antigravity 校验逻辑与账号准备

账号和网络没对齐之前千万别急着充钱。很多人明明挂了海外代理，拿手头的 Gmail 登录 Antigravity 还是照样弹出一句冷冰冰的拦截提示：Unable to Access Antigravity: Sorry, this account is ineligible to use Antigravity. Please sign in with a different Google account.（或提示当前所在地区不可用）。

实际上 Google Antigravity 在后台同时卡着三道完全不同的地区门槛，表格参考自@starflowai：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/33b3e4b67c35a2dd.jpg)

把上面这张表看懂，所有莫名其妙的登录报错就全通透了：**想正常用上 Antigravity，你的「账号所在地」和「网络节点」必须同时落在「提供服务地」之内。**

哪怕你节点挂在美国，只要账号所在地是中国，照样无法使用Antigravity；反过来，哪怕账号已经是美区户籍，只要代理软件切到了延迟最低的香港节点，谷歌一查香港不在开放大名单内，同样当场拦截。下面按「新号注册 → 查改账号所在地 → 核验网络节点」三步把这三道关依次打通。

### 2.1 Gamil新号注册

低价区订阅建议单独准备一个干净的 Gmail，别拿平时绑满核心资产的主力老号去折腾。现在电脑端网页直接注册新 Gmail，经常强制弹出二维码让你用相机扫，扫完逼着你给 96831 或 244444 发国际验证短信，国内卡发不出去直接卡成死循环。

手里有安卓手机的朋友扫码有概率直接跳过发短信；如果没有安卓机，用任何手机上的 Gmail 客户端走下面三步，都能直接切回正常接码注册：

1. 先把手机代理切到干净的美国节点，打开手机端 Gmail 客户端，点右上角自己的头像，选「添加其他账号」。
2. 选择「Google」，在登录框底部点「使用其他账号」，接着点「创建账号」（选个人用途）。
3. 按正常流程填好姓名、生日和邮箱名往下走，到手机号验证这一步就会自动切回填写手机号接收短信验证码（接码），填完验证码就能顺利建好新账号。

注意尽量用外区esim接码，这样不会被送回国区。

参考推文：https://x.com/xueyu1125/status/2119291329943580695

### 2.2 Gmail账号转区

在浏览器里登录你要用的 Gmail，直接打开官方 [关联国家修改申请表](https://policies.google.com/country-association-form)（也可以同步打开 [Google 服务条款页](https://policies.google.com/terms) 核对「国家/地区版本」），页面上会直接显示你账号当前关联的国家或地区。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/2cf82b10fc2fb440.jpg)

如果已经显示美国、日本、新加坡等官方开放大名单内的国家，可以跳过这一步；如果显示 「中国」 或 「香港」，就需要把这枚“户籍章”改到开放地区。

先把电脑代理锁死在稳定干净的目标国家节点（推荐美国 IP），就在同一个 [关联国家修改申请表](https://policies.google.com/country-association-form) 页面里：第一个下拉框选择你要转去的目标国家（如美国），下面「为什么您认为更新后的账号关联国家/地区更准确？」，选择「我的工作地/学习地和居住地分属不同的地区」。

如果未通过则勾选最后一项「以上都不是」，然后把下面这段话复制进补充说明框提交即可：

```text
因为我是留学生，使用Google所在地和我居住所在地不同，目前我会长期在美国读书，请协助更新账号关联国家。
```

图片是我小号中国改日本的邮件：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/5a2043bb3535001c.jpg)

### 2.3 出口节点自检

Antigravity 在登录及日常使用过程中，需要全程开启海外节点（非中国大陆节点即可，例如新加坡、美区等）。

国内很多VPN默认开启「自动选择最低延迟」，会自动切到物理距离最近的香港（`HK`）或澳门节点，而香港并不在 Antigravity 的官方开放大名单里，一连上去照样触发地区拦截。

推荐使用「[Claude IP查询出口IP](https://ip.net.coffee/claude/)」：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/61f88d0672240cc8.jpg)

## 03｜3 分钟低价订阅：SEAGM 买土区苹果卡

因为我没有安卓手机，所以本文是基于iOS订阅，目前土区的Google 订阅都会跳转到Google内购，月费只要 1,989.99 里拉。

如果是新注册不久的土区 Apple ID，充值前先挂在固定网络下正常用几天，别高频换设备或跨地区切节点，防止苹果直接把余额冻进 72 小时审核。

订阅本身三分钟就能搞定：

1. 买卡充进土区余额：打开全球数字点卡平台 [SEAGM](https://www.seagm.com/)，搜 Apple Gift Card (Turkey)（或 iTunes Gift Card TR），买够覆盖 1,989.99 里拉 的面额（一般直接买 2,000 里拉卡密，支持支付宝付款）。国内用户图省事也可以在闲鱼搜「土耳其 App Store 礼品卡」，但 SEAGM 这类老牌平台卡源更干净，不容易踩到黑卡撤单坑。拿到兑换码后打开手机土区 App Store，点右上角头像选「兑换礼品卡或代码」充进余额。
2. 在 App 内直接选中 1,989.99 里拉档位：去土区 App Store 下载官方的 Google One 或 Gemini 客户端，打开后登录你第 2 章准备好的外区 Gmail（确认账号策略地区已在开放名单内），点进设置里的「管理 Google One」或升级订阅页面，在套餐列表里直接选中 1,989.99 里拉/月 的 Google AI Ultra 5x 套餐，拉起苹果付款弹窗用里拉余额扣款。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/edf1b9a7a5730729.jpg)

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/66d7f3cbe6139f68.jpg)

## 04｜Antigravity安装与必装插件

去官方下载中心 https://antigravity.google/download 下好对应平台安装包，装好通过浏览器完成 OAuth 授权登录，桌面端、IDE 和 agy CLI 就会共用同一份额度和配置。

推荐AntiGravity安装插件：

- [elviscjn-cjn/antigravity-context-viewer](https://github.com/elviscjn-cjn/antigravity-context-viewer)：顶栏实时上下文与速度胶囊、52 周 Token 热力图与 API 回本账本、客户端简体中文汉化与系统增强
- [yiheng8023/antigravity-chinese](https://github.com/yiheng8023/antigravity-chinese)：如果不想装上面的插件，可以安装一个独立的汉化脚本
- [n2ns/antigravity-panel](https://github.com/n2ns/antigravity-panel)：侧边栏插件，能看各模型还剩多少额度、什么时候重置，还能看用量趋势和上下文占用，支持中文

## 05｜Orchestrator和模型选择

客户端和看板就位后，模型下拉框里排着一堆名字：Carbon、Orchestrator (Carbon)、Argon，居然还有 Claude 5.5 系列。如果不分场景全程拿最重的旗舰单模型硬跑，5 小时额度很容易刷刷往下掉。对照下面这张分工表选模型，速度、质量、省配额三头都能顾到：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/bbe4d9171fc0f6eb.jpg)

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/81943f0ee68f6705.jpg)

## 06｜Antigravity 反代与防封指南

很多人不喜欢用 Antigravity 想要反代到其他Agent中使用，但是其实目前 Antigravity 能力并不差，目前整理在对标codex了。

Google 官方明确禁止第三方软件直接盗用客户端登录态，近期对异常流量查得极严，处理不好就会直接吃 403 Forbidden 封禁权限。

目前围绕 Magpie 共有三种反代接法，安全边界差异极大，动手前先看对比：

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/01d8fd081a2e4ec5.jpg)

### 6.1 方案一：Google 家庭组 + 小号跑 Magpie 反代（物理隔离“邪修”）

如果你既想爽用外部 Agent 工具链，又绝对不想拿自己充了钱的主力大号赌运气，最稳妥的办法就是利用 Google 家庭组做物理风险隔离：

1. 按第 2 章的流程，额外准备一两个账号所在地已落在开放名单内的空白干净 Gmail 当小号。
2. 用开了 Ultra 5x 订阅的付费大号创建 Google 家庭组（Family Group），邀请小号加入家庭组共享 AI 额度；付费大号自己只在官方 Antigravity 客户端里规规矩矩使用，永远不碰任何反代配置。
3. 在本地 Magpie 里只登录并绑定这个家庭组小号，外部 Agent 的请求全部走小号转发。
4. 万一小号跑得太猛触发风控被封掉 Antigravity 权限，直接用大号进家庭组把废掉的小号踢出去，换下一个备用新小号拉进来顶上，付费大号本身毫发无损。

用这套方案有两个前提得心里有数：第一，Google 家庭组成员共用同一个 5 小时与每周额度池，小号在外面跑反代会实打实扣减你大号的剩余配额；第二，别在短时间内连续踢出多个被封小号又高频拉新，避免极端情况下牵连整个家庭组触发异常审查。

### 6.2 方案二：Magpie 安装 agy-cli 插件借道官方客户端（低风险新方案）

针对直连协议容易被风控识别的问题，Magpie 官方近期专门给出了更安全的替代方案（[参考官方推文](https://x.com/magpie_router/status/2121631706218447086)）：在 Magpie 里改用社区插件 「Antigravity (local agy CLI)」（简称 agy-cli）。

它的核心讨巧之处在于底层走了 ACP（Agent Client Protocol） 协议，直接驱动你本机已经安装好、登录好的官方 agy CLI 去干活。换句话说，所有发往 Google 服务器的请求全部由 Google 官方客户端自己发出，不再由网关去伪装模拟客户端直连 Google 接口，协议指纹层面的封号风险会低很多。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/7f9f743ead85e64f.jpg)

注意这招只是显著降低了协议特征被抓的概率，推的评论里也有被封的人，封不封最终仍由 Google 风控决定。Magpie 官方同样提醒尽量用备用号挂载，且切忌多账号同时高频并发狂刷；最稳妥的进阶玩法是把方案一和方案二叠起来用，拿家庭组小号登录本机 agy CLI 再通过该插件接入 Magpie。

### 6.3 方案三：主力大号直接挂 Magpie 原生反代（封号风险极高）

最省事但也最容易翻车的做法，就是不建家庭组也不装本地 CLI 桥接插件，直接把付费主力大号的 OAuth 授权绑进 Magpie 默认渠道里模拟客户端直连反代。

这种裸奔接法一旦遇上外部 Agent 动辄几十万 Token 的高频长上下文请求，流量特征和请求头细节跟真人在 IDE 里写代码差异巨大，极易撞上谷歌自动化滥用检测。目前社区里哭诉直接吃 403 Forbidden 被封禁 Antigravity 权限的案例，绝大多数都是拿主力号硬挂直连反代导致的。除非你手头是准备随时弃用的临时号，否则付费大号千万别省这几分钟隔离功夫。

## 07｜手机远控访问

跑动辄半小时起步的长任务时没必要一直守在电脑前。只要电脑端 Antigravity 启动着，出门在外直接掏出手机就能远控本机工作台，实时看任务进度、点权限审批弹窗、顺手追加下一轮指令。

人离开电脑前先打开左下角 Settings -> Application -> General（快捷键 Ctrl + , 或 Cmd + ,），把下面两个保活开关勾上：

- 开启 `Prevent Sleep`：阻止电脑自动休眠，防止挂机跑一半的长任务和底层代理网络被系统挂起冻结。
- 开启 `Enable Remote Control`：拿手机相机扫界面弹出的二维码在浏览器打开，即可实时同步当前对话流远程监工，页面右上角还支持直接切换账号与实例。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/179a1ed9c1d43adc.jpg)

## 08｜每月 40 美元 API 赠金领取攻略

第一章提过一嘴，开通 Google AI 订阅后会通过 Google Developer Program 按月赠送官方云与 Gemini API 抵扣额度（Pro 送 10 美元/月、Ultra 5x 送 40 美元/月、Ultra 20x 送 100 美元/月）。按土区每月 280 元人民币算，光这 40 美元官方赠金就已经把月费赚回来了。领到手生成 API Key 后，直接填进 Cursor、DSH 或各类第三方 Agent 里就能光明正大调官方 Gemini 接口，日常轻量外部调用甚至不用折腾第六章的反代。

领取攻略：

1. 用开通了 Google AI Ultra 5x 的同一个谷歌主号，登录 [Google AI Studio](https://aistudio.google.com/)。
2. 在左侧边栏或工作台首页找到 「Claim your free API credits」 提示卡片点进去（没看到卡片就直接点左侧菜单的 Billing）。
3. 弹窗里点确认关联开发者身份，哪怕你之前没注册过 Google Developer Program，向导也会自动帮你免费建档并绑定。 如果是新号可能会报错，去Google Cloud注册。
4. 激活预付费账单（最容易卡壳的一步）：官方赠金必须挂在已激活的计费账户下才能生效。首次在 AI Studio 开通预付费账单时，通常需要绑一张外币卡并最低预充值 5 美元来激活账户（也可能是$30）。放心充，调用 API 时系统优先扣每月赠送的 40 美元额度，只有把赠金彻底烧光了才会动你预充的 5 美元本金。
5. 切到左侧 API keys 页面，确认你的 Project 已经关联上刚才激活的计费账户，复制生成的 API Key 填进第三方工具即可开用。
6. 有效期 12 个月，月底不清零：当月没用完的赠金不会作废，每笔额度发放后有效期长达 12 个月，下个月新发的 40 美元会继续往上累加，调用时自动优先扣除最快到期的那一笔。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/cc2b2444d31a75a5.jpg)

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/c099f6863688ffff.jpg)

## 09｜疑难杂症

即便前面每一步都按部就班操作，上号头两天依然极有可能撞上下面这三个经典拦路虎。真碰到了别慌，按对应步骤两分钟就能解决。

### 9.1 弹 Eligibility check failed 逼你发短信死循环：借 Cloud Shell 换号接码秒过

用新准备好的外区 Gmail 登进 Antigravity 时，很多人会突然被一行报错弹回登录页：

```text
Eligibility check failed: Your current account is not eligible for Antigravity. Verify your account to continue.
Please verify your account in your browser to continue
```

跳转浏览器后又给你弹扫码，逼着你拿美国手机号发验证短信，卡死在原地。我排查下来，本质原因是你之前绑过或者用过的手机号码收谷歌验证码太多次，被风控系统标红了。

绕开死循环只要三步：

1. 在同一个已经登录该美区 Gmail 的浏览器里，直接打开 [Google Cloud Console](https://console.cloud.google.com/)，点顶部工具栏终端图标唤起 Cloud Shell，触发谷歌云控制台的校验弹窗。
2. Cloud Shell 弹出的校验窗口会同时提供「扫码」和「接收短信」两个入口。选接收短信，如果常用手机号依然提示「此号码用于验证次数过多」，直接换一个平时没怎么接过谷歌验证码的新手机号完成短信验证。
3. 验证通过后，回到 Antigravity 客户端彻底退出账号再重新登录，拦截弹窗当场消失。

### 9.2 网页端已是 Ultra，客户端却锁在 Antigravity Starter Quota：一行链接补年龄验证

另一种特别迷惑的翻车现场是：网页端和 Google One 早就显示 Ultra 5x 生效了，回到 Antigravity 的 Settings -> Account 里一看，状态却卡在 `Antigravity Starter Quota`，下面还挂着一行警告：

```text
This account is ineligible for higher rate limits through a Google AI plan at this time. Verify your age on your Google Account to unlock access.
```

遇到这行提示别急着退订，只是这个谷歌号还没做过年龄验证。直接在当前浏览器里访问官方年龄验证入口 https://myaccount.google.com/age-verification，按提示完成年龄核验，再回 Antigravity 彻底退出重登一次，5x 高阶额度立刻解锁。

### 9.3 登录无限转圈或子进程漏代理：Clash Verge 单开 TUN 模式

明明浏览器能秒开 Gemini 网页，但 Antigravity 登录框一直转圈或者聊两句就报连接超时，这是因为Antigravity网络策略不同的问题。

打开 Clash Verge（Clash Verge Rev），直接打开「TUN 模式」。单开 TUN 模式让虚拟网卡接管全部底层流量后，客户端和终端工具都会立刻满速连通。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/83d08ff70edcbf62.jpg)

整套流程跑顺之后，每个月花不到三百块钱就能把 Gemini 4 和满血 Claude 5.5 两套顶配模型换着用，彻底告别到处找野鸡中转站和天天担心封号的折腾。
