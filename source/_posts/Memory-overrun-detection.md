---
title: C编程实现带有越界检查的内存管理函数
categories:
  - 技术小札
tags:
  - C/C++编程
  - 系统编程

date: 2021-03-28 12:25:16
---

C语言具有高效、灵活、功能丰富和可移植性强等特点，在程序设计尤其是系统软件开发中备受青睐。它的高效灵活性很大程度上得益于其通过指针对存储器进行低端控制的功能，但代价是程序员必须格外谨慎处理内存的访问细节，避免内存泄漏和缓冲区溢出等运行错误。<!--more-->

{% note success no-icon %}
**Writing in C or C++ is like running a chain saw with all the safety guards removed. It’s powerful, but it’s easy to cut off your fingers.**<br>
**— *Bob Gray*（senior director of consulting firm Virtual Solutions, cited in Byte (1998) Vol 23, Nr 1-4. p . 70.  ）**
{% endnote %}

为了克服C语言程序设计的这一弱点，研发人员开发了许多运行期内存调试工具，以便快速检测内存泄漏及实时定位缓冲区溢出错误。知名的开源免费内存调试器有[Valgrind](https://www.valgrind.org)、[dmalloc](https://dmalloc.com)和[AddressSanitizer](https://en.wikipedia.org/wiki/AddressSanitizer)等。内存调试工具的一个通用的设计思想是，在分配内存时预留一些存储空间保存相关信息，然后在运行期和内存释放时利用这些信息做状态检查。

特别地，如果内存分配函数在返回给调用者使用的内存区域前后保留一些存储块，填入固定的字节序列作为边界标识符，那么就可以在后续程序运行时实时查验，看看前后边界标识符是否被改动。如果是，就说明出现了缓冲区溢出错误，马上报告内存使用存在问题。这些保留的存储块也被称为红区（redzone），言下之意当内存访问越界时，好比程序运行踩了红线，应当告警。

### 程序目标

出于学习的目的，这里演示用C语言编程实现的、支持越界检查功能的内存管理函数。 程序到达成的目标是：

* 编写自己的内存分配和释放函数，内部封装标准库函数`malloc()/free()`
* 分配内存时，在返回的内存区域首尾各添加4字节的红区
	* 首端（header）写入`0x0D0C0B0A`
	* 尾部（footer）写入`0x12345678`
* 写一个审查函数，对给定的内存分配地址进行核对，出错则告警
* 释放内存时，再检查红区是否被修改，如是则告警
* 编写测试代码验证以上内存管理函数完成所设计的功能

### 设计实现

下面来讲叙程序的实现细节。首先，我们了解标准库函数`malloc()`返回所分配的内存地址，内存区域大小由输入参数`size`决定：

``` c
void *malloc(size_t size);
```
考虑到首尾各4字节的红区，显然新的内存分配函数必须请求额外的8个字节的内存。但这还不够，要检查尾部红区，审查函数必须知道所分配内存的大小，不然无法定位尾部。所以还要再多分配4个字节，保存内存区域大小`size`。由此，整个内存分配的结构如下图所示：

![](memcheck.jpg)

所以实际需要传递给标准库函数`malloc()`的内存大小值，是申请的内存量加上12。而新的内存分配函数返回的可用内存地址，是`malloc()`返回的指针加地址偏移量8。掌握这些关键细节之后，新的内存分配函数的实现就呼之欲出了：

``` c
/* redzone patterns */
unsigned int header = 0x0D0C0B0A;
unsigned int footer = 0x12345678;

void* my_malloc(size_t sz)
{
    void *p = malloc (4 + 4 + sz + 4);
    *(unsigned int *)p = header;
    *(unsigned int *)(p+4) = sz;
    *(unsigned int*) (p+8+sz) = footer;
    return p + 8;
}
```
相应的内存审查和释放函数的实现也就简单了。内存审查函数可以调用断言`assert()`库函数，确认可用内存大小值和首尾红区字节序列没有被更改。释放内存时做同样的检查，没有差错后再释放。这两个函数的实现如下：

``` c
void my_check(void *p, size_t size)
{
    assert(*(unsigned int*)(p-8) == header);
    assert(*(unsigned int*)(p-4)== size);
    assert(*(unsigned int *)(p+size) == footer);
}

void my_free(void *p)
{
    void *real_p = p - 8;
    assert(*(unsigned int*)real_p == header);
    unsigned int *size = real_p + 4;
    assert(*(unsigned int*)(real_p+8+*size)==footer);
    free(real_p);
}
```
接下来就是写测试代码。软件调试和测试时，常常需要以16进制格式打印存储区域的内容，下面的`my_hexdump()`提供了此项辅助功能（宏`HDMP_COLS`定义了每行打印16个字节）：

``` c
#ifndef HDMP_COLS
#define HDMP_COLS 16
#endif

void my_hexdump(void *mem, unsigned int len)
{
    unsigned int i, j, extra;
    extra = (len % HDMP_COLS) ? (HDMP_COLS - len % HDMP_COLS) : 0;
    
    for (i = 0; i < len + extra; i++) {
        if (i % HDMP_COLS == 0) {
            /* print address */
            printf("\n%p: ", mem + i); 
        }   
 
        if (i < len) {
            /* print hex data */
            printf("%02x ", 0xFF & ((char*)mem)[i]);
        } else {
            /* print 3 space chars for alignment */
            printf("   ");
        }   

        if (i % HDMP_COLS == (HDMP_COLS - 1)) {
            /* print ASCII dump */
            for (j = i - (HDMP_COLS - 1); j <= i; j++) {
                if (j >= len) {
                    /* end of block */
                    printf("\n\n");
                    return;
                } else if (isprint(((char*)mem)[j])) {
                    /* printable char */
                    putchar(0xFF & ((char*)mem)[j]);
                } else {
                    /* other char, print '.' instead */
                    putchar('.');
                }   
            }   
        }   
    }   
}
```

下面代码段显示，主函数先对新的内存管理函数进行正面测试，即没有越界写操作，不会出现断言错误：

``` c
int main()
{
    int size = 32;
    void *ptr = my_malloc(size);
    printf( "Usable memory start at %p\n", ptr);
    my_hexdump(ptr - 8, size + 12);
    my_check(ptr, size);
    my_free(ptr);
    printf("Basic test passed!\n");
    
    strcpy_test();
}
```
而最后一行，主函数调用`strcpy_test()`（实现代码如下）。这是一个负面测试函数。它使用不安全的字符串复制库函数`strcpy()`，复制一个12个字符的字符串到动态分配的缓冲区中，缓冲区的大小也是12个字节。但是，因为`strcpy()`会连带复制字符串结尾的终止符 ('\0')，就产生了缓冲区溢出错误。所以，如果新的带有越界检查的释放函数`my_free()`功能运行正确，我们将会看到程序在此出现断言错误。

``` c
void strcpy_test(void)
{
    char *msg = "Hello world!";
    int mlen = strlen(msg);
    char *buffer = my_malloc(mlen);
    strcpy(buffer, msg);
    printf("%s\n", buffer);
    my_hexdump(buffer-8, mlen+12);
    my_free(buffer);
}
```

### 编译运行

在红帽企业Linux 8.1的系统环境下，使用GCC 8.3.1编译链接程序及最后的运行结果是：

``` bash
> gcc -v
Using built-in specs.
COLLECT_GCC=gcc
COLLECT_LTO_WRAPPER=/usr/libexec/gcc/x86_64-redhat-linux/8/lto-wrapper
OFFLOAD_TARGET_NAMES=nvptx-none
OFFLOAD_TARGET_DEFAULT=1
Target: x86_64-redhat-linux
Configured with: ../configure --enable-bootstrap --enable-languages=c,c++,fortran,lto --prefix=/usr --mandir=/usr/share/man --infodir=/usr/share/info --with-bugurl=http://bugzilla.redhat.com/bugzilla --enable-shared --enable-threads=posix --enable-checking=release --enable-multilib --with-system-zlib --enable-__cxa_atexit --disable-libunwind-exceptions --enable-gnu-unique-object --enable-linker-build-id --with-gcc-major-version-only --with-linker-hash-style=gnu --enable-plugin --enable-initfini-array --with-isl --disable-libmpx --enable-offload-targets=nvptx-none --without-cuda-driver --enable-gnu-indirect-function --enable-cet --with-tune=generic --with-arch_32=x86-64 --build=x86_64-redhat-linux
Thread model: posix
gcc version 8.3.1 20190507 (Red Hat 8.3.1-4) (GCC) 
>
> gcc -o memcheck memcheck.c
> 
> memcheck
Usable memory start at 0x1823268

0x1823260: 0a 0b 0c 0d 20 00 00 00 00 00 00 00 00 00 00 00 .... ...........
0x1823270: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................
0x1823280: 00 00 00 00 00 00 00 00 78 56 34 12             ........xV4.

Basic test passed!
Hello world!

0x18236b0: 0a 0b 0c 0d 0c 00 00 00 48 65 6c 6c 6f 20 77 6f ........Hello wo
0x18236c0: 72 6c 64 21 00 56 34 12                         rld!.V4.

memcheck: memcheck.c:86: my_free: Assertion `*(unsigned int*)(real_p+8+*size)==footer' failed.
Abort
```

可以看到，输出的`Basic test passed!`表明正面测试通过，之前打印出的存储区域也显示正确的红区字节序列和可用内存区大小值0x20。注意，该主机系统是`Little Endian`的，所以红区字节序列与程序中定义的次序正好相反。最后是负面测试用例的输出结果，可以看到，使用`strcpy()`造成了缓冲区溢出，将尾部红区的第一个字节0x78更改为0x00，这一错误被释放函数`my_free()`抓到了，程序在执行尾部字节序列查验时断言出错，提前退出了（Abort）。

总结一下，我们这里学习并编程实践了一种基本的内存越界检查方法。虽然其工作原理很简单，但这是理解和应用更高级内存调试工具的基础。类似问题也许会出现在程序员面试中，充分掌握了上述所有内容，你就可以做出准确无误的回答。

完整的程序可点击这里下载：[memcheck.c.gz](memcheck.c.gz)