## Go 方法集问题 

go 语言方法定义和其他语言有很大的不同，调用一个 struct 的 method 实际上会被转化为对一个 func 进行调用，而所谓的函数接受者就是 function 的第一个参数。

### backgroud

```go
package main

import (
    "fmt"

    "github.com/aws/aws-sdk-go/aws"
)

type A struct {
    name *string
}

func (a A) foo() {
	fmt.Println("foo")
}

func (a *A) bar() {
	fmt.Println("bar")
}
```

我们的定义一个 A 结构，他有两个方法`foo` 和`bar` ，对于 `foo`每次调用的时候，都会完整复制结构体 `A` 的内存，对这个新的结构体在调用 `A`。而 `bar` 方法则是复制指针的值然后调用。

### pointer or structer?

本来，对于 `a`只能调用 `foo`,对于`b`只能调用 `bar`,但是编译器在方法调用的时候回进行判断，允许我们简写结构体调用指针方法，以及指针调用结构体方法这两种行为。

```go
func main() {
	a := A{name: aws.String("A")}
	b := &A{name: aws.String("B")}
	// normal function
	a.foo()

	a.bar() // equal to (&a).bar()
	// actually do &a,
	// not work if a can not address, for example map[0].bar()

	// normal function
	b.bar()

	b.foo() // equal to (*b).foo()
	// actually use *b, and method will copy *b
	// not work if a is nil, since you can not got the object after nil
}
```

结构体调用指针方法在取不到结构体对应指针的时候调用会失败，比如`map`里的结构体

指针为`nil`的时候无法调用结构体方法, 但是可以调用指针方法

### 方法集概念

看起来接受者是结构体还是指针并没有多少区别, 那么为什么书上要说

> 指针的方法集是全部的方法
>
> 结构体集是结构体接收者方法

因为在go里可以将一个方法转化为函数

```go
func main() {
    // we have a concept name: method collection
	// A only have receive struct method
	// *A have receive struct method and pointer method
	Foo := A.foo

	Foo2 := (*A).foo
	Bar := (*A).bar

	Foo(a)
	Bar(&a)

	Foo2(b)
	Bar(b)
}
```



深入了解之后还是很清楚的,对不对?