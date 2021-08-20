#!/usr/bin/python
# -*- coding:UTF-8 -*-
# use comway map to com port，then read data from com
# com read and save to mysql for 无锡红旗新村
# python 3.x
# programer: hanxiaojian
# 2020.6
_author_ = 'hanxiaojian njtech'
import json
import time
import pymysql
import serial


def connetDB():
    try:
        # 连接数据库
        conn = pymysql.connect(host='njgdsp.oicp.net', user='root', password='song', port=3306, db='test',
                               charset='utf8')
        conn.autocommit(True)
        cur = conn.cursor()
        return (conn, cur)
    except:
        print('failue connect to db')
        return None


def colseDB(conn, cur):
    conn.close()
    cur.close()


def insertDB(devId, projectID, devType, saveTime, jdata):
    (db, cursor) = connetDB()
    # print(db,cursor)
    sql = 'INSERT INTO wuxi(projectID,devId,devType,saveTime,jData) VALUES (%s,%s,%s,%s,%s)'
    try:
        if cursor.execute(sql, (projectID, devId, devType, saveTime, jdata)):
            db.commit()
            print('successful saved.')
    except:
        print('failed')
        db.rollback()
    cursor.execute(sql)
    db.comit()
    print("data saved.")
    return


def readSerial(c):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=1)
    if not ser.isOpen(): ser.open()
    print('waiting data...无锡红旗新村 ')
    while True:
        time.sleep(1)
        if ser.inWaiting() > 0:  # 缓存中有数据
            s = ser.readline()
            hexstr = s.hex()
            return hexstr
        else:
            continue
    ser.close()


# 定义传感器类别字典
Sensor_Types = {'01': '裂缝', '02': '单轴倾斜', '19': '静力水准仪', '04': '双轴倾斜带温度', '05': '应变', '06': '温湿度'}
t = 0
while t < 2:
    try:
        # 采集数据
        data = readSerial(5)
        # print(data)
        # 计算机本地时间
        insertTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
        print(insertTime)
        # 解析数据
        data = data[6:]
        # acqtime = "20" + data[0:2] + "-" + data[2:4] + "-" + data[4:6] + " " + data[6:8] + ":" + data[8:10] + ":" + data[10:12]  # 采集仪日期
        data = data[12:]
        devId = data[0:4]  # 采集仪编号 入库
        print(devId)
        projectID = '无锡红旗花园'  # 入库
        devType = 'BT-16'  # 入库
        data = data[4:]
        Sensor_All = int(data[0:2])  # 传感器数量
        data = data[2:]
        dataout = []
        klist04 = ['ch', 'type', 'datax', 'datay', 'temp']
        klist19 = ['ch', 'type', 'data']
        klist01 = ['ch', 'type', 'data']
        for each in range(0, Sensor_All):
            da = []
            sn = str(data[0:2])  # numID
            st = str(data[2:4])  # type
            Sensor_T = Sensor_Types[st]
            da.append(sn)
            da.append(Sensor_T)
            if st == "04":  # 双向倾角
                for i in range(0, 3):  # 有x,y,t 3组数据
                    if int(data[4:6]) == 0:
                        dataX = float(data[6:8] + data[8:10] + data[10:12]) / 10000
                    elif int(data[4:6]) == 1:
                        dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 10000
                    else:
                        dataX = -1
                    da.append(dataX)
                    data = data[8:]
                data = data[4:]
                eachdata = dict(zip(klist04, da))
                dataout.append(eachdata)
            elif st == '19':  # 静力水准
                if int(data[4:6]) == 0:
                    dataX = float(data[6:8] + data[8:10] + data[10:12]) / 100
                elif int(data[4:6]) == 1:
                    dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 100
                else:
                    dataX = -1
                da.append(dataX)
                data = data[20:]
                eachdata = dict(zip(klist19, da))
                dataout.append(eachdata)
            elif st == '01':  # 裂缝
                if int(data[4:6]) == 0:
                    dataX = float(data[6:8] + data[8:10] + data[10:12]) / 10000
                elif int(data[4:6]) == 1:
                    dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 10000
                else:
                    dataX = -1
                da.append(dataX)
                data = data[12:]
                eachdata = dict(zip(klist01, da))
                dataout.append(eachdata)
        # print(dataout)
        jdata = json.dumps(dataout, ensure_ascii=False)  # 入库 jdata
        print('jdata=', jdata)
        print(type(jdata))
        insertDB(devId, projectID, devType, insertTime, jdata)
        time.sleep(1)
    except:
        time.sleep(1)
        continue
    time.sleep(10)
