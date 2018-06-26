## epoll 边沿触发和水平触发

在学习`socket`处理模式的时候, 听到过epoll这种模式,当时对他的理解就是, 一个操作系统提供的事件注册,通知功能,你告诉操作系统你想要监听`fd`的什么动作,循环执行`poll`的时候,操作系统上一次poll之后触发的操作返回给你,如果没有就等到有再返回.

epoll的好处

1. 在一个线程中可以处理多个文件描述符(处理多个连接)
2. 是能够处理更多的文件描述符, select只能处理1024个 
3. 3.不需要遍历所有的文件描述符就可以知道哪些有通知.性能更好.



epoll的编程范式有两种,一种是水平触发, 一种是边缘触发.

### 水平触发和边缘触发

最早接触这两个词其实是从电路信号中学到的, 水平触发是level trigger 一旦触发就能维持那个level. 而边缘触发edge trigger 就是一次稍纵即逝的变化.

ET: `___1____`  LT: `____1------`



### epoll

#### 水平触发的例子: 

```python
 1  import socket, select
 2
 3  EOL1 = b'\n\n'
 4  EOL2 = b'\n\r\n'
 5  response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
 6  response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
 7  response += b'Hello, world!'
 8
 9  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
10  serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
11  serversocket.bind(('0.0.0.0', 8080))
12  serversocket.listen(1)
13  serversocket.setblocking(0)
14
15  epoll = select.epoll()
16  epoll.register(serversocket.fileno(), select.EPOLLIN)
17
18  try:
19     connections = {}; requests = {}; responses = {}
20     while True:
21        events = epoll.poll(1)
22        for fileno, event in events:
23           if fileno == serversocket.fileno():
24              connection, address = serversocket.accept()
25              connection.setblocking(0)
26              epoll.register(connection.fileno(), select.EPOLLIN)
27              connections[connection.fileno()] = connection
28              requests[connection.fileno()] = b''
29              responses[connection.fileno()] = response
30           elif event & select.EPOLLIN:
31              requests[fileno] += connections[fileno].recv(1024)
32              if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
33                 epoll.modify(fileno, select.EPOLLOUT)
34                 print('-'*40 + '\n' + requests[fileno].decode()[:-2])
35           elif event & select.EPOLLOUT:
36              byteswritten = connections[fileno].send(responses[fileno])
37              responses[fileno] = responses[fileno][byteswritten:]
38              if len(responses[fileno]) == 0:
39                 epoll.modify(fileno, 0)
40                 connections[fileno].shutdown(socket.SHUT_RDWR)
41           elif event & select.EPOLLHUP:
42              epoll.unregister(fileno)
43              connections[fileno].close()
44              del connections[fileno]
45  finally:
46     epoll.unregister(serversocket.fileno())
47     epoll.close()
48     serversocket.close()
```

当有`epollin`事件的时候, 我们去读, 这个时候有可能没有读完全部的信息, 没关系, 下一次poll还会返回这个事件让你接着读,代码写的很省心.

当有`epollout`的时候, 一次没写完同理也可以接着写. 但是当你写完之后,注意要关闭对读事件的监听,否则他每次都会通知你可写了, 即使你不想写.这样的效率就很低.

#### 优缺点

水平触发的优点是只要时间没有处理完,就会一直收到通知, 编程简单,不容易丢事件.

缺点是性能不好, 需要频繁调用epoll.modify, 对底层红黑树修改是很麻烦的.



#### 边缘触发

```python
 1  import socket, select
 2
 3  EOL1 = b'\n\n'
 4  EOL2 = b'\n\r\n'
 5  response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
 6  response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
 7  response += b'Hello, world!'
 8
 9  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
10  serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
11  serversocket.bind(('0.0.0.0', 8080))
12  serversocket.listen(1)
13  serversocket.setblocking(0)
14
15  epoll = select.epoll()
16  epoll.register(serversocket.fileno(), select.EPOLLIN | select.EPOLLET)
17
18  try:
19     connections = {}; requests = {}; responses = {}
20     while True:
21        events = epoll.poll(1)
22        for fileno, event in events:
23           if fileno == serversocket.fileno():
24              try:
25                 while True:
26                    connection, address = serversocket.accept()
27                    connection.setblocking(0)
28                    epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
29                    connections[connection.fileno()] = connection
30                    requests[connection.fileno()] = b''
31                    responses[connection.fileno()] = response
32              except socket.error:
33                 pass
34           elif event & select.EPOLLIN:
35              try:
36                 while True:
37                    requests[fileno] += connections[fileno].recv(1024)
38              except socket.error:
39                 pass
40              if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
41                 epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
42                 print('-'*40 + '\n' + requests[fileno].decode()[:-2])
43           elif event & select.EPOLLOUT:
44              try:
45                 while len(responses[fileno]) > 0:
46                    byteswritten = connections[fileno].send(responses[fileno])
47                    responses[fileno] = responses[fileno][byteswritten:]
48              except socket.error:
49                 pass
50              if len(responses[fileno]) == 0:
51                 epoll.modify(fileno, select.EPOLLET)
52                 connections[fileno].shutdown(socket.SHUT_RDWR)
53           elif event & select.EPOLLHUP:
54              epoll.unregister(fileno)
55              connections[fileno].close()
56              del connections[fileno]
57  finally:
58     epoll.unregister(serversocket.fileno())
59     epoll.close()
60     serversocket.close()
```

因为边沿触发只会通知一次,所以对每一个事件都要处理干净, 

1. accept: 有两个client并发连接server, 此时只会通知一次, 读的时候, 要accept两次.
2. epollin: 只会通知一次有数据到来, 如果一次没读干净, 之后就不会通知了
3. epollout: 写也是只通知一次可以写了, 以后不再通知你可以写 



性能好,减少epoll的调用次数, 但是编程模式麻烦,容易丢事件



### 总结

没啥, 过了好久终于仔细看了看这个东西.









