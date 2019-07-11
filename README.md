# PureGithubBolg

静态博客生成器, 将你写的markdown发布到GitHub的page中. [例如](https://petelin.github.io/)

样式来源于[王垠的博客](http://www.yinwang.org/)，简单优雅的博客，也可以自定义css样式.


### 链接
[样式和Readme](https://petelin.github.io/2016/07/ReadMe.html) 


### 怎么使用
1. clone 代码

    ```
    git clone https://github.com/Petelin/PureGithubBolg.git
    ```
2. 在`post`中添加markdown文件

3. 更改`pure.py`中的`website_dir`变量为你的`github page`(需要你自己创建一个github page,然后克隆到本地,不要克隆我的)文件夹路径.

4. 运行 `python3 pure.py`

#### 配置

```python
# 将产生的所有文件输出到page文件夹下
website_dir = "绝对路径/xxx.github.io"

jinja_env.globals["title"] = "博客名字"

# 网站头像
jinja_env.globals["icon"] = "直接输入文件名字(直接放在static/images下)"

# 直接在后面添加社交账号即可
jinja_env.globals["sociallist"] = (("github", "https://github.com/Petelin"),)
```

#### 代码结构

```
PureGithubBolg
├── README.md
├── requirements # 依赖包
├── post # 将你想要发布的文章放在这个文件夹下,文件结构直接被映射为url地址
├── pure.py # 所有的代码
├── static # 如果你想改样式,修改main.css 和 home.css
└── templates # 模板文件
```

#### 库
使用 [markdown2](https://github.com/trentm/python-markdown2) + `fenced-code-blocks` 插件

[更换代码高亮颜色,点击链接找到一个css,替换codehighlight.css](https://github.com/richleland/pygments-css)


#### 欢迎交流
任何问题,欢迎issue
