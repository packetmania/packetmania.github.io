---
title: Hello World
date: 2020-11-23 20:48:25
comments: false

---

欢迎来到**网络热度**的博客站点！

{% note success no-icon %}
**Somewhere, something incredible is waiting to be known.**<br>
**— *Carl Sagan*（卡尔·萨根，美国天文学家、科幻和科普作家）**
{% endnote %}
 
这是一个专注于计算机网络技术及软件设计与实现的博客站点，我是博主**子曦**。在这里，我会分享多年工作和学习中积累的许多经验和体会，主题包括TCP/IP协议族、路由与交换技术、网络安全和密码学、系统编程、数据结构与算法，以及思科技术和产品介绍。



## 新的开始

作为一个非常热爱计算机科学和工程技术的程序员，自己很早于2005年就开了自己的博客。可惜由于研发工作繁忙，在发表了两篇文章之后就再无暇再写了。近年来，由于工作性质的变化，逐渐有了一些时间，于是就有了全面整理和总结自己的实践经验和学习体会想法。今年惊奇地发现，虽然域名有了一些变化，[原始的博客站点](http://packetmania.bokee.com/)竟然还在线。但是位于国内的原始站点访问不是很方便，文章更新和存档管理也不理想，所以必须寻找新的博客构建和管理系统。

上网搜索`程序员博客平台`，才大开眼界，时过境迁，已经有多个新一代的 **amazing** 博客技术平台，极大地方便了博主建站和发布过程。经过一些研究，并参考和比较了一些优秀的博客网站，最终选择了 Hexo 这个快速、简洁且高效的博客框架，及基于 Hexo + Next + GitHub Pages 组合的解决方案：

| 系统  | 功能  | 特点 |
|:-------------: |:---------------:|:-------------:|
| [Hexo](https://hexo.io/zh-cn/) | 博客框架 |[Markdown](https://www.markdownguide.org) 解析文章，强大的插件系统 |
| [Next](https://github.com/next-theme/hexo-theme-next)|  博客主题 | 为Hexo量身定制的高品质优雅主题页面|
| [GitHub Pages](https://pages.github.com)|  博客部署 | 开源协作社区 GitHub 免费博客发布站点 | 


## 建站过程

在2020年的感恩节假期突击三天建站成功。得益于不少博主的文章，再加上之前已有用 GitHub 管理项目仓储（repository）的经验，一步步走到底还比较顺利。在 MacBook Pro (v10.15.7) 系统上，基本的过程如下：

1. [安装 Node.js JavaScript 运行环境](https://nodejs.org/zh-cn/)
2. [安装 Git 应用程序](https://git-scm.com)
3. [安装 Hexo 博客框架](https://hexo.io/zh-cn/docs/) 
	* 确实遇到并修复了[EACCES 权限错误](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally)
4. [初始化 Hexo 站点](https://hexo.io/zh-cn/docs/setup)
     * 完成后在根目录下运行`hexo g && hexo s`启动本地站点
     * 浏览器输入 *http://localhost:4000* 可看到站点主题样式
     * Hexo 缺省使用 Landscape 主题
5.  [安装 Next 主题](https://theme-next.js.org/docs/getting-started/)
     * 输入命令行`npm install hexo-theme-next`
     * 成功后运行`hexo version`显示：
``` bash
========================================
NexT version 8.0.2
Documentation: https://theme-next.js.org
========================================
hexo: 5.2.0
hexo-cli: 4.2.0
os: Darwin 17.7.0 darwin x64
node: 15.2.1
v8: 8.6.395.17-node.17
uv: 1.40.0
zlib: 1.2.11
brotli: 1.0.9
ares: 1.16.1
modules: 88
nghttp2: 1.41.0
napi: 7
llhttp: 2.1.3
openssl: 1.1.1g
cldr: 37.0
icu: 67.1
tz: 2020a
unicode: 13.0
```
     * 修改根目录下站点配置文件`_config.yml`，设定`theme: next`
     * 拷贝`node_modules/hexo-theme-next`至`theme/next`
     * 重新启动本地站点`hexo g && hexo s`，浏览器显示 Next 主题
     * Next 主题缺省使用 Muse 分区结构
    
6. [创建 GitHub Pages](https://pages.github.com/)
    * 配置本地 SSH-Key，拷贝公钥到 SSH and GPG Keys 页面
    * 测试本地 SSH 连接`ssh -T git@github.com`
    * 设置 Git 全局参数
       *  `git config --global user.name "Name"`
       *  `git config --global user.email "email@example.com"`

7.  [安装 Git Deployer 和 Backup 插件](https://github.com/hexojs/hexo-deployer-git)
    * 在根目录下运行 npm 安装命令
       * `npm install hexo-deployer-git --save`
       * `npm install hexo-git-backup --save`
    * 修改站点配置文件`_config.yml`，设定`deploy`和`backup`参数：
``` yaml
deploy:
  type: git
  repo:
    github: git@github.com:packetmania/packetmania.github.io.git,master

backup:
  type: git
  theme: next
  repo:
    github: git@github.com:packetmania/packetmania.github.io.git,hexo
```

8. 查看所有已安装模块和插件`npm list`：
``` bash
├── hexo-asset-link@2.1.0
├── hexo-deployer-git@2.1.0
├── hexo-generator-archive@1.0.0
├── hexo-generator-category@1.0.0
├── hexo-generator-index@2.0.0
├── hexo-generator-searchdb@1.3.3
├── hexo-generator-sitemap@2.1.0
├── hexo-generator-tag@1.0.0
├── hexo-git-backup@0.1.3
├── hexo-math@4.0.0
├── hexo-renderer-ejs@1.0.0
├── hexo-renderer-pandoc@0.3.0
├── hexo-renderer-stylus@2.0.1
├── hexo-server@2.0.0
├── hexo-theme-next@8.0.2
├── hexo-word-counter@0.0.2
└── hexo@5.2.0
```
9.  [部署 GitHub Pages](https://hexo.io/zh-cn/docs/one-command-deployment)
    * 在根目录下运行`hexo clean && hexo g -d`（部署 ）和`hexo b`（备份）
    * 成功后查看 GitHub repository 会看得到两个分支
        * master：博客站点（本地根目录下 *public* 目录的全部内容）
        * hexo: 博客框架和主题系统备份
    * 浏览器输入 *https://packetmania.github.io* **BOOM!**



## 主题配置

博客站点上线以后，需要精细调整 Next 主题配置，进行个性优化和美化。调整过程一波三折，开始时读其他博主的文章，应用时却发现许多对自己的系统不适用。后来发现，我的 NexT 版本 8.0.2 非常新，已经集成了大多数主题配置选项和第三方服务，只需要简单修改主题配置文件`theme/next/_config.yml`就可以了。一些第三方服务需要单独注册，整个过程又折腾了三天时间，终于打造出现在的模样。下表总结了我的主题配置：

配置选项        | 配置参数           | 说明     |
|:--------------------:|:------------------:|:-----------------------:|
分区结构 | Gemini  | 流行的双栏结构，就是现在看到的布局   |
菜单      | menu   | 添加首页、关于、标签、分类和归档菜单项   |
字体    | font  |  设置各个部分中英文字体   |
配色    | darkmode  |  设置自动明暗配色模式   |
代码块  | codeblock     | 设定[高亮主题](https://theme-next.js.org/highlight/)和拷贝按钮 |
内置标签      |  note    |   设定[内置笔记标签](https://theme-next.js.org/docs/tag-plugins/note) |
站点概览    | site_state  | 侧栏显示日志、分类和标签统计    |
标签图标 |    tag_icon |  显示标签图标而非 # 字符 |
本地搜索 |    local_search | 添加搜索菜单项，需要安装[搜索插件](https://github.com/next-theme/hexo-generator-searchdb)  |
社交链接        |  social，social_icons    |   侧栏概览显示带链接的社交图标 |
文章目录         |  toc    |   侧栏显示当前文章目录结构 |
文章预览         |   excerpt_description   |  首页只显示文章开头部分  |
阅读全文         |   read\_more\_btn   |  首页添加`阅读全文`按钮  |
字数统计    | symbols\_count\_time |  需要安装[字数统计插件](https://github.com/next-theme/hexo-word-counter)  |
阅读进度        | reading_progress |   侧栏显示阅读进度 % |
回到顶部       | back2top |   侧栏添加回到顶部图标 |
添加书签      | bookmark |   文章页面右上方显示书签图标 |
访客统计   | busuanzi_count |   添加[不蒜子](http://ibruce.info/2015/04/04/busuanzi)访客和阅读次数统计 |
数学公式    | math:mathjax |  需要安装 [Pandoc 插件](https://theme-next.js.org/docs/third-party-services/math-equations.html), [Mathjax参考](https://math.meta.stackexchange.com/questions/5020/mathjax-basic-tutorial-and-quick-reference/5044%20MathJax%20basic%20tutorial%20and%20quick%20reference) |
流程图  | mmermaid |  [Mermaid](https://theme-next.js.org/docs/tag-plugins/mermaid.html?highlight=mermaid) 可绘制多种流程、时序和甘特图 |
图像缩放     | fancybox |   添加[图像缩放功能](https://fancyapps.com/fancybox) |
添加书签      | bookmark |   文章页面右上方显示书签图标 |
许可协议          |    creative_commons   |   选用 [BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 版权协议       |
评论系统         | comments |  添加了 [Gitalk](https://github.com/gitalk/gitalk)，[LiveRe](https://livere.com)，[Disqus](https://disqus.com) 三种评论  |
网页分享        | add\_this\_id | 页面底部加入 [AddThis](https://www.addthis.com) 分享图标  |

Next 主题配置没有运行网站时间统计，搜索一番，选择的办法是打开主题布局脚注文件，在`powered-by`层下面插入另一个`<div class="powered-by">...</div>`代码段计算运行时间，效果就是在页面底部`由 Hexo & NexT.Gemini 强力驱动`下加入新行显示：`本站已运行#年#天#小时#分钟#秒`。代码段如下：


``` javascript themes/next/layout/_partials/footer.njk
  <div class="powered-by">
    {%- set next_site = 'https://theme-next.js.org' if theme.scheme === 'Gemini' else 'https://theme-next.js.org/' + theme.scheme | lower + '/' %}
    {{- __('footer.powered', next_url('https://hexo.io', 'Hexo', {class: 'theme-link'}) + ' & ' + next_url(next_site, 'NexT.' + theme.scheme, {class: 'theme-link'})) }}
  </div>
  <div class="powered-by">
<span>本站已运行<span id="showDays"></span></span>
<script>
  var seconds = 1000;
  var minutes = seconds * 60;
  var hours = minutes * 60;
  var days = hours * 24;
  var years = days * 365;
  var birthDay = Date.UTC(2020,11,25,14,00,00); // 这里设置建站时间
  setInterval(function() {
    var today = new Date();
    var todayYear = today.getFullYear();
    var todayMonth = today.getMonth()+1;
    var todayDate = today.getDate();
    var todayHour = today.getHours();
    var todayMinute = today.getMinutes();
    var todaySecond = today.getSeconds();
    var now = Date.UTC(todayYear,todayMonth,todayDate,todayHour,todayMinute,todaySecond);
    var diff = now - birthDay;
    var diffYears = Math.floor(diff/years);
    var diffDays = Math.floor((diff/days)-diffYears*365);
    var diffHours = Math.floor((diff-(diffYears*365+diffDays)*days)/hours);
    var diffMinutes = Math.floor((diff-(diffYears*365+diffDays)*days-diffHours*hours)/minutes);
    var diffSeconds = Math.floor((diff-(diffYears*365+diffDays)*days-diffHours*hours-diffMinutes*minutes)/seconds);
      document.getElementById('showDays').innerHTML=""+diffYears+"年"+diffDays+"天"+diffHours+"小时"+diffMinutes+"分钟"+diffSeconds+"秒";
  }, 1000);
</script>
  </div>
```

## 博客更新

主题配置完成之后，就是更新文章或日志了。我使用的是 macOS上的 [MacDown](https://macdown.uranusjr.com) 开源 Markdown 文件编辑器，非常易学好用，强烈推荐。发布文章或日志的步骤很简单：

1. 在根目录下运行`hexo new <new-post-title>`创建新文章或日志
2. 用 [Markdown](https://www.markdownguide.org) 编辑器编辑 `source/_posts/<new-post-tiltle>.md`
3. 运行`hexo clean && hexo g && hexo s`，用浏览器本地查看校对
4. 重复以上第2，3步直到文章或日志内容完整无误
5. 运行`hexo clean && hexo g && hexo d`一键部署
6. 运行`hexo b`一键备份


## 联系交流

博客网站上线是我的一个新的起点。在这里，我既要总结自己，又要回馈社区，争取保持每周至少一篇文章或日志的产出量。未来也希望分类整理、结集开源出版。如果读者有任何意见和建议，请发[电邮](mailto:zixiruoxue@gmail.com)或者直接在文章或日志页面底部添加评论。无论您在哪里，三种评论系统应该总有一个可以适用您的网络环境。

最后，如果觉得我的博客站点能够对您有一些帮助或启迪，敬请推荐给您觉得需要的人。卡尔·萨根说过“我们都是星尘”，那么在我们回归宇宙之前，让**网络热度**一直保持传递下去！

祝您每天都能有新的发现，谢谢！