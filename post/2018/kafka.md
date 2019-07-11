##Kafka 实现的特点

kafka可谓是一个工程上的利器, 就像Redis一样, 基本是每个服务都用的到的东西. Kafka里的地方并不是理论创新或者架构创新, 而是其完美的平衡了各个功能(需求)与实现. 

打比方说, 最新版的kafka已经支持加密了, 但是为了支持加密损失了(20/30%)的速度, 因为之前的zero-copy没法用了. 但是Java最新版的加密库性能提升了10%, 所以他们评估之后觉得还可以接受.就开发了这个功能.

正是这种平衡.让kafka流行起来,就像是神兵利器一样, 无所不能, 功能够多, 速度够快.



### 一些链接

笔者通读了 <Kafka 权威指南> , 强烈推荐一下, 这本书深度广度都有, 是研究kafka不可多得的好书.

另外一篇文章 [kafka七年止痒](https://mp.weixin.qq.com/s/x3l9eKN0-DKIfDOmpkal8Q) 回顾了kafka从诞生到现在的变化. 包括了几乎所有的特性, 以及为什么需要他们, 怎么实现的他们.

这个系列的kafka文章是最好的. [链接](https://www.infoq.cn/profile/1278686?menu=publish)



下面是笔者认为比较track的东西, 记起来防止忘记.

### 1. 顺序

>  通过生产者发送到特定主题的消息将按其发送顺追加。那就是，如果记录M1和M2由同一个生产者发送，且M1先发送，那么M1的偏移量会小于M2且更早出现在中志中。

这是怎么做到的呢? 原因就在一个producer里面有一个queue, 用来对你要写的log进行排序然后batch的形式发送.

同事还要保证一个一个mute发出去, Broker收到了,才能发下一个, 否则虽然是一个一个发的, 但是到Broker的时候可能是乱序的. 也就是说只能有一个connection

```java
this.guaranteeMessageOrder = (config.getInt(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION) == 1)
```

如果只有一个connection, m每次send的时候都会mute对应TP, 阻止并发.这样才可以保证有序.

参考: <http://matt33.com/2017/09/10/produccer-end/>

### 2. 消费者故障

> 在订阅了一组主题后，当poll(Duration)方法被调用时，该消费都会自动加入组。poll这个API被设计成确保消费者活力。只要你持续的调用poll，该消费者将会保持在组中，持续的从被分配的分区中接收到消息。在底层，该消费会发送定期心跳信号给服务器。如果消费都崩溃或者在持续session.timeout.ms时间内无法发送心跳信号，则该消费者将会被认为已经死亡，并且它的分区将会被重新分配。

这里讨论的是多个消费者组成的消费组. 一个消费者本来是固定消费一个分区. 如果

- 持续发送心跳, 但是不poll新的日志() --- 一直在处理
    客户端的实现为了避免在这种情况下消费者被分区持续持有，我们用max.poll.interval.ms配置提供了一个活锁发现机制。如果你在配置的max interval内没有调用poll方法，该客户端会主动的离开组，以便其它的消费者可以接管它的分区。**这个也不应该设置的过大, 否则如果某个消费着真的有问题, 也没办法解锁其所拥有的分区了**
- 不发送心跳了 --- 机器死了
    自然会重新balance

####暂停/恢复消费

Kafka支持使用pause(Collection)和resume(Collection)动态控制消费流，以便在未来的轮询(持续时间)调用中分别暂停指定分区上的消费和恢复指定暂停分区上的消费。

这个本来是用来控制速度的. 但是如果用来在处理log失败的时候, 暂停消费直至处理成功, 好像也是可以的. 因为只有正常流程才会暂停, 所以也不用担心假死什么的. 

### 3. Exact Once

为什么追求原子性:

1. **便于故障恢复**
2. 结果可控,你想写入一条, 结果因为重试写入多条, 或者乱序



严格的说, `Kafka`支持生产者仅仅写入一次不重复, 但是没法做到消费者只消费一次(因为使用户自己消费的, 成不成功是对于kafka是未知的)

####生产者

在Exactly once语义下, 多次重试写数据, broker也能保证流里只有一条. 

实现方法: 

>  Broker 端也会为每个`<PID, Topic, Partition>`(PID是生产者ID的意思不是进程ID)维护一个序号(其实这个在一定程度上就是ID)，并且每次 Commit 一条消息时将其对应序号递增。对于接收的每条消息，如果其序号比 Broker 维护的序号（即最后一次 Commit 的消息的序号）大一，则 Broker 会接受它，否则将其丢弃：
>
> - 如果消息序号比 Broker 维护的序号大一以上，说明中间有数据尚未写入，也即乱序，此时 Broker 拒绝该消息，Producer 抛出`InvalidSequenceNumber`
>
> - 如果消息序号小于等于 Broker 维护的序号，说明该消息已被保存，即为重复消息，Broker 直接丢弃该消息，Producer 抛出`DuplicateSequenceNumber`

#### 消费者

但是consumer读的时候就复杂多了, 因为处理和提交是两个过程/系统, 无论如何也没法保证原子性

- 不保证原子性, 使用**幂等性**,保证多次读也不会出现问题.
- 就要原子性, 把处理结果和提交放在一起. 这个东西非常有意思. 就是让**你自己去记录offset**, 比如你处理之后要把数据更新到MySQL(没写之前都是没用的), 那么开启一个事物, 把Offset也一并记录在MySQL里.这样就能保证数据被Handle的Offset, 之后不会在被Handle. 但是缺点很大很大. 你需要自己实现一套Offset Commit语义, 而且对不不同的Handle, 实现还不一样(有的写MySQL, 有的写ES, 诸如此类). 这个点子书上也有, 但是在 [这篇文章](https://www.infoq.cn/article/kafka-analysis-part-1)里才真正看懂.

外置偏移量使得支持exactly once.

> 消费者应用程序非必须使用Kafka内置的偏移量存储，即可以在自己选择的一个存储中保存偏移量。这样做的主要用例是允许应用程序在同一个系统中保存偏移量和消费的结果，即以原子方式保存结果和偏移量。这并不总是可行的，但是当它出现时，它将使消费完全原子化，并提供“恰好一次”语义，这比使用Kafka的偏移提交功能得到的默认“至少一次”语义更强。

### 4. High Availabl

#### replica 的设计

1. 需要有多个备份, 必然要消除单点
2. 备份只是备份不能被使用(因为会增加维护一致性的复杂度), raft协议不也是这样
3. replica 要均匀, 典型的部署方式是一个 Topic 的 Partition 数量大于 Broker 的数量. 然后副本还可以通过**配置Broker机架信息**, 来保证尽量分散开(那个作者特别喜欢强调这一点,每次都要强调一次不同机架, 是不是被坑过- - - -)
4. 主动pull数据. 为了性能收到数据就像Leader发送ack,而非写入.         ------   其实这还是一个问题, 突然断电就凉了

#### Partition

1. 一个分区下的都是副本, 其中一个是副本首领, 他负责所有的读写. 其他副本负责同步
2. Partition创建的时候是均衡的. 但是如果你的物理机是不均衡的, 也是可以通过`Kafka`提供的脚本来手动改. 比如让多几个分区都在一台性能比较好的机器上
3. Parition是通过Zookeeper来选举首领的, 一旦发现这个分区没有首领了, 就开始强占写入, 谁成功谁就成了老大  ---    这个实现非常的简单, 把最难得部分交给了Zookeeper. 

#### commit

kafka是认为只有in-sync Replica中足够多(可以配)的机器ack了,才算是commit  -> 消费者才能看见.

但是对于生产者, 可以选择等待commit, 也可以选择视而不见, 三个等级随便挑.  这种处理手法还是很灵活的

另外通过配置多少台Replica ack才算commit, 可以在吞吐率和一致性中作出权衡.(其实就是丢数据和速度慢 的权衡)



#### Leader 选举

这块其实没怎么看懂, 我的看法就是你配置了n个ack就可以commit, 那么能忍受的失败就是n-1. 

这种和大多数选举的区别就是, 一个独裁, 一个民主, 大多数是老大死了之后, 剩下的人谁占优势谁上来. Kafka这种是, 一直维护一个皇子池子, 皇上死了就从皇子里挑选, 平时要保证皇子和自己的心思一致.

> 如果一个 Follower 宕机，或者落后太多，Leader 将把它从 ISR 中移除。这里所描述的“落后太多”指 Follower 复制的消息落后于 Leader 后的条数超过预定值（该值可在 `$KAFKA_HOME/config/server.properties` 中通过`replica.lag.max.messages`配置，其默认值是 4000）或者 Follower 超过一定时间（该值可在 `$KAFKA_HOME/config/server.properties` 中通过`replica.lag.time.max.ms`来配置，其默认值是 10000）未向 Leader 发送 fetch 请求。

>  Kafka 在 ZooKeeper 中动态维护了一个 ISR（in-sync replicas），这个 ISR 里的所有 Replica 都跟上了 leader，只有 ISR 里的成员才有被选为 Leader 的可能。在这种模式下，对于 f+1 个 Replica，一个 Partition 能在保证不丢失已经 commit 的消息的前提下容忍 f 个 Replica 的失败。在大多数使用场景中，这种模式是非常有利的。事实上，为了容忍 f 个 Replica 的失败，Majority Vote 和 ISR 在 commit 前需要等待的 Replica 数量是一样的，但是 ISR 需要的总的 Replica 的个数几乎是 Majority Vote 的一半。

> 虽然 Majority Vote 与 ISR 相比有不需等待最慢的 Broker 这一优势，但是 Kafka 作者认为 Kafka 可以通过 Producer 选择是否被 commit 阻塞来改善这一问题，并且节省下来的 Replica 和磁盘使得 ISR 模式仍然值得。

 

#### replica都不工作了

- 等待 ISR 中的任一个 Replica“活”过来，并且选它作为 Leader
- 选择第一个“活”过来的 Replica（不一定是 ISR 中的）作为 Leader



#### 如何选举 Leader -- 为什么需要在所有的broker里选择一个controler

最简单最直观的方案是，所有 Follower 都在 ZooKeeper 上设置一个 Watch，一旦 Leader 宕机，其对应的 ephemeral znode 会自动删除，此时所有 Follower 都尝试创建该节点，而创建成功者（ZooKeeper 保证只有一个能创建成功）即是新的 Leader，其它 Replica 即为 Follower。

但是该方法会有 3 个问题：

- split-brain 这是由 ZooKeeper 的特性引起的，虽然 ZooKeeper 能保证所有 Watch 按顺序触发，但并不能保证同一时刻所有 Replica“看”到的状态是一样的，这就可能造成不同 Replica 的响应不一致
- herd effect 如果宕机的那个 Broker 上的 Partition 比较多，会造成多个 Watch 被触发，造成集群内大量的调整
- ZooKeeper 负载过重 每个 Replica 都要为此在 ZooKeeper 上注册一个 Watch，当集群规模增加到几千个 Partition 时 ZooKeeper 负载会过重。

Kafka 0.8.* 的 Leader Election 方案解决了上述问题，它在所有 broker 中选出一个 controller，所有 Partition 的 Leader 选举都由 controller 决定。controller 会将 Leader 的改变直接通过 RPC 的方式（比 ZooKeeper Queue 的方式更高效）通知需为为此作为响应的 Broker。同时 controller 也负责增删 Topic 以及 Replica 的重新分配。



