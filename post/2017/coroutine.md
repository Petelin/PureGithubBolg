## python的异步编程

如果一个函数中使用了yield关键字,那么他就成了特殊的generator对象.

!['内存分布'](http://aosabook.org/en/500L/crawler-images/generator.png)

一个generator的Code和Frame都是放在堆上的, 所以可以很方便的更改, 任何时候都能停下来,或者接着执行.

Frame的有个lasti(last instruction)变量, 就是用来标识流程执行到了哪里. 如果还没开始为-1.


### yield from

yield from iterator was (essentially) equivalent to:

```python
for x in iterator:
    yield x
```

举一个栗子:

Future class 的特殊之处就在于, yield from future, 只要future还没有准备好,就会一直yield在这里,实现如下

```python
# Method on Future class.
def __iter__(self):
    # Tell Task to resume me here.
    while True
        if self.ready:
            return self.result
        yield self
```

### send(), 发送信息给协程

```python
def jumping_range(up_to):
    """Generator for the sequence of integers from 0 to up_to, exclusive.

    Sending a value into the generator will shift the sequence by that amount.
    """
    index = 0
    while index < up_to:
        jump = yield index
        if jump is None:
            jump = 1
        index += jump


if __name__ == '__main__':
    iterator = jumping_range(5)
    print(next(iterator))  # 0
    print(iterator.send(2))  # 2
    print(next(iterator))  # 3
    print(iterator.send(-1))  # 2
    for x in iterator:
        print(x)  # 3, 4
```

iterrator.send(None) is equal to next(iterator)

### async and await

为了将`generator`和`coroutine`分开,我们将`coroutine`标记成这个样子

```
import types

@types.coroutine
def coroutine():
    yield
```

而`async`和`await`的加入更加明确了什么是`coroutine`, 只有使用了这两个关键字的才是协程,完全与`yield`分开了 比如`inspect.iscoroutine()`会严格的检查`async`是否被使用.

而`await`和`yield from`及其相似, 同样也是规范化了定义, 当你`await`什么东西的时候, 实际上是在调用`object.__await__`这个钩子函数, 而不是`__iter__`,python 设计原则就是一个关键字只有一个作用). 

## 协程, 说到底是用来协作的

那怎么协作呢? 事件循环.

loop开启, 检查若干个队列, 先检查io, time等等这些功能队列, 发现有能执行的任务放到ready队列中.
然后从ready队列中pop出一个任务.执行一次,此时如果该任务在内部写了yield就会将执行权还给loop, 就像函数执行完成了一样(只不过没有进出栈), loop会:

1. 看看这个协程结束了没有(有没有raise stopIterator),如果结束了,做一些收尾工作,处理返回值
2. 没结束拿到协程的返回值(hack的玩法就是通过抛出一个特殊的object, 然后在主循环进行一些处理, 主循环相当于操作系统, 特殊的object就是系统接口), 这个返回值相当于协程给loop一个信号,标识下一步想要怎么做.


