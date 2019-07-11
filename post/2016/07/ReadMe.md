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

![水滴](http://img2.imgtn.bdimg.com/it/u=1556814207,191248649&fm=21&gp=0.jpg)

再来一大段文字

抛去样式,间间单单的写文章,样式这种东西顺眼就好.什么标签啊,分类啊,都抵不过一篇有价值的文章,博客是用来分享东西.要记录知识,请用云笔记.

### 怎么使用
1. clone 代码

```
git clone https://github.com/Petelin/PureGithubBolg.git
```
2. 在`post`中添加markdown格式文件

3. 更改`pure.py`中的`website_dir`变量为你的github `page`文件夹路径

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
