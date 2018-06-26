# PureGithubBolg

效果请看: <https://petelin.github.io/2016/07/ReadMe.html>

来源于[王垠的博客](http://www.yinwang.org/)，非常简单优雅的博客，使用markdown写作，可以自定义css样式。
更多的是一种思路,markdown 就是 html,我们只要自定义标签的样式,就可以做自己想要的东西.简单而高效.

##介绍文档

### 你只需要四种样式
1. 支持二级到六级标题
2. 支持代码上色
3. 支持图片
4. 支持数字标题
5. [不建议]支持原生html

代码

```python
print("hello world")
```

图片

![简单](http://img.52jbj.com/uploads/allimg/150606/co150606150444-0.jpg)

再来一大段文字

抛去样式,间间单单的写文章,样式这种东西顺眼就好.什么标签啊,分类啊,都抵不过一篇有价值的文章,博客是用来分享东西.要记录知识,请用云笔记.

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
