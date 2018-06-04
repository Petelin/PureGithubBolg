## 多进程IPC与Python支持

### linux下进程间通信的几种主要手段简介:

1. 管道（Pipe）及有名管道（named pipe）：管道可用于具有亲缘关系进程间的通信，有名管道克服了管道没有名字的限制，因此，除具有管道所具有的功能外，它还允许无亲缘关系进程间的通信；

2. 信号（Signal）：信号是比较复杂的通信方式，用于通知接受进程有某种事件发生，除了用于进程间通信外，进程还可以发送信号给进程本身；linux除了支持Unix早期信号语义函数sigal外，还支持语义符合Posix.1标准的信号函数sigaction（实际上，该函数是基于BSD的，BSD为了实现可靠信号机制，又能够统一对外接口，用sigaction函数重新实现了signal函数）；

3. 报文（Message）队列（消息队列）：消息队列是消息的链接表，包括Posix消息队列system V消息队列。有足够权限的进程可以向队列中添加消息，被赋予读权限的进程则可以读走队列中的消息。消息队列克服了信号承载信息量少，管道只能承载无格式字节流以及缓冲区大小受限等缺点。

4. 共享内存：使得多个进程可以访问同一块内存空间，是最快的可用IPC形式。是针对其他通信机制运行效率较低而设计的。往往与其它通信机制，如信号量结合使用，来达到进程间的同步及互斥。

5. 信号量（semaphore）：主要作为进程间以及同一进程不同线程之间的同步手段。

6. 套接口（Socket）：更为一般的进程间通信机制，可用于不同机器之间的进程间通信。起初是由Unix系统的BSD分支开发出来的，但现在一般可以移植到其它类Unix系统上：Linux和System V的变种都支持套接字。

python 原生支持的有:1, 2, 6.
信号这个比较简单, 一种注册监听机制.本文不涉及

管道是可以通过 (mutiprocessing.Pipe) 获得, 由c写的

套接字这个通过 AF_UNIX协议 就可以完成啦, 和网络编程类似的~

其实仔细想想还有第三种即, 利用文件, 生产者写到文件中, 消费者从文件中读.(简单化成一个生产者, 一个消费者, 否者竞争关系有点复杂.), 当然我们知道文件写入肯定很慢, 但是有多慢还是要测试一下的.

### 工具函数:

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   zhangxiaolin
#   E-mail  :   petelin1120@gmail.com
#   Date    :   17/8/17 12:08
#   Desc    :   ...
# through pipe 269667.7903995848 KB/s

data_size = 8 * 1024  # KB


def gen_data(size):
    onekb = "a" * 1024
    return (onekb * size).encode('ascii')
```

### 管道:

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   zhangxiaolin
#   E-mail  :   petelin1120@gmail.com
#   Date    :   17/8/17 12:08
#   Desc    :   ...
import multiprocessing

from mutiprocesscomunicate import gen_data, data_size


def send_data_task(pipe_out):
    for i in range(data_size):
        pipe_out.send(gen_data(1))
    # end EOF
    pipe_out.send("")
    print('send done.')


def get_data_task(pipe_in):
    while True:
        data = pipe_in.recv()
        if not data:
            break
    print("recv done.")


if __name__ == '__main__':
    pipe_in, pipe_out = multiprocessing.Pipe(False)
    p = multiprocessing.Process(target=send_data_task, args=(pipe_out,), kwargs=())
    p1 = multiprocessing.Process(target=get_data_task, args=(pipe_in,), kwargs=())

    p.daemon = True
    p1.daemon = True
    import time

    start_time = time.time()
    p1.start()
    p.start()
    p.join()
    p1.join()
    print('through pipe', data_size / (time.time() - start_time), 'KB/s')
```
注意这个地方 Pipe(True)默认为双工的, 然而标准的是单工的, 单工缓冲区大小在OSX上有64KB, 设置缓存区是为了协调流入流出速率, 否者写的太快, 没人取走也是浪费.
结果: `through pipe 99354.71358973449 KB/s`

### file

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
import os
from mutiprocesscomunicate import gen_data, data_size


def send_data_task(file_name):
    # 是否同步写入磁盘, 如果同步写进去, 慢的一 b, 牛逼的是, 不同步写进去, 也可以读.操作系统厉害了.
    # os.sync()
    with open(file_name, 'wb+') as fd:
        for i in range(data_size):
            fd.write(gen_data(1))
            fd.write('\n'.encode('ascii'))
            # end EOF
        fd.write('EOF'.encode('ascii'))
    print('send done.')


def get_data_task(file_name):
    offset = 0
    fd = open(file_name, 'r+')
    i = 0
    while True:
        data = fd.read(1024)
        offset += len(data)
        if 'EOF' in data:
            fd.truncate()
            break
        if not data:
            fd.close()
            fd = None
            fd = open(file_name, 'r+')
            fd.seek(offset)
            continue
    print("recv done.")


if __name__ == '__main__':
    import multiprocessing

    pipe_out = pipe_in = 'throught_file'
    p = multiprocessing.Process(target=send_data_task, args=(pipe_out,), kwargs=())
    p1 = multiprocessing.Process(target=get_data_task, args=(pipe_in,), kwargs=())

    p.daemon = True
    p1.daemon = True
    import time

    start_time = time.time()
    p1.start()
    import time

    time.sleep(0.5)
    p.start()
    p.join()
    p1.join()
    import os
    print('through file', data_size / (time.time() - start_time), 'KB/s')
    open(pipe_in, 'w+').truncate()
```

有两个点, 一个是, 打开文件之后, 如果有人在写入, 需要重新打开才能发现新内容, 另外需要设置offset,只读取新内容.

!!!重点, 测试的时候这个速度有 
`through file 110403.02025891568 KB/s`这么多, 甚至比管道还要高一点, 这是怎么回事呢?

> quite often file data is first written into the page cache (which is in RAM) by the OS kernel.

并没有被写入文件, 而是被写到内存中了, 随后(不会通知你)被操作系统调度写入文件.操作系统比较厉害的是, 即使没有写到文件中, 读写仍然像写到文件中一样.

如果设置了 `os.sync()`, 所有写操作立即执行, 会发现慢的...类似于卡死.

### 本地socket
```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   zhangxiaolin
#   E-mail  :   petelin1120@gmail.com
#   Date    :   17/8/17 12:08
#   Desc    :   ...
import multiprocessing
import os
import socket

from mutiprocesscomunicate import gen_data, data_size


minissdpdSocket = '/tmp/m.sock'  # The socket for talking to minissdpd


def send_data_task():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            os.remove(minissdpdSocket)
        except OSError:
            pass

        server.bind(minissdpdSocket)

        server.listen(1)

        conn, _ = server.accept()
        with conn:
            for i in range(data_size):
                conn.send(gen_data(1))
            conn.shutdown(socket.SHUT_WR)
            print('send done.')


def get_data_task():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(minissdpdSocket)
        client.shutdown(socket.SHUT_WR)
        while True:
            data = client.recv(1024)
            if not data:
                break
        print("recv done.")


if __name__ == '__main__':
    p = multiprocessing.Process(target=send_data_task, args=(), kwargs=())
    p1 = multiprocessing.Process(target=get_data_task, args=(), kwargs=())

    p.daemon = True
    p1.daemon = True
    import time

    start_time = time.time()
    p.start()

    p1.start()
    p.join()
    p1.join()
    print('through pipe', data_size / (time.time() - start_time), 'KB/s')
```

本地socket, 会走传输层也就是被tcp或者udp封装一下,到网络层,网络层自己有路由表, 发现是本机, 则走本地回环接口, 不经过物理网卡, 发到接受队列中去.

这个速度不稳定, 最快有```through socket 261834.36615940317 KB/s```

## 参考

1. [深刻理解Linux进程间通信（IPC）](https://www.ibm.com/developerworks/cn/linux/l-ipc/)
2. [文件没有直接写入磁盘](https://stackoverflow.com/questions/45727981/why-write-to-a-file-is-faster-than-mutiprocessing-pipe#comment78415844_45727981)
3. [pipe缓存区大小](https://unix.stackexchange.com/questions/11946/how-big-is-the-pipe-buffer/11954#11954)



