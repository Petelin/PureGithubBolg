# 内存模型

In computing, a memory model describes the interactions of threads through memory and their shared use of the data.

用来描述内存之间是怎么share的.

## go

对于go来说, share内存一定是在多个goroutine之间. 两个goroutine同是对一个变量,数据结构进行操作就会有并发问题,为了解决这个问题go定义了happen-before语义,说明了几种可以保证顺序的写法 可以看文章

- [官方文档](https://golang.org/ref/mem)
- [之前的文章](http://petelin.github.io/golang/go_memory_model.html)

这里面讲了锁,channel,goroutine,以及一些常用的编程工具,比如wait group这个东西其实就是多线程里的join. -- 这些东西在go语言里的语义

### atomic

go 的atomic语义很弱, 文档介绍是说对底层cpu提供的指令的封装, 如果不是很有必要请不要使用

因为用atomic只能保证一个值被原子的读写. **文档里** 没有将是否会阻止乱排序, 也没有happen before语义.把他用作控制多个goroutine对一个值的读写不会有data race是可以的. 其他的操作还是要用上面的更高层的东西.

## Java

Java里面有很多种锁, 我在查atomic的时候最关心的就是volition这种锁. 因为他的用法很像atomic包, 都是避免对同一个数据的读写产生的data race. 但是volition还有happen before语言的, 他会加内存屏障. 根绝是读是写, 后面前面对这个变量是是读是写, 加的屏障还很不一样.非常的复杂.
