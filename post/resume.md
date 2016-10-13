
## 张晓林的后端简历

### 经历
1. 2016/4 – 2016/6 | 北京至信普林科技 | python后端开发实习

    数据嗨客大数据平台二期开发,服务器搭建,解决前后端技术上遇到问题。

2. 2015/9 – 至今 | ebtbu微信公众号开发

    独立开发web页面,提供查成绩、查课表等功能以及失物发布、招领平台,教务管理系统寒暑假每天访问量最高10W。

3. 2013/9 – 2017/6 | 北京工商大学 | 本科

### 项目

1. 2016/4 – 2016/6 | [数据嗨客平台](http://www.hackdata.cn/)
    1. 主要负责开发教室模块，部署管理服务器。特别的，我实现了单点登录，使用rqworker任务队列异步计算结果，使用rlimit 限制内存，定时器限制时间。为了快速搭建环境、部署项目、迁移数据，我编写了fabric脚本。项目用到Jupyter，但是安全性不够，我使用Docker封装了一个有Python和R核心用于科学计算的Jupyter。我还优化了几个SQL语句，查询时间从50ms以上减少到10ms。我发现使用 装饰器可以大大减少了重复代码。
    2. 用到:CentOS、Nginx、Django、Gunicorn、MySQL、MongoDB、Redis(RQ)、Memcache。

2. [教务系统实时爬虫](https://github.com/Petelin/BTBU-Spider)

    1. 因为我校教务网站只能用内网登录,只能用IE浏览器,不适配手机。登录操作步骤太多。所以我开发了
一键教务管理。
    2. 难点在于:验证码识别(做到了100%)、封IP、数据解析,结构化。
    3. 使用Nginx +Ajax+Flask,由Nginx处理前端页面,使用了免费代理,顺利的上线。 

3. 小游戏

    1. 以三角形为基础元素的“俄罗斯方块”,java swing 实现,用 4 位支持自表示一个最小三角形,支持自定 义组成。可选难度,暂停,加速,得分,下一个方块等。
    2. 暗黑迷宫,python tkinter 只能看见主角身边的一定范围的地图,地图内随机出口和奖励,奖励是,在通 往出口的路径上铺满金币。

### 技能

1. 熟练度:Python / MySQL / Linux / Git > Java / Django / Flask > C / Lisp / Redis / Docker / Html > / JS / Css
2. 英语4，6级，无障碍阅读技术文档，GitHub，Stack Overflow。

### 个人

有很强自学能力,喜欢折腾新东西,代码洁癖,对每个技术有自己的认识。

### 联系我

实习时间: 即日 -- 2017/6

电话: 18514281433

岗位: python后端开发

邮箱: [petelin1120@gmail.com](mailto:petelin1120@gmail.com)

坐标: 北京


### [下载pdf版本](https://petelin.github.io/resume.pdf)
