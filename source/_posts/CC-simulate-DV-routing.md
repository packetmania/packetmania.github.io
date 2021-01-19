---
title: C++编程实现的距离矢量路由协议仿真程序
date: 2020-11-25 21:16:24
categories:
- 技术小札
tags:
- C/C++编程
- 路由与交换
mathjax: true

---

距离矢量 (Distance-vector) 和链路状态 (Link-state) 是路由协议的两大分类。距离矢量路由协议在互联网早期得到广泛应用，之后一些协议实现逐渐演变成为标准化的“[路由信息协议](https://tools.ietf.org/html/rfc2453)” (Routing Information Protocol，缩写 RIP)。由于其简单和实用性，RIP 现今仍旧是小型网络配置的首选。

<!--more-->

许多年以前，笔者在南加州大学 (University of Southern California，缩写USC) 攻读计算机工程硕士学位时，选修了编号*CS551: Computer Communication* 的课程。这是一门面向研究生的计算机网络通信课程，非常受到学生欢迎[^CS551]。但是CS551也以其难度较大的软件课件项目而著称，让不少缺乏编程经验的非EE/CS专业的学生望而却步。笔者那一学期的两个项目，第一个就是用C/C++编程实现距离矢量路由协议的仿真。完成这一课件作业，的确让自己增长了不少网络编程的经验，也加深了对距离矢量路由协议的理解。现在总结共享出来，希望对其他人有所帮助。


{% note success no-icon %}
**Mathematicians makes natural questions precise.**<br>
**— *Richard Bellman*（理查德·贝尔曼，美国应用数学家，动态规划的创始人）**
{% endnote %}

### 路由算法

距离矢量路由协议的核心是贝尔曼-福特算法 (Bellman–Ford algorithm)，以美国两位数学家理查德·贝尔曼(Richard Bellman) 和小莱斯特·福特 (Lester Ford Jr.) 命名。贝尔曼1958年发布最短路径路由算法的论文，而福特与另一位美国数学家德尔伯特·富尔克森 (Delbert Fulkerson) 先于1956年在他们的网络流著作中提出了计算最大流通量的分布式贪心算法。二者相结合就产生了距离矢量路由协议，用于计算网络的最佳路由。全球互联网的鼻祖ARPANET就是使用的距离矢量路由协议。

先来看看这一算法是如何工作的。对于给定的网络拓扑图及其顶点集合 $V$ 和带权重的边集合 $E$，目的是要求得从每一个顶点到其它顶点的最短路径。贝尔曼-福特算法以松弛操作为基础，先预估到其它顶点的路径最大值，然后逐次计算出更加准确的最短路径值替换原来的估计值，重复迭代最终得到最优解。算法的伪代码描述如下：

``` pascal
procedure BellmanFord(list vertices, list edges, vertex source)
    // 输入由n个顶点(vertice)和边(edge)的列表构成的图，执行算法找到从源点到
    // 其它顶点的最短路径，保存到距离(distance)和前向顶点(predecessor)数组
    distance := list of size n
    predecessor := list of size n

    // 第一步：初始化图
    for each vertex v in vertices:
        distance[v] := infinity
        predecessor[v] := null
        
    distance[source] := 0 // 源点到自身的距离为0

   // 第二步：重复松弛操作
   for i from 1 to size(vertices)-1:
       for each edge (u, v) with weight w in edges:
           if distance[u] + w < distance[v]:
               distance[v] := distance[u] + w
               predecessor[v] := u

   // 第三步：检查是否有负权重的回路
   for each edge (u, v) with weight w in edges:
       if distance[u] + w < distance[v]:
           error "图包含负权重的回路"
           
   return distance, predecessor
```
在以上的算法描述中，松弛操作循环每次都是作用于所有边，重复次数实际上对应所得到的最短路径的深度。以 $|V|$ 和 $|E|$ 分别代表节点和边的数量，则贝尔曼-福特算法的时间复杂度可以表示为 $O(|V|\cdot|E|)$。另外还注意到，算法的基本操作实质上是在广度上探寻，所以负权重的边不会影响运算结果。

那么距离矢量在哪里？其实对于计算机网络这样的分布式系统，每个网络节点 (就是图中的顶点) 最初只有与自己相邻节点的距离 (就是图中边的权重) 信息。所以要执行贝尔曼-福特算法，节点就必须向其邻接点发送路由信息，这样邻接点才能实现松弛操作运算。路由信息包括**本节点到达所有其它节点的最短路径值序列，也就是距离矢量**。每当节点收到邻接点发来距离矢量，就执行一轮松弛操作运算。如果运算结果产生了新的最短距离，就更新路由表并发出新的距离矢量给所有邻接点。如此往复，直到收敛得到最短距离，算法结束。

下面以一个6节点的网络来说明距离矢量路由协议的执行细节：

{% mermaid graph LR %}

subgraph 网络拓扑图
    G((A)) --- |1| H((B))
    G((A)) --- |4| I((C))
    G((A)) --- |6| J((D))
    H --- |1| I
    I --- |1| J
    J --- |1| K((E))
    I --- |1| K
    K --- |1| L((F))
    I --- |4| L
    H --- |5| L
end

{% endmermaid %}

上图由6个节点 $A-F$ 和 $10$ 条链路构成网络连接拓扑。每个节点的距离矢量组合成一个 $6\times6$ 距离矩阵。如下第一个表 (Init) 所示，链路的权重值确定了距离矩阵的初始化状态。矩阵是沿着左上到右下对角线对称的，对角线上的元素代表源点到自身的距离，所以全为0。第一行元素为节点 $A$ 到其它节点的距离，即它的距离矢量。因为 $A$只与 $B/C/D$ 相邻，距离为 $1/4/6$。$A$ 到 $E/F$ 的距离初始设置为无穷大。

$$
% outer vertical array of arrays
\begin{array}{c}
% inner horizontal array of arrays
\begin{array}{cc}
% inner array of minimum values
\begin{array}{c|ccccc}
\text{Init} & A & B & C & D & E & F\\
\hline
A & 0 & 1 & 4 & 6 & \infty & \infty\\
B & 1 & 0 & 1 & \infty & \infty & 5\\
C & 4 & 1 & 0 & 1 & 1 & 4\\
D & 6 & \infty & 1 & 0 & 1 & \infty\\
E & \infty & \infty & 1 & 1 & 0 & 1\\
F & \infty & 5 & 4 & \infty & 1 & 0
\end{array}
&
&
&
% inner array of maximum values
\begin{array}{c|ccccc}
\text{No.1} & A & B & C & D & E & F\\
\hline
A & 0 & 1 & \color{fuchsia}{2} & \color{fuchsia}{5} & \color{fuchsia}{5} & \color{fuchsia}{6}\\
B & 1 & 0 & 1 & \color{fuchsia}{2}  & \color{fuchsia}{2} & 5\\
C & \color{fuchsia}{2}  & 1 & 0 & 1 & 1 & \color{fuchsia}{2}\\
D & \color{fuchsia}{5}  & \color{fuchsia}{2}  & 1 & 0 & 1 & \color{fuchsia}{2} \\
E & \color{fuchsia}{5} & \color{fuchsia}{2} & 1 & 1 & 0 & 1\\
F & \color{fuchsia}{6} & 5 & \color{fuchsia}{2}  & \color{fuchsia}{2}  & 1 & 0
\end{array}
\end{array}
\\[2ex]
\\
% inner horizontal array of arrays
\begin{array}{cc}
% inner array of minimum values
\begin{array}{c|ccccc}
\text{No.2} & A & B & C & D & E & F\\
\hline
A & 0 & 1 & 2 & \color{fuchsia}{3} & \color{fuchsia}{3} & 6 \\
B & 1 & 0 & 1 & 2  & 2 & \color{fuchsia}{3}\\
C & 2 & 1 & 0 & 1 & 1 & 2\\
D & \color{fuchsia}{3}  & 2 & 1 & 0 & 1 & 2\\
E & \color{fuchsia}{3} & 2 & 1 & 1 & 0 & 1\\
F & 6 & \color{fuchsia}{3} & 2 & 2 & 1 & 0
\end{array}
&
&
&
% inner array of maximum values
\begin{array}{c|ccccc}
\text{No.3} & A & B & C & D & E & F\\
\hline
A & 0 & 1 & 2 & 3 & 3 & \color{fuchsia}{4}\\
B & 1 & 0 & 1 & 2  & 2 & 3\\
C & 2 & 1 & 0 & 1 & 1 & 2 \\
D & 3 & 2 & 1 & 0 & 1 & 2\\
E & 3 & 2 & 1 & 1 & 0 & 1\\
F & \color{fuchsia}{4} & 3 & 2 & 2 & 1 & 0
\end{array}
\end{array}
\end{array}
$$

接下来第一轮路由信息交换，$A$ 收到 $B$ 的距离矢量。$B$ 到 $C/F$ 的距离为 $1/5$，$A$ 执行松弛操作运算，得到新的距离值 $2/6$。这小于 $A$ 当前到 $C/F$ 的距离 $4/\infty$，所以 $A$ 更新它的距离矢量。同理，$A$ 在处理完收到的 $C$ 的距离矢量之后，将它到 $D/E$ 的最短距离更新为 $5/5$。这就是以上表No.1里第一行颜色高亮所示的变化。第一轮里其它节点也同时执行松弛操作运算，其距离矢量的变化也由颜色高亮显示。

重复这一过程，每一轮的最短距离变化都由颜色高亮显示。至第三轮(No.3)结束，距离矩阵不再变化，算法收敛完毕。最后生成的最短路径如下图中的粗实线所示：

{% mermaid graph LR %}

subgraph 最短路径图
    A((A)) === |1| B((B))
    A((A)) --- |4| C((C))
    A((A)) --- |6| D((D))
    B === |1| C
    C === |1| D
    D === |1| E((E))
    C === |1| E
    E === |1| F((F))
    C --- |4| F
    B --- |5| F
end

{% endmermaid %}

这时节点 $A$ 的路由表如下：

| 目的节点 | 下一跳 | 链路开销 | 路径 |
|:-:|:-:|:-:|:----:|
| B | B | 1 | A-B |
| C | B | 2 | A-B-C |
| D | B | 3 | A-B-C-D |
| E | B | 3 | A-B-C-E |
| F | B | 4 | A-B-C-E-F |

### 算法改进

贝尔曼-福特算法本身是无瑕的，应用于距离矢量路由协议也发挥了有效的路由功能。然而，在现实的网络部署中，由于系统的动态和分布式特质，距离矢量路由协议在实际运行中暴露出来了一些问题。下面对两个突出的问题做一些简单讨论：

* **反弹效应**：参考下图的4节点网络，最短路径为A-B-C-D。现在C和D之间的链路突然中断，C马上检测到这一故障，并把到D的距离改为无穷大。但是在C发出新的距离矢量之前，先收到来自B的距离矢量。这是很常见的，因为许多协议实现规定周期性的发送距离矢量报文，以防丢失。由于B的距离矢量里到D的距离为2，所以C将到D的距离更新为3，并把B设为到D的下一跳。然后C又发出路由更新到B。B随之更新到D的距离为4，并依然将C设为下一跳。这就形成了一个循环，A/B/C所有到D的数据包将在B和C间反复传输，直至“存活时间” (TTL) 超时而被抛弃。这就是“反弹效应”。只有当B计算出通过C到达D的距离大于7时，B才将Dz直接设为下一跳，循环中止。

{% mermaid graph LR %}

subgraph 反弹效应
    E((A)) --- |1| F((B))
    F --- |1| G((C))
    F --- |7| H((D))
    G -.- |1| H
end

{% endmermaid %}

* **计数到无穷大**：同样的4节点网络，假定现在B到C和D之间的链路同时中断了，网络被完全分隔成两个独立子网A/B及C/D。当反弹效应产生时，因为不存在到达另一个子网中任何节点的真正可达路径，每个子网里的循环都不会中止。由于无法收敛，在A和B的路由表里到C和D距离会一直增大下去。C和D之间也可能出现类似的现象，它们到A和B距离会一直循环往复增大。这种过程被称为“计数到无穷大”。当出现这一情况时，网路数据传输处于极度混乱状态，大量数据包被循环发送，链路拥塞，路由更新也会因此而丢失。

{% mermaid graph LR %}

subgraph 计数到无穷大
    A((A)) --- |1| B((B))
    B -.- |1| C((C))
    B -.- |7| D((D))
    C --- |1| D
end
{% endmermaid %}

反弹效应和计数到无穷大问题，对距离矢量路由协议在实际网络中的功效带来了困扰。对此，研究人员采纳了一些技术措施来将这些不利影响降低至最小。具体应用到RIP协议中的有“水平分割” (split-horizon) 和“触发更新” (triggered-updates)等。

水平分割的思想是，如果节点A到目的地X的下一跳是节点B，那么A不应该告知B它有一条更短的路径到达X。在实现上，A可以从它发给B的距离矢量消息中拿掉到X的路由。还有一种更积极的方法，称为“毒性反转水平分割” (split-horizon with poisonous reverse)，是让A继续发出到X的路由，但是将其距离设定为无穷大。这样就可以立即消除两个节点间的循环。触发更新指定节点在察觉到链路中断时，立即发出更新消息，而不用等到下一个发送周期开始。这当然可以加快收敛速度，大幅减少路由循环的出现。

然而，即使使用毒性反转水平分割和触发更新，也不能完全消除路由循环。在以上的4节点网络中，如果A到B的连接掉线，在出现路由更新丢失或不对等时延的情况下，B/C/D仍然可能会形成B-D-C-B的三点路由循环。所以，距离矢量路由协议还是必须设置一个路径距离的上限，以及时认定计数到无穷大的发生并马上中止循环。对于以跳转次数作为距离度量的RIP协议，规定最大距离值为15，超过15即被视为不可达。

还有其他的研究者给出了不同的环路解构方案。在1989年的ACM SIGCOMM会议上，陈俊祥 (Chunhsiang Cheng) 等人[^Cheng]提出了一种**扩展的贝尔曼-福特算法**以消除环路。新算法在贝尔曼-福特算法的基础上添加了“源跟踪”功能。其设想是在路由表和路由更新里加入路径头 (head) 信息，在他们的论文中对路径头的定义是：

> The *head* of a path $R_{ij}$ is defined to be the last node preceding node j in the sequence of nodes in $R_{ij}$ (i.e., if $R_{ij}=(i,n_1,n_2,..,n_r,j)$, then head of $R_{ij}$ is $n_r$ if r > 0, and equal to i if r=0).

显然路径头就是到目的地的路径中逆向的第一个节点。如果目的地是直接相邻的节点，本地节点就是路径头。将路径头加入到路由更新里，就会在网络中随着距离矢量一直传播到所有节点。那么如何检测环路呢？论文给出名为**IN_PATH**的函数伪代码：

> **Function** IN\_PATH($Node,Neighbor,Dest$);  
(* return true or false \*)  
$\qquad$ **begin**  
$\qquad$$\qquad$ $h \gets HEAD_{Node}(Dest)$;  
$\qquad$$\qquad$ (* find head from Node to Dest \*)  
$\qquad$$\qquad$ **if** $h=Node$ **then**   
$\qquad$$\qquad$ (* Neighbor is not in $R_{NodeDest}$ \*)  
$\qquad$$\qquad$$\qquad$ **return**(false)  
$\qquad$$\qquad$ **else if** $h=Neighbor$ **then**  
$\qquad$$\qquad$ (* Neighbor is in $R_{NodeDest}$ \*)  
$\qquad$$\qquad$$\qquad$ **return**(true)  
$\qquad$$\qquad$ **else**  
$\qquad$$\qquad$$\qquad$ IN\_PATH($Node,Neighbor, HEAD_{Node}(h)$);  
$\qquad$$\qquad$$\qquad$ (* cannot determine yet,try again \*)  
$\qquad$ **end;**

当节点 (Node) 想要向邻接点 (Neighbor) 发布去往目的地 Dest 的路由消息时，就执行IN_PATH函数。函数先取出目的地的路径头节点，检查其是否为节点本身，是就返回false；否则看看其是否为邻接点，是就返回true；两者都不是，就将路径头节点作为目的地，取出新的路径头节点，递归调用函数自身。所以当函数返回true时，表明路由消息的接收者就是路径头，节点完全没有必要发布此路由。换而言之，我们检测到一个环路，此时节点应该将距离值设为无穷大。当函数返回false时，节点正常发布路由消息。

“源跟踪”算法可以更有效的解构环路，但是却增加了不少计算量，这与RIP协议简单通用和易于实现的设计原则相违背。此外，实际局域网的路由广播特性和子网聚合配置，不能保证提供和传播准确的路径头信息。所以这一类扩展的贝尔曼-福特算法并没有投入实用。然而，它却是很好的网络路由协议学习和实验素材，CS551 软件课件项目就是要求仿真实现**扩展的贝尔曼-福特算法**！


### 仿真设计

#### 项目要求和建议

以下是 CS551 任课教师 [Ramesh Govindan](https://nsl.usc.edu/people/ramesh/)[^Ramesh] 教授给出的课件项目要求和参考建议：

1. 写一个简单的**管理员**程序读入网络连接描述文件，然后生成几个子进程。每个子进程仿真一个路由器。
   * 网络连接描述文件的格式是：
	  * 第一行包含单个整数$N$，表示网络中有$N$个节点，地址从$0$到$N-1$
	  * 后面每一行描述一个网络中的点对点链路。每一行有三个空格分开的整数：$X$、$Y$和$C$。$X$和$Y$是$[0,N-1]$范围内的节点编号，$C$是一个代表$X$和$Y$之间链路开销的正整数
  * 每个路由器都开启一个UDP套接字 (socket)，用以与邻接路由器交换路由信息；在此之前，路由器必须知道其地址和邻接表信息
  * 你必须实现一个简单的协议，让管理员告知路由器这一信息。建议的方法是：
	  * 在每个路由器启动之后，建立一个TCP连接到管理员 (想想如何实现）
	  * 路由器向管理员发送消息，消息包含它的UDP端口号
	  * 管理员回复路由器的地址和邻接表信息 (使用自己定义的消息格式)

2. 在每个仿真路由器收到它的邻接表后，开始执行**扩展的贝尔曼-福特算法** (参见陈俊祥的论文)：
	* 每个路由器都需要与邻接路由器交换距离矢量信息，设计你的路由表和距离矢量消息格式
	* 你可以假定不会出现节点失误或链路断线的情况，不需要仿真由此触发的路由更新
	* 你必须仔细阅读和理解协议处理规则，先在简单的拓扑图上熟悉算法
	* 每个路由器在收到邻接表后，发出第一个路由更新，之后只在路由表变化才发出路由更新
	* 你可以设置一定时长的定时器，以决定仿真结束时刻，结束后所有进程都必须及时终止

3. 仿真结束输出两类文件：
	* 一个名为 ports 的文件，有$N$行。每行列出以空格分开的两个数字$X$和$Y$，$X$为节点地址，$Y$为其UDP端口号。全部行以地址从低到高排序。
	* 每个路由器的路由表文件，文件名为路由器地址 ($[0,N-1]$)，总共有$N$个文件
		* 每个路由表文件有$N$行，每行对应一条到目标路由器的路由
		* 路由格式是：“X Y C P1,P2,P3”
		* X是目标路由器地址，Y是到从本路由器到X的下一跳地址，C是链路开销
		* P1,P2,P3是从X到本路由器的 (逆向) 路径，以逗号分隔

以上的要求和建议其实给出了仿真程序设计的框架和运行流程，在此基础上可以进一步考虑管理员和路由器进程的许多设计细节。

#### 管理员进程

从流程上看，管理员进程是主进程，负责读入网络连接信息；同时它也是父进程，为每个路由器生成子进程。管理员要开启TCP套接字，以接收每个路由器所监听的UDP端口号。那么路由器怎么知道管理员的TCP端口号呢？答案就在生成子进程的过程里。当管理员调用`fork()`生成子进程时，立即传递自己的TCP套接字文件描述符和总节点数目给路由器函数。而当路由器连接到管理员后，管理员也会从`accept()`的返回值得到路由器的TCP套接字文件描述符，这样管理员就可以发送后续的邻接表信息。

理清了这一过程之后，整个管理员进程的运行时序就很清晰了。以下列出穿插关键数据结构定义的完整流程：

1. 启动，读入命令行参数`argv[1]`，也就是网络连接描述文件名。
2. 初始化网络节点邻接表：一个结构类型`source`的数组，记录节点地址`id`、相邻节点数`numNeighbor`以及邻接点信息的链表`link`；邻接点信息定义为另一个结构类型`neighbor`，包含节点地址`id`、链路开销`cost`和下一个邻接点指针：

   ``` c++
   struct neighbor {
       int id;
       int cost;
       neighbor *next;
   };
   struct source {
       int id;
       int numNeighbor;
       neighbor *link;
   };
   ```

3. 读入网络连接描述文件，分析后构造网络节点邻接表。
4. 创建TCP套接字，然后调用绑定`bind()`和监听`listen()`函数。
5. 循环调用`fork()`生成全部路由器子进程，传递TCP套接字文件描述符和总节点数目给路由器启动函数：

	``` c++
	   // fork the routers
    for (i = 0; i <numNode; i++) {
        if ((childpid = fork())==0) {
            router(i, listenfd, numNode);
            exit(0);
        }
    }
	```

6. 循环调用`accept()`接收每个路由器发过来的UDP端口号，保存到 ports 文件；同时记录每个路由器的TCP连接文件描述符。
7. 循环给每个路由器发送邻接信息：
	* 先是路由器地址和相邻节点总数：

	    ``` c++
	    // This is header message to each router to tell it its own
	    // ID and how many neighbors it has.
	    struct message {
	        int routerId;
	        int numNeighbor;
	    };
	    ```

	* 后面是每一个邻接点的*<节点地址，链路开销，UDP端口号>*信息三元组：
    
	    ``` c++
	    // This message is used for the manager to tell each router
	    // its neighbor information including <id, cost, UDP_port>.
	    struct nb_tuple {
	        int neighborId;
	        int cost;
	        int UDP_port;
	    };
	    ```

8. 循环调用`wait()`等待每个路由器子进程结束，然后整个仿真过程结束。

#### 路由器进程

路由器进程的设计和实现要复杂得多。这里要创建距离矢量矩阵和路由表、实现节点间距离矢量的交换，还要处理距离矢量信息、更新路由表并重发距离矢量。这是一个典型的异步多进程软件设计的问题。另外还要记得必须实现**扩展的贝尔曼-福特算法**的环路解构功能。

先来看看核心数据结构的定义和初始化代码：

* 距离矢量结构及其二维矩阵初始化
	* 距离矢量包含距离度量值和环路解构需要的路径头节点地址：
	
	    ``` c++
		struct Dis_matrix {
		    int distance;
		    int headId;
		};
	    ```
	* 初始化 [总节点数] $\times$ [本节点的相邻节点数] 的二维矩阵 (-1代表不可达)：
	
	    ``` c++
	    // create distance matrix entries
	    Dis_matrix **entry;
	    entry = new Dis_matrix*[numNode];

	    // initialize distance matrix
	    for (i=0; i<numNode; i++) {
	        entry[i] = new Dis_matrix[msg.numNeighbor];
	        for (j=0; j<msg.numNeighbor; j++) {
	            if (tup[j].neighborId==i) {
	                entry[i][j].distance=tup[j].cost;
	                entry[i][j].headId=id;
	            } else {
	                entry[i][j].distance=-1;
	                entry[i][j].headId=-1;
	            }   
	        }   
	    }
	    ```
* 路由表结构及其初始化
	* 路由表项是一个*<目的节点，链路开销，下一跳，路径头节点>*的四元组：
	
	    ``` c++
		struct RtableEntry {
		    int dest;
		    int cost;
		    int nexthop;
		    int head;
		};
	    ```
	* 初始化为 [总节点数] 一维数组：
	 
		``` c++
		// initialize routing table
		RtableEntry *table = new RtableEntry[numNode];
		for (i=0; i<numNode; i++) {
		    int tmp_cost = -1; 
		    int tmp_next = tup[0].neighborId; 
		    int tmp_head = -1; 
		    for (j=0; j<msg.numNeighbor; j++) {
		        if (entry[i][j].distance != -1) {
		            tmp_cost = entry[i][j].distance;
		            tmp_head = entry[i][j].headId;
		            tmp_next = tup[j].neighborId;
		            break;
		        }   
		    }   
		    table[i].dest = i;
		    table[i].cost = tmp_cost;
		    table[i].nexthop = tmp_next;
		    table[i].head = tmp_head;
		}
		```

接下来一个重要设计是实现论文中的IN\_PATH函数以检测环路。原文的伪代码用到了递归，是为了说明的方便。所有的递归都可以转化为迭代，从性能上考虑迭代更好。仿真程序实现的IN\_PATH函数如下：

``` c++
bool IN_PATH (int NB, int dest, RtableEntry *table, int id)
{
    int head=table[dest].head;
    if (head==-1)
        return false;

    while ((head!=id) && (head!=NB) && (head!=-1))
        head=table[head].head;

    if (head==id || head==-1) return false;
    else return true;
}
```

函数里的变量名与论文中的的基本一致。可以看到，其实这是一个简单的代码实现，但是其中蕴含的思想却很重要。如论文中所述，这个函数在每次向邻接点发送路由更新时都要被调用。

在以上这些都就绪后，整个路由器的运行流程就可以清楚地表述如下：

1. 创建TCP套接字，连接到管理员进程。
2. 创建UDP套接字，绑定`bind()`后调用`getsockname()`取得端口号并发给管理员。
3. 从管理员接收相邻节点信息，包括链路开销和UDP端口号
4. 初始化距离矢量矩阵和路由表，开始路由。
5. 先发送第一个距离矢量消息给每个邻接点，消息是字符串格式：
	* 开头："<本节点地址>[空格]<邻节点地址>[空格]<总节点数>**\***"
	* 然后对每一个目的地重复："<目的节点地址>[空格]<链路开销>[空格]<路径头节点地址>**#**"
6. 调用`select()`开始事件循环，并设置定时为三倍总节点数的秒数。当在超时前收到邻接点发来的距离矢量时，`select()`返回大于0的值，路由器作如下处理：

     * 分析收到的距离矢量，更新自身距离矢量矩阵，然后生成新的路由表，原始的贝尔曼-福特算法的实现就在这里：
 
		``` c++
		void UpdateDisMatrix (char* recv, Dis_matrix **Entry,int numNode, int id,
		                      int numNeighbor, nb_tuple *tup)
		{
		    int sour, dest, tempDest, tempDist, tempHead, i, j, k;
		    char *temp;
		    
		    temp=strchr(recv,'*')+1;
		    sscanf(recv,"%d %d %d*",&sour,&dest,&numNode);
		    
		    for (i=0;i<numNode;i++) {
		        sscanf(temp,"%d %d %d",&tempDest,&tempDist,&tempHead);
		        temp=strchr(temp,'#')+1;
		        
		        if ((tempDest==id)||(tempDest==sour))
		            continue;
		            
			    for (j=0; j<numNode; j++) {
			        if (j==tempDest) {
			            for (k=0;k<numNeighbor; k++)
			                if (tup[k].neighborId==sour)
			                    break;
			            if (tempDist==-1) {
			                Entry[j][k].distance=-1;
			                Entry[j][k].headId=-1;
			            } else {
			                Entry[j][k].distance=tempDist+tup[k].cost;
			                Entry[j][k].headId=tempHead;
			            }
			            break;
			        }
			    }
		    }
		}
	    
		void CreateRTfromDM (RtableEntry *rtEntry_new, Dis_matrix **Entry,
		                     nb_tuple *tup, int numDest, int numNB)
		{
		    int i,j, tmp, k;
		    
		    for (i=0; i<numDest; i++) {
		        tmp=Entry[i][0].distance;
		        k=0;
		        for (j=1;j<numNB; j++) {
		            if (Entry[i][j].distance==-1)
		                continue;
		            else if (tmp==-1||Entry[i][j].distance<tmp) {
		                tmp=Entry[i][j].distance;
		                k=j;
		            }
		    	}
		        rtEntry_new[i].dest=i;
		        rtEntry_new[i].cost=tmp;
		        rtEntry_new[i].nexthop=tup[k].neighborId;
		        rtEntry_new[i].head=Entry[i][k].headId;
		    }
		}
		```

     * 比较新旧路由表，如果有变化就替换掉旧的，并发送新的距离矢量给所有邻节点。发送代码调用IN\_PATH函数实现**扩展的贝尔曼-福特算法**：
     
	     ``` c++
        for (i=0; i<numNode; i++) {
            if (IN_PATH(tup[j].neighborId, i, table, id)) {
                tmpRT[i].cost=-1;
                tmpRT[i].head=-1;
                tmpRT[i].dest=i;
            } else {
                tmpRT[i].cost=table[i].cost;
                tmpRT[i].head=table[i].head;
                tmpRT[i].dest=i;
            }
        }
	     ```
     * 重新开始定时的事件循环。
7. 如果`select()`返回0，事件循环超时，这时假定网络路由已收敛，输出自己的路由表。
8. 路由器进程结束。

### 程序运行

原始的仿真程序当年在Sun SPARK工作站中编译，通过了教师提供的10节点网络测试用例。之后又测试自己编写的6节点 (就是前面路由算法举例的网络图) 和12节点测试用例，才最后提交。几天后从教学助理那里得知，仿真程序获得了满分！

现在将仿真程序重新拿出来，在Red Hat Linux和macOS系统中编译链接，两个系统的编译运行环境如下：

* Red Hat Enterprise Linux 8.1 (Ootpa)：
	* 内核: Linux 4.18.0-147.3.1.el8_1.x86_64
	* 体系结构: x86-64
	* 处理器: Intel(R) Xeon(R) CPU E5-2667 v4 @ 3.20GHz
	* 编译器: g++ (GCC) 8.3.1 20190507 (Red Hat 8.3.1-4)
* macOS Catalina Version 10.15.7：
	* 内核: Darwin 19.6.0: Tue Nov 10 00:10:30 PST 2020
	* 体系结构: x86_64
	* 处理器: 2.2 GHz 6-Core Intel Core i7
	* 编译器: Apple clang version 12.0.0 (clang-1200.0.32.28)

在macOS上需要对程序原文件做一个小改动[^socklen]才编译成功。而在链接阶段发现在两个系统上都不需要原来的socket和nsl目标库文件，因为它们都已经被包含在缺省加载的标准libc库中。清除这些障碍后，运行时却发现路由器收不到相邻节点的距离矢量消息，而发送方调用`sendto()`时并没有报错，在两个系统中的症状一样。

困扰了一天半后，终于找到原因了。原来的代码里，路由器从管理员收到相邻节点的UDP端口号后，保存时做了一个Endianness转换：

``` c++
	neibaddr[i].sin_port = htons(tup[i].UDP_port);
```

Sun SPARK是`Big Endian`系统，而现在运行Red Hat Linux和macOS的系统是用的Intel x86_64体系结构，它们都是`Little Endian`的。注意到UDP端口号是从网络数据包中直接取出来的，所以这里可能不需要转换。果然，拿掉`htons()`之后，路由器之间的消息传递恢复正常，同样的三个测试用例全部通过。

参考前面的路由算法讨论例图，以下是6节点网络的测试输入用例。节点A-F对应路由器ID 0-5：

``` bash
cc-simulate-dv:9 > cat test6.txt 
6
0 1 1
0 2 4
1 2 1
0 3 6
2 3 1
3 4 1
2 4 1
5 1 5
2 5 4
4 5 1
```

仿真程序编译和运行的记录如下：

``` bash
cc-simulate-dv:10 > make
g++ -O2 -c manager.cc
g++ -O2 -c router.cc 
g++ -O2 -o manager manager.o router.o  
cc-simulate-dv:11 > manager test6.txt
numnode is: 6
0 3: 3.6 2.4 1.1 
1 3: 5.5 2.1 0.1 
2 5: 5.4 4.1 3.1 1.1 0.4 
3 3: 4.1 2.1 0.6 
4 3: 5.1 2.1 3.1 
5 3: 4.1 2.4 1.5 
R1 begin routing
R2 begin routing
R3 begin routing
R4 begin routing
R0 begin routing
R5 begin routing
R4 timeout!
R2 timeout!
R3 timeout!
R5 timeout!
R0 timeout!
R1 timeout!
```

运行结果显示节点A与F的路由表与逆向路径完全正确：

``` bash
cc-simulate-dv:11 > cat ports 
0 37352
1 24551
2 45772
3 33265
4 38391
5 36583
cc-simulate-dv:12 > cat 0
0 -1 0
1 1 1 1,0
2 1 2 2,1,0
3 1 3 3,2,1,0
4 1 3 4,2,1,0
5 1 4 5,4,2,1,0
cc-simulate-dv:13 > cat 5
0 4 4 0,1,2,4,5
1 4 3 1,2,4,5
2 4 2 2,4,5
3 4 2 3,4,5
4 4 1 4,5
5 -1 0
```

完整的修正过的仿真程序打包下载链接在此：[cc-simulate-dv.tgz](cc-simulate-dv.tgz)

总结这一项目的完成，加深了对距离矢量路由协议的深刻理解，也熟悉了Unix类系统上的网络编程的许多规范和细节，笔者收获很大。另一方面，从课程设计上看，此软件项目还可以做一些优化和扩展实验：

* 创建面向对象的路由器类，实现完全模块化的路由器
* 处理距离矢量时直接更新原来的路由表，不必生成新的路由表再比较
* 设计仿真节点失误或链路断线的情况，验证协议实现的收敛性
* 在同样的仿真架构下，实现链路状态路由协议 ([OSPF](https://en.wikipedia.org/wiki/Open_Shortest_Path_First))
* 修改仿真架构，实现路径矢量路由协议 ([BGP](https://en.wikipedia.org/wiki/Border_Gateway_Protocol))

回顾起来，CS551讲解的计算机网络知识点和软件作业都让人受益良多。总体上看，CS551可能是笔者在USC上的最具有挑战性、但也学到最多东西的一门课程。这样的学习和训练为笔者之后长期的网络研发工作打下了坚实的基础。非常感谢任课教师 Ramesh Govindan 教授！


[^CS551]: 时至今日，CS551依然如当年一样火热，报名需要资格审批 (Clearance) ，之后可能还要通过一个预考 (Placement Exam) 才能正式注册。
[^Cheng]: C. Cheng, R. Riley, S. P. R. Kumar, and J. J. Garcia-Luna-Aceves. *[A loop-free Bellman-Ford routing protocol without bouncing effect](https://dl.acm.org/doi/abs/10.1145/75247.75269)*. In ACM SIGCOMM '8g, pages 224-237, September 1989
[^Ramesh]: Govindan教授专注于大型网络路由基础设施和无线及移动网络体系结构研究。他是IEEE和ACM双会士 (Fellow)，曾任 IEEE *移动计算* 会刊主编。Govindan教授2018年荣获 IEEE Internet Award。他现今依然活跃在科研和教学的一线。
[^socklen]: 在macOS系统中，socket系列API的接口定义使用`socklen_t *restrict address_len`。这要求调用者传递严格类型定义的变量给地址长度参数`address_len`。