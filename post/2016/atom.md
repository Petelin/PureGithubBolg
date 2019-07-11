## 同步互斥锁的实现方式

三种方式:  

1. 禁用中断
2. 软件实现
3. 高级硬件支持
4. 通过信号量

### 禁用中断  
很好理解,就是在临界区关掉中断.然后在退出区在恢复中断.这个东西最大的问题就是只能在单核上使用.这就意味着根本没什么用.(也不能这么说,想想python实现都是有全局锁的,指不定哪天单核机器又火了)

### 软件实现  
涉及到两个算法: Peterson算法 和 Dekker算法.

#### Peterson算法
改算法完美的解决了两个线程的同步互斥问题.

共享变量:  
```c
//flag[] is boolean array; and turn is an integer
flag[0]   = false;
flag[1]   = false;
int turn;
```

```c
P0: flag[0] = true;
    turn = 1;
    while (flag[1] == true && turn == 1)
    {
        // busy wait
    }
    // critical section
    ...
    // end of critical section
    flag[0] = false;

P1: flag[1] = true;
    turn = 0;
    while (flag[0] == true && turn == 0)
    {
        // busy wait
    }
    // critical section
    ...
    // end of critical section
    flag[1] = false;
```

flag数据代表自己想不想进去, turn标识轮到了谁进去.turn的值可能被覆盖,但是在临界区检查的时候一定是唯一的,要么是0要么是1.各种情况我们就不分析了,不过今天(12.12)我仔细想过各种情况,都能够满足要求.
注意到实现处的临界区是一个忙等待.


#### Dekker算法
改算法很容易扩充为n线程的情况,伪代码如下

```c
CSEnter(int i)
{
    inside[i] = true;                   #我要进入
    while(inside[J])                    #有别人也想进入,那就解决冲突去.
    {                                   
      if (turn == J)                    #解决冲突时发现别人持有turn
      {                                 
         inside[i] = false;             #暂时放弃进入
         while(turn == J) continue;     #忙等待到持有turn的J释放掉
         inside[i] = true;              #重新表明我要进入
       }
    }
}

CSExit(int i)
{
    turn = J;
    inside[i] = false;
}
```

缺点

>Dekker’s algorithm will not work with many modern CPUs
CPUs execute their instructions in an out-of-order (OOO) fashion
This algorithm won't work on Symmetric MultiProcessors (SMP) CPUs equipped with OOO without the use of memory barriers


#### 现代cpu支持

硬件可以提供两种原子操作方式:
1. test_or_set: test to set x = 1, if succeed return ture, else if x is 1 return false;
2. exchange: 交换内存中的两个值

通过这两个原语,我们就能实现锁机制.

![实现锁机制](/images/os/atom.png)

#### 信号量解决资源竞争问题
信号量是由Dijkstra大神当年提出来的

![信号量的实现](/images/os/singnal.png)

信号量通过操作系统保证P和V函数在执行时候不会不被中断来确保其原子性.  
通过控制资源数量和*获取释放顺序*来实现各种锁操作.
