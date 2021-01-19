---
title: 解析IPv4和IPv6报文首部校验和算法
date: 2020-11-24 21:59:09
categories:
- 学习体会
tags:
- TCP/IP
- C/C++编程

---


关于IP报文首部校验和(checksum)算法，简单的说就是16位累加的反码运算，但具体是如何实现的，许多资料不得其详。TCP和UDP数据报首部也使用相同的校验算法，但参与运算的数据与IP报文首部不一样。此外，IPv6对校验和的运算与IPv4又有些许不同。因此有必要对IP分组的校验和算法作全面的解析。
<!--more-->

{% note success no-icon %}
**Nothing in life is to be feared, it is only to be understood.**<br>
**— *Marie Curie*（居里夫人，波兰裔法国籍物理学家、化学家，两届诺贝尔奖得主）**
{% endnote %}

## IPv4首部校验和

IPv4报文首部的结构如下所示：

```
   0                   1                   2                   3    
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1  
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |Version|  IHL  |Type of Service|          Total Length         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |         Identification        |Flags|      Fragment Offset    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Time to Live |    Protocol   |        Header Checksum        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                       Source Address                          |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Destination Address                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

其中的`Header Checksum`域即为首部校验和部分。当要计算IPv4报文首部校验和时，发送方先将其置为全0，然后按16位逐一累加至IPv4报文首部结束，累加和保存于一个32位的数值中。如果总的字节数为奇数，则最后一个字节单独相加。累加完毕将结果中高16位再加到低16位上，重复这一过程直到高16位为全0。最后将结果取反存入首部校验和域。

下面用实际截获的IPv4分组来演示整个计算过程：

```
0x0000: 00 60 47 41 11 c9 00 09 6b 7a 5b 3b 08 00 45 00 
0x0010: 00 1c 74 68 00 00 80 11 59 8f c0 a8 64 01 ab 46 
0x0020: 9c e9 0f 3a 04 05 00 08 7f c5 00 00 00 00 00 00 
0x0030: 00 00 00 00 00 00 00 00 00 00 00 00
```

在上面的16进制采样中，起始为以太网 (Ethernet) 帧的开头。IPv4报文首部从地址偏移量0x000e开始，第一个字节为0x45，最后一个字节为0xe9。根据以上的算法描述，我们可以作如下计算：

```
(1) 0x4500 + 0x001c + 0x7468 + 0x0000 + 0x8011 +
    0x0000 + 0xc0a8 + 0x6401 + 0xab46 + 0x9ce9 = 0x3a66d
(2) 0xa66d + 0x3 = 0xa670
(3) 0xffff - 0xa670 = 0x598f
```

注意在第一步我们用<u>0x0000</u>设置首部校验和部分。可以看出这一报文首部的校验和与收到的值完全一致。以上的过程仅用于发送方计算初始的校验和，实际中对于中间转发的路由器和最终接收方，可将收到的IPv4报文首部校验和部分直接按同样算法相加，如果结果为<u>0xffff</u>，则校验正确。

## C语言实现

如何编程计算 IPv4 首部校验和？[RFC 1071](https://tools.ietf.org/html/rfc1071) (Computing the Internet Checksum) 给出了一个C语言的参考实现，如下所示：

```c
   {
       /* Compute Internet Checksum for "count" bytes
        * beginning at location "addr".
        */
       register long sum = 0;

       while( count > 1 )  {
           /* This is the inner loop */
           sum += * (unsigned short *) addr++;
           count -= 2;
       }

       /*  Add left-over byte, if any */
       if ( count > 0 )
           sum += * (unsigned char *) addr;

       /*  Fold 32-bit sum to 16 bits */
       while (sum>>16)
           sum = (sum & 0xffff) + (sum >> 16);

       checksum = ~sum;
   }
```

在实际的网络连接中，源点设备可以调用以上代码产生初始IPv4报文首部校验和。而后在每一步的路由跳转中，因为路由器必须递减首部存活时间 (Time To Live，简写TTL) 字段，所以要更新首部校验和。[RFC 1141](https://tools.ietf.org/html/rfc1141) (Incremental Updating of the Internet Checksum) 给出了快速更新校验和的参考实现：

```c
      unsigned long sum;
      ipptr->ttl--;                  /* decrement ttl */
      sum = ipptr->Checksum + 0x100; /* increment checksum high byte*/
      ipptr->Checksum = (sum + (sum>>16)); /* add carry */
```


## TCP/UDP首部校验和

对于TCP和UDP的数据报，其首部也包含16位的校验和，由目的地接收端验证。校验算法与IPv4报文首部完全一致，但参与校验的数据不同。这时校验和不仅包含整个TCP/UDP数据报，还覆盖了一个伪首部。IPv4伪首部的定义如下：

```
                  0      7 8     15 16    23 24    31 
                 +--------+--------+--------+--------+
                 |          source address           |
                 +--------+--------+--------+--------+
                 |        destination address        |
                 +--------+--------+--------+--------+
                 |  zero  |protocol| TCP/UDP length  |
                 +--------+--------+--------+--------+
```
其中有IP源地址，IP目的地址，协议号(TCP:6/UDP:17)及TCP或UDP数据报的总长度(首部+数据)。将伪首部加入校验的目的，是为了再次核对数据报是否到达正确的目的地，并防止IP欺骗攻击 (spoofing)。另外对于IPv4，UDP首部校验和是可选的，不用时该字段应被填充为全0。

## IPv6的不同

IPv6是网际协议第6版，其设计的主要目的是为了解决IPv4地址枯竭问题，当然它在其他方面也有许多改进。虽然IPv6的使用量增长缓慢，但是其趋势不可阻挡。IPv6的最新互联网标准由[RFC 8200](https://tools.ietf.org/html/rfc8200) (Internet Protocol, Version 6 (IPv6) Specification)规范。IPv6报文首部的结构如下所示：

```
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |Version| Traffic Class |           Flow Label                  |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |         Payload Length        |  Next Header  |   Hop Limit   |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                                                               |
   +                                                               +
   |                                                               |
   +                         Source Address                        +
   |                                                               |
   +                                                               +
   |                                                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                                                               |
   +                                                               +
   |                                                               |
   +                      Destination Address                      +
   |                                                               |
   +                                                               +
   |                                                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

注意到IPv6首部并没有包含校验和字段，这也是与IPv4的一个显著不同点。IPv6协议的设计延展了互联网设计端到端原则，取消首部校验和字段简化了路由器的处理过程，加快了IPv6报文网络传输。对报文数据完整度的保护可由链路层或端点间高层协议（TCP/UDP）的差错检测功能完成。这也是为什么IPv6强制要求UDP层设定首部校验和字段的原因。

对于IPv6数据报TCP/UDP首部校验和的计算，其IPv6伪首部的定义如下：

```
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                                                               |
   +                                                               +
   |                                                               |
   +                         Source Address                        +
   |                                                               |
   +                                                               +
   |                                                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                                                               |
   +                                                               +
   |                                                               |
   +                      Destination Address                      +
   |                                                               |
   +                                                               +
   |                                                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                   Upper-Layer Packet Length                   |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                      zero                     |  Next Header  |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

## UDP-Lite应用

在实际的IPv6网络应用中，为了兼顾差错检测和传输效率，可以采用UDP-Lite（Lightweight UDP，轻量用户数据报协议）。UDP-Lite有自己的IP协议号136，其规范定义于 [RFC 3828](https://tools.ietf.org/html/rfc8200) (The Lightweight User Datagram Protocol (UDP-Lite))。参考以下的UDP-Lite首部格式，它使用与UDP相同的[端口分配](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)，但是它将原来UDP首部的“长度”字段重定义为“校验和覆盖”（Checksum Coverage）域，这样就可以允许应用层自行控制需要计算校验和的数据长度，从而容许没被覆盖的数据部分可能有损地传输。

```
       0              15 16             31
      +--------+--------+--------+--------+
      |     Source      |   Destination   |
      |      Port       |      Port       |
      +--------+--------+--------+--------+
      |    Checksum     |                 |
      |    Coverage     |    Checksum     |
      +--------+--------+--------+--------+
      |                                   |
      :              Payload              :
      |                                   |
      +-----------------------------------+
```

UDP-Lite协议规定了“校验和覆盖”域的取值（以8位组为单位）：

| 校验和覆盖值  | 校验和覆盖区域  | 说明 |
|:-------------: |:---------------:|:-------------:|
| 0      | 整个UDP-Lites数据报 |        计算要包括IP伪首部 |
| 1-7 |      （无效值）   | 接收方必须抛弃数据报 |
| 8 | UDP-Lites首部       |      计算要包括IP伪首部 | ](https://theme-next.js.org/docs/getting-started/)
| > 8 | UDP-Lites 首部 + 部分负载数据 (payload)      |      计算要包括IP伪首部 | 
| > IP 数据报长度 |  （无效值）|  接收方必须抛弃数据报


对于多媒体应用，采用VoIP或流视频数据传输协议，接收有一定程度损坏的数据比没接收到任何数据要好。另一个实例，是思科（Cisco）的无线局域网控制器和无线接入点之间的连接所基于的 [CAPWAP](https://tools.ietf.org/html/rfc5415) 协议规范，它就规定了当连接建立于IPv6网络之上时，其数据通道缺省使用校验和覆盖值为8的UDP-Lite协议。

最后，分享一小段C程序，示例如何初始化Berkeley套接字 (socket) 以建立 IPv6 UDP-Lite 连接：

``` c
#include <sys/socket.h>
#include <netinet/in.h>
#include <net/udplite.h>

int udplite_conn = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDPLITE);
int val = 8;    /* 校验和只覆盖8字节的UDP-Lite首部 */
(void)setsockopt(udplite_conn, IPPROTO_UDPLITE, UDPLITE_SEND_CSCOV, &val, sizeof val);
(void)setsockopt(udplite_conn, IPPROTO_UDPLITE, UDPLITE_RECV_CSCOV, &val, sizeof val);
```

这里 `IPPROTO_UDPLITE` 为协议号136，用它和`AF_INET6`地址集参数一起调用`socket()`函数来创建 IPv6 套接字。`UDPLITE_SEND_CSCOV`(10) 和 `UDPLITE_RECV_CSCOV`(11) 为套接字选项设置函数`setsockopt()`的控制参数，分别用来指定发送和接受时的校验和覆盖值。注意收发双方必须设置同样的数值，否则接受方无法正确验证校验和。


