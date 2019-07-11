## 通过cors政策来规避csrf

### csrf
大家应该很收悉csrf了,我就不赘述了.总结一下现在通用的几种防csrf的方法.

- 通过在生成的form里添加隐藏字段.优点是简单,直观.缺点:纯api网站无法使用.
- 后端将csrf_token写进cookie,前端获得到之后写进请求body里.优点:通用,api也可以使用.缺点:delete和put之类的方法发请求是没有body,不能校验.
- 前端将获得到的token写到自定义header中.目前来看是最好的解决方案,有人提到请求头可能不兼容

### cors
cors是浏览器执行的跨域政策.基础的我就不写了,分享两个特别的地方:

- 简单请求是先实实在在发送到服务器上,然后服务器做校验不合法直接打回来.
- 前端想要定义除了规定的Header之外任何header,都会直接变成复杂请求.

### 通过cors来规避csrf

做法很简单,让前端在每个请求前都加上

    crsf_avoid_header: whatever

服务器校验一下有没有这个header就好了.

原理就很简单了,我们知道恶意网站无论如何是不能设置这个header的,想设置先变成复杂请求,然后判断一下是否同源,只要你没有信任恶意网站,那么除了你自己没人能带着header成功访问.

我发现这个问题之后,在v2ex发了帖子,发现很多人根本没有理解csrf是什么,争论的根本不是一件事.无奈只能去英文社区寻找支持,果然质量就搞了很多.

我想出来的方法更简单,而且足以防范crsf,但是为什么没有成为更广泛的做法呢?

- crsf攻击比制定corf要早.(没求证)
- flash这个坑爹货能绕过.
- 双重验证更保险.还能一定程度上防小爬虫和重复提交.
- Http Request 分裂，一些浏览器实现上的问题或者bug.


资源:

https://security.stackexchange.com/questions/10227/csrf-with-json-post

http://blog.alutam.com/2011/09/14/jersey-and-cross-site-request-forgery-csrf/

http://security.stackexchange.com/questions/22903/why-refresh-csrf-token-per-form-request

http://security.stackexchange.com/questions/23371/csrf-protection-with-custom-headers-and-without-validating-token

