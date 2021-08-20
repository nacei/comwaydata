#!/usr/bin/python
# -*- coding:UTF-8 -*-
# use comway map to com port，then read data from com
# com read and save to mysql for 南通
# python 3.x
# programer: hanxiaojian
# 2020.6
_author_ = 'hanxiaojian njtech'
import serial
import json
import time
import pymysql

def connetDB():
    try:
        # 连接数据库
        conn = pymysql.connect(host='njgdsp.oicp.net', user='root', password='song', port=3306, db='comway',
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


def insertDB(time,number,x1,y1,t1,x2,y2,t2,level,level2,level3):
# def insertDB(devId, devFactory, devType, saveTime, jdata):
    (db, cursor) = connetDB()
    # print(db,cursor)
    sql = 'INSERT INTO nantong(time,number,x1,y1,t1,x2,y2,t2,level,level2,level3) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        if cursor.execute(sql, (time,number,x1,y1,t1,x2,y2,t2,level,level2,level3)):
            print('successful saved.')
            db.commit()
    except:
        print('failed')
        db.rollback()
    return


def readSerial(c):
    com = 'com' + str(c)
    ser = serial.Serial(com, 115200, timeout=0.5)
    if not ser.isOpen(): ser.open()
    print('waiting data...南通数据')
    while True:
        time.sleep(1)
        if ser.inWaiting() > 0:  # 缓存中有数据
            s = ser.readline()
            hexstr = s.hex()
            startposition = hexstr.find('aa')
            endposition = hexstr.rfind('bb')
            data = hexstr[startposition:endposition + 2]  # 原始数据
            return data
        else:
            continue
    ser.close()


# 定义传感器类别字典
Sensor_Types = {'01': '裂缝', '02': '单轴倾斜', '26': '激光静力水准仪', '04': '双轴倾斜带温度', '05': '应变', '06': '温湿度'}
t = 0
while t < 2:
    time.sleep(1)
#     time=insertTime, number=devId, x1, y1, t1, x2, y2, t2, level, level2, level3
# AA 00 71 00 FF FF 23 10 59 00 62 05 01 04 01 00 66 71 00 00 97 36 00 46 20 00 02 04 01 01 08 11 01 00 17 04 00 46 20 00 03 19 00 00 24 76 00 00 00 04 04 19 00 00 65 24 00 00 00 04 05 19 00 00 06 08 00 00 00 04 BB
    try:
        # 采集数据
        data = readSerial(4)
        print(data)
        # 计算机本地时间
        insertTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 入库savetime
        print(insertTime)
        # 解析数据
        data = data[6:]
        # acqtime = "20" + data[0:2] + "-" + data[2:4] + "-" + data[4:6] + " " + data[6:8] + ":" + data[8:10] + ":" + data[10:12]  # 采集仪日期
        data = data[12:]
        devId = data[0:4]  # 采集仪编号 入库
        print(devId)
        # devFactory = '常州比天智能科技有限公司'  # 入库
        # devType = 'BT-16'  # 入库
        data = data[4:]
        Sensor_All = int(data[0:2])  # 传感器数量
        print(Sensor_All)
        data = data[2:]
        dataout = []
        klist04 = ['ch', 'type', 'datax', 'datay', 'temp']
        klist26 = ['ch', 'type', 'data']
        for each in range(0, Sensor_All):
            da = []
            sn = str(data[0:2])  # numID
            st = str(data[2:4])  # type
            Sensor_T = Sensor_Types[st]
            da.append(sn)
            if st == "04":
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
                # eachdata = dict(zip(klist04, da))
                # dataout.append(eachdata)
                # print(da)
            elif st == '19':
                if int(data[4:6]) == 0:
                    dataX = float(data[6:8] + data[8:10] + data[10:12]) / 100
                elif int(data[4:6]) == 1:
                    dataX = -float(data[6:8] + data[8:10] + data[10:12]) / 100
                else:
                    dataX = -1
                da.append(dataX)
                data = data[20:]
                # eachdata = dict(zip(klist26, da))
                # dataout.append(eachdata)
            print(da)
            dataout.append(da)
        print(dataout)
        # jdata = json.dumps(dataout, ensure_ascii=False)  # 入库 jdata
        # print(jdata)
        # insertDB(insertTime,devId, jdata)
    except:
        continue
