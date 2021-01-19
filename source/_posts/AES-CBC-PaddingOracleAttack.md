---
title: AES-CBC 密文填充攻击 — 深入理解和编程实现
categories:
  - 学习体会
tags:
  - 密码学
  - 网络安全
  - Python编程
date: 2020-12-01 21:18:32

---

密文填充攻击 (Padding Oracle Attack) 可能是现代密码学史上的最有名也最成功的攻击方法。攻击者利用密文的填充验证信息，实现密文破解。

<!--more-->

{% note success no-icon %}
**Every secret creates a potential failure point.**<br>
**— *Bruce Schneier*（布鲁斯·施奈尔，美国密码学和信息安全专家、作家）**
{% endnote %}

> 很快更新，敬请期待