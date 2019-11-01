# 内存模型

In computing, a memory model describes the interactions of threads through memory and their shared use of the data.

用来描述内存之间是怎么share的.

## go

对于go来说, share内存一定是在多个goroutine之间. 两个goroutine同是对一个变量,数据结构进行操作就会有并发问题,为了解决这个问题go定义了happen-before语义,说明了几种可以保证顺序的写法 可以看文章
