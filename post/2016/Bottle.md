## Bottle源码总结

从好友github上看到了Bottle这个框架,因其单文件,不依赖第三方,简介酷似flask,所以想要阅读一下源代码.代码写的很规整,一看就是特意调整过,专门为了让大家阅读.不想流水账一样记录过程,分享几个受用的点.

### import

官方给出的最小bottle应用:

```
from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080)
```

只要你import了bottle任何一个变量,整个bottle.py文件都会被解释器加载执行.只不过其他的变量并没有加载到local中.当你再次import的时候,并不会再次执行bottle.py而是直接将名字加载到命令空间. 所以from ... import ... 并没有减少时间或者空间的占用,只是避免污染命名空间而已.


### context local

刚接触到这个[名词](http://werkzeug.pocoo.org/docs/0.11/local/#module-werkzeug.local),这个命令并不是很合适,叫 thread local 更加合适,其实他就是`threading.local()`.是的作用域和线程绑定,你在线程A下给 `trd_local.a = 2`,在线程B根本看不到,完全隔离.实现上也很简单将变量和线程id进行绑定即可,在访问变量的时候判断一下当前线程id.

这里面有一个hack,官方的库threading只提供了线程版本,如果你要使用gevent之类的第三方协程是不起作用的.

解决的办法是打上猴子补丁
```
if not isinstance(threading.local(), local.local):
   msg = "Bottle requires gevent.monkey.patch_all() (before import)"
   raise RuntimeError(msg)
```
以前不是很理解为什么threading都需要打补丁,这下就明白了,不打的话换需要写多余的代码,判断一下到底从哪里import,打完就不需要了.

context local 用处很光, 比如request, response对象都是内部封装了他.这使得我们能够创建出一个 `thread-safe` 的变量. **一个全局的但是线程安全的变量.**

### http处理流程

根据python wsgi规范,我们只要提供一个这种接口

```
def handler(environ, start_response):
    """ Each instance of :class:'Bottle' is a WSGI application. """
    return self.wsgi(environ, start_response)
```

所以有这种类

```
class Bottle():
    def __call__(self, environ, start_response):       
        pass
```

这就完成了服务器传递到框架的过程.

### route, request, response

python在加载文件的时候,发现装饰器会立即执行装饰器的内容,此时就完成了url和view的绑定.

request和response 是在每个请求过来的时候bind(其实就是初始化一个context local对象),每个线程唯一.

### 自动reload

```
lockfile = os.environ.get('BOTTLE_LOCKFILE')
bgcheck = FileCheckerThread(lockfile, interval)
    with bgcheck:
        server.run(app)
    if bgcheck.status == 'reload':
        sys.exit(3)
```

FileCheckerThread是一个线程,用with是很合适的,可以自动start和join.


### 巧妙的cache装饰器

如果想给一个类的变量,加一个一次性缓存,有一个很巧妙地方法:

> 装饰器是一个property,设置__get__方法,使得类在访问属性的时候可以执行计算,在一次计算之后,直接self.__dict[func.__name__] = value,这样就覆盖了这个property,变成了真正有值的属性.
