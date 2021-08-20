#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Python version:
# Memo：本程序用于远程设置比天科技采集仪，16进制发送折腾了很久才搞定，主要不是字符转16进制，而是直接拼成16进制。
# 改进了串口接收数据的等待机制，这样不需要设定延时。
# Programe by:Hxj
# Date:2020-10

import serial



def readSerial(c):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=3)
    if not ser.isOpen(): ser.open()
    print('waiting data...')
    while True:
        if ser.inWaiting() > 0:  # 缓存中有数据
            s = ser.readline()
            hexstr = s.hex()
            ser.close()
            return hexstr
        else:
            continue



def writeSerial(c, data):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=5)
    if not ser.isOpen(): ser.open()
    value =bytes.fromhex(data) # 字符串转换16进制格式
    print('sent out：', value)
    result = ser.write(value)
    ser.close()
    return result


def settime(port):
    # 设置时间
    while True:
        data = input('设置时间：yy-mm-dd hh:mm')
        data = data.replace('-', '')
        data = data.replace(' ', '')
        data = data.replace(':', '')
        data = '5501' + data + 'BB'
        if len(data) == 16:
            writeSerial(port, data)
            rd = readSerial(port)
            print('feedback:', rd)
            break
        else:
            print('输入格式错误')
            continue
    return


def setinterval(port):
    # 传输间隔
    while True:
        data = input('设置时间间隔：分钟')
        data = data.zfill(4)
        data = '5502' + data + '000000BB'
        print(data)
        if len(data) == 16:
            writeSerial(port, data)
            rd = readSerial(port)
            print('feedback:', rd)
            break
        else:
            print('输入格式错误')
            continue
    return


def setbaud(port):
    while True:
        # 设置波特率
        data = input('设置波特率：1=2400,2-4800,3-9600,4-19200,5-38400')
        if len(data) == 1:
            data = data.zfill(4)
            data = '5503' + data + '000000BB'
            print(data)
            writeSerial(port, data)
            rd = readSerial(port)
            print('feedback:', rd)
            break
        else:
            print('输入格式错误')
            continue


def setID(port):
    # 设置主机号
    while True:
        data = input('设置主机号：0001-1000')
        data = data.zfill(4)
        data = '5504' + data + '000000BB'
        print(data)
        if len(data) == 16:
            writeSerial(port, data)
            rd = readSerial(port)
            print('feedback:', rd)
            break
        else:
            print('输入格式错误')
            continue


def setSenNum(port):
    # 设置传感器数量
    while True:
        data = input('设置传感器数量：1-16')
        data = data.zfill(4)
        data = '5505' + data + '000000BB'
        print(data)
        if len(data) == 16:
            writeSerial(port, data)
            rd = readSerial(port)
            print('feedback:', rd)
            break
        else:
            print('输入格式错误')
            continue


def setSenType(port):
    # 设置传感器类型
    while True:
        data = input('设置传感类型：通道-类型（常用类型1-裂缝，4-双向倾斜带温度，5-三通道应变，6-温湿度，9-单通道应变带温度，18-德尔森静力水准，19-鲲鹏位移计，26-激光静力水准）')
        if '-' in data:
            data = data.split('-')
            data1 = data[0].zfill(2)
            data2 = data[1].zfill(2)
            data = '5506' + data1 + data2 + '000000BB'
            print(data)
            writeSerial(port, data)
            rd = readSerial(port)
            print('feedback:', rd)
            break
        else:
            print('输入格式错误')
            continue


def main():
    while True:
        port = input('输入串口号：1-n, 0-exit:')
        if port == '0' : exit()
        select = input('选择：1-时间设置，2-时间间隔，3-波特率，4-主机编号，5-传感器个数，6-传感器类型,0-退出 :')
        if select == '1':
            settime(port)
        elif select == '2':
            setinterval(port)
        elif select == '3':
            setbaud(port)
        elif select == '4':
            setID(port)
        elif select == '5':
            setSenNum(port)
        elif select == '6':
            setSenType(port)
        elif select == '0':
            break
        else:
            continue


if __name__ == '__main__':
    main()
