## Go 的一道题

翻公司的Go文档, 翻到如何深入学习Go, 然后这帮人一步一步给了很多文档.

其中一道题非常有意思, 只适合面试装逼用. 综合了很多Go的基本概念在里面.





请问这个输出是什么? 

```Go
package main

import (  
    "fmt"
    "time"
)

type field struct {  
    name string
}

func (p *field) print() {  
    fmt.Println(p.name)
}

func main() {  
    data := []*field{{"one"},{"two"},{"three"}}

    for _,v := range data {
        go v.print()
    }

    time.Sleep(3 * time.Second)
}
```

1. 如果你答 "three", "three", "three", 那么你只考虑了其中一个点.
2. 如果你觉得这个题很简单就是 1,2,3, 那么你不是Go的高级开发, 就是啥都不会......
3. 即使你答 "One", "Two", "Three", 那么我还可以偷偷装逼说, Goroutine执行顺序是不一定的.漏了吧...

答案是: 如果在多核机器上执行, 且`GOMAXPROCS > 1`, 则为不确定顺序的"One", "Two", "Three"



这里面有多少点呢, 我来罗列一下

1. `for range`每次迭代的item, 在下次迭代的时候回重复赋值, 而不是创建一个新的

2. Go的方法集问题, 调用`v.print`其实就是调用 `print(v)`

   ```go
   type field struct {  
       name string
   }
   func (p field) print() {
   	fmt.Println(p.name)
   }
   func main() {
   	data := []field{{"one"}, {"two"}, {"three"}}
   
   	for _, v := range data {
   		go v.print()   // 会怎么样?
   	}
   
   	time.Sleep(3 * time.Second)
   	//goroutines print: one, two, three
   }
   ```

3. Go只有数值传递, 以及编译器会帮你做 &v, 使得你能调用print

   ```go
   type field struct {  
       name string
   }
   func (p *field) print() {  
       fmt.Println(p.name)
   }
   func main() {  
       data := []field{{"one"},{"two"},{"three"}}
   
       for _,v := range data {
           go v.print()   // 会怎么样?
       }
   
       time.Sleep(3 * time.Second)
       //goroutines print: three, three, three
   }
   ```

4. go/defer 关键字会先计算参数的值

   ```go
   type field struct {  
       name string
   }
   func (p *field) print() {  
       fmt.Println(p.name)
   }
   func main() {  
       data := []field{{"one"},{"two"},{"three"}}
   
       for _,v := range data {
           go func(){v.print()} // 会怎么样?
       }
   
       time.Sleep(3 * time.Second)
   }
   ```



其实这些都是很基础的东西, 放在一起就可以把人搞懵逼. 平时开发, 还是

`v:=v`

`func(v interface{}){}(v)` 

多用着, 别给自己找麻烦.