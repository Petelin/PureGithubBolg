## 事件等待器和条件变量

条件变量本质上是对休眠/唤醒功能的封装. 替代实现可以轮训,只不过效率不高.而条件变量可以无竞争的使线程工作.

### 条件

`条件`是一个可以结果为bool的表达式, 而条件变量是通知`条件`改变的方式. 

`条件`是谓词, 比如队列是不是空, 状态值是不是1.

注意: 条件变量一定是需要和一个条件一起使用的,凡是没有`条件`只使用条件变量函数的用法一定是错的.

很多人都没有注意到这一点, 这套接口的范式就得这样用才能保证各种情况的正确性.

### wait 调用非常复杂

条件变量的接口`pthread_cond_wait(&cond_, &mutex_)`非常的反人类:

1. 需要一个已经锁定了的mutex,  因为要配合条件使用,需要在确保`条件`没有发生变化的前提下执行等待,.
2. 有 spurious wakeup的副作用
3. `wait`必须在`notify`之前,否则得不到通知,也就是说是边缘触发的,只通知一次.
4. 内部会将本线程放到全局条件队列里,然后释放锁,开始休眠,等到被唤醒的之后,在重新拿到锁.

### spurious wakeup

spurious wakeup 指的是一次 signal() 调用唤醒两个或以上 wait()ing 的线程，或者没有调用 signal() 却有线程从 wait() 返回。

### 正确的使用方法

演示一种多线程个线程等待一个事件发生的函数, 线程可以并发的调用`wait`和`signal`而不会有任何问题, 需要注意的是,`signal`之后,`wait`永远不会在阻塞.

```c++
class Waiter4 : private WaiterBase
{
 public:
  void wait()
  {
    CHECK_SUCCESS(pthread_mutex_lock(&mutex_));
    while (!signaled_)
    {
      CHECK_SUCCESS(pthread_cond_wait(&cond_, &mutex_));
    }
    CHECK_SUCCESS(pthread_mutex_unlock(&mutex_));
  }

  void signal()
  {
    CHECK_SUCCESS(pthread_mutex_lock(&mutex_));
    signaled_ = true;
    CHECK_SUCCESS(pthread_cond_broadcast(&cond_));
    CHECK_SUCCESS(pthread_mutex_unlock(&mutex_));
  }

 private:
  bool signaled_ = false;
};
```

如果我们没有`signaled_`这个谓词, 那么先调用`signal`在调用`wait`就会丢掉信号,对变量进行操作自然是要加锁的.

用while不能用if的原因是wait可能被意外唤醒,即并没有发生真正的条件变量改变就被唤醒了.

`pthread_cond_broadcast` 和 `pthread_cond_signal` 可以放在锁里,也可以放在锁外.这个是没有影响的.



### 后记

使用条件变量，调用 signal() 的时候无法知道是否已经有线程等待在 wait() 上。因此一般总是要先修改`条件`(储存变化的发生)，使其为 true，再调用 signal()；这样 wait 线程先检查“条件”，只有当条件不成立时才去 wait()，避免了丢事件的可能。换言之，通过使用`条件`，将边沿触发（edge trigger）改为电平触发（level trigger）。这里“修改条件”和“检查条件”都必须在 mutex 保护下进行，而且这个 mutex 必须用于配合 wait()。

### 资源

chensuo写的常见版本,并给出了正确和错误的原因: 

1. [代码](https://gist.github.com/chenshuo/6430925) 
2. [文章](http://www.cppblog.com/Solstice/archive/2013/09/09/203094.html)

