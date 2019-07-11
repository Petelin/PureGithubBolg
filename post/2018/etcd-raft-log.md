## Etcd 里的 raft

[TOC]

### Etcd项目的结构

```
---etcd

	---raft: 核心系统库

		---node -> run() -> 写Ready()

	---etcdserver: 包含了应用的对raft核心的包装.

		---raft -> start() -> 读Ready()
```

### etcd最让人confuse的地方

etcd的raft库只实现了raft最核心的协议，其他的诸如WAL、SNAPSHOT、网络传输等都留给了使用该库的应用程序来实现, 只需要提供一个storage的接口给核心库就可以了.

这种解耦的方式直接看ercd/raft代码基本上是不可能明白的. 需要从大的地方着手往下看, 或者先看项目结构介绍.



### etcd-raft核心库的Log介绍

先看一下结构体

```go
type raftLog struct {
   storage Storage # 这个地方就是上层应用暴露给核心库的
   unstable unstable
   committed uint64
   applied uint64
}
```

这个里面committed, applied对应raft协议里的概念. 

unstable就是所有被提交到raft系统里的日志集合.Leader收到的日志会先放在这里, Follower收到Leader同步的日志也是先放在这里. 那为什么说他们是unstable呢? 因为他们都是在内存中, 没有被落地.

storage是一个interface, 具体的实现是memoryStorage, 也是内存中的结构. 需要注意的是: **storage的写入是由应用完成的, 而不是内部核心处理器**. 很好理解, 外部的应用处理完所有落地的日志, 然后暴露出来一个接口给需要这些数据的人访问而已.



### 上层应用到底做了什么?

主从节点上的日志首先被存储在内存的unstable中，但这些unstable中的日志项最终需要被应用获取到并作进一步处理。协议处理层的后台任务会将unstable中的日志项以及协议状态信息等打包成Ready结构塞进一个管道`readyc`, 上层应用通过Node.**Ready**()接口获取此类任务并作如下处理：

1. 处理状态, 比如更新commit index
2. 如果是Leader, 给其他Follower发通知(非阻塞的)
3. 将已经unstable日志项写入WAL(storage)；
4. 处理Snapshot，如果有的话；
5. 追加至raftStorage(这一步就是cache上面的WAL, 并通过接口暴露出去）；



### Follower处理接受到的append日志请求

Follower节点的数据最终也是被写入了日志模块的unstable日志中，其实就是被追加至内存中的日志项数组。之后和Leader一样统一交给上层应用来落地



### 总结

- 日志项会被存储在三个地方，按照其出现的顺序分别为：unstable、WAL、storage
- unstable维护协议层的日志项，这也是raft进行日志复制的数据源泉；
- WAL负责日志项的持久化存储；
- storage其实就是WAL的cache, 向外暴露的接口.
- 应用负责串联这些日志存储模块。