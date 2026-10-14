---
title: '完全面向小白的AI出海建站教程'
date: '2026-10-14'
updated: '2026-10-14'
---

因为自己淋过雨，所以想为别人撑伞。于是我做了一个完全面向小白的AI出海建站教程

教程提供了上站全流程文字说明。完全面向新手小白，只需要你：用过AI、不用懂代码，不用懂英文，跟着流程走，你要是跑不通我提头来见。

我人麻了，X不给上传那么多图片。。。教程后半段图片都加载不出来，完整带图片的教程流程在飞书的文档里，如果有帮助到你的话，请给它点一个赞吧～如果有哪里有阻碍的，也可以留下标注，我看到会及时解决

👉 [完整带图教程（飞书文档）](https://qcnj3k0hgb3d.feishu.cn/wiki/BqrRwoyjDidlcLk6H7FcVN0unnc)

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/1ce24d3ea64cb6c8.jpg)


### 叠甲：
这篇教程只教会你如何跑通【找到需求关键词】-【做网站】-【部署上线】的流程，想要通过这个赚到钱，还有很多事要做，一步登天不可取。

为了便于新手理解，工具我都推荐了最便宜或者最方便的，基本功练扎实了，才能想赚钱的事。

大约需要花费0.5~2天可以跑通全流程，中间有任何问题，都可以复制文本或者截图问AI，实在不行留个言，我来补充到这篇教程里(#^.^#)

---

### 开工准备
最理想的花费在30以下，如果算上编码工具codex/claude code和魔法工具clash，一个月内最多200块。

- **域名商**：spaceship（最便宜的域名几块钱、支持支付宝）
- **服务器部署**：vercel（免费）
- **SEO工具**（其实新手可以不买，但是出海肯定会用上）：semrush
- **找词工具**：google trends（免费）https://trends.google.com/
- **站长工具**，做完网站，在这里提交。可以在这里查看你的网站数据：\
  - 谷歌（免费）https://search.google.com/   google search console简称gsc\
  - 必应（免费）Bing Webmaster
- **AI编码工具**：最好是codex或者claude code，没有用国产免费的workbuddy或者trae也行，但是国产的不咋好用。
- **代码仓库**：github（免费）

---

### 第一步，找需求关键词：

找需求关键词分两种：

1. **老词**（长期有人会搜索的词，比如说【word转pdf】，一直都有人搜）
2. **新词**（当下流行的事，比如说【26年世界杯】这种，过一段时间就没啥人讨论了）。

目前跟练我们就暂时不区分得那么细，直接任选一个我们感兴趣的方向就好。

新词，在 https://trends.google.com/ 上找

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/cd06344c99d0bd64.jpg)


怎么判断一个关键词有没有人搜索？我怎么知道做出来不是白忙活？\
中间的1M+和200K+这些数据就是搜索量，分别代表着100万+和20万+，右侧就是这段时间的搜索趋势数据。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/994210e2d309488c.jpg)


这里需要一定的经验才能判断出什么词适合我们出海做，有一个简单的筛选原则就是：\
**不做体育比赛/天气预报/政治时事消息/娱乐新闻**\
因为这些领域都有非常成熟的大平台，我们基本不可能在短时间之内和他们竞争到流量。再者，他们的时效性都非常短，经常过了两天就根本没有搜索量了。

老词，可以在以下的词根里去拓展。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/b36881505d641dbd.jpg)


当你选好要做什么词的时候，去semrush（付费工具，一个月几十）上搜这个关键词，看看适不适合做。

以generator为例，我们来筛选看看有哪些好做的关键词：

- kd筛选0~30的
- CPC筛选0.1~10的，CPC为0可以基本理解为毫无变现价值
- **KD**：关键词难度，新手适合0~30的
- **CPC**：商业意图指数，价格越高，代表市场付费意愿越强
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f63c8a08f0d841ff.jpg)

---

### 第二步，做网站
当我们选好了关键词，就准备开始制作网站。\
注意，这一步完全不需要你实际操作，你全程只需要和AI交流，让他出方案和写代码即可。

以UUID generator为例，我们要做的就是生成唯一ID的网站。

让我用codex来为你演示：

> 我是一个出海网站的新手，我现在要做一个网站进行练习，关键词是【xxx】我要做一个功能为【xxx】的网站，请你使用一个新手可以听得懂的方式反问我问题，不要使用专业词汇，以确认这个项目的项目边界，然后给我生成项目需求文档和可以跟着执行的部署文档。\
> 项目背景：\
> 技术栈由你直接决定\
> 需要使用vercel进行部署\
> 需要提交到google search console\
> 练习到以下程度算完成：\
> 功能可用 → 部署 Vercel → 绑定域名 → 可以通过域名直接访问网站 →验证 Google Search Console → 提交站点地图。收录和排名作为后续观察，不作为项目完成条件。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/eb231d8ecb67cd74.jpg)

文档出来后，让他直接实现就行，右边就是网页结果。\
你看，很简单吧？有写过啥代码吗？完全不需要懂代码！
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/1f825888cce60819.jpg)

---

### 第三步，部署
到上面为止，网页都只是在我们电脑本地能看到，想要其他人看到，就要把代码放到服务器上。\
这一步操作叫部署。\
而vercel恰好有免费的部署额度，我们前期白嫖他就行。

1. 我们需要让vercel读到我们的代码，所以我们要把代码传上去。这里我们需要提前注册好github的账号\
   github.com\
   注册好之后，新建一个仓库
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/b358b937b63187c1.jpg)
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/ef767d1dffe95e27.jpg)

把这个复制给AI，这个是我们要上传代码的路径：
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/88c8932d06e0d106.jpg)

**AI提示词**\
【这里放上面复制下来的地址】\
把我的代码上传到这个地址，可能需要我使用网页登录，如果需要我登录的，停下来告诉我，登录后我会让你继续。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/be6e19a3abffff3d.jpg)

上传后就可以看得到代码。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/9a53451cce21af7a.jpg)

这个是本次演示的代码，我已经公开了，可以直接拿去用：\
https://github.com/cloud-hu2000/uuid-generator

到这里代码就上传结束了。\
后续如果你做了任何代码更新，和AI直接说，把我需要提交的代码全部提交到github上，这样vercel就可以实时同步到代码了。

接下来我们进入vercel，这个就是能让别人看到你网站的地方，专业术语叫部署网站\
vercel.com

点击右上角新建项目 → 登录你的github账号 → 选择我们的网站进行导入
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/7927e33c44e004f5.jpg)
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/281d89c55d5d794f.jpg)
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/77832fa4f8ff6674.jpg)

这个界面看不懂怎么办？直接复制给AI让它告诉你怎么填。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f83765771c7659cb.jpg)
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/fac5e8207dd66dda.jpg)

按AI说的直接部署就行了，那我们点一下deploy，就部署好啦~
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/75d2f975765472d5.jpg)
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/f6b2165c999aabe6.jpg)
别人就已经可以访问啦~\
https://uuid-generator-iota.vercel.app/zh/

---

### 第四步 （可选）域名
这一步作者就不买了，我直接用以前的记录来演示。

![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/a7bd72d178ac7b58.jpg)

uuid-generator-iota.vercel.app 这个vercel给我们分配的域名太丑了，如果是uuid-generator.com就顺眼多了。

那我们直接去spaceship买域名，最好的地方在于它可以支付宝哦~\
https://www.spaceship.com/
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/30ed06889526c397.jpg)

这里练手的话，我们买个便宜的域名就好了。\
后面正式上站，我还是推荐com和org这两个域名，ai域名太贵了，有条件的话也可以上。

（毕竟站在用户视角，第一眼看到taobao.online这种域名，第一时间肯定是觉得这个网站不正规）

买好了之后，我们回到首页去关联域名到vercel。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/85015442589e327e.jpg)
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/4da87f0e98f100f5.jpg)

找到刚刚买的域名，点开【Nameservers & DNS】
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/a419071210efd74f.jpg)

此时切换到vercel的这个界面，输入刚刚买好的域名。
![image](https://pub-8dc0158e77a140d4b502b52ab75765b5.r2.dev/docs/d2879d9e42c17088.jpg)

这个时候列表页面会报错：“invalid configuration”，按照截图点击：“vercel dns”即可。

复制下面的两个nameservers到spaceship里。

过一段时间，vercel上面显示valid Configuration就是没问题了，就可以用域名直接访问网站啦~

中间出现任何问题，都可以直接截图或者把网页内容全部copy给AI，让他们来解决，如果没有解决，可以找作者~

---

### 第五步 登记网站到谷歌、bing
谷歌需要翻墙，bing不用

- https://search.google.com/search-console
- https://www.bing.com/webmasters

你一开始的界面可能不是这样的，因为我有网站，只能在这里添加，注意看add property就行。

选择Domain，把你vercel或者买好的域名输上去。

然后把这一部分copy给AI，让它写到网站里：

> 我要把网站注册到google search console\
> 这个是它提供给我的TXT内容，请帮我加到网站里，并且上传到github\
> 【刚刚复制的txt内容】

注：vercel是可以自动获取到最新的github代码并且自动更新网站的，所以一般情况下直接把代码传到github就行，不过也要注意Vercel上的部署情况：如果出错了，网站是不会更新的。

bing的就比较简单了，你在google那里设置好了，就可以直接同步过来了。

数据方面最好不要抱有期待，本次我们只是新手跟练，目的是为了跑通整个流程。要想让网站真的让别人看到，我们还有其他事得做。
