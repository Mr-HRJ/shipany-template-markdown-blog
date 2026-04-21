---
title: 'Stripe Checkout 自动应用优惠配置'
---

> 这篇文章是我在接 Stripe Checkout 时，怎么做到“用户下单时自动带上优惠”，让用户**不用手动输入优惠码**。核心做法分两种：一种是开放输入框（`allow_promotion_codes=true`），用户自己填；另一种是我更常用的自动应用，在创建 Checkout Session 时直接传 `discounts` 并指定优惠对象 ID。需要特别注意：**`discounts` 和 `allow_promotion_codes` 不能同时开**，否则创建 Session 会直接报错，导致支付流程起不来。


我这次要解决的点很明确：**用户进入 Checkout 支付页时，系统自动把优惠打上去，不需要用户手动输入。**

同时我也把“允许用户手动输入优惠码”的方案一起整理出来，方便你按业务取舍。Stripe 对这两种方式的支持是明确的：

* `allow_promotion_codes` 用来展示输入框，让用户自行兑换优惠码
* `discounts` 用来在服务端创建 Checkout Session 时直接应用折扣

---

## 一、两种方案对照

| 方案          | 用户是否需要输入 | 你在服务端要传的参数                                                                      | 适合场景              | 关键注意点                                                          |
| ----------- | -------- | ------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------- |
| 允许用户手动输入优惠码 | 需要       | `allow_promotion_codes=true`                                                    | 你要发券/让用户自己填码      | Checkout 会出现兑换框                |
| 自动应用优惠      | 不需要      | `discounts=[{coupon:COUPON_ID}]` 或 `discounts=[{promotion_code:PROMO_CODE_ID}]` | 新用户首单、渠道专属优惠、默认折扣 | **不要同时开启 `allow_promotion_codes`**，否则会报“只能二选一”的错误

> 我重点讲第二种：自动应用优惠。

---

## 二、先在 Stripe 后台创建优惠券

第一步不是写代码，而是在 Stripe Dashboard 把优惠对象建好。

### 1. 新增优惠券

在 Stripe 平台的优惠相关入口里创建一个优惠券，常见要填的信息包括：

* 优惠名称
* 折扣力度
* 持续次数

这里你填完并创建成功后，Stripe 会给你一个对应的 ID（后续代码里要用到的就是它）。

> Stripe 的 Checkout 折扣能力本质就是基于 Coupons/Promotion Codes 这套对象体系来的。

---

## 三、在 Checkout Session 创建逻辑里自动带上优惠

优惠券创建好之后，下一步是在你创建 Checkout Session 的代码逻辑里加上 `discounts`。

### 1. 关键点：用 discounts 指定优惠对象 ID

你需要在 Checkout 的创建参数里加入 `discounts`，并把优惠对象的 ID 填进去。Stripe 官方把这块归类在 Checkout discounts 的能力里。

常见写法就是二选一：

* 用 Coupon：`discounts: [{coupon: COUPON_ID}]`
* 用 Promotion Code：`discounts: [{promotion_code: PROMO_CODE_ID}]`

你原文里说“加 discounts 信息和优惠码 id”，落地时要注意你拿到的是哪种 ID：

* 如果你建的是**优惠券**，一般用 `coupon`
* 如果你额外建了面向用户的**兑换码**，才会走 `promotion_code`

---

### 2. 必须去掉 allow_promotion_codes，否则会报错

这是我踩坑最明确的一点：

* 如果你想“自动应用优惠”，就不要再开 `allow_promotion_codes`
* 因为 Stripe 这两种方式是互斥的，很多人会遇到创建 Session 直接报错，错误信息类似“只能指定其中一个参数”。

也就是说：
**自动优惠=只用 `discounts`**
**手动输入=只用 `allow_promotion_codes`**

不要混着来。

---

## 四、我用的最小可复用检查清单

为了避免你照着配还翻车，我把这条链路压成一个检查清单，你逐条过一遍就行：

* 已在 Stripe Dashboard 创建优惠券，并拿到对应 ID
* Checkout Session 创建参数里已加入 `discounts`
* `discounts` 里填的是正确类型的 ID（coupon 还是 promotion_code）
* **已移除 `allow_promotion_codes`**（自动优惠场景下）
* 走一次真实支付流程验证折扣是否生效（看 Checkout 页面金额是否已变化）

---

## 五、官方参考资料

Stripe 对 Checkout 折扣的官方说明在这里，里面包含 `discounts` 的用法与示例：https://docs.stripe.com/payments/checkout/discounts?utm_source=chatgpt.com
