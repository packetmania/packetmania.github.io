---
title: Endianness一点通
date: 2020-11-24 21:58:43
categories:
- 技术小札
tags:
- 计算机体系结构
- 网络通信
- 系统编程
- C/C++编程

---

Endianness 的问题实质就是关于计算机如何存储大的数值的问题。
<!--more-->

{% note success no-icon %}
**I do not fear computers. I fear lack of them.**<br>
**— *Isaac Asimov*（艾萨克·阿西莫夫，美籍犹太裔生化学家、科幻和科普作家）**
{% endnote %}

我们知道一个基本存储单元可以保存一个字节，每个存储单元对应一个地址。对于大于十进制 255（16进制 0xff）的整数，需要多个存储单元。例如，4660 对应于 0x1234，需要两个字节。不同的计算机系统使用不同的方法保存这两个字节。在我们常用的 PC 机中，低位的字节 0x34 保存在低地址的存储单元，高位的字节 0x12 保存在高地址的存储单元；而在 Sun 工作站中，情况恰恰相反，0x34 位于高地址的存储单元，0x12 位于低地址的存储单元。前一种就被称为`Little Endian`，后一种就是`Big Endian`。
  
如何记住这两种存储模式？其实很简单。首先记住我们所说的存储单元的地址总是由低到高排列。对于多字节的数值，如果先见到的是低位的字节，则系统就是`Little Endian`的，Little 就是"小，少"的意思，也就对应"低"。相反就是`Big Endian`，这里 Big "大"对应"高"。

## 程序实例

为了加深对 Endianness 的理解，让我们来看下面的C程序例子：

```c
 char a = 1; 	 	 	 
 char b = 2;                       
 short c = 255;	/* 0x00ff */
 long d = 0x44332211;
```

在基于Intel 80x86的系统上, 变量a，b，c，d对应的内存映像如下表所示：

地址偏移量      | 内存映像
------------- | -------------
0x0000        | 01 02 FF 00
0x0004        | 11 22 33 44

显然我们可以马上判定这一系统是`Little Endian`的。对于16位的整形数`short c`，我们先见到其低位的0xff，下一个才是 0x00。同样对于32位长整形数`long d`，在最低的地址 0x0004 存的是最低位字节 0x11。如果是在`Big Endian`的计算机中，则地址偏移量从 0x0000 到 0x0007 的整个内存映像将为：*01 02 00 FF 44 33 22 11*。

所有计算机处理器都必须在这两种 Endian 间作出选择。但某些处理器(如 ARM, MIPS 和 IA-64)支持两种模式，可由编程者通过软件或硬件设置一种 Endian。以下是一个处理器类型与对应的 Endian 的简表：

*  纯`Big Endian`: Sun SPARC, Motorola 68000，Java 虚拟机 
*  Bi-Endian, 运行`Big Endian`模式: MIPS 运行 IRIX, PA-RISC，大多数 Power 和 PowerPC 系统 
*  Bi-Endian, 运行`Little Endian`模式: ARM, MIPS 运行 Ultrix，大多数 DEC Alpha, IA-64 运行 Linux 
*  `Little Endian`: Intel x86，AMD64，DEC VAX

如何在程序中检测本系统的 Endianess？可调用下面的函数来快速验证，如果返回值为1，则为`Little Endian`；为0则是`Big Endian`：

```c
int test_endian() {
    int x = 1;
    return *((char *)&x);
}
```

## 网络序

Endianness 对于网络通信也很重要。试想当`Little Endian`系统与`Big Endian`的系统通信时，如果不做适当处理，接收方与发送方对数据的解释将完全不一样。比如对以上 C 程序段中的变量d，`Little Endian`发送方发出 *11 22 33 44* 四个字节，`Big Endian`接收方将其转换为数值 0x11223344。这与原始的数值大相径庭。为了解决这个问题，TCP/IP 协议规定了专门的“网络字节次序”(简称“网络序”），即无论计算机系统支持何种 Endian，在传输数据时，总是数值最高位的字节最先发送。从定义可以看出，网络序其实是对应`Big Endian`的。

为了避免因为 Endianness 造成的通信问题，及便于软件开发者编写易于平台移植的程序，特别定义了一些C语言预处理的宏来实现网络字节与本机字节次序之间的相互转换。`htons()`和`htonl()`用来将本机字节次序转成网络字节次序，前者应用于16位无符号数，后者应用于32位无符号数。`ntohs()`和`ntohl()`实现反方向的转换。这四个宏的原型定义可参考如下(Linux 系统中可在`netinet/in.h`文件里找到)：


``` c
#if defined(BIG_ENDIAN) && !defined(LITTLE_ENDIAN)

#define htons(A)  (A)
#define htonl(A)  (A)
#define ntohs(A)  (A)
#define ntohl(A)  (A)

#elif defined(LITTLE_ENDIAN) && !defined(BIG_ENDIAN)

#define htons(A)  ((((uint16)(A) & 0xff00) >> 8) | \
                   (((uint16)(A) & 0x00ff) << 8))
#define htonl(A)  ((((uint32)(A) & 0xff000000) >> 24) | \
                   (((uint32)(A) & 0x00ff0000) >> 8)  | \
                   (((uint32)(A) & 0x0000ff00) << 8)  | \
                   (((uint32)(A) & 0x000000ff) << 24))
#define ntohs     htons
#define ntohl     htohl

#else

#error "Either BIG_ENDIAN or LITTLE_ENDIAN must be #defined, but not both."

#endif
```

