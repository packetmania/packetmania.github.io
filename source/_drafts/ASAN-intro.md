---
title: AddressSanitizer — C/C++程序员检测内存访问错误的利器
categories:
  - 工具使用
tags:
  - C/C++编程
  - 系统编程

---


<!--more-->

{% note success no-icon %}
**One man's "magic" is another man's engineering. "Supernatural" is a null word.  罗伯特·安森·海因莱因 美国硬科幻小说作家，人称“科幻先生”**<br>
**— *Robert Anson Heinlein*（罗伯特·安森·海因莱因，美国硬科幻小说作家，人称“科幻先生”）**
{% endnote %}

* Use after free (dangling pointer dereference)
* Heap buffer overflow
* Stack buffer overflow
* Global buffer overflow
* Use after return
* Use after scope
* Initialization order bugs

### 工作原理

It consists of two modules:

* A compiler instrumentation module.
* A run-time library that replaces malloc/free.


### 源码分析



### 应用示例


### 参考资料

Konstantin Serebryany; Derek Bruening; Alexander Potapenko; Dmitry Vyukov. "[*AddressSanitizer: a fast address sanity checker*](https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf)". Proceedings of the 2012 USENIX conference on Annual Technical Conference.

[Clang 13 documentation: ADDRESSSANITIZER](https://clang.llvm.org/docs/AddressSanitizer.html)

[AddressSanitizer Wiki](https://github.com/google/sanitizers/wiki/AddressSanitizer)
