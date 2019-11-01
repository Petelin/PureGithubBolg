# go 内存模型

[toc]

## 链接

[官方文档](https://note.youdao.com/)

## 笔记

官方的态度: 

> If you must read the rest of this document to understand the behavior of your program, you are being too clever. 
>
> Don't be clever.

### happens before

定义: If event e1 happens before event e2, then we say that e2 happens after e1. Also, if e1 does not happen before e2 and does not happen after e2, then we say that e1 and e2 happen concurrently.

Within a single goroutine, the happens-before order is the order expressed by the program.

单个goroutine里面, 代码顺序就是happens-before顺序

#### 定义1 read 允许看到 write 的条件, 允许代表可能

A read _r_ of a variable `v` is _allowed_ to observe a write _w_ to `v` if both of the following hold:

> 1. _r_ does not happen before _w_.
> 2. There is no other write _w'_ to `v` that happens after _w_ but before _r_.

这里第一条说的是r不能明确的happens beofre w. 那么它有两种选择

- w happens before v
- w 和 v 是 happen concurrently

#### 定义2 read 一定能看到 write 操作的条件

To guarantee that a read _r_ of a variable `v` observes a particular write _w_ to `v`, ensure that _w_ is the only write _r_ is allowed to observe. That is, _r_ is _guaranteed_ to observe _w_ if both of the following hold:

> 1. _w_ happens before _r_.
> 2. Any other write to the shared variable `v` either happens before _w_ or after _r_.

This pair of conditions is stronger than the first pair; it requires that **there are no other writes happening concurrently with _w_ or _r_.**

Within a single goroutine, there is no concurrency, so the two definitions are equivalent: a read _r_ observes the value written by the most recent write _w_ to `v`. When multiple goroutines access a shared variable `v`, they must use synchronization events to establish happens-before conditions that ensure reads observe the desired writes.

#### 特殊定义

- The initialization of variable `v` with the zero value for `v`'s type behaves as a write in the memory model.

    初始化变量被视为写,

- Reads and writes of values larger than a single machine word behave as multiple machine-word-sized operations in an unspecified order.

    读写不是单个机器字的操作被视为没有明确顺序的读取多个机器字

### 同步原语

#### 初始化

程序初始化一定只有一个goroutine, 但是一个goroutine可以创建多个并

If a package `p` imports package `q`, the completion of `q`'s `init` functions happens before the start of any of `p`'s.

The start of the function `main.main` happens after all `init` functions have finished.

#### 创建goroutine

The `go` statement that starts a new goroutine happens before the goroutine's execution begins.

#### Goroutine 销毁

The exit of a goroutine is not guaranteed to happen before any event in the program.

```go
var a string

func hello() {
	go func() { a = "hello" }()
	print(a)
}
```

it is not guaranteed to be observed by any other goroutine. In fact, an **aggressive compiler might delete the entire `go` statement.**

因为这段代码有race condition. Any race is a bug. When there is a race, the compiler is free to do whatever it wants.

#### channel 消息通知

- A send on a channel happens before the corresponding receive from that channel completes.

发消息一定在收消息之前, 如果只看这句话, 可能觉得那不一定的吗? 

```go
var c = make(chan int, 10)
var a string

func f() {
	a = "hello, world"
	c <- 0
}

func main() {
	go f()
	<-c
	print(a)
}
```

如果不是`c <- 0` 和`<-c` 而是读写一个single machine word, 这里依然会有竞态.

is guaranteed to print `"hello, world"`. The write to `a` happens before the send on `c`, which happens before the corresponding receive on `c` completes, which happens before the `print`.

因为`<-c`的成功, 一定意味着拿到了`c<-0`的数据. 

- The closing of a channel happens before a receive that returns a zero value because the channel is closed.

- A receive from an unbuffered channel happens before the send on that channel completes.

    go语义保证阻塞的channel,  接受是在写发送之前的

- The _k_th receive on a channel with capacity _C_ happens before the **_k_+_C_th** send from that channel completes.

    有缓存的buffer, 仅仅能保证第k次读是在`k+cap(C)`(下一轮)写之前完成的.

    


#### Locks

_For any_ `sync.Mutex` _or_ `sync.RWMutex` _variable_ `l` _and_ _n_ _\<_ _m\*\*, call_ _n_ _of_ `l.Unlock()` _happens before call_ _m_ _of_ `l.Lock()` _returns._

#### Once

```go
type Once struct {
	m    Mutex
	done uint32
}

func (o *Once) Do(f func()) {
	if atomic.LoadUint32(&o.done) == 1 {
		return
	}
	// Slow-path.
	o.m.Lock()
	defer o.m.Unlock()
	if o.done == 0 {
		defer atomic.StoreUint32(&o.done, 1)
		f()
	}
}
```

*A single call of `f()` from `once.Do(f)` happens (returns) before any call of `once.Do(f)` returns.*

do返回的时候f()一定已经call return.

### Incorrect synchronization

*Note that a read r may observe the value written by a write w that happens concurrently with r. Even if this occurs, it **does not** imply that reads happening after r will observe writes that happened before w.*

```go
var a string
var done bool
func doprint() {
	if !done {
    once.Do(func (){
      a = "hello, world"
      done = true})
	}
	print(a)
}
func twoprint() {
	go doprint()
	go doprint()
}
```

