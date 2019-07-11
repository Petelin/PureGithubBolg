## linux 系统网络栈调优

默认情况下, 系统内核并没有将参数调优到大流量网络传输模式下.

比如

`net.ipv4.tcp_max_syn_backlog` 代表并发连接数, 默认就很小1024.

`net.core.netdev_max_backlog` 调大可以帮助应对网络流量突然爆发. 让更多数据在内核排队.



> socket系统读写缓冲区

net.core.rmem_default = 131072

net.core.rmem_max = 2097152

net.core.wmem_default = 131072

net.core.wmem_max = 2097152

> tcp socket 系统读写缓冲区

net.ipv4.tcp_rmem = 4096  65536  4088000

net.ipv4.tcp_wmem = 4096  65536  4088000

> tcp时间窗扩展

net.ipv4.tcp_window_scaling = 1

> tcp syn队列大小

sysctl -w net.ipv4.tcp_max_syn_backlog="2048"

