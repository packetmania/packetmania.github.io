---
title: 用ISIC测试网络设备IP协议栈的健壮性
date: 2020-11-25 21:15:51
categories:
- 工具使用
tags:
- TCP/IP
- 软件测试
- 网络安全
- C/C++编程
mathjax: true

---

ISIC是一个开放源码的IP协议栈健壮性测试工具集。许多网络设备的安全漏洞 (比如拒绝服务等) 源于IP协议栈的软件设计或实现错误，应用此工具集可以及时发现和修复这些差错，确保系统运行的稳定性和可靠性。
<!--more-->

 
{% note success no-icon %}
**Testing leads to failure, and failure leads to underatanding.**<br>
**— *Burt Rutan*（伯特·鲁坦，美国航空工程师，2004年首次率领民间团队制造载人航天器飞上太空）**
{% endnote %}


### 工具概要

[ISIC](http://isic.sourceforge.net/)是英文全称 **I**P **S**tack **I**ntegrity **C**hecker 的首字母缩写，翻译过来就是“IP协议栈完整性检查器”。这是一个用于测试IPv4和IPv6及其附属协议族 (TCP，UDP，ICMP等) 软硬件实现的工具集。其思想是产生目标协议的部分参数可控的随机数据包，然后将数据包发送到指定的被测试设备，观察设备的输出结果和运行状态。被测试设备可以是路由器、交换机、网络防火墙、入侵检测/预防系统 (IDS/IPS) 或者任何联网主机。ISIC也包含一个产生原始以太网帧的工具，用于检验以太网底层的软硬件实现。

ISIC工具集包含的十个可执行的命令行工具如下，它们覆盖了几乎所有的TCP/IP核心协议：

* isic：IPv4协议栈完整性检查器
* tcpsic：TCP协议栈完整性检查器
* udpsic：UDP协议栈完整性检查器
* esic：以太网协议栈完整性检查器
* icmpsic：ICMP协议栈完整性检查器
* multisic: 组播UDP协议栈完整性检查器
* isic6：IPv6协议栈完整性检查器
* tcpsic6：IPv6 TCP协议栈完整性检查器
* udpsic6：IPv6 UDP协议栈完整性检查器
* icmpsic6：ICMPv6协议栈完整性检查器

ISIC支持Unix类 (Linux/BSD/macOS) 系统，其编译和运行都需要[Libnet库](https://github.com/libnet/libnet) (版本1.1以上) 。Libnet是一个可移植的底层网络数据包构造和注入框架，ISIC调用它的应用程序接口 (API) 来创建和发送网络层数据包和链路层数据帧。ISIC在其主页上以源代码的压缩包发布，也可以使用RPM安装。ISIC的最后版本是0.07，它以BSD风格的许可证发布，对使用者的限制很少。

ISIC最早的0.01版在1999年由迈克·弗兰岑 (Mike Frantzen) 在Redhat Linux 5.1上用了两周的时间写成。一开始弗兰岑用它来检测防火墙的漏洞，但是意外地发现它竟然造成许多设备崩溃。弗兰岑把ISIC放到网上后，得到了很好反响，许多IDS/IPS研发和测试工程师都在工作中使用它。直到0.05版，ISIC一直由弗兰岑自己维护和更新。2004年初，Libnet的作者迈克·希夫曼 (Mike Schiffman) 重写了这一API库，新的1.1.x版本不再向后兼容。至此，ISIC无法再与最新的Libnet库编译和链接。

2004年晚些时候，思科公司的安全测试工程师[Shu Xiao](https://www.linkedin.com/in/shu-xiao-7925a3/)将一份补丁发送给弗兰岑，使ISIC能够工作于新版Libnet之上，补丁也包含了对其它一些错误的修复。这成为了弗兰岑移交责任给Xiao的完美时机，0.06版就此诞生。Xiao继续进一步增强ISIC的功能。他添加了新的IPv6协议测试工具 (*sic6)，以及组播测试工具 (multisic)，同时还改进了随机性和发送效率。最终的0.07版由Xiao于2006年12月发布。

虽然原来的开发目的是做防火墙的功能测试，但ISIC在发现IP协议栈完整性漏洞方面的惊人表现，使得它成为一个网络系统安全评估的一个重要工具。[ISIC在Sourceforge的项目页面](https://sourceforge.net/projects/isic/)显示，截止到2020年一月0.07版下载量接近两万。如果包含RPM的下载安装，实际的使用量应该远远大于这个数目。搜索网上<u>公共漏洞和暴露</u> (Common Vulnerabilities and Exposures，缩写CVE) 数据库，可以找到下面由ISIC工具集披露的安全漏洞：


| 编号 (CVE-ID) | CVSS[^c] 评分 | 相关产品/系统 | 问题描述 | ISIC工具 |
|:-:|:-------:|:----:|:-----|:-----:|
| CVE-2000-0451 | 5.0 MEDIUM | 英特尔 Express 8100 ISDN 路由器 | 允许远程攻击者使用过大或分片ICMP数据包进行拒绝服务攻击 | icmpsic |
| CVE-2000-0463 | 5.0 MEDIUM | BeOS 5.0 操作系统 | 允许远程攻击者使用分片TCP数据包进行拒绝服务攻击 | tcpsic |
| CVE-2008-1746 | 7.8 HIGH | 思科统一通信管理器 (CUCM) | 允许远程攻击者通过一系列格式错误的UDP数据包导致拒绝服务 (核心转储和服务重启) | udpsic |
| CVE-2013-7470 | 7.1 HIGH | Linux 内核 <3.11.7版本 | 允许攻击者造成拒绝服务 (无限循环和崩溃) | icmpsic |

由于存在被黑客利用的风险，大量CVE都不给出所使用工具的信息。所以，有理由相信用ISIC找到的安全弱点及漏洞也远不止上面这些。比如，在网上对[2019年风河系统VxWorks的IPv4选项堆栈溢出漏洞](https://attackerkb.com/topics/12890azSfK/cve-2019-12256-vxworks-ipv4-options-buffer-overflow)的讨论中，就有人问到为什么VxWorks没有做“isic"：

> _In this particular case, it’s really surprising however that **VxWorks did not just isic**, which has been around for years and years to find a vulnerability like this: http://isic.sourceforge.net/_

从计算机科学和工程的学术研究上看，ISIC可被归类为自动软件测试技术中的模糊 (fuzzing) 测试。[许多研究文献](https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=%22IP+Stack+Integrity+Checker%22&oq=I)都提及对ISIC的直接应用或间接参考。这种技术的基本思想是将无效、未被考虑或随机的数据输入到计算机程序，然后监视程序运行是否发生异常，例如崩溃、死循环、内置代码断言失败 (assert) 或潜在的内存泄漏等。从缓冲区溢出到跨站点脚本攻击的大多数安全漏洞，通常是对用户提供的输入数据验证不足的结果。模糊测试发现的网络系统安全漏洞常常是严重的，如果不及时发现和清除，会给用户造成重大损失。有证据显示，一些主要的网络设备厂商都集成了ISIC到质量控制的测试工程实践中。


### 安装过程

这里以树莓派 (Respberry Pi 4 Model B) 目标系统为例，说明ISIC的安装过程。首先，使用几个命令查看系统软硬件和GCC编译器版本信息：

``` bash
pi@raspberrypi:~ $ cat /proc/device0tree/model
Raspberry Pi 4 Model B Rev 1.4
pi@raspberrypi:~ $ uname -a
Linux raspberrypi 4.19.118-v7l+ #1311 SMP Mon Apr 27 14:26:42 BST 2020 armv7l GNU/Linux
pi@raspberrypi:~ $ gcc --version
gcc (Raspbian 8.3.0-6+rpi1) 8.3.0
Copyright (C) 2018 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

如前所述，ISIC的编译和运行需要Libnet库的支持。最新的Libnet 1.2版可以从其[GitHub项目发布主页下载](https://github.com/libnet/libnet/releases)，然后执行以下步骤编译和安装：

``` bash
tar xf libnet-1.2.tar.gz
cd libnet-x.y.z/
./configure && make
sudo make install
```

安装完可以在`/usr/local/lib`目录下找到Libnet的静态库文件`libnet.a`和动态链接库文件`libnet.so`，而所有的编程需要的头文件位于`/usr/local/include`目录下。这些验证无误后，接下来就可以开始ISIC的安装：

1. 从ISIC的主页 ([http://isic.sourceforge.net/](http://isic.sourceforge.net/)) 下载压缩的打包文件**isic-0.07.tgz**
2. 用`tar xzvf isic-0.07.tgz`命令解压展开：
3. 进入`isic-0.07`目录，执行`./configure`命令配置编译环境：

	``` bash
	pi@raspberrypi:~/Downloads/isic-0.07 $ ./configure 
	creating cache ./config.cache
	checking for gcc... gcc
	checking whether the C compiler (gcc  ) works... yes
	checking whether the C compiler (gcc  ) is a cross-compiler... no
	checking whether we are using GNU C... yes
	checking whether gcc accepts -g... yes
	checking for a BSD compatible install... /usr/bin/install -c
	checking for /usr/local/lib/libnet.a... no
	checking for -lnet... no
	checking for libnet_init in -lnet... yes
	checking how to run the C preprocessor... gcc -E
	checking for ANSI C header files... no
	checking for u_int16_t... yes
	checking for u_int32_t... yes
	checking for in_addr_t... no
	checking whether gcc needs -traditional... no
	updating cache ./config.cache
	creating ./config.status
	creating Makefile
	```
4. 执行`make`命令编译和链接：

	``` bash
	pi@raspberrypi:~/Downloads/isic-0.07 $ make
	gcc -o isic isic.c -Wall -W -g -O2 -I/usr/local/include `libnet-config --cflags` -DHAVE_LIBNET=1 -Din_addr_t=u_int32_t  `libnet-config --defines` -DVERSION=\"0.07\" -lnet -L/usr/local/lib  `libnet-config --libs` 
	gcc -o tcpsic tcpsic.c -Wall -W -g -O2 -I/usr/local/include `libnet-config --cflags` -DHAVE_LIBNET=1 -Din_addr_t=u_int32_t  `libnet-config --defines` -DVERSION=\"0.07\" -lnet -L/usr/local/lib  `libnet-config --libs` 
	tcpsic.c: In function ‘main’:
	tcpsic.c:274:7: error: dereferencing pointer to incomplete type ‘struct tcphdr’
	    tcp->th_off = rand() & 0xf;
	       ^~
	make: *** [Makefile:27: tcpsic] Error 1
	```
	糟糕！有一个编译错误！不必惊慌，这是Linux系统的TCP/IP头文件的变化造成的 (毕竟从最后的0.07版发布到现在已经十多年了)。如下修改`isic.h`文件就可以清除这个错误：

	``` diff
	pi@raspberrypi:~/Downloads/isic-0.07 $ git diff isic.h.bak isic.h
	diff --git a/isic.h.bak b/isic.h
	index c12f716..8a8641c 100644
	--- a/isic.h.bak
	+++ b/isic.h
	@@ -10,6 +10,8 @@
	 #include <netinet/icmp6.h>
	 #include <netinet/ip6.h>
	 #include <netinet/if_ether.h>
	+#include <netinet/tcp.h>
	+#include <netinet/udp.h>
	
	 #ifndef ETHER_FRAME_SIZE
	 #define ETHER_FRAME_SIZE 1500
	```
5. 下一步执行`sudo make install`，将可执行文件安装到`/usr/local/bin`目录，同时将用户手册安装到`/usr/local/man/man1`目录：

	``` bash
	pi@raspberrypi:~/Downloads/isic-0.07 $ sudo make install
	/usr/bin/install -c -m 0755 -d /usr/local/bin
	/usr/bin/install -c -m 0755 -c isic tcpsic udpsic icmpsic esic multisic isic6 tcpsic6 udpsic6 icmpsic6 /usr/local/bin
	/usr/bin/install -c -m 0755 -d /usr/local/man/man1
	/usr/bin/install -c -m 0755 -c isic.1 /usr/local/man/man1
	```
	
至此安装过程结束，运行`man isic`可以在终端直接在线查询[用户手册](https://linux.die.net/man/1/isic)。**注意，因为ISIC工具集调用原始套接字 (raw socket) 发送数据包，运行命令行需要超级用户权限，或者授予普通用户特殊权限以`sudo`方式运行。**

### 用户指南

#### 命令行选项

下表给出了通用的命令行选项的使用说明：

| 选项字符  | 相关参数  | 说明 | 默认值 |
|:-:|:-------:|:----:|:-----:|
| c | 数据包数目 | 只适用于esic |  $2^{32}$ |
| d | 目的MAC/IP地址 | 对esic可选，对其它为必需。设为“rand”选择随机地址 | 对esic为FF:FF:FF:FF:FF:FF |
| i | 接口标识 |  对esic和multisic为必需，其它不适用 | 由系统路由选定 |
| k | 跳过的数据包数目 |  指定跳过（不发送）的初始数据包数目 | 0 |
| l | 数据包长度 |  只适用于esic | 1500 |
| m | 打印速率或最大速率 |  指定esic的打印间隙，对其它为最大速率 (kB/s) | 对esic为1000 |
| p | 协议号或数据包数目 |  指定esic的上层协议号，对其它为数据包数目 |  对esic为0x0800 (IP)，对其它为$2^{32}$ |
| r | 随机数种子 |  指定伪随机序列的种子 |  当前进程标识 (ID) |
| s | 源MAC/IP地址 | 对esic可选，对其它为必需。设为“rand”选择随机地址  |  对esic为接口的MAC地址 |
| x | 重复次数 |  适用于esic以外的全部工具，设置数据包的重复次数 | 1 |
| v | 无 | 打印当前版本号 | 无 |
| z | 源MAC地址 |  只适用于multisic，设置源MAC地址 | 指定接口的MAC地址 |
| D | 无  |  适用于esic以外的全部工具，打印调试输出 | 无 |

有几点要特别解释一下：

1. $p/k/x$三个参数决定了总计发送多少个数据包。假设数据包总数为$N$，那么 $N＝(p-k)\cdot x$。所以$k$一定要小于$p$，不然就没有数据包发出。
2. 如果$r$参数固定，伪随机序列的种子不变，那么ISICI构造和发送的数据包集合就完全一致。应用这一点可以重复测试序列。
3. 实际的数据包传输速率由网络接口卡决定，ISIC不能控制，但是它可以指定每秒生成和发送数据包的数量。

此外，除esic以外的全部工具还支持特定的百分比选项，说明如下：

| 选项字符  | 相关百分比参数  | 说明 | 默认值 (%) |
|:-:|:-------:|:----:|:-----:|
| i | 错误的ICMP校验和 |  只用于icmpsic和icmpsic6 | 10 |
| t | 错误的TCP校验和 |  只用于tcpsic和tcpsic6 | 10 |
| u | TCP高优先级 (URG) 标志符置位 |  只用于tcpsic和tcpsic6 | 10 |
| F | 分片的数据包 |  对isic6意味着包括随机的分片扩展报头 | 10 |
| I | IP选项或随机长度值 | 对isic为IP报头随机长度值，对其它为IP选项 | 10 |
| T | 有TCP选项的数据包 | 只用于tcpsic和tcpsic6  | 10 |
| U | 错误的UDP校验和 |  只用于udpsic和udpsic6  | 10 |
| V | 错误的IP版本号 |  适用于全部工具 | 10 |


#### 命令行示例

* 使用esic生成具有首部包含随机协议编号的以太网帧，并通过eth0接口发送出去；在帧中，源MAC地址固定为01:02:34:56:07:89，目的MAC地址是默认的广播地址；每5000帧会有一条打印输出行：

	``` bash
	esic -i eth0 -s 01:02:34:56:07:89 -p rand -m 5000
	```

* 指定isic生成带有随机源地址的100个IP数据包，目的地址固定为10.11.12.13；随机种子设置为10；一半的数据包将是分片报文；发送时，将跳过前20个数据包，从第21个数据包开始：

	``` bash
	isic -s rand -d 10.11.12.13 -F 50 -p 100 -k 20 -r 10
	```

* 指定tcpsic生成源地址为1.2.3.4和源TCP端口69，目的地址21.22.23.24和随机目的TCP端口的数据包；每个数据包将被发送两次；整体最大速度为1000kB/s；在所有生成的TCP数据包中，30％的数据包将具有随机的TCP选项；而50％的TCP校验和将不正确。

	``` bash
	tcpsic -s 1.2.3.4,69 -d 21.22.23.24 -x 2 -m 1000 -T 30 -t 50
	```

* 使用以下multisic命令向组播地址224.0.0.5发送50000个UDP数据包；随机源地址和源/目的UDP端口；输出接口被强制为eth2；50％的传出数据包将是分片报文；并且源MAC地址设置为ff:ff:ff:ff:ff:ff：

	``` bash
	multisic -s rand -d 224.0.0.5 -i eth2 -p 50000 -F 50 -z 	ff:ff:ff:ff:ff:ff
	```

* 使用以下udpsic6命令发送100万个具有随机源地址和源UDP端口的IPv6 UDP数据包；目的地址为2001:1:2:3:4::2，目的UDP端口161 (SNMP端口)；90％的传出数据包将具有随机的IPv6目的选项标头，而总数据包中的20％将包含不正确的UDP校验和：

	``` bash
	udpsic6 -s rand -d 2001:1:2:3:4::2,161 -p 1000000 -I 90 -U 20
	```

{% note danger %}

当心：请务必谨慎使用ISIC工具集，尽量在封闭的实验网络中运行，以避免给共享的工作环境造成破坏，否则可能要为给团体或他人所带来的损失负责！

{% endnote %}

最后，给出一段完整的`isic`工具运行记录及解读：

``` bash
pi@raspberrypi:~ $ sudo isic -v
Version 0.07 
pi@raspberrypi:~ $ sudo isic -s rand -d 10.0.23.1 -p 5000
Using random source IP's
Compiled against Libnet 1.2
Installing Signal Handlers.
Seeding with 1445
No Maximum traffic limiter
Bad IP Version = 10% Odd IP Header Length = 10% Frag'd Pcnt = 10%
 1000 @ 18317.7 pkts/sec and 11797.1 k/s
 2000 @ 20195.5 pkts/sec and 12885.9 k/s
 3000 @ 26723.7 pkts/sec and 17110.4 k/s
 4000 @ 27171.0 pkts/sec and 17936.8 k/s

Wrote 5000 packets in 0.22s @ 23122.03 pkts/s
```
从上面的记录可以看到，该`isic`命令指定发送5000个的IP数据包。数据包源地址随机，目的地址为10.0.23.1。输出显示`isic`工具使用Libnet 1.2版编译和链接，随机数种子默认为进程号1445。之后是三个百分比选项：错误的IP版本号、IP报头随机长度值和分片数据包，都取默认值10%。每一千个数据包会打印一行，显示累计数据包发送速率和当前一千个数据包的字节发送速率，单位分别为pkt/s和k(B)/s。全部数据包发送完毕，打印总计运行时间0.22秒和累计数据包发送速率约23k pkts/s。

#### 使用经验

* ISIC的基本应用场景总结如下：
	* 检验防火墙是否有数据包泄漏
	* IDS/IPS 的穿透性测试
	* 路由器、交换机和主机协议栈的健壮性测试

* ISIC的主要延伸应用，是对网络安全极为重要的脆弱性/漏洞审查。可以运行下面的测试，并观察是否会发生系统崩溃或死机状态：
	* 模糊 (fuzzing) 测试
	* 充溢 (flooding) 测试
	* 拒绝服务 (DoS) 攻击

* 另外还可以在测试进行中，并行监测被测设备的健康性，主要指标为：
	* CPU和内/外存资源利用率
	* 响应SNMP查询的能力
	* 命令行接口/图形用户界面的访问性能

* 当出现问题时，可以使用同样的`-r`参数，然后组合`-p/c/k`选项运用二分查找算法定位相关的数据包。比如，假定发`isic`送1000个数据包造成被测设备异常，那么将`-p`减半为500运行。如果发生同样的异常，则继续减半搜索；如果异常没有出现，就将`-p`改回1000并设定`-k 500`跳过前半段数据包运行。重复这一过程，不超过10步就可以找到造成问题的单个
IP数据包。

### 工具扩展

未来如果有需求且有开源开发者愿意贡献，可以考虑加入以下功能扩展：

* 新的选项指定isic或isic6报文首部IP协议号 (建议为`-P`)
* 开发前端图形用户界面 (GUI)，参考[Zenmap](https://nmap.org/zenmap/)
* 支持多协议标签交换 (MPLS) 的帧格式
* 支持因特网组管理协议 (IGMP) 的报文
* 支持IEEE 802.1Q以及虚拟局域网标签 (VLAN Tagging) 的帧格式
* 支持调试打印输出的详细程度 (verbosity) 分级
* 支持加载预先捕获的[pcap格式](https://gitlab.com/wireshark/wireshark/-/wikis/Development/LibpcapFileFormat)的网络数据包文件
* 与其它的测试工具集成为完整的网络安全测试方案

[^c]: 公共漏洞评分系统 (Common Vulnerability Scoring System，缩写CVSS) 是一种用于评估计算机系统安全漏洞严重性的开放行业标准。CVSS为每一个漏洞的严重性评分，分数范围是0到10，其中最严重的是10。

