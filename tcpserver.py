#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 接受刘凯华设备数据MQTT协议
import socket
import threading
import time
# 创建socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 绑定ip port
s.bind(("139.224.61.49", 5004))
# 使用socket创建的套接字默认的属性是主动的，
# 使用listen将其变为被动的，这样就可以接收别人的链接了
s.listen(5)
print("Waiting for connection...")
# 如果有新的客户端来链接服务器，
# 那么就产生一个新的套接字专门为这个客户端服务
# client_socket用来为这个客户端服务
# tcp_server_socket就可以省下来专门等待其他新客户端的链接
# 接收对方发送过来的数据
def tcplink(client_socket,addr):
    print("Accept new connection from %s:%s" % addr)
    insertTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
    while True:
        # 接收对方发送过来的数据
        recv_data = client_socket.recv(1024)  # 接收1024个字节
        if recv_data:
            print(insertTime,' Recived Data:', recv_data.decode('gbk'))
        else:
            break
    client_socket.close()
    print("Connection from %s:%s is closed" % addr)

while True:
    # 等待新的客户端连接
    client_socket, clientAddr = s.accept()
    t=threading.Thread(target=tcplink(client_socket,clientAddr))
    t.start()

s.close()