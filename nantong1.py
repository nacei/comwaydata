#！/user/bin/python
# -*- coding:UTF-8 -*-
# use comway map to com port，then read data from com
# com read and save to mysql for 南通
# python 3.x
# programer: hanxiaojian
# 2020.11
import pymysql
import serial
import binascii
import datetime
import time,sys



def insert(data): #数据库写入模块
    db = pymysql.connect("njgdsp.oicp.net","root","song","comway",charset='utf8')#连接数据库
    cursor = db.cursor() #创建数据库操作对象

    #Sql语句
    sql = "insert into nantong(time,number,x1,y1,t1,x2,y2,t2,level,level2,level3) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10])

    try:
        cursor.execute(sql) #执行sql语句

        db.commit() #提交事务到数据库
        print("保存进数据库成功")

    except:
        db.rollback()#事务回滚
        print("保存进数据库失败")
    db.close()


def bin(l): #获取数据
    s = serial.Serial(l,12000,timeout = 10) #连接端口
    if not(s.isOpen()): #判断com端口是否打开
        s.open()
    t = True        #判断标准
    data = ""
    i = 0
    j = 19
    dataAll = []
    while t :
        time.sleep(1)
        n = s.inWaiting()
        if n > 0:
            today = datetime.date.today()#获取当前日期
            now = time.strftime("%H:%M:%S")#获取当前时间
            timing = str(today) +" " + str(now)
            data = s.read(s.inWaiting()) #接受数据
            datahex = binascii.b2a_hex(data) #进行转码
            datahex=str(datahex.upper())
            # print(datahex)
            startposition = datahex.find('AA')
            endposition = datahex.rfind('BB')
            data = datahex[startposition+2:endposition]#截取数据
            print(data)
            host_id = data[16:20]   #获取主机ID
            print(host_id)
            sensor = data[22:endposition] #获取传感器数据
            if(len(sensor) > 0 ):   #获取到数据，解析
                #解析第一个传感器数据
                number = host_id
                print(number)
                x1 = sensor[4:12]
                y1 = sensor[12:20]
                t1 = sensor[20:28]
                x2 = sensor[32:40]
                y2 = sensor[40:48]
                t2 = sensor[48:56]
                level = sensor[60:68]
                level2 = sensor[80:88]
                level3 = sensor[100:108]
                if(x1[0:2] == "00"):
                    x1 = str(int(x1[2:])/10000)
                else:
                    x1 = "-"  + str(int(x1[2:])/10000)
                if(y1[0:2] == "00"):
                    y1 = str(int(y1[2:])/10000)
                else:
                    y1 = "-" + str(int(y1[2:])/10000)

                if(t1[0:2] == "00"):
                    t1 = str(int(t1[2:])/10000)
                else:
                    t1 = "-" + str(int(t1[2:])/10000)
                if(x2[0:2] == "00"):
                    x2 = str(int(x2[2:])/10000)
                else:
                    x2 = "-"  + str(int(x2[2:])/10000)

                if(y2[0:2] == "00"):
                    y2 = str(int(y2[2:])/10000)
                else:
                    y2 = "-" + str(int(y2[2:])/10000)
                if(t2[0:2] == "00"):
                    t2 = str(int(t2[2:])/10000)
                else:
                    t2 = "-" + str(int(t2[2:])/10000)
                if(level[0:2] == "00"):
                    level = str(int(level[2:])/100)
                else:
                    level = "-"  + str(int(level[2:])/100)
                if(level2[0:2] == "00"):
                    level2 = str(int(level2[2:])/100)
                else:
                    level2 = "-"  + str(int(level2[2:])/100)
                if(len(level3)>0):
                    if(level3[0:2] == "00"):
                        level3 = str(int(level3[2:])/100)
                    else:
                        level3 = "-"  + str(int(level3[2:])/100)
                data_01 = [timing,number,x1,y1,t1,x2,y2,t2,level,level2,level3] #数据写入list
                dataAll.append(data_01) #写入总list
                aa='%s获取%s号数据OK'%(timing,number)
                print(aa)
                bb=aa.encode()
                bb=binascii.b2a_hex(bb)
                s.write(bb) #写入数据
                return dataAll
                t = False
            else :  #没有获取到数据终止循环
                return dataAll
                t = False
    s.close()


while True:
    time.sleep(1)
    # m=input('请输入你要监控的端口号：')
    # #n = input('请输入你要监控的传感器代号：')
    # l='COM%s'%m
    dataAll = bin('com4')


    for n in range(len(dataAll)) :

        print(dataAll[n])

        insert(dataAll[n])

    #time.sleep(600)







