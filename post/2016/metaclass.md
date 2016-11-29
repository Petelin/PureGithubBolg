## python 元类

之前想清楚了写到了笔记中,最近看到python3.6又出了个`__init_subclass__`,之前的东西又全忘了.这次在总结一下.

### 以一个实用的实例

```python
#!/usr/bin/env python
class Type(object):
    print("运行到", "Type")

    def __init__(self, type_):
        print("set type", type_)

        self.type_class = type_

    def vaild(self, value):
        return isinstance(value, self.type_class)


class TypeCheckMeta(type):
    print("运行到", "TypeCheckMeta")

    def __new__(cls, name, bases, dict):
        print("元类 __new__")
        inst = super(TypeCheckMeta, cls).__new__(cls, name, bases, dict)
        inst._fileds = {}
        for k, v in dict.items():
            if isinstance(v, Type):
                inst._fileds.setdefault(k, v)
        return inst

    def __init__(cls, *args, **kwargs):
        print("元类 __init__")
        super(TypeCheckMeta, cls).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        print("元类 __call__")
        return super(TypeCheckMeta, self).__call__(*args, **kwargs)


class Test(metaclass=TypeCheckMeta):
    print("运行到", "Test")
    name = Type(str)
    age = Type(int)

    def __new__(cls, *args, **kwargs):
        print("类 __new__")
        print(args, kwargs)
        return super(Test, cls).__new__(cls)


    def __setattr__(self, key, value):
        print("类 __setattr__")
        if key in self._fileds:
            if not self._fileds[key].vaild(value):
                raise TypeError("invaild...")
        super(Test, self).__setattr__(key, value)

    def __init__(self, a):
        print("类 __init__")

    def __call__(self, *args, **kwargs):
        print("类 __call__")

t = Test(1)
print(t)
```
场景就是需要你对变量做强制性检查.

### 加载过程  
注释掉最后两行代码,会发现如下输出  

```python
运行到 Type
运行到 TypeCheckMeta
运行到 Test
set type <class 'str'>
set type <class 'int'>
元类 __new__
元类 __init__
```

首先,Python在加载的时候扫过整个文件.遇到类定义的时候如下执行:

1. 先找到改类的元类,然后调用元类的`__new__`方法,参数是`(类名where,类基类bases,类空间dict)`
2. 元类的`__new__`最终一定会调用内置类型`type.__new__`
3. `type.__new__`会调用元类的`__init__`创建出一个类对象放在内存中.至此类对象已经加载完成了.


### 执行过程  
现在我们来看看执行的  

```python
t = Test(1)
print(t)
```

1. `Test`是什么?是一个类啊,是经过上面的加载步骤生成的实例,所以`Test()`会调用元类的`__call__`方法.
2. 元类一定又得陷入`type.__call__`方法.
3. `type.__call__`方法调用类`__new__`方法.
4. 类的`__new__`方法一定又陷入`object.__new__`
5. `object.__new__`调用类的`__init__`方法,最终一个实例被创建出来了.

### 新的方法`__init_subclass__(self, k=...)`  

触发时机: 子类加载时触发.
具体的: 加载子类时发现父类定义了`__init_subclass__`方法,那么在元类`__new__`之后`__init__`之前调用这个`__init_subclass__`.(实现不是这样子的,应该是hook那种模式,先留空,然后注册那种).

这样就不需要写元类就可以修饰子类了.  

其传参数方式并没有什么魔法,

```python
class SubClass(Father, param="haha"):
    pass
```  

在传递给`__new__`的时候给现在要多一个位置参数


```python
def __new__(cls, name, bases, dict, **kwargs):
    pass
```

这样子`__init_subclass__`也可以获取到了.
