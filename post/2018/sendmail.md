## 发送任意格式邮件与sendmail

#### send mail 是什么

`sendmail` 是一个命令, 同时也是一个有历史的`service` 你可以 `sudo service sendmail restart`

这个服务的作用是在你本机启动一个SMTP的服务器. 有了这个服务器, 你就可以和其他SMTP服务器交流.



自己搞一个SMTP的好处是,

1.  可以不受限制的发邮件. 我之前使用163的, 发的多了, 就会拦截不让发. 
2. 不用配置账号密码
3. 可以自定义from地址, 发件人姓名



### 因为最近使用go开发所以写了一个调用sendmail的库

遇到的问题

title不能有中文, 要用`echo "=?UTF-8?B?`echo 重新启动TRADE系统| base64`?="` 这样转化一下

sendmail设置header, 使用HTML格式, 是需要从stdin穿进去的, 没有参数可以配置

-f 发件人邮箱, 可以随意配置, 但是QQ的服务会检查你这个合不合法, 有一些域名是绑定了IP, 你不是这个IP的却使用qq.com发邮箱会被拒绝的. 